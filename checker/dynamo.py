import csv
from datetime import datetime
import os
import time
import uuid

import boto3


DYNAMODB_CLIENT = boto3.client('dynamodb')
DYNAMODB_TABLE_NAME_CHECKS = os.environ.get('DYNAMODB_TABLE_NAME_CHECKS')
DYNAMODB_TABLE_NAME_FAILURES = os.environ.get('DYNAMODB_TABLE_NAME_FAILURES')


def create_check(parsed_args):
    print("Creating new check for {}".format(parsed_args.hostname))
    response = DYNAMODB_CLIENT.put_item(
        TableName=DYNAMODB_TABLE_NAME_CHECKS,
        Item={
            "Id": {
                "S": str(uuid.uuid4())[:8],
            },
            "Hostname": {
                "S": parsed_args.hostname,
            },
            "Port": {
                "N": str(parsed_args.port),
            },
            "CheckIntervalMinutes": {
                "N": str(parsed_args.check_interval_minutes),
            },
            "LastChecked": {
                "N": "-1",
            },
            "LastFailure": {
                "N": "-1",
            },
            "NotificationTarget": {
                "S": str(parsed_args.notification_target),
            },
            "NotificationTargetIsSnsSubscribed": {
                "BOOL": False,
            },
            "NotificationMinutesBeforeResending": {
                "N": str(parsed_args.notification_minutes_before_resending),
            },
            "CertExpiryNotifyBeforeDays": {
                "N": str(parsed_args.cert_expiry_notify_before_days),
            },
            "FailedChecksRetentionDays": {
                "N": str(parsed_args.failed_checks_retention_days),
            },
            "Created": {
                "N": str(int(time.time())),
            },
        }
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] is 200
    print("New SSL check for {} successfully created".format(
        parsed_args.hostname,
    ))


def get_checks():
    print("Retrieving list of ongoing SSL checks from DynamoDB..")
    checks = []
    response = DYNAMODB_CLIENT.scan(
        TableName=DYNAMODB_TABLE_NAME_CHECKS,
        Select="ALL_ATTRIBUTES",
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] is 200
    for check in response["Items"]:
        checks.append(dict(
            id=check["Id"]["S"],
            hostname=check["Hostname"]["S"],
            port=int(check["Port"]["N"]),
            check_interval_minutes=int(check["CheckIntervalMinutes"]["N"]),
            notification_target=check["NotificationTarget"]["S"],
            notification_target_is_sns_subscribed=bool(
                check["NotificationTargetIsSnsSubscribed"]["BOOL"]
            ),
            notification_minutes_before_resending=int(
                check["NotificationMinutesBeforeResending"]["N"]
            ),
            cert_expiry_notify_before_days=int(
                check["CertExpiryNotifyBeforeDays"]["N"]
            ),
            last_checked=datetime.fromtimestamp(int(
                check["LastChecked"]["N"]
            )),
            last_failure=datetime.fromtimestamp(int(
                check["LastFailure"]["N"]
            )),
            failed_check_retention_days=datetime.fromtimestamp(int(
                check["FailedChecksRetentionDays"]["N"]
            )),
            created=datetime.fromtimestamp(int(
                check["Created"]["N"]
            ))
        ))
    print("{} SSL check(s) successfully loaded".format(len(checks)))
    return checks


def delete_check(check_id):
    response = DYNAMODB_CLIENT.delete_item(
        TableName=DYNAMODB_TABLE_NAME_CHECKS,
        Key={"Id": {"S": check_id}},
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] is 200
    print("SSL check with ID {} was successfully deleted".format(check_id))


def update_check_date(check_id, field_name, epoch_time):
    response = DYNAMODB_CLIENT.update_item(
        TableName=DYNAMODB_TABLE_NAME_CHECKS,
        Key={"Id": {"S": check_id}},
        UpdateExpression="SET {} = :value".format(field_name),
        ExpressionAttributeValues={":value": {"N": str(epoch_time)}},
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] is 200
    print(
        "Check with ID {check_id} {field_name} updated to {new_date}".format(
            check_id=check_id,
            field_name=field_name,
            new_date=epoch_time,
        )
    )


def update_sns_subscription_status(check_id, status):
    response = DYNAMODB_CLIENT.update_item(
        TableName=DYNAMODB_TABLE_NAME_CHECKS,
        Key={"Id": {"S": check_id}},
        UpdateExpression="SET NotificationTargetIsSnsSubscribed = :value",
        ExpressionAttributeValues={":value": {"BOOL": status}},
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] is 200
    print(
        "Check with ID {check_id} SNS subscription "
        "status updated to {new_status}".format(
            check_id=check_id,
            new_status=status,
        )
    )


def create_failed_check(check, failed_result):
    if not "cert_expiry" in failed_result:
        failed_result["cert_expiry"] = "-1"
    response = DYNAMODB_CLIENT.put_item(
        TableName=DYNAMODB_TABLE_NAME_FAILURES,
        Item={
            "Id": {
                "S": str(uuid.uuid4())[:8],
            },
            "CheckId": {
                "S": check["id"],
            },
            "FailureTimestamp": {
                "N": str(failed_result["failure_timestamp"]),
            },
            "FailureMode": {
                "S": failed_result["failure_mode"],
            },
            "CertExpiry": {
                "N": failed_result["cert_expiry"],
            },
        }
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] is 200
    print(
        "Successfully stored failed check for "
        "{host}:{port} in DynamoDB".format(
            host=check["hostname"],
            port=check["port"],
        )
    )


def get_failed_checks():
    print("Retrieving list of failed SSL checks from DynamoDB..")
    failed_checks = []
    response = DYNAMODB_CLIENT.scan(
        TableName=DYNAMODB_TABLE_NAME_FAILURES,
        Select="ALL_ATTRIBUTES",
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] is 200
    for failed_check in response["Items"]:
        failed_checks.append(dict(
            id=failed_check["Id"]["S"],
            check_id=failed_check["CheckId"]["S"],
            failure_timestamp=datetime.fromtimestamp(int(
                failed_check["FailureTimestamp"]["N"]
            )),
            failure_mode=failed_check["IdFailureMode"]["S"],
            cert_expiry=datetime.fromtimestamp(int(
                failed_check["CertExpiry"]["N"]
            )),
        ))
    print("{} failed checks loaded".format(len(failed_checks)))
    return failed_checks
