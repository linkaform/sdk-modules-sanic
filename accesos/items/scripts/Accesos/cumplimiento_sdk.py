#!/usr/local/bin/python
# coding: utf-8
# Puente entre el script-runner de Django y las rutas /accesos/cumplimiento/* de
# Contratistas (ME-15). El front de clave10 lo llama con
# script_name="cumplimiento_sdk.py" + option="<nombre de la ruta>".
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
    return dispatch(f"cumplimiento/{end_point}", module='accesos', params=payload, method='post', **params)


def list_cumplimiento(params):
    data = params.get("data", {})
    return _post("list_cumplimiento", {
        'relacion_id': data.get('relacion_id'),
        'contrato_id': data.get('contrato_id'),
        'sujeto_tipo': data.get('sujeto_tipo'),
        'empleado_id': data.get('empleado_id'),
        'anio': data.get('anio'),
    }, params)


def set_estado_cumplimiento(params):
    data = params.get("data", {})
    return _post("set_estado_cumplimiento", {
        'cumplimiento_id': data.get('cumplimiento_id', ''),
        'estado': data.get('estado'),
        'motivo': data.get('motivo', ''),
    }, params)


def recalcular_cumplimiento(params):
    data = params.get("data", {})
    return _post("recalcular_cumplimiento", {
        'contrato_id': data.get('contrato_id'),
        'relacion_id': data.get('relacion_id'),
    }, params)


DISPATCHER = {
    "list_cumplimiento": list_cumplimiento,
    "set_estado_cumplimiento": set_estado_cumplimiento,
    "recalcular_cumplimiento": recalcular_cumplimiento,
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
