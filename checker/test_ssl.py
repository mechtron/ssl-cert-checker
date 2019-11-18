from datetime import datetime
import subprocess
import time

from certifier import CertInfo


def curl_exit_code_to_error_code(exit_code):
    error_codes = {
        6: "HOSTNAME_INVALID",
        7: "FAILED_TO_CONNECT",
        16: "HTTP2_ERROR",
        22: "400_LEVEL_STATUS_CODE",
        27: "CURL_OUT_OF_MEMORY",
        28: "CONNECTION_TIMED_OUT",
        33: "HTTP_RANGE_ERROR",
        35: "SSL_HANDSHAKE_FAILED",
        47: "TOO_MANY_REDIRECTS",
        51: "SSL_CERTIFICATE_SIGNATURE_INVALID",
        52: "SSL_EMPTY_RESPONSE",
        55: "CURL_NETWORK_FAILED_SEND",
        56: "CURL_NETWORK_FAILED_RECEIVE",
        58: "CURL_SSL_LOCAL_CERTIFICATE_ERROR",
        60: "SSL_CERTIFICATE_EXPIRED",
        77: "CURL_SSL_CA_CERTIFICATE_READ_ERROR",
        80: "CURL_SSL_CONNECTION_CLOSURE_FAILED",
        83: "SSL_CERTIFICATE_ISSUER_CHECK_FAILED",
        90: "SSL_PUBLIC_KEY_DOES_NOT_MATCH_PINNED_KEY",
        91: "SSL_CERTIFICATE_STATUS_INVALID",
    }
    if exit_code in error_codes:
        return error_codes[exit_code]
    return "CURL_UNKNOWN_EXIT_CODE_{}".format(exit_code)


def test_ssl_with_curl(url):
    print("Checking {}'s SSL with curl..".format(url))
    curl_command = (
        "curl -L -fail --silent -o /dev/null --max-time 5 https://{}"
    ).format(url)
    proc = subprocess.Popen(curl_command, shell=True)
    proc.wait()
    if proc.returncode is 0:
        return True, None
    failure_mode = curl_exit_code_to_error_code(proc.returncode)
    print(
        "{url} failed the curl SSL connectivity test due to {reason}".format(
            url=url,
            reason=failure_mode,
        )
    )
    return False, failure_mode


def inspect_certificate(hostname, port, expiry_threshold_days):
    url = "{}:{}".format(hostname, port)
    print("Inspecting {}'s SSL certificate..".format(url))
    try:
        cert = CertInfo(hostname, port)
    except Exception as e:
        print("Error with {url}: {error_message}".format(
            url=url,
            error_message=e.verify_message,
        ))
        return dict(
            cert_expiry_datetime=None,
            check_pass=False,
            failure_mode=e.verify_message,
        )
    cert_expiry_datetime = (
        datetime.strptime(cert.expire(), "%b %d %H:%M:%S %Y GMT")
    )
    cert_expiry_epoch = int(cert_expiry_datetime.timestamp())
    delta_seconds = (cert_expiry_datetime - datetime.now()).total_seconds()
    days_until_expiry = delta_seconds / (24*60*60)
    if days_until_expiry <= expiry_threshold_days:
        print("SSL certificate for {url} is expiring soon! ({date})".format(
            url=url,
            date=cert_expiry_datetime,
        ))
        return dict(
            cert_expiry=cert_expiry_epoch,
            check_pass=False,
            failure_mode="SSL_CERTIFICATE_EXPIRING_SOON",
        )
    return dict(
        cert_expiry=cert_expiry_epoch,
        check_pass=True,
        failure_mode=None,
    )


def test_ssl(check):
    url = "{}:{}".format(check["hostname"], check["port"])
    return_dict = dict(timestamp=int(time.time()))
    curl_test_passed, curl_failure_mode = test_ssl_with_curl(url)
    if not curl_test_passed:
        return_dict["check_pass"] = False
        return_dict["failure_mode"] = curl_failure_mode
        return return_dict
    cert_test_result = inspect_certificate(
        check["hostname"],
        check["port"],
        check["cert_expiry_notify_before_days"],
    )
    return_dict["check_pass"] = True
    if not cert_test_result["check_pass"]:
        return_dict["check_pass"] = False
        return_dict["failure_mode"] = cert_test_result["failure_mode"]
        return_dict["cert_expiry"] = cert_test_result["cert_expiry"]
    return return_dict
