import os
from postgresql_interface.postgresql_interface import postgres_sql_connector_factory
from google.cloud import storage


class LookerStudioDataRefresher:
    """
    Class that uploads/creates all blobs as indicated on table: controls.looker_studio_reports_configuration.
    Solution is to upload blobs as csv files.
    """
    def __init__(self):
        self.db_conn = postgres_sql_connector_factory(
            vendor='gcp', host=os.environ['SERVER_HOST'], database_name=os.environ['DATABASE_NAME'],
            user_name=os.environ['USER_NAME'], user_password=os.environ['USER_PASSWORD'],
            port=os.environ['DATABASE_PORT_N'])
        self.config = self.get_config_from_database()
        self.storage_client = storage.Client()

    def get_config_from_database(self):
        """
        Method that returns the content of table controls.looker_studio_reports_configuration as a dataframe.

        :return:
            dataframe with the content of table controls.looker_studio_reports_configuration
        """
        return self.db_conn.query("SELECT * FROM controls.looker_studio_reports_configuration")

    def upload_to_gcp_bucket(self, df, bucket_name, bucket_object_name):
        """
        Method that creates/uploads the object bucket_object_name on bucket bucket_name. Content of object is the
        dataframe df. Files are uploaded as CSV.

        :param df: what is going to be populated into the object.
        :param bucket_name: name of the bucket where the file is going to be uploaded.
        :param bucket_object_name: name of the object at bucket.
        """
        bucket = self.storage_client.get_bucket(bucket_name)
        blob = bucket.blob(bucket_object_name)
        blob.upload_from_string(df.to_csv(index=False), 'text/csv')
        print("Object: %s created on Bucket: %s" % (bucket_object_name, bucket_name))

    def create_data_reports(self):
        """
        Method that iterates through self.config to create/update all blobs

        :raise:
            Print error message on Logs if there are problems when creating an object,
        """
        for index, row in self.config.iterrows():
            try:
                data = self.db_conn.query(row['query'])
                self.upload_to_gcp_bucket(data, os.environ['BUCKET_NAME_LOOKER_STUDIO'], row['bucket_object_name'])

            except Exception as error:
                print("When creating Query: %s next Error occurred: %s" % (row['query_nickname'], error))
