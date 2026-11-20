#!/usr/local/bin/python
# coding: utf-8
# Reporte de artículos concesionados de clave10 (/dashboard/reportes/reporte_concesionados).
# La lógica vive en lkf-sanic-apps/addons/accesos/service.py → get_reporte_concesionados.
import sys, simplejson, lkf_addons
from middleware.auth import dispatch


def _as_list(value):
    if isinstance(value, list):
        return value
    return [value] if value else []

def get_prestamos(params):
    # Una fila por unidad prestada, ya con fechas, tipo de cierre y estado resueltos.
    data = params.get("data", {})
    return dispatch("get_reporte_concesionados", params={
        'locations': _as_list(data.get('locations')),
        'date_from': data.get('date_from', ''),
        'date_to': data.get('date_to', ''),
    }, method='post', **params)


DISPATCHER = {
    "get_prestamos": get_prestamos,
}

if __name__ == "__main__":
    params = simplejson.loads(sys.argv[2])
    data = params.get("data", {})
    option = data.get("option")
    print('..... arranca script reporte_concesionados')
    handler = DISPATCHER.get(option)
    if not handler:
        response = {"error": f"Option '{option}' not supported", "valid_options": list(DISPATCHER.keys())}
        sys.stdout.write(simplejson.dumps(response))
    else:
        response = handler(params)
        body = response.json()
        if response.status_code >= 400:
            # Mismo formato que un LKFException: el mini-back lo extrae del stderr
            exception = body if 'msg' in body else {'title': 'Error', 'msg': [body.get('error', str(body))]}
            sys.stderr.write('Exception: ' + simplejson.dumps({'exception': exception}))
            sys.exit(1)
        sys.stdout.write(simplejson.dumps(body))
