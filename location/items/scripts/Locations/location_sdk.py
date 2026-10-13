#!/usr/local/bin/python
# coding: utf-8
import sys, simplejson, lkf_addons
from middleware.auth import dispatch


def exception_from_response(body):
    """Dict de LKFException a partir de la respuesta de error de Sanic:
    {"exception": {...}}, el dict interno de LKFException (con "msg") o {"error": "..."}."""
    if isinstance(body, dict):
        if isinstance(body.get('exception'), dict):
            exception = dict(body['exception'])
        elif 'msg' in body:
            exception = dict(body)
        else:
            exception = {'title': 'Error', 'msg': body.get('error', str(body))}
    else:
        exception = {'title': 'Error', 'msg': str(body)}
    if isinstance(exception.get('msg'), str):
        exception['msg'] = [exception['msg']]
    return exception


def get_catalog_ubicaciones_formatted(params):
    data = params.get("data", {})
    return dispatch("get_catalog_ubicaciones_formatted", module='location', params={
        'locations': data.get('locations', []),
        'dynamic_filters': data.get('dynamic_filters', []),
        'limit': data.get('limit', 25),
        'offset': data.get('offset', 0),
        'search': data.get('search', ''),
        'search_fields': data.get('search_fields', []),
    }, method='post', **params)


def get_ubicacion_by_id(params):
    data = params.get("data", {})
    return dispatch("get_ubicacion_by_id", module='location', params={
        'record_id': data.get('record_id', ''),
    }, method='get', **params)


def get_empleados_by_ubicacion(params):
    data = params.get("data", {})
    return dispatch("get_empleados_by_ubicacion", module='location', params={
        'ubicacion': data.get('ubicacion', ''),
    }, method='get', **params)


def create_ubicacion(params):
    data = params.get("data", {})
    return dispatch("create_ubicacion", module='location', params={
        'nombre': data.get('nombre', ''),
        'direccion': data.get('direccion', ''),
        'colonia': data.get('colonia', ''),
        'ciudad': data.get('ciudad', ''),
        'estado': data.get('estado', ''),
        'pais': data.get('pais', ''),
        'codigo_postal': data.get('codigo_postal', ''),
        'telefono': data.get('telefono', ''),
        'email': data.get('email', ''),
        'geolocalizacion': data.get('geolocalizacion', {}),
    }, method='post', **params)


def update_ubicacion(params):
    data = params.get("data", {})
    payload = {
        'record_id': data.get('record_id', ''),
        'nombre_actual': data.get('nombre_actual', ''),
    }
    for key in (
        'nombre', 'direccion', 'colonia', 'ciudad', 'estado',
        'pais', 'codigo_postal', 'telefono', 'email', 'geolocalizacion',
    ):
        if key in data:
            payload[key] = data.get(key)
    return dispatch("update_ubicacion", module='location', params=payload, method='post', **params)


DISPATCHER = {
    "get_catalog_ubicaciones_formatted": get_catalog_ubicaciones_formatted,
    "get_ubicacion_by_id": get_ubicacion_by_id,
    "get_empleados_by_ubicacion": get_empleados_by_ubicacion,
    "create_ubicacion": create_ubicacion,
    "update_ubicacion": update_ubicacion,
}

if __name__ == "__main__":
    params = simplejson.loads(sys.argv[2])
    data = params.get("data", {})
    option = data.get("option", "")
    handler = DISPATCHER.get(option)
    print('aqui....')
    if not handler:
        response = {"error": f"Option '{option}' not supported", "valid_options": list(DISPATCHER.keys())}
        sys.stdout.write(simplejson.dumps(response))
    else:
        response = handler(params)
        body = response.json()
        if response.status_code >= 400:
            # Igual que LKFException: el mini-back responde success:false con
            # error.exception y el front muestra el mensaje en vez de un exito.
            sys.stderr.write('Exception: ' + simplejson.dumps({'exception': exception_from_response(body)}))
            sys.exit(1)
        sys.stdout.write(simplejson.dumps(body))
