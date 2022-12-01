from cloud_function.looker_studio_data_refresher import LookerStudioDataRefresher
import os
import pandas as pd


def test_class_correct_data(capfd, storage_client, populate_good_data_to_database, remove_files_from_test_bucket):
    """
    GIVEN some files to be created at a GCP Bucket
    WHEN it is processed by class LookerStudioDataRefresher()
    THEN check that the file are created at destination and the content is the right one
    """
    df = populate_good_data_to_database
    my_data_refresher = LookerStudioDataRefresher()
    my_data_refresher.create_data_reports()
    out, err = capfd.readouterr()
    out = out.split('\n')

    results = []
    for blob in storage_client.list_blobs(os.environ['BUCKET_NAME_LOOKER_STUDIO']):
        results.append(pd.read_csv(
            'gs://%s/%s' % (os.environ['BUCKET_NAME_LOOKER_STUDIO'],
                            blob.name)).drop(columns=['created_date', 'id']))

    assert results.__len__() == 2
    for result in results:
        assert result.equals(df)
    assert 'Object: test1/test1.csv created on Bucket: %s' % os.environ['BUCKET_NAME_LOOKER_STUDIO'] in out[0]
    assert 'Object: test2/test2.csv created on Bucket: %s' % os.environ['BUCKET_NAME_LOOKER_STUDIO'] in out[1]


def test_class_incorrect_data(capfd, storage_client, populate_bad_data_to_database, remove_files_from_test_bucket):
    """
    GIVEN some files to be created at a GCP Bucket being one of the records one with an invalid query
    WHEN it is processed by class LookerStudioDataRefresher()
    THEN check that the first record is correctly created and the second creates the error message
    """
    df = populate_bad_data_to_database
    my_data_refresher = LookerStudioDataRefresher()
    my_data_refresher.create_data_reports()
    out, err = capfd.readouterr()
    out = out.split('\n')

    results = []
    for blob in storage_client.list_blobs(os.environ['BUCKET_NAME_LOOKER_STUDIO']):
        results.append(pd.read_csv(
            'gs://%s/%s' % (os.environ['BUCKET_NAME_LOOKER_STUDIO'],
                            blob.name)).drop(columns=['created_date', 'id']))

    assert '' in out
    assert results.__len__() == 1
    for result in results:
        assert result.equals(df)
    assert 'Object: test1/test1.csv created on Bucket: %s' % os.environ['BUCKET_NAME_LOOKER_STUDIO'] in out[0]
    assert 'When creating Query: test2 next Error occurred:' in out[1]
