#!/usr/local/bin/python
# coding: utf-8
# Puente entre el script-runner de Django y las rutas /base/* de la pantalla
# Administracion > Usuarios del front clave10 (script_name="users_sdk.py").
import sys, simplejson, lkf_addons
from middleware.auth import dispatch


def raise_for_error(response):
    """ Si sanic respondio un error (>= 400) se relanza como excepcion. Imprimirlo como
    resultado haria que el runner de LinkaForm lo reporte como exito (HTTP 200,
    success true) y el front mostraria "Usuario creado" aunque la ruta haya fallado.

    Con la excepcion el runner regresa success false y, en `error`, el objeto
    {"exception": {...}} que ya entiende el front. El codigo original (por ejemplo
    440) viaja en exception.status_code: el runner solo emite HTTP 200 o 400. """
    if response.status_code < 400:
        return
    try:
        body = response.json()
    except ValueError:
        body = {}
    if not isinstance(body, dict):
        body = {'msg': [str(body)]}
    # sanic manda su traceback en el cuerpo del error: a stdout, que LinkaForm
    # muestra en el log del script (stderr queda solo para el Exception parseable).
    if isinstance(body, dict) and body.get('traceback'):
        print('--- traceback sanic [request_id=%s] HTTP %s ---\n%s' % (
            body.get('request_id'), response.status_code, body['traceback']))
    # sanic desenvuelve el {"exception": {...}} de LKFException; se vuelve a envolver
    exception = body.get('exception') if isinstance(body.get('exception'), dict) else body
    exception.setdefault('title', 'Error')
    exception.setdefault('msg', [str(exception.get('error') or response.text[:300] or 'HTTP %s' % response.status_code)])
    exception.setdefault('status_code', response.status_code)
    raise Exception(simplejson.dumps({'exception': exception}))


def list_users(params):
    data = params.get("data", {})
    return dispatch("list_users", module='base', params={
        'limit': data.get('limit', 25),
        'skip': data.get('offset', 0),
        'status': data.get('status'),
        'name': data.get('name', ''),
        'username': data.get('username', ''),
        'email': data.get('email', ''),
        'search': data.get('search', ''),
    }, method='post', **params)

def get_user_detail(params):
    data = params.get("data", {})
    return dispatch("get_user_detail", module='base', params={
        'record_id': data.get('record_id', ''),
    }, method='post', **params)

def get_user_options(params):
    return dispatch("get_user_options", module='base', params={}, method='get', **params)

def create_user(params):
    data = params.get("data", {})
    return dispatch("create_user", module='base', params={
        'name': data.get('name', ''),
        'username': data.get('username', ''),
        'email': data.get('email', ''),
        'phone': data.get('phone', ''),
        'role': data.get('role', ''),
        'empleado': data.get('empleado', ''),
        'empleado_nombre': data.get('empleado_nombre', ''),
        'timezone': data.get('timezone', ''),
        'language': data.get('language', ''),
    }, method='post', **params)

def update_user(params):
    data = params.get("data", {})
    return dispatch("update_user", module='base', params={
        'record_id': data.get('record_id', ''),
        'name': data.get('name'),
        'phone': data.get('phone'),
        'role': data.get('role'),
        'email': data.get('email'),
        'timezone': data.get('timezone'),
        'language': data.get('language'),
    }, method='post', **params)

def reset_password(params):
    data = params.get("data", {})
    return dispatch("reset_password", module='base', params={
        'record_id': data.get('record_id', ''),
    }, method='post', **params)

def create_users(params):
    data = params.get("data", {})
    return dispatch("create_users", module='base', params={
        'rows': data.get('rows', []),
        'create_employee': data.get('create_employee', False),
    }, method='post', **params)


DISPATCHER = {
    "list_users": list_users,
    "get_user_detail": get_user_detail,
    "get_user_options": get_user_options,
    "create_user": create_user,
    "update_user": update_user,
    "reset_password": reset_password,
    "create_users": create_users,
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
