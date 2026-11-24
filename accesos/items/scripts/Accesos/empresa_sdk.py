#!/usr/local/bin/python
# coding: utf-8
# Puente entre el script-runner de Django y las rutas /accesos/empresa/* de
# Contratistas (Mi Empresa · Generales, ME-01). El front de clave10 lo llama con
# script_name="empresa_sdk.py" + option="<nombre de la ruta>".
import sys, simplejson, lkf_addons
from middleware.auth import dispatch


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
    return dispatch(f"empresa/{end_point}", module='accesos', params=payload, method='post', **params)


def get_mi_empresa(params):
    return _post("get_mi_empresa", {}, params)


def get_empresa(params):
    return _post("get_empresa", {'empresa_id': params.get("data", {}).get('empresa_id', '')}, params)


def update_mi_empresa(params):
    return _post("update_mi_empresa", {'empresa': params.get("data", {}).get('empresa', {})}, params)


def save_contacto(params):
    data = params.get("data", {})
    return _post("save_contacto", {'contacto': data.get('contacto', {}), 'indice': data.get('indice')}, params)


def delete_contacto(params):
    return _post("delete_contacto", {'indice': params.get("data", {}).get('indice')}, params)


DISPATCHER = {
    "get_mi_empresa": get_mi_empresa,
    "get_empresa": get_empresa,
    "update_mi_empresa": update_mi_empresa,
    "save_contacto": save_contacto,
    "delete_contacto": delete_contacto,
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
