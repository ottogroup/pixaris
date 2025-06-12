import sys
import types
import unittest
from types import SimpleNamespace

# Create fake google.cloud.bigquery module for import
fake_bigquery = types.ModuleType("google.cloud.bigquery")


class FakeSchemaField(SimpleNamespace):
    pass


class FakeTable:
    def __init__(self, table_ref, schema=None):
        self.table_ref = table_ref
        self.schema = schema


class FakeBigQueryClient:
    def __init__(self):
        self.created_tables = {}
        self.existing_tables = {}

    def get_table(self, table_ref):
        if table_ref in self.existing_tables:
            return self.existing_tables[table_ref]
        raise Exception("Not found: Table")

    def create_table(self, table):
        self.created_tables[table.table_ref] = table
        self.existing_tables[table.table_ref] = table


# populate fake_bigquery namespace
fake_bigquery.SchemaField = FakeSchemaField
fake_bigquery.Table = FakeTable
fake_bigquery.Client = FakeBigQueryClient

sys.modules.setdefault("google", types.ModuleType("google"))
sys.modules.setdefault("google.cloud", types.ModuleType("google.cloud"))
sys.modules["google.cloud.bigquery"] = fake_bigquery

from pixaris.utils import bigquery as bq_utils  # noqa: E402


class TestBigQueryUtils(unittest.TestCase):
    def test_python_type_to_bq_type(self):
        self.assertEqual(bq_utils.python_type_to_bq_type(str), "STRING")
        self.assertEqual(bq_utils.python_type_to_bq_type(int), "INTEGER")
        self.assertEqual(bq_utils.python_type_to_bq_type(float), "FLOAT")
        self.assertEqual(bq_utils.python_type_to_bq_type(bool), "BOOLEAN")
        self.assertEqual(bq_utils.python_type_to_bq_type(bytes), "BYTES")
        # default case
        self.assertEqual(bq_utils.python_type_to_bq_type(dict), "STRING")

    def test_create_schema_from_dict(self):
        data = {"a": "text", "b": 1}
        schema = bq_utils.create_schema_from_dict(data)
        self.assertEqual(len(schema), 2)
        self.assertEqual(schema[0].name, "a")
        self.assertEqual(schema[0].field_type, "STRING")
        self.assertEqual(schema[1].field_type, "INTEGER")

    def test_ensure_table_exists_creates(self):
        client = FakeBigQueryClient()
        bq_utils.ensure_table_exists(
            "dataset.table",
            {"a": 1},
            client,
        )
        self.assertIn("dataset.table", client.created_tables)

    def test_ensure_table_exists_exists(self):
        client = FakeBigQueryClient()
        existing = FakeTable("dataset.table")
        client.existing_tables["dataset.table"] = existing
        bq_utils.ensure_table_exists(
            "dataset.table",
            {"a": 1},
            client,
        )
        # Should not create new table
        self.assertEqual(client.created_tables, {})


if __name__ == "__main__":
    unittest.main()
