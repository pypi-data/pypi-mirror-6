from optparse import make_option

from django.core.management.base import BaseCommand
from elasticutils import get_es
from pyelasticsearch.exceptions import IndexAlreadyExistsError, ElasticHttpError

from elastimorphic.conf import settings
from elastimorphic.models import polymorphic_indexable_registry


class Command(BaseCommand):
    args = "<?index_suffix>"
    help = "Creates indexes and mappings for for PolymorphicIndexable objects."
    option_list = BaseCommand.option_list + (
        make_option("--drop-existing-indexes",
            action="store_true",
            dest="drop_existing_indexes",
            default=False,
            help="Recreate existing indexes"
        ),
        make_option("--force",
            action="store_true",
            dest="force",
            default=False,
            help="Force a close and reopen to update analysis settings"
        ),
    )

    def handle(self, *args, **options):
        es = get_es(urls=settings.ES_URLS)
        index_alias_map = {}
        if args:
            index_suffix = args[0]
            index_suffix = "_" + index_suffix
        else:
            # No suffix supplied. Let's create a map of existing aliases -> indexes
            # and try to update those instead of creating new indexes.
            index_suffix = ""
            aliases = es.aliases()
            for index_name in aliases:
                index_aliases = aliases[index_name]["aliases"]
                if index_aliases:
                    index_alias_map[index_aliases.keys()[0]] = index_name

        # build a dict of index -> mapping type configurations
        indexes = {}
        for name, model in polymorphic_indexable_registry.all_models.items():
            index = model.get_index_name()
            if index_suffix:
                index = index + index_suffix
            else:
                index = index_alias_map[index]
            if index not in indexes:
                indexes[index] = {}
            indexes[index].update(model.get_mapping())

        for index, mappings in indexes.items():
            if options.get("drop_existing_indexes", False) and index_suffix:
                try:
                    es.delete_index(index)
                except ElasticHttpError:
                    pass

            try:
                es.create_index(index, settings={
                    "settings": settings.ES_SETTINGS
                })
            except IndexAlreadyExistsError:
                try:
                    # TODO: Actually compare the settings.
                    es.update_settings(index, settings.ES_SETTINGS)
                except ElasticHttpError as e:
                    if e.status_code == 400:
                        if options.get("force", False):
                            es.close_index(index)
                            es.update_settings(index, settings.ES_SETTINGS)
                            es.open_index(index)
                        else:
                            self.stderr.write("Index '%s' already exists, and you're trying to update non-dynamic settings. You will need to use a new suffix, or use the --force option" % index)
                    else:
                        self.stderr.write("ElasticSearch Error: %s" % e)

            for doctype, mapping in mappings.items():
                try:
                    es.put_mapping(index, doctype, dict(doctype=mapping))
                except ElasticHttpError as e:
                    self.stderr.write("ES Error: %s" % e.error)
