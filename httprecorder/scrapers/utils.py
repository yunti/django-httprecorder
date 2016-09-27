import random
import csv
import decimal
import requests
import json
import logging
import time
from urllib.parse import urlsplit
from collections import OrderedDict

from ..models import ApiResponse

logger = logging.getLogger(__name__)


def get_data(url, headers, method, params, data, recording_type):
    if recording_type == 1:
        response = scrape_data(url, headers, method, params, data)
        if response.status_code == 200:
            logger.info('{}: {}'.format(response.url, response.status_code))
            print('{}: {}'.format(response.url, response.status_code))
            save_api_response(response, params, data)
            return json.loads(response.text, parse_float=decimal.Decimal)
        else:
            logger.warning('{}: {} {}'.format(response.url, response.status_code, response.text))
            print('{}: {}'.format(response.url, response.status_code))
            instance = read_data(url, headers, method, params, data)
            if instance and instance.status_code == 200:
                print("Retrieved good data from db after bad scrape".format(url, method))
                return instance.response_json or instance.response_text
            save_api_response(response, params, data)
            return response.raise_for_status()

    instance = read_data(url, headers, method, params, data)
    if recording_type == 3:
        if instance:
            if instance.status_code != 200:
                return scrape_and_process_response(url, headers, method, params, data)
            else:
                return instance.response_json or instance.response_text
        else:
            return scrape_and_process_response(url, headers, method, params, data)
    elif recording_type == 4:
        if instance:
            if instance.status_code != 200:
                raise requests.HTTPError
            return instance.response_json or instance.response_text
        else:
            return scrape_and_process_response(url, headers, method, params, data)
    elif recording_type == 5:
        if instance:
            return instance.response_json or instance.response_text
        else:
            print('Unable to retrieve {}, {} from db'.format(url, method.upper()))
    elif recording_type == 6:
        response = scrape_data(url, headers, method, params, data)
        print('{}: {}'.format(response.url, response.status_code))
        response_json = json.loads(response.text)
        assert response_json == instance.response_json
        return instance.response_json
    else:
        raise ValueError("The recording type specified is not a valid option")


def scrape_data(url, headers, method, params, data):
    headers['User-Agent'] = random_user_agent()
    if data:
        headers['Content_Type'] = 'application/json'
    # TODO if data isn't json send via data=data
    time.sleep(random.random())
    response = requests.request(method, url=url, params=params, json=data, headers=headers)
    return response


def scrape_and_process_response(url, headers, method, params, data):
    response = scrape_data(url, headers, method, params, data)
    if response.status_code == 200:
        logger.info('{}: {}'.format(response.url, response.status_code))
        print('{}: {}'.format(response.url, response.status_code))
        save_api_response(response, params, data)
        return json.loads(response.text, parse_float=decimal.Decimal)
    else:
        logger.warning('{}: {} {}'.format(response.url, response.status_code, response.text))
        print('{}: {}'.format(response.url, response.status_code))
        save_api_response(response, params, data)
        return response.raise_for_status()


def _prepare_data(params, data):
    try:
        params = str(sort_nested_dict(params))
    except (TypeError, AttributeError):
        params = None
    try:
        data = str(sort_nested_dict(data))
    except (TypeError, AttributeError):
        data = None
    return params, data


def save_api_response(response, params, data):
    full_url = urlsplit(response.request.url)
    params, data = _prepare_data(params, data)
    try:
        response_json = response.json()
        response_text = None
    except ValueError:
        response_json = None
        response_text = response.text
    ApiResponse.objects.create(scheme=full_url.scheme,
                               hostname=full_url.hostname,
                               path=full_url.path,
                               method=response.request.method,
                               request_headers=str(response.request.headers),
                               query=params,
                               payload=data,
                               status_code=response.status_code,
                               response_headers=str(response.headers),
                               response_json=response_json,
                               response_text=response_text)


def read_data(url, headers, method, params, data):
    method = method.upper()
    full_url = urlsplit(url)
    sorted_params, sorted_data = _prepare_data(params, data)
    instance = ApiResponse.objects.filter(scheme=full_url.scheme,
                                          hostname=full_url.hostname,
                                          path=full_url.path,
                                          method=method,
                                          query=sorted_params,
                                          payload=sorted_data).first()
    if instance:
        print('{}: {} {}, Data Retrieved'.format(url, method, instance.status_code))
    return instance


def sort_nested_dict(unsorted_dict):
    sorted_dict = OrderedDict(sorted(unsorted_dict.items()))
    for key, value in sorted(unsorted_dict.items()):
        if isinstance(value, dict):
            sorted_dict[key] = sort_nested_dict(value)
        else:
            sorted_dict[key] = value
    return sorted_dict


def decimal_to_float(dict_with_decimal):
    """Takes a dictionary and turns any contained floats to Decimals"""
    for key, value in dict_with_decimal.items():
        if isinstance(value, decimal.Decimal):
            dict_with_decimal[key] = float(value)
        elif isinstance(value, dict):
            dict_with_decimal[key] = decimal_to_float(value)
        else:
            dict_with_decimal[key] = value
    return dict_with_decimal


def random_user_agent():
    user_agent_list = [
        # 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.2704.79 Safari/537.36',
        # 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
        # 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36,'
        # 'Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36',
        # 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36',
        # 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36',
        # 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36',
        # 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135'
        # ' Safari/537.36 Edge/12.246',
        # 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko',
        # 'Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko',
        # 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
        # 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/5.0)',
        # 'Mozilla/4.0 (Compatible; MSIE 8.0; Windows NT 5.2; Trident/6.0)',
        # 'Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)',
    ]
    return random.choice(user_agent_list)


def csv_to_dict_list(filename):
    with open(filename) as csv_file:
        reader = csv.DictReader(csv_file)
        dict_list = [row for row in reader]
    return dict_list


def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError


def make_int(string):
    """"Converts to int and handles empty strings"""
    s = string.strip()
    return int(s) if s else None
