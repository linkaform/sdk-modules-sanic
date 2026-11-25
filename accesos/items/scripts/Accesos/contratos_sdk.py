#!/usr/local/bin/python
# coding: utf-8
# Puente entre el script-runner de Django y las rutas /accesos/contratos/* de
# Contratistas (ME-14 y ME-13). El front de clave10 lo llama con
# script_name="contratos_sdk.py" + option="<nombre de la ruta>".
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
    return dispatch(f"contratos/{end_point}", module='accesos', params=payload, method='post', **params)


def list_contratos(params):
    data = params.get("data", {})
    return _post("list_contratos", {
        'relacion_id': data.get('relacion_id'),
        'estatus': data.get('estatus'),
        'fin_desde': data.get('fin_desde'),
        'fin_hasta': data.get('fin_hasta'),
        'search': data.get('search', ''),
        'limit': data.get('limit', 25),
        'offset': data.get('offset', 0),
    }, params)


def get_contrato(params):
    data = params.get("data", {})
    return _post("get_contrato", {'contrato_id': data.get('contrato_id', '')}, params)


def create_contrato(params):
    data = params.get("data", {})
    return _post("create_contrato", {'contrato': data.get('contrato', {})}, params)


def update_contrato(params):
    data = params.get("data", {})
    return _post("update_contrato", {
        'contrato_id': data.get('contrato_id', ''),
        'contrato': data.get('contrato', {}),
    }, params)


def change_status_contrato(params):
    data = params.get("data", {})
    return _post("change_status_contrato", {
        'contrato_id': data.get('contrato_id', ''),
        'estatus_manual': data.get('estatus_manual'),
        'motivo': data.get('motivo', ''),
    }, params)


def get_historial_contrato(params):
    data = params.get("data", {})
    return _post("get_historial_contrato", {'contrato_id': data.get('contrato_id', '')}, params)


def get_mapeo_contrato(params):
    data = params.get("data", {})
    return _post("get_mapeo_contrato", {'contrato_id': data.get('contrato_id', '')}, params)


def sugerir_mapeo(params):
    data = params.get("data", {})
    return _post("sugerir_mapeo", {'filas': data.get('filas', []), 'solo_sin_match': bool(data.get('solo_sin_match'))}, params)


def save_mapeo_contrato(params):
    data = params.get("data", {})
    return _post("save_mapeo_contrato", {'contrato_id': data.get('contrato_id', ''), 'filas': data.get('filas', [])}, params)


def crear_en_catalogo(params):
    data = params.get("data", {})
    return _post("crear_en_catalogo", {'requerimiento': data.get('requerimiento', {})}, params)


DISPATCHER = {
    "get_mapeo_contrato": get_mapeo_contrato,
    "sugerir_mapeo": sugerir_mapeo,
    "save_mapeo_contrato": save_mapeo_contrato,
    "crear_en_catalogo": crear_en_catalogo,
    "list_contratos": list_contratos,
    "get_contrato": get_contrato,
    "create_contrato": create_contrato,
    "update_contrato": update_contrato,
    "change_status_contrato": change_status_contrato,
    "get_historial_contrato": get_historial_contrato,
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
