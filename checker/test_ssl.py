# import requests


def test_ssl(hostname, port):
    print("Checking {hostname}:{port}'s SSL..".format(
        hostname=hostname,
        port=port,
    ))
    # response = requests.get("{}".format(hostname))
    # print(response)
    return dict(
        check_pass=False,
        failure_mode="HOSTNAME_INVALID",
        failure_timestamp=-1,
    )
