#!/usr/local/bin/python
# coding: utf-8
# Puente entre el script-runner de Django y las rutas /accesos/sanciones/* de
# Contratistas (Sanciones de empleados y contratistas, R-07 y ME-05). El front de
# clave10 lo llama con script_name="sanciones_sdk.py" + option="<nombre de la ruta>".
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
    return dispatch(f"sanciones/{end_point}", module='accesos', params=payload, method='post', **params)


# option -> claves de data que se mandan a la ruta (mismo nombre).
OPCIONES = {
    "get_opciones_sancion": (),
    "list_sanciones": ("empleado_id", "relacion_id", "sujeto_tipo", "estatus", "search", "limit", "offset"),
    "get_sancion": ("sancion_id",),
    "save_sancion": ("sancion", "sancion_id"),
    "comment_sancion": ("sancion_id", "texto", "evidencias"),
    "delete_sancion": ("sancion_id",),
    "imprimir_acta": ("sancion_id",),
}


def _handler(option, claves):
    def run(params):
        data = params.get("data", {})
        return _post(option, {k: data.get(k) for k in claves if data.get(k) is not None}, params)
    return run


DISPATCHER = {option: _handler(option, claves) for option, claves in OPCIONES.items()}


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
