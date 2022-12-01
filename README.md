# Looker Studio Data Refresher
Simple solution to upload Data Reports to a Cloud Storage Bucket, so they can be used as sources for Looker Studio 
Reports. This solution is needed due to the limitation on the number of connections that can be done simultaneously 
to a Cloud SQL instance that runs on a very small budget. 

These Data Reports are created from a Data Warehouse located on a Cloud SQL instance Database. On that same Cloud 
SQL Instance Database, should be a table, which schema can be found below, that provides configuration for 
all Data Reports to create.

```
CREATE SCHEMA controls;

CREATE TABLE controls.looker_studio_reports_configuration
(
    id SERIAL PRIMARY KEY,
    bucket_object_name VARCHAR(255),
    query_nickname VARCHAR(100),
    query VARCHAR,
    created_by VARCHAR(100),
    created_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP 
);

GRANT ALL ON SCHEMA controls to {_user};
GRANT ALL ON TABLE controls.looker_studio_reports_configuration TO {_user};
GRANT ALL ON SEQUENCE controls.looker_studio_reports_configuration_id_seq TO {_user};
```

Deployed with Terraform as a Cloud Function(GCP) which is triggered by a Pub/Sub Topic. Messages 
are posted to this Pub/Sub Topic by a Cloud Scheduler every day at 01:00 (midnight). The Python code is uploaded into a 
GCP Bucket. A Service Account is created and given Cloud SQL Client role so the Cloud Function can connect to Cloud SQL
instance, Secret Accessor role, so it can access Secrets from Secret Manager, and Admin Storage role for the destination 
Bucket. This Terraform code also creates the destination Bucket. Above SQL script has to be deployed manually.

## Terraform
Before Executing the Terraform code, the creation of 5 secrets on Secret Manager is needed to provide connection 
settings and credentials for the Cloud SQL instance. These are: host address, host port, database name, 
username with permission to update raw table and user password. Names for these secrets are open, 
as these names have to be provided on the file _*.tfvars_ which is not included on the repo.
Also, on the same file are provided id of the project, a name for the service account, a name for the cloud function
to create and a name for the destination bucket.

```terraform
secret_database_name = ""
secret_port          = ""
secret_server        = ""
secret_db_user       = ""
secret_db_password   = ""
service_account_name = ""
project_id           = ""
cloud_function_name  = ""
bucket_name          = ""
```

*The format for the value of the host is: "/cloudsql/{project_id}:{region}:{instance_name}"

Easier way to execute terraform code is to use an admin user. It can be done writing on CLI: 
```commandline
gcloud auth application-default login
```
Several APIs will need to be enabled. If any is not enabled, during deployment a message will be prompted to request the 
activation of the service.

## Testing
To execute the Python tests use next command on the CLI:
```commandline
python -m pytest -vv
```

It is needed a _.env_ file with the next settings and credentials to connect to a Cloud SQL instance. This file is
as follows:

```
SERVER_HOST = 
DATABASE_NAME = 
USER_NAME = 
USER_PASSWORD = 
DATABASE_PORT_N =
GOOGLE_APPLICATION_CREDENTIALS = 
BUCKET_NAME_LOOKER_STUDIO =  
```

*In this case, host is just the IP address.
**GOOGLE_APPLICATION_CREDENTIALS is the path to a SA json credentials.

The control table should have been previously created in the test database.

You will find a terraform code to create resources needed to execute the Pytest tests.