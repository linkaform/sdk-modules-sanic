#!/usr/local/bin/python
# coding: utf-8
# Puente PÚBLICO entre el script-runner de Django y /accesos/registro/* de
# Contratistas (RG-01 y RG-03-B). La página de registro no tiene sesión: el front manda el
# account_id de la URL y este script corre con el API key de ESA cuenta. No
# acepta un api_key del cliente.
import sys, simplejson, lkf_addons
from account_settings import *
from middleware.auth import dispatch_with_api_key


def raise_for_error(response):
    """ Si sanic respondio un error (>= 400) se relanza como excepcion, para que el
    runner regrese success false y el front reciba {"exception": {...}}. """
    if response.status_code < 400:
        return
    try:
        body = response.json()
    except ValueError:
        body = {}
    if not isinstance(body, dict):
        body = {'msg': [str(body)]}
    if body.get('traceback'):
        print('--- traceback sanic [request_id=%s] HTTP %s ---\n%s' % (
            body.get('request_id'), response.status_code, body['traceback']))
    exception = body.get('exception') if isinstance(body.get('exception'), dict) else body
    exception.setdefault('title', 'Error')
    exception.setdefault('msg', [str(exception.get('error') or response.text[:300] or 'HTTP %s' % response.status_code)])
    exception.setdefault('status_code', response.status_code)
    raise Exception(simplejson.dumps({'exception': exception}))


def _post(end_point, payload, params):
    params = {k: v for k, v in params.items() if k not in ('jwt', 'Bearer')}
    return dispatch_with_api_key(f"registro/{end_point}", config.get('APIKEY'), module='accesos',
                                 params=payload, method='post', **params)


def registrar_empresa(params):
    data = params.get("data", {})
    return _post("registrar_empresa", {'registro': data.get('registro', {})}, params)


def leer_documento_registro(params):
    data = params.get("data", {})
    return _post("leer_documento_registro", {
        'archivo': data.get('archivo', {}),
        'tipo': data.get('tipo'),
        'rfc': data.get('rfc'),
    }, params)


DISPATCHER = {
    "registrar_empresa": registrar_empresa,
    "leer_documento_registro": leer_documento_registro,
}

if __name__ == "__main__":
    params = simplejson.loads(sys.argv[2])
    data = params.get("data", {})
    option = data.get("option", "")
    handler = DISPATCHER.get(option)
    if not handler:
        response = {"error": f"Option '{option}' not supported", "valid_options": list(DISPATCHER.keys())}
        sys.stdout.write(simplejson.dumps(response))
    else:
        response = handler(params)
        raise_for_error(response)
        sys.stdout.write(simplejson.dumps(response.json()))
