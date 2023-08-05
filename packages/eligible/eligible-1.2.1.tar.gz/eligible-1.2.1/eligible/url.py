from __future__ import print_function
import eligible
import eligible.header
import eligible.errors
import os.path
import json
import requests


def request(method, endpoint_format, payload, version, extension='.json', payload_prep_func=json.dumps):
    if eligible.api_key == None:
       raise eligible.errors.AuthenticationError("No API key provided. Set it with `eligible.api_key = 'your-api-key'`.")

    # include api key set in config
    payload['api_key'] = eligible.api_key

    # include testing parameter if it's set in config
    if eligible.test == True:
        payload['test'] = 'true'

    # Mechanism for dealing with resources that use numeric IDs
    if 'reference_id' in payload.keys():
        endpoint = endpoint_format.format(reference_id=payload["reference_id"])
        del payload['reference_id']
    else:
        endpoint = endpoint_format.format(reference_id="")
        # get rid of trailing slash if there is one
        if endpoint.endswith('/'):
            endpoint = endpoint[:-1]

    endpoint = os.path.join(eligible.api_base, 'v' + version, endpoint + extension)

    # Catch any errors raised by requests
    try:
        response = request_dispatch(method, endpoint, payload,
                                    eligible.header.headers, payload_prep_func)
    except requests.exceptions.HTTPError as e:
        raise eligible.errors.APIError(str(e))
    except (requests.exceptions.ConnectionError,
            requests.exceptions.TooManyRedirects,
            requests.exceptions.RequestException) as e:
        raise eligible.errors.APIConnectionError(str(e))

    # Deal with other API errors
    if response.status_code != 200:
        handle_api_error(response.text, response.status_code)

    return response.text


def request_dispatch(method, endpoint, payload, headers, payload_prep_func):
    '''Send a request to the api server using params or data based on method type'''
    method = method.upper()
    if method in ('HEAD', 'GET', 'DELETE'):
        response = requests.request(method, endpoint,
                                    params=payload, headers=headers,
                                    verify=True)
    else:
        response = requests.request(method, endpoint,
                                    data=prepare_payload(payload_prep_func, payload),
                                    headers=headers, verify=True)
    return response


def prepare_payload(payload_prep_func, payload):
    '''Payload preparation, allowing for python 2/3 compatability'''
    try:
        return bytes(payload_prep_func(payload), 'utf-8')
    except TypeError:
        return payload_prep_func(payload)


def handle_api_error(response, response_code):
    '''Handle errors retruned from the API server based on the response code'''
    # Arguably a defaultdict could be used here, but it's a simple enough case
    # to not really be useful
    error_map = {400: (eligible.errors.InvalidRequestError, "Bad request"),
                 404: (eligible.errors.InvalidRequestError, "Endpoint not recognised"),
                 401: (eligible.errors.AuthenticationError, "Unauthorised Access")}

    if response_code in error_map.keys():
        error_type, message = error_map[response_code]
        raise error_type(': '.join((message, response)), response_code, response)
    else:
        raise eligible.errors.APIError(': '.join(message, response), response_code, response)
