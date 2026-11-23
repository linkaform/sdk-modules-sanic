#!/usr/local/bin/python
# coding: utf-8
# Puente entre el script-runner de Django y las rutas /accesos/configuracion/* de
# Contratistas (CF-01 a CF-04). El front de clave10 lo llama con
# script_name="configuracion_sdk.py" + option="<nombre de la ruta>".
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
    return dispatch(f"configuracion/{end_point}", module='accesos', params=payload, method='post', **params)


def list_requerimientos(params):
    data = params.get("data", {})
    return _post("list_requerimientos", {k: data.get(k) for k in (
        'tipo', 'ambito', 'estatus', 'search', 'limit', 'offset') if data.get(k) is not None}, params)


def get_requerimiento(params):
    data = params.get("data", {})
    return _post("get_requerimiento", {'requerimiento_id': data.get('requerimiento_id', '')}, params)


def save_requerimiento(params):
    data = params.get("data", {})
    return _post("save_requerimiento", {
        'requerimiento': data.get('requerimiento', {}),
        'requerimiento_id': data.get('requerimiento_id'),
    }, params)


def get_aplicacion_requerimiento(params):
    data = params.get("data", {})
    return _post("get_aplicacion_requerimiento", {'requerimiento_id': data.get('requerimiento_id', '')}, params)


def list_recursos(params):
    data = params.get("data", {})
    return _post("list_recursos", {k: data.get(k) for k in (
        'tipo', 'categoria', 'clase', 'estatus', 'search', 'limit', 'offset') if data.get(k) is not None}, params)


def get_recurso(params):
    data = params.get("data", {})
    return _post("get_recurso", {'recurso_id': data.get('recurso_id', '')}, params)


def save_recurso(params):
    data = params.get("data", {})
    return _post("save_recurso", {'recurso': data.get('recurso', {}), 'recurso_id': data.get('recurso_id')}, params)


def get_aplicacion_recurso(params):
    data = params.get("data", {})
    return _post("get_aplicacion_recurso", {'recurso_id': data.get('recurso_id', '')}, params)


DISPATCHER = {
    "list_recursos": list_recursos,
    "get_recurso": get_recurso,
    "save_recurso": save_recurso,
    "get_aplicacion_recurso": get_aplicacion_recurso,
    "list_requerimientos": list_requerimientos,
    "get_requerimiento": get_requerimiento,
    "save_requerimiento": save_requerimiento,
    "get_aplicacion_requerimiento": get_aplicacion_requerimiento,
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
