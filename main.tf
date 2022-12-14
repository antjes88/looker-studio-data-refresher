provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_storage_bucket" "destination" {
  name                        = var.bucket_name
  storage_class               = "STANDARD"
  location                    = var.region
  uniform_bucket_level_access = false

}

resource "google_service_account" "default" {
  account_id = var.service_account_name
  display_name = "Looker Studio Data Refresher Cloud Function SA"
}

resource "google_project_iam_binding" "sql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"

  members = [
    "serviceAccount:${google_service_account.default.email}",
  ]
}

resource "google_project_iam_binding" "secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"

  members = [
    "serviceAccount:${google_service_account.default.email}",
  ]
}

resource "google_storage_bucket_iam_binding" "binding" {
  bucket = google_storage_bucket.destination.name
  role = "roles/storage.admin"
  members = [
    "serviceAccount:${google_service_account.default.email}",
  ]
}

resource "google_storage_bucket" "source_code" {
  name                        = "${var.cloud_function_name}-source-code-location"
  storage_class               = "STANDARD"
  location                    = var.region
  uniform_bucket_level_access = false
}

data "archive_file" "source" {
  type        = "zip"
  source_dir  = "${path.root}/cloud_function"
  output_path = "${path.root}/zip_to_cloud_function.zip"
}

resource "google_storage_bucket_object" "zip" {
  name   = "cloud-function-source-code-for-${var.cloud_function_name}.zip"
  bucket = google_storage_bucket.source_code.name
  source = data.archive_file.source.output_path
}

resource "google_pubsub_topic" "default" {
  name = "cloud-function-${var.cloud_function_name}"
}

resource "google_cloud_scheduler_job" "default" {
  name = "cloud-function-${var.cloud_function_name}"
  description = "Scheduler to trigger the cloud function: ${var.cloud_function_name}"
  schedule = "0 1 * * *"

  pubsub_target {
    topic_name = google_pubsub_topic.default.id
    data = base64encode("Trigger Cloud Function")
  }
}

resource "google_cloudfunctions_function" "ecb" {
  name                  = var.cloud_function_name

  runtime               = "python38"
  available_memory_mb   = 256
  timeout               = 240
  source_archive_bucket = google_storage_bucket.source_code.name
  source_archive_object = google_storage_bucket_object.zip.name
  entry_point           = var.function_entry_point
  service_account_email = google_service_account.default.email
  max_instances         = 3

  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = google_pubsub_topic.default.name
  }

  secret_environment_variables {
    key        = "DATABASE_NAME"
    project_id = var.project_id
    secret     = var.secret_database_name
    version    = "latest"
  }
  secret_environment_variables {
    key        = "DATABASE_PORT_N"
    project_id = var.project_id
    secret     = var.secret_port
    version    = "latest"
  }
  secret_environment_variables {
    key        = "SERVER_HOST"
    project_id = var.project_id
    secret     = var.secret_server
    version    = "latest"
  }
  secret_environment_variables {
    key        = "USER_NAME"
    project_id = var.project_id
    secret     = var.secret_db_user
    version    = "latest"
  }
  secret_environment_variables {
    key        = "USER_PASSWORD"
    project_id = var.project_id
    secret     = var.secret_db_password
    version    = "latest"
  }
  environment_variables = {
    BUCKET_NAME_LOOKER_STUDIO = var.bucket_name
  }
}