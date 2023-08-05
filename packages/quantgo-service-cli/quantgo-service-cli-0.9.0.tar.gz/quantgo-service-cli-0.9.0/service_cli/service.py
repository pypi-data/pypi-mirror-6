# ======================= QuantGo Copyright Notice ============================
# Copyright 2013 QuantGo, LLC.  All rights reserved.
# Permission to use solely inside a QuantGo Virtual Quant Lab
# Written By: Nikolay
# Date: 12-12.2013
# ======================= QuantGo Copyright Notice ============================

import json
import config
import logging
import os

import errors

from functools import wraps
from service_cli import __version__
from client import SRClient

GET_DATA_SCHEMA = lambda action, name: \
    {"Action": action, "Parameters": {"ServiceName": name}}
GET_SERVICE_SPECIFIC_SCHEMA = lambda action, name: \
    {"Action": action, "Parameters": {"ServiceName": name}}
AVAILABLE_SCHEMA = lambda action: {"Action": action}
LIST_SCHEMA = lambda action: {"Action": action}
DESCRIPTION_SCHEMA = lambda action, name: {"Action": action, "Parameters": {"ServiceName": name}}
GET_ACTION_RESULT_SCHEMA = lambda id_value: \
    {"Action": "get-action-result", "Parameters": {"id": id_value}}


def with_client(f):
    """Wrapper which instantiates SRClient and passes it into wrapped function
    as first argument.
    """
    @wraps(f)
    def __wrapper(*args, **kwargs):
        logging.debug('ARGS %r, KWARGS %r', args, kwargs)
        host = kwargs.get('host', config.HOST)
        port = kwargs.get('port', config.PORT)
        stdout = kwargs.get('stdout')
        with SRClient(host, port, stdout=stdout) as client:
            return f(client, *args, **kwargs)
    return __wrapper


def service(command, args, **kwargs):
    service_name = args.name if 'name' in args else None
    params = args.params if 'params' in args else None
    if command == 'get-data':
        return do_get_data(service_name, params, **kwargs)
    elif command == 'get-service-specific':
        return do_get_service_specific(service_name, params, **kwargs)
    elif command == 'available':
        return do_available(**kwargs)
    elif command == 'list':
        return do_list(**kwargs)
    elif command == 'description':
        return do_description(service_name, **kwargs)
    else:
        assert False, 'Programming mistake: command argument has value %s, ' \
                      'which normally should never happen.' % (command)


@with_client
def do_get_data(client, service_name, params=None, **kwargs):
    if params:
        try:
            params = json.loads(params)
        except ValueError, e:
            raise ValueError('Please check --params argument value syntax. ' \
                             'It\'s value should be valid json blob. ' \
                             'Syntax error: %s' % (str(e)))
    if params.get('ticker-file'):
        filepath = params['ticker-file']
        logging.debug('Using tickers file %s', filepath)
        if os.path.exists(filepath) and os.path.isfile(filepath):
            with open(filepath, 'r') as fp:
                tickers = fp.read()
            del params['ticker-file']
            params['TickerNames'] = [t.strip() for t in tickers.split(',')]
            logging.debug('Setting TickerNames param to %r',
                          params['TickerNames'])
        else:
            raise ValueError('ticker-file  %s does not exist or is not a ' \
                             'valid file.' % (filepath,))
    request = GET_DATA_SCHEMA('get-data', service_name)
    request['Parameters'].update(params)
    return do_data_request(client, request, **kwargs)


def check_response(response_json):
    try:
        response = json.loads(response_json)
    except ValueError:
        raise errors.ClientError('Invalid JSON blob from server-side: %s' % response_json)
    result = response['Result']
    if not isinstance(result, bool):
        raise errors.ClientError('Invalid response from server-side: %s' % response_json)
    if not result:
        raise errors.ServerError(response['Data']['ErrorMessage'])
    return response


@with_client
def check_execution(client, response, received):
    id_value = response['Data']['id']
    # do not check execution if id is not given (no data)
    if id_value is None:
        return
    request = GET_ACTION_RESULT_SCHEMA(id_value)
    client.send(json.dumps(request))
    exec_response = check_response(client.read_response())
    data = exec_response['Data']
    code = data['code']
    if code == 0:
        size = data['size']
        if received != size:
            raise errors.ClientError('Data size mismatch. Got %d bytes but should be %d bytes' % (received, size))
    else:
        raise errors.ServerError('Error code: %d. %s' % (code, data['error']))


@with_client
def do_get_service_specific(client, service_name, params=None, **kwargs):
    if params:
        try:
            params = json.loads(params)
        except ValueError, e:
            raise ValueError('Please check --params argument value syntax. ' \
                             'It\'s value should be valid json blob. ' \
                             'Syntax error: %s' % (str(e)))
    request = GET_SERVICE_SPECIFIC_SCHEMA('get-service-specific', service_name)
    request['Parameters'].update(params)
    return do_data_request(client, request, **kwargs)


@with_client
def do_available(client, **kwargs):
    request = AVAILABLE_SCHEMA('available')
    do_request(client, request, True, **kwargs)


@with_client
def do_list(client, **kwargs):
    request = LIST_SCHEMA('list')
    do_request(client, request, True, **kwargs)


@with_client
def do_description(client, service_name, **kwargs):
    request = DESCRIPTION_SCHEMA('description', service_name)
    do_request(client, request, True, **kwargs)


def do_request(client, request, do_print, **kwargs):
    logging.debug('Request: %r', request)
    client.send(json.dumps(request))
    response = check_response(client.read_response())
    if do_print:
        stdout = kwargs.get('stdout')
        if stdout:
            stdout.write(json.dumps(response, indent=4, separators=(',', ': ')))
            stdout.write('\n')
    return response


def do_data_request(client, request, **kwargs):
    response = do_request(client, request, False, **kwargs)
    data = client.receive()
    check_execution(response, client.received)
    return data
