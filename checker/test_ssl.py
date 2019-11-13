import subprocess
import time


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


def test_ssl(hostname, port=443):
    url = "https://{hostname}:{port}".format(
        hostname=hostname,
        port=port,
    )
    print("Checking {}'s SSL..".format(url))
    curl_command = (
        "curl -L -fail --silent -o /dev/null --max-time 5 {}"
    ).format(url)
    proc = subprocess.Popen(curl_command, shell=True)
    proc.wait()
    return_dict = dict(timestamp=int(time.time()))
    if proc.returncode is 0:
        return_dict["check_pass"] = True
    else:
        return_dict["check_pass"] = False
        return_dict["failure_mode"] = curl_exit_code_to_error_code(
            proc.returncode,
        )
        print(
            "{url} failed the SSL connectivity test due to {reason}".format(
                url=url,
                reason=return_dict["failure_mode"],
            )
        )
    return return_dict
