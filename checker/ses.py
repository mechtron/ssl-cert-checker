import os
import time

import boto3

from dynamo import update_ses_subscription_email_sent_status


SES_CLIENT = boto3.client('ses')
SES_FROM_EMAIL = os.environ.get("SES_FROM_EMAIL")


def subscribe_email_to_ses(check):
    print("Subscribing {} to SES..".format(check["notification_target"]))
    response = SES_CLIENT.verify_email_identity(
        EmailAddress=check["notification_target"],
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
    update_ses_subscription_email_sent_status(check["id"], True)


def email_is_verified(email):
    print("Looking-up verified SES email addresses..")
    response = SES_CLIENT.list_verified_email_addresses()
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
    for verified_email in response["VerifiedEmailAddresses"]:
        if verified_email == email:
            print("{} was already verified!".format(email))
            return True
    print("{} needs to be verified".format(email))
    return False


def send_email_notification(check, subject, message):
    if not check["subscription_email_sent"]:
        if email_is_verified(check["notification_target"]):
            update_ses_subscription_email_sent_status(check["id"], True)
        else:
            subscribe_email_to_ses(check)
    print("Sending email notification to {}..".format(
        check["notification_target"],
    ))
    response = SES_CLIENT.send_email(
        Destination={
            'ToAddresses': [check["notification_target"]],
        },
        Message={
            'Body': {
                'Text': {
                    'Charset': 'UTF-8',
                    'Data': message,
                },
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': subject,
            },
        },
        Source=SES_FROM_EMAIL,
    )
    assert "MessageId" in response
