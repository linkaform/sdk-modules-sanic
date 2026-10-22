#!/usr/local/bin/python
# coding: utf-8
# Puente entre el script-runner de Django y las rutas /base/* de la pantalla
# Administracion > Usuarios del front clave10 (script_name="users_sdk.py").
import sys, simplejson, lkf_addons
from middleware.auth import dispatch


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
    }, method='post', **params)

def update_user(params):
    data = params.get("data", {})
    return dispatch("update_user", module='base', params={
        'record_id': data.get('record_id', ''),
        'name': data.get('name'),
        'phone': data.get('phone'),
        'role': data.get('role'),
        'email': data.get('email'),
    }, method='post', **params)

def reset_password(params):
    data = params.get("data", {})
    return dispatch("reset_password", module='base', params={
        'record_id': data.get('record_id', ''),
    }, method='post', **params)


DISPATCHER = {
    "list_users": list_users,
    "get_user_detail": get_user_detail,
    "create_user": create_user,
    "update_user": update_user,
    "reset_password": reset_password,
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
