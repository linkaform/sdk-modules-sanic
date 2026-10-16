#!/usr/local/bin/python
# coding: utf-8
# Puente entre el script-runner de Django (/api/infosync/scripts/run/) y la ruta
# publica /base/set_user_password. Lo invoca la pagina /auth/set-password del
# front clave10 con script_name="user_activation_sdk.py".
#
# Sin prints de debug: por aqui pasa la contraseña y todo lo que se imprima va
# al stdout que captura el runner de Django.
import sys, simplejson, lkf_addons
from middleware.auth import dispatch


def set_user_password(params):
    data = params.get("data", {})
    return dispatch("set_user_password", module='base', params={
        'record_id': data.get('record_id', ''),
        'token': data.get('token', ''),
        'password': data.get('password', ''),
        'password2': data.get('password2', ''),
    }, method='post', **params)


DISPATCHER = {
    "set_user_password": set_user_password,
}

if __name__ == "__main__":
    params = simplejson.loads(sys.argv[2])
    data = params.get("data", {})
    option = data.get("option", "")
    handler = DISPATCHER.get(option)
    if not handler:
        sys.stdout.write(simplejson.dumps({
            "error": f"Option '{option}' not supported",
            "valid_options": list(DISPATCHER.keys()),
        }))
    else:
        response = handler(params)
        sys.stdout.write(simplejson.dumps(response.json()))
