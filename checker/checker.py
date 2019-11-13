from datetime import datetime
import pytz
import time

from dynamo import (
    create_failed_check,
    get_checks,
    update_check_date,
)
from ses import send_email_notification
from test_ssl import test_ssl


def time_to_check(check):
    delta_seconds = (
        datetime.utcnow() - check["last_checked"]
    ).total_seconds()
    last_checked_minutes = delta_seconds / 60
    time_to_check = last_checked_minutes >= check["check_interval_minutes"]
    print("Time to check {hostname}:{port}? {result}".format(
        hostname=check["hostname"],
        port=check["port"],
        result=time_to_check,
    ))
    return time_to_check


def time_to_notify(check):
    delta_seconds = (
        datetime.now() - check["last_failure_notification"]
    ).total_seconds()
    last_failure_minutes = delta_seconds / 60
    time_no_notify = (
        last_failure_minutes >= check["notification_minutes_before_resending"]
    )
    print("Time to notify about {hostname}:{port} failure? {result}".format(
        hostname=check["hostname"],
        port=check["port"],
        result=time_no_notify,
    ))
    return time_no_notify


def generate_email_message(check, failed_result):
    subject = (
        "ssl-cert-checker | {} has failed SSL checks".format(
            check["hostname"],
        )
    )
    message = (
        "{host}:{port} has failed SSL checks at "
        "{timestamp} due to {failure_mode}"
    ).format(
        host=check["hostname"],
        port=check["port"],
        timestamp=failed_result["timestamp"],
        failure_mode=failed_result["failure_mode"],
    )
    return subject, message


def main():
    checks = get_checks()
    for check in checks:
        if time_to_check(check):
            result = test_ssl(check['hostname'], check['port'])
            now = int(time.time())
            update_check_date(check["id"], "LastChecked", now)
            if not result["check_pass"]:
                create_failed_check(check, result)
                update_check_date(check["id"], "LastFailure", now)
                if time_to_notify(check):
                    subject, message = generate_email_message(check, result)
                    send_email_notification(check, subject, message)
                    update_check_date(
                        check["id"], "LastFailureNotification", now
                    )


def handler(_event, _context):
    main()


if __name__ == "__main__":
    main()
