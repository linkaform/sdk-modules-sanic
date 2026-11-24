#!/usr/local/bin/python
# coding: utf-8
# Puente entre el script-runner de Django y las rutas /accesos/relaciones/* de
# Contratistas (R-01). El front de clave10 lo llama con
# script_name="relaciones_sdk.py" + option="<nombre de la ruta>".
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
    return dispatch(f"relaciones/{end_point}", module='accesos', params=payload, method='post', **params)


def list_relaciones(params):
    data = params.get("data", {})
    return _post("list_relaciones", {
        'direccion': data.get('direccion'),
        'estatus': data.get('estatus'),
        'search': data.get('search', ''),
        'limit': data.get('limit', 25),
        'offset': data.get('offset', 0),
    }, params)


def get_relacion(params):
    data = params.get("data", {})
    return _post("get_relacion", {'relacion_id': data.get('relacion_id', '')}, params)


def create_relacion(params):
    data = params.get("data", {})
    return _post("create_relacion", {'relacion': data.get('relacion', {})}, params)


def update_relacion(params):
    data = params.get("data", {})
    return _post("update_relacion", {
        'relacion_id': data.get('relacion_id', ''),
        'cambios': data.get('cambios', {}),
    }, params)


def change_status_relacion(params):
    data = params.get("data", {})
    return _post("change_status_relacion", {
        'relacion_id': data.get('relacion_id', ''),
        'estatus': data.get('estatus'),
    }, params)


def get_arbol_relacion(params):
    data = params.get("data", {})
    return _post("get_arbol_relacion", {'relacion_id': data.get('relacion_id', '')}, params)


DISPATCHER = {
    "get_arbol_relacion": get_arbol_relacion,
    "list_relaciones": list_relaciones,
    "get_relacion": get_relacion,
    "create_relacion": create_relacion,
    "update_relacion": update_relacion,
    "change_status_relacion": change_status_relacion,
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
