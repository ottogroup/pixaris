from google.cloud import bigquery


def python_type_to_bq_type(python_type):
    """
    Maps a Python data type to a corresponding BigQuery data type.

    :param python_type: The Python data type to map.
    :type python_type: type
    :return: The corresponding BigQuery data type as a string.
    :rtype: str
    """
    type_mapping = {
        str: "STRING",
        int: "INTEGER",
        float: "FLOAT",
        bool: "BOOLEAN",
        bytes: "BYTES",
    }
    return type_mapping.get(
        python_type, "STRING"
    )  # Default to STRING if type is unknown, such as datetime


def create_schema_from_dict(data_dict):
    """
    Creates a BigQuery schema from a dictionary of data.

    :param data_dict: A dictionary where keys are field names and values are field values.
    :type data_dict: dict
    :return: A list of BigQuery SchemaField objects.
    :rtype: list[bigquery.SchemaField]
    """
    schema = []
    for key, value in data_dict.items():
        field_type = python_type_to_bq_type(type(value))
        schema.append(
            bigquery.SchemaField(name=key, field_type=field_type, mode="NULLABLE")
        )
    return schema


def ensure_table_exists(
    table_ref: str, bigquery_input: dict, bigquery_client: bigquery.Client
):
    """
    Ensures that the BigQuery table exists with the correct schema.

    :param table_ref: The reference to the BigQuery table.
    :type table_ref: str
    :param bigquery_input: The dictionary used to generate the schema.
    :type bigquery_input: dict
    """
    schema = create_schema_from_dict(bigquery_input)

    try:
        table = bigquery_client.get_table(table_ref)
        if table.schema != schema:
            raise ValueError(f"Schema mismatch for table {table_ref}.")
    except Exception:
        table = bigquery.Table(table_ref, schema=schema)
        bigquery_client.create_table(table)
        print(f"Created table {table_ref}.")
