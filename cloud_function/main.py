from looker_studio_data_refresher import *


def func_entry_point(event, context):
    """
    Entry point to the Python solution for the GCP Function Execution.
    This function creates an instance of class LookerStudioDataRefresher() and executes the update/creation of the
    object such as it is stated on table controls.looker_studio_reports_configuration.

    Args:
         event: The dictionary with data specific to this type of event. The `@type` field maps to
                `type.googleapis.com/google.pubsub.v1.PubsubMessage`. The `data` field maps to the PubsubMessage data
                in a base64-encoded string. The `attributes` field maps to the PubsubMessage attributes
                if any is present.
         context: Metadata of triggering event including `event_id` which maps to the PubsubMessage
                  messageId, `timestamp` which maps to the PubsubMessage publishTime, `event_type` which maps to
                  `google.pubsub.topic.publish`, and `resource` which is a dictionary that describes the service
                  API endpoint pubsub.googleapis.com, the triggering topic's name, and the triggering event type
                  `type.googleapis.com/google.pubsub.v1.PubsubMessage`.
    Returns:
        None
    """
    my_data_refresher = LookerStudioDataRefresher()
    my_data_refresher.create_data_reports()
