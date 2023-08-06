from __future__ import absolute_import

import copy
import datetime

from django.core.management import call_command
from django.test import TestCase

from elasticutils import get_es
from pyelasticsearch.exceptions import ElasticHttpError

from elastimorphic.conf import settings
from elastimorphic.models import polymorphic_indexable_registry

from .base import BaseIndexableTestCase
from .testapp.models import (
    ChildIndexable, GrandchildIndexable, ParentIndexable, SeparateIndexable)


class IndexableTestCase(BaseIndexableTestCase):

    def setUp(self):
        super(IndexableTestCase, self).setUp()

        ParentIndexable.objects.create(foo="Fighters")
        ChildIndexable.objects.create(foo="Fighters", bar=69)
        GrandchildIndexable.objects.create(foo="Fighters", bar=69, baz=datetime.datetime.now() - datetime.timedelta(hours=1))

        SeparateIndexable.objects.create(junk="Testing")

        ParentIndexable.search_objects.refresh()
        SeparateIndexable.search_objects.refresh()

    def test_mapping_type_names(self):
        self.assertEqual(ParentIndexable.get_mapping_type_name(), "testapp_parentindexable")
        self.assertEqual(ChildIndexable.get_mapping_type_name(), "testapp_childindexable")
        self.assertEqual(GrandchildIndexable.get_mapping_type_name(), "testapp_grandchildindexable")
        self.assertEqual(SeparateIndexable.get_mapping_type_name(), "testapp_separateindexable")
        self.assertEqual(
            ParentIndexable.get_mapping_type_names(), [
                ParentIndexable.get_mapping_type_name(),
                ChildIndexable.get_mapping_type_name(),
                GrandchildIndexable.get_mapping_type_name(),
            ]
        )
        self.assertEqual(
            SeparateIndexable.get_mapping_type_names(), [
                SeparateIndexable.get_mapping_type_name(),
            ]
        )

    def test_get_index_mappings(self):
        pass

    def test_primary_key_name_is_correct(self):
        a, b, c = [klass.get_mapping().values()[0]["_id"]["path"] for klass in (
            ParentIndexable, ChildIndexable, GrandchildIndexable
        )]
        self.assertEqual(a, b)
        self.assertEqual(b, c)

    def test_search(self):
        self.assertEqual(ParentIndexable.search_objects.s().count(), 3)
        self.assertEqual(ParentIndexable.search_objects.query(bar=69).count(), 2)
        self.assertEqual(ParentIndexable.search_objects.query(foo__match="Fighters").count(), 3)
        self.assertEqual(ParentIndexable.search_objects.query(baz__lte=datetime.datetime.now()).count(), 1)

        self.assertEqual(SeparateIndexable.search_objects.s().count(), 1)

    def test_instance_of(self):
        self.assertEqual(ParentIndexable.search_objects.s().instance_of(ParentIndexable, exact=True).count(), 1)
        self.assertEqual(ParentIndexable.search_objects.s().instance_of(ChildIndexable, exact=True).count(), 1)
        self.assertEqual(ParentIndexable.search_objects.s().instance_of(GrandchildIndexable, exact=True).count(), 1)

        self.assertEqual(ParentIndexable.search_objects.s().doctypes("testapp_parentindexable").count(), 1)
        self.assertEqual(ParentIndexable.search_objects.s().doctypes("testapp_childindexable").count(), 1)
        self.assertEqual(ParentIndexable.search_objects.s().doctypes("testapp_grandchildindexable").count(), 1)

        self.assertEqual(ParentIndexable.search_objects.s().instance_of(ParentIndexable).count(), 3)
        self.assertEqual(ParentIndexable.search_objects.s().instance_of(ChildIndexable).count(), 2)
        self.assertEqual(ParentIndexable.search_objects.s().instance_of(GrandchildIndexable).count(), 1)

    def test_model_results(self):
        qs = ParentIndexable.search_objects.s().full()
        for obj in qs:
            self.assertTrue(obj.__class__ in [ParentIndexable, ChildIndexable, GrandchildIndexable])

        self.assertEqual(len(qs[:2]), 2)

    def test_s_all_respects_slicing(self):
        s = ParentIndexable.search_objects.s()
        num_s = s.count()
        self.assertEqual(len(s), num_s)
        sliced = s[1:2]
        self.assertEqual(len(sliced.all()), 1)


class ManagementTestCase(BaseIndexableTestCase):

    def test_synces(self):
        backup_settings = copy.copy(settings.ES_SETTINGS)
        settings.ES_SETTINGS.update({
            "index": {
                "analysis": {
                    "tokenizer": {
                        "edge_ngram_test_tokenizer": {
                            "type": "edgeNGram",
                            "min_gram": "3",
                            "max_gram": "4"
                        }
                    }
                }
            }
        })
        call_command("synces", self.index_suffix, force=True)
        es_settings = self.es.get_settings(ParentIndexable.get_index_name())
        index_settings = es_settings[es_settings.keys()[0]]["settings"]
        self.assertTrue("index.analysis.tokenizer.edge_ngram_test_tokenizer.type" in index_settings)

        settings.ES_SETTINGS = backup_settings

    def test_bulk_index(self):
        ParentIndexable(foo="Fighters").save(index=False)
        ChildIndexable(foo="Fighters", bar=69).save(index=False)

        GrandchildIndexable(
            foo="Fighters",
            bar=69,
            baz=datetime.datetime.now() - datetime.timedelta(hours=1)
        ).save(index=False)

        SeparateIndexable(junk="Testing").save(index=False)

        # Let's make sure that nothing is indexed yet.
        self.assertEqual(ParentIndexable.search_objects.s().count(), 0)
        self.assertEqual(SeparateIndexable.search_objects.s().count(), 0)

        # Now that everything has been made, let's try a bulk_index.
        call_command("bulk_index")
        ParentIndexable.search_objects.refresh()
        SeparateIndexable.search_objects.refresh()

        # Let's make sure that everything has the right counts
        self.assertEqual(ParentIndexable.search_objects.s().count(), 3)
        self.assertEqual(SeparateIndexable.search_objects.s().count(), 1)

        # Let's add another one, make sure the counts are right.
        ParentIndexable(foo="Mr. T").save(index=False)
        self.assertEqual(ParentIndexable.search_objects.s().count(), 3)
        call_command("bulk_index")
        ParentIndexable.search_objects.refresh()
        self.assertEqual(ParentIndexable.search_objects.s().count(), 4)

        # Let's fuck up some data in ES.
        obj = ParentIndexable.objects.all()[0]
        es = get_es(urls=settings.ES_URLS)
        doc = obj.extract_document()
        doc["foo"] = "DATA LOVERS"
        es.update(obj.get_index_name(), obj.get_mapping_type_name(), obj.id, doc=doc, upsert=doc, refresh=True)

        # Make sure the bad data works
        self.assertEqual(ParentIndexable.search_objects.query(foo__match="DATA LOVERS").count(), 1)
        call_command("bulk_index")
        ParentIndexable.search_objects.refresh()
        self.assertEqual(ParentIndexable.search_objects.query(foo__match="DATA LOVERS").count(), 0)

        # Let's delete an item from the db.
        obj = ParentIndexable.objects.all()[0]
        obj.delete()

        # Make sure the count is the same
        self.assertEqual(ParentIndexable.search_objects.s().count(), 4)

        # This shoulnd't remove the item
        call_command("bulk_index")
        ParentIndexable.search_objects.refresh()
        self.assertEqual(ParentIndexable.search_objects.s().count(), 4)

        # This should
        call_command("synces", self.index_suffix, drop_existing_indexes=True)
        call_command("es_swap_aliases", self.index_suffix)
        call_command("bulk_index")
        ParentIndexable.search_objects.refresh()
        self.assertEqual(ParentIndexable.search_objects.s().count(), 3)

    def test_index_upgrade(self):
        ParentIndexable(foo="Fighters").save()
        ChildIndexable(foo="Fighters", bar=69).save()
        GrandchildIndexable(
            foo="Fighters",
            bar=69,
            baz=datetime.datetime.now() - datetime.timedelta(hours=1)
        ).save()
        SeparateIndexable(junk="Testing").save()
        # make sure we have some indexed stuff
        ParentIndexable.search_objects.refresh()
        SeparateIndexable.search_objects.refresh()
        self.assertEqual(ParentIndexable.search_objects.s().count(), 3)
        self.assertEqual(SeparateIndexable.search_objects.s().count(), 1)

        call_command("synces", "vtest123", drop_existing_indexes=True)
        call_command("bulk_index", index_suffix="vtest123")
        call_command("es_swap_aliases", "vtest123")
        ParentIndexable.search_objects.refresh()
        SeparateIndexable.search_objects.refresh()
        # Let's make sure that everything has the right counts
        self.assertEqual(ParentIndexable.search_objects.s().count(), 3)
        self.assertEqual(SeparateIndexable.search_objects.s().count(), 1)
        self.delete_indexes_with_suffix("vtest123")  # clean up


class TestDynamicMappings(BaseIndexableTestCase):

    def test_bad_index(self):
        """Check to make sure that the mappings are strict"""
        mapping = self.es.get_mapping(ParentIndexable.get_index_name(), ParentIndexable.get_mapping_type_name())
        self.assertDictEqual(mapping, ParentIndexable.get_mapping())

        obj = ParentIndexable.objects.create(foo="Fighters")
        ParentIndexable.search_objects.refresh()
        doc = obj.extract_document()
        doc["extra"] = "Just an additional string"

        with self.assertRaises(ElasticHttpError):
            self.es.update(
                obj.get_index_name(),
                obj.get_mapping_type_name(),
                obj.id,
                doc=doc,
                upsert=doc
            )

        mapping = self.es.get_mapping(ParentIndexable.get_index_name(), ParentIndexable.get_mapping_type_name())
        self.assertDictEqual(mapping, ParentIndexable.get_mapping())


class TestPolymorphicIndexableRegistry(TestCase):
    def test_registry_has_models(self):
        self.assertTrue(polymorphic_indexable_registry.all_models)
        self.assertTrue(polymorphic_indexable_registry.families)
        types = polymorphic_indexable_registry.get_doctypes(ParentIndexable)
        desired_classes = set([ParentIndexable, ChildIndexable, GrandchildIndexable])
        result_classes = set()
        for name, klass in types.items():
            result_classes.add(klass)
        self.assertEqual(desired_classes, result_classes)
