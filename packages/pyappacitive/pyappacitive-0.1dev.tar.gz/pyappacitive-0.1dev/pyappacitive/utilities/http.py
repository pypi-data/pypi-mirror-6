__author__ = 'sushant'

from . import customjson
import requests
import logging, time
from pyappacitive import AppacitiveError

logger = logging.getLogger('pyappacitive')
logger.addHandler(logging.NullHandler())


def put(url, headers, payload):

    start_time = time.time()

    response_from_api = requests.put(url, payload, headers=headers)

    elapsed_time = time.time() - start_time

    response = to_dict(response_from_api)

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug('PUT : %s', url, extra={
            'HEADERS': ','.join([key for key in headers.iterkeys()]),
            "PAYLOAD": payload,
            "RESPONSE": response,
            "TIME_TAKEN": float(elapsed_time)
        })
    status = response.get('status', None)
    if status is not None:
        code = status.get('code', None)
        if code is not None:
            if code != '200':
                raise AppacitiveError(status)
    return response


def post(url, headers, payload):

    start_time = time.time()
    response_from_api = requests.post(url, payload, headers=headers)
    elapsed_time = time.time() - start_time

    response = to_dict(response_from_api)

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug('POST : %s', url, extra={
            'HEADERS': ','.join([key for key in headers.iterkeys()]),
            "PAYLOAD": payload,
            "RESPONSE": response,
            "TIME_TAKEN": str(elapsed_time)
        })
    status = response.get('status', None)
    if status is not None:
        code = status.get('code', None)
        if code is not None:
            if code != '200':
                raise AppacitiveError(status)
    return response


def delete(url, headers):

    start_time = time.time()
    response_from_api = requests.delete(url, headers=headers)
    elapsed_time = time.time() - start_time

    response = to_dict(response_from_api)

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug('DELETE : %s', url, extra={
            'HEADERS': ','.join([key for key in headers.iterkeys()]),
            "RESPONSE": response,
            "TIME_TAKEN": str(elapsed_time)
        })
    status = response.get('status', None)
    if status is not None:
        code = status.get('code', None)
        if code is not None:
            if code != '200':
                raise AppacitiveError(status)
    return response


def get(url, headers):

    start_time = time.time()
    response_from_api = requests.get(url, headers=headers)
    elapsed_time = time.time() - start_time

    response = to_dict(response_from_api)

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug('DELETE : %s', url, extra={
            'HEADERS': ','.join([key for key in headers.iterkeys()]),
            "RESPONSE": response,
            "TIME_TAKEN": str(elapsed_time)
        })
    status = response.get('status', None)
    if status is not None:
        code = status.get('code', None)
        if code is not None:
            if code != '200':
                raise AppacitiveError(status)
    return response


def to_dict(response):
    return customjson.deserialize(response.content.decode('utf-8-sig'))

