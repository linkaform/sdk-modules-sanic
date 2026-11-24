#!/usr/local/bin/python
# coding: utf-8
# Puente entre el script-runner de Django y las rutas /accesos/empleados/* de
# Contratistas (ME-03 a ME-05). El front de clave10 lo llama con
# script_name="empleados_sdk.py" + option="<nombre de la ruta>".
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
    return dispatch(f"empleados/{end_point}", module='accesos', params=payload, method='post', **params)


def _pick(data, keys):
    return {k: data.get(k) for k in keys if data.get(k) is not None}


def list_empleados(params):
    return _post("list_empleados", _pick(params.get("data", {}), (
        'empresa_id', 'estatus', 'usuario', 'cumplimiento', 'perfil_id', 'contrato_id', 'search',
        'limit', 'offset')), params)


def get_empleado(params):
    return _post("get_empleado", {'empleado_id': params.get("data", {}).get('empleado_id', '')}, params)


def create_empleado(params):
    return _post("create_empleado", {'empleado': params.get("data", {}).get('empleado', {})}, params)


def update_empleado(params):
    data = params.get("data", {})
    return _post("update_empleado", {'empleado_id': data.get('empleado_id', ''),
                                     'empleado': data.get('empleado', {})}, params)


def change_status_empleado(params):
    data = params.get("data", {})
    return _post("change_status_empleado", {'empleado_id': data.get('empleado_id', ''),
                                            'estatus': data.get('estatus')}, params)


def analizar_documentos_empleado(params):
    return _post("analizar_documentos_empleado", _pick(params.get("data", {}), ('archivos', 'model')), params)


def validar_carga_empleados(params):
    return _post("validar_carga_empleados", {'archivo': params.get("data", {}).get('archivo')}, params)


def cargar_empleados(params):
    return _post("cargar_empleados", {'archivo': params.get("data", {}).get('archivo')}, params)


def list_documentos_empleado(params):
    return _post("list_documentos_empleado", _pick(params.get("data", {}), (
        'empleado_id', 'estatus', 'origen', 'search', 'limit', 'offset')), params)


def get_qr_empleado(params):
    return _post("get_qr_empleado", {'empleado_id': params.get("data", {}).get('empleado_id', '')}, params)


def vetar_empleado(params):
    data = params.get("data", {})
    return _post("vetar_empleado", {'empleado_id': data.get('empleado_id', ''), 'motivo': data.get('motivo', '')},
                 params)


def levantar_veto_empleado(params):
    return _post("levantar_veto_empleado", {'empleado_id': params.get("data", {}).get('empleado_id', '')}, params)


def update_preferencias_empleado(params):
    data = params.get("data", {})
    return _post("update_preferencias_empleado", {'empleado_id': data.get('empleado_id', ''),
                                                  'preferencias': data.get('preferencias', {})}, params)


def restaurar_password_empleado(params):
    return _post("restaurar_password_empleado", {'empleado_id': params.get("data", {}).get('empleado_id', '')},
                 params)


def list_contratos_empleado(params):
    return _post("list_contratos_empleado", _pick(params.get("data", {}), (
        'empleado_id', 'estatus', 'search', 'limit', 'offset')), params)


def list_contratos_para_ligar(params):
    return _post("list_contratos_para_ligar", _pick(params.get("data", {}), (
        'empleado_id', 'cliente_id', 'perfil_id', 'search')), params)


def ligar_contrato_empleado(params):
    return _post("ligar_contrato_empleado", _pick(params.get("data", {}), (
        'empleado_id', 'contrato_id', 'perfiles')), params)


def editar_perfiles_contrato_empleado(params):
    return _post("editar_perfiles_contrato_empleado", _pick(params.get("data", {}), (
        'empleado_id', 'contrato_id', 'perfiles')), params)


def remover_contrato_empleado(params):
    return _post("remover_contrato_empleado", _pick(params.get("data", {}), ('empleado_id', 'contrato_id')), params)


DISPATCHER = {
    "list_empleados": list_empleados,
    "get_empleado": get_empleado,
    "create_empleado": create_empleado,
    "update_empleado": update_empleado,
    "change_status_empleado": change_status_empleado,
    "analizar_documentos_empleado": analizar_documentos_empleado,
    "validar_carga_empleados": validar_carga_empleados,
    "cargar_empleados": cargar_empleados,
    "list_documentos_empleado": list_documentos_empleado,
    "get_qr_empleado": get_qr_empleado,
    "vetar_empleado": vetar_empleado,
    "levantar_veto_empleado": levantar_veto_empleado,
    "update_preferencias_empleado": update_preferencias_empleado,
    "restaurar_password_empleado": restaurar_password_empleado,
    "list_contratos_empleado": list_contratos_empleado,
    "list_contratos_para_ligar": list_contratos_para_ligar,
    "ligar_contrato_empleado": ligar_contrato_empleado,
    "editar_perfiles_contrato_empleado": editar_perfiles_contrato_empleado,
    "remover_contrato_empleado": remover_contrato_empleado,
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
