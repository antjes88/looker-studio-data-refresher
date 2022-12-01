provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_storage_bucket" "default" {
  name                        = var.bucket_name
  storage_class               = "STANDARD"
  location                    = var.region
  uniform_bucket_level_access = false
}

resource "google_service_account" "default" {
  account_id = "${var.service_account_name}"
  display_name = "Test Looker Studio Data Refresher Cloud Function SA"
}

resource "google_storage_bucket_iam_binding" "binding" {
  bucket = google_storage_bucket.default.name
  role = "roles/storage.admin"
  members = [
    "serviceAccount:${google_service_account.default.email}",
  ]
}
