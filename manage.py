#!/usr/bin/env python3

import argparse
from prettytable import PrettyTable

from checker.dynamo import (
    create_check,
    delete_check,
    get_checks,
    get_failed_checks,
)


def print_checks(checks):
    table = PrettyTable([
        "Id", "Hostname", "Port", "CheckIntervalMinutes", 
        "NotificationTarget", "SubscriptionEmailSent",
        "NotificationMinutesBeforeResending", "CertExpiryNotifyBeforeDays",
        "LastChecked", "LastFailure", "LastFailureNotification",
        "FailedChecksRetentionDays", "Created"
    ])
    for check in checks:
        table.add_row([
            check["id"],
            check["hostname"],
            check["port"],
            check["check_interval_minutes"],
            check["notification_target"],
            check["subscription_email_sent"],
            check["notification_minutes_before_resending"],
            check["cert_expiry_notify_before_days"],
            check["last_checked"],
            check["last_failure"],
            check["last_failure_notification"],
            check["failed_check_retention_days"],
            check["created"],
        ])
    print(table)


def print_failed_checks(failed_checks):
    table = PrettyTable([
        "Id", "CheckId", "FailureTimestamp", "FailureMode", "CertExpiry",
    ])
    for failed_check in failed_checks:
        table.add_row([
            failed_check["id"],
            failed_check["check_id"],
            failed_check["timestamp"],
            failed_check["failure_mode"],
            failed_check["cert_expiry"],
        ])
    print(table)


def manage_checks(parsed_args):
    if parsed_args.action == "create":
        create_check(parsed_args)
    elif parsed_args.action == "delete":
        delete_check(parsed_args.id)
    elif parsed_args.action == "list":
        checks = get_checks()
        print_checks(checks)
    elif parsed_args.action == "list-failures":
        failed_checks = get_failed_checks()
        print_failed_checks(failed_checks)
    else:
        raise ValueError("Invalid action {}".format(parsed_args.action))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="ssl-cert-checker management interface"
    )
    parser.add_argument(
        "--action",
        "-a",
        help='Action (create, delete, list or list-failures)',
        choices=["create", "delete", "list", "list-failures"],
        required=True,
    )
    parser.add_argument(
        "--id",
        help="Check ID to delete (optional)",
        default=None,
    )
    parser.add_argument(
        "--hostname",
        help="The hostname of the target service",
        default=None,
    )
    parser.add_argument(
        "--port",
        help="The port of the target service ",
        type=int,
        default=443,
    )
    parser.add_argument(
        "--check-interval-minutes",
        help="How often (in minutes) to check the target hostname",
        type=int,
        default=15,
    )
    parser.add_argument(
        "--notification-target",
        help="The target address to send failure notifications to",
        default=None,
    )
    parser.add_argument(
        "--notification-minutes-before-resending",
        help="How long (in minutes) before re-sending failure notifications",
        type=int,
        default=60,
    )
    parser.add_argument(
        "--cert-expiry-notify-before-days",
        help="Notify this many days before certificate expires",
        type=int,
        default=30,
    )
    parser.add_argument(
        "--failed-checks-retention-days",
        help=(
            "How long (in days) to retain records of failed checks "
            "in DynamoDB (enter 0 for unlimited storage)"
        ),
        type=int,
        default=0,
    )
    parsed_args = parser.parse_args()
    manage_checks(parsed_args)
