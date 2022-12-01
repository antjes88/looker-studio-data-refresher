# public libraries
import pytest
import os
from postgresql_interface.postgresql_interface import postgres_sql_connector_factory
from google.cloud import storage
import pandas as pd


@pytest.fixture(scope='session')
def db_conn():
    """
    Fixture that returns connector to database.

    Returns: API to interact with database in a sql manner.
    """
    return postgres_sql_connector_factory(
        vendor='gcp', host=os.environ['SERVER_HOST'], database_name=os.environ['DATABASE_NAME'],
        user_name=os.environ['USER_NAME'], user_password=os.environ['USER_PASSWORD'],
        port=os.environ['DATABASE_PORT_N'])


@pytest.fixture(scope='session')
def storage_client():
    """
    Fixture that returns client to connect to Cloud Storage.

    Returns: client to connect to Cloud Storage.
    """
    return storage.Client()


@pytest.fixture(scope='function')
def remove_files_from_test_bucket(storage_client):
    """
    Fixture that deletes all object from environment variable: BUCKET_NAME_LOOKER_STUDIO
    """
    for blob in storage_client.list_blobs(os.environ['BUCKET_NAME_LOOKER_STUDIO']):
        blob.delete()

    yield

    for blob in storage_client.list_blobs(os.environ['BUCKET_NAME_LOOKER_STUDIO']):
        blob.delete()


@pytest.fixture(scope='function')
def populate_good_data_to_database(db_conn):
    """
    Fixture that populates table controls.looker_studio_reports_configuration with 2 records for test purposes.

    :param db_conn: connector to PostgreSQL database
    """
    df = pd.DataFrame.from_dict({
        'bucket_object_name': ['test1/test1.csv', 'test2/test2.csv'],
        'query_nickname': ['test1', 'test2'],
        'query': ['SELECT * FROM controls.looker_studio_reports_configuration'] * 2,
        'created_by': ['Antonio'] * 2,
    })
    db_conn.insert_table('controls.looker_studio_reports_configuration', df, truncate=True)

    yield df

    db_conn.execute("TRUNCATE TABLE controls.looker_studio_reports_configuration")


@pytest.fixture(scope='function')
def populate_bad_data_to_database(db_conn):
    """
    Fixture that populates table controls.looker_studio_reports_configuration with 2 records for test purposes being one
    of those incorrectly setup.

    :param db_conn: connector to PostgreSQL database
    """
    df = pd.DataFrame.from_dict({
        'bucket_object_name': ['test1/test1.csv', 'test2/test2.csv'],
        'query_nickname': ['test1', 'test2'],
        'query': ['SELECT * FROM controls.looker_studio_reports_configuration',
                  'SELECT controls.looker_studio_reports_configuration'],
        'created_by': ['Antonio'] * 2,
    })
    db_conn.insert_table('controls.looker_studio_reports_configuration', df, truncate=True)

    yield df

    db_conn.execute("TRUNCATE TABLE controls.looker_studio_reports_configuration")
