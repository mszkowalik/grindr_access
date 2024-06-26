import pycurl
import json
import zlib
from utils import gen_l_dev_info
import logging

def generic_post(path, data, auth_token=None):
    response_data = []

    request_data = data

    data_json = json.dumps(request_data)
    c = pycurl.Curl()
    c.setopt(c.URL, "https://grindr.mobi" + path)
    c.setopt(c.CUSTOMREQUEST, "POST")

    headers = [
        "accept: application/json",
        "accept-encoding: gzip",
        "accept-language: en-US",
        "connection: Keep-Alive",
        "content-type: application/json; charset=UTF-8",
        "host: grindr.mobi",
        f"l-device-info: {gen_l_dev_info()}",
        "l-locale: en_US",
        "l-time-zone: Europe/Oslo",
        "requirerealdeviceinfo: true",
        "user-agent: grindrx/24.0.6 (iPhone; iOS 17.3.1; Scale/3.00)",
    ]

    if auth_token is not None:
        headers.append("authorization: Grindr3 " + auth_token)

    c.setopt(c.HTTPHEADER, headers)

    c.setopt(c.POSTFIELDS, data_json)

    def handle_response(data):
        response_data.append(data)

    c.setopt(c.WRITEFUNCTION, handle_response)
    c.perform()
    c.close()

    response_data_source = response_data
    response_data = b"".join(response_data)
    try:
        decompressed_response = zlib.decompress(response_data, zlib.MAX_WBITS | 16)

    except zlib.error:
        print(response_data_source)
        logging.debug("Error decompressing response")
        decompressed_response = ""
        return None

    return json.loads(decompressed_response)


def generic_get(path, data, auth_token=None):
    response_data = []

    request_data = data

    c = pycurl.Curl()

    c.setopt(
        c.URL,
        "https://grindr.mobi"
        + path
        + "?"
        + "&".join([key + "=" + request_data[key] for key in request_data]),
    )
    c.setopt(c.CUSTOMREQUEST, "GET")

    headers = [
        "accept: application/json",
        "accept-encoding: gzip",
        "accept-language: en-US",
        "connection: Keep-Alive",
        "content-type: application/json; charset=UTF-8",
        "host: grindr.mobi",
        f"l-device-info: {gen_l_dev_info()}",
        "l-locale: en_US",
        "l-time-zone: Europe/Oslo",
        "requirerealdeviceinfo: true",
        "user-agent: grindrx/24.0.6 (iPhone; iOS 17.3.1; Scale/3.00)",
    ]

    if auth_token is not None:
        headers.append("authorization: Grindr3 " + auth_token)

    c.setopt(c.HTTPHEADER, headers)

    def handle_response(data):
        response_data.append(data)

    c.setopt(c.WRITEFUNCTION, handle_response)
    c.perform()
    c.close()

    response_data = b"".join(response_data)

    decompressed_response = zlib.decompress(response_data, zlib.MAX_WBITS | 16)
    return json.loads(decompressed_response)

def cdn_get(path, auth_token=None):
    response_data = []

    c = pycurl.Curl()

    c.setopt(
        c.URL,
        "https://cdns.grindr.com"
        + path
    )
    c.setopt(c.CUSTOMREQUEST, "GET")

    headers = [
        "accept: application/json",
        "accept-encoding: gzip",
        "accept-language: en-US",
        "connection: Keep-Alive",
        "content-type: application/json; charset=UTF-8",
        "host: cdns.grindr.com",
        # f"l-device-info: {gen_l_dev_info()}",
        'l-device-info: 2938f76cff50af57;GLOBAL;2;2069590016;2277x1080;a9ffffa4-2b0e-479d-b3db-ae117c0a9686'
        "l-locale: en_US",
        "l-time-zone: Europe/Oslo",
        "requirerealdeviceinfo: true",
        "user-agent: grindr3/9.17.3.118538;118538;Free;Android 14;sdk_gphone64_x86_64;Google",
        # "user-agent: grindrx/24.0.6 (iPhone; iOS 17.3.1; Scale/3.00)",
    ]

    # if auth_token is not None: 
    #     headers.append("authorization: Grindr3 " + auth_token)

    c.setopt(c.HTTPHEADER, headers)

    def handle_response(data):
        response_data.append(data)

    c.setopt(c.WRITEFUNCTION, handle_response)
    c.perform()
    c.close()

    response_data = b"".join(response_data)

    return response_data