#!/usr/local/bin/python
# coding: utf-8
import sys, simplejson, lkf_addons
from middleware.auth import dispatch

# Asistencia (Disponible/Ausente) y Check In/Out de cualquier usuario: employee en Sanic.


def get_asistencia(params):
    return dispatch("asistencia", module='employee', method='get', **params)

def set_asistencia(params):
    data = params.get("data", {})
    return dispatch("asistencia", module='employee', params={
        'estatus': data.get('estatus', ''),
    }, method='post', **params)

def get_checkin(params):
    return dispatch("checkin", module='employee', method='get', **params)

def get_lugares(params):
    return dispatch("checkin/lugares", module='employee', method='get', **params)

def get_roles(params):
    return dispatch("checkin/roles", module='employee', method='get', **params)

def checkin(params):
    data = params.get("data", {})
    return dispatch("checkin", module='employee', params={
        'ubicacion': data.get('ubicacion', ''),
        'caseta': data.get('caseta', ''),
        'rol': data.get('rol'),
        'suplente': data.get('suplente'),
        'motivo': data.get('motivo'),
        'foto': data.get('foto', []),
    }, method='post', **params)

def checkout(params):
    data = params.get("data", {})
    return dispatch("checkout", module='employee', params={
        'comentario': data.get('comentario'),
        'foto': data.get('foto', []),
    }, method='post', **params)

def get_booth_config(params):
    data = params.get("data", {})
    return dispatch("booth_config", module='accesos', params={
        'location': data.get('location', ''),
    }, method='get', **params)


def _reporte(end_point, keys):
    def handler(params):
        data = params.get("data", {})
        return dispatch(end_point, module='employee', params={k: data.get(k) for k in keys if data.get(k) is not None},
                        method='post', **params)
    return handler


DISPATCHER = {
    "reporte_hoy": _reporte("reporte/hoy", ["locations"]),
    "reporte_periodo": _reporte("reporte/periodo", ["desde", "hasta", "locations"]),
    "reporte_dia": _reporte("reporte/dia", ["user_id", "fecha"]),
    "reporte_ubicaciones": _reporte("reporte/ubicaciones", []),
    "get_asistencia": get_asistencia,
    "set_asistencia": set_asistencia,
    "get_checkin": get_checkin,
    "get_lugares": get_lugares,
    "get_roles": get_roles,
    "checkin": checkin,
    "checkout": checkout,
    "get_booth_config": get_booth_config,
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
        sys.stdout.write(simplejson.dumps(response.json()))
