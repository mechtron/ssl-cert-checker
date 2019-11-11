import os
import time

import boto3

from dynamo import update_sns_subscription_status


SNS_CLIENT = boto3.client('sns')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')


def subscribe_email_to_sns_topic(check, sns_topic):
    print("Subscribing {} to SNS topic..".format(
        check["notification_target"],
    ))
    response = SNS_CLIENT.subscribe(
        TopicArn=sns_topic,
        Protocol="email",
        Endpoint=check["notification_target"],
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
    update_sns_subscription_status(check["id"], True)


def send_email_notification(check, subject, message):
    if not check["notification_target_is_sns_subscribed"]:
        subscribe_email_to_sns_topic(check, SNS_TOPIC_ARN)
    print("Sending email notification to {}..".format(
        check["notification_target"],
    ))
    ses_client = boto3.client('ses')
    response = ses_client.send_email(
        Destination={
            'ToAddresses': [check["notification_target"],],
        },
        Message={
            'Body': {
                'Text': {'Data': message},
            },
            'Subject': {
                'Data': subject,
            },
        },
        Source="ssl-cert-notifier@lambda-funtion.local",
    )
    assert "MessageId" in response
