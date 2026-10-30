#!/usr/local/bin/python
# coding: utf-8
# Puente entre los workflows del form Usuarios y las rutas /base/* de sanic.
# Dos fases con el mismo script (igual que el create_user.py de addons):
#  - 'crear'    (runtime before): POST /base/create_user_account. Da de alta el
#    usuario y regresa las respuestas en 'creado' como replace_ans.
#  - 'activado' (runtime after, cuando el usuario fija su contraseña):
#    POST /base/setup_user_employee. Crea o liga el empleado y su Configuracion
#    Accesos.
import sys, simplejson, lkf_addons
from middleware.auth import dispatch

STATUS_FIELD = '679d023876ad7f5ba642f4ed'


def create_user_account(record_id, answers, params):
    return dispatch("create_user_account", module='base', params={
        'record_id': record_id,
        'answers': answers,
    }, method='post', **params)


def setup_user_employee(answers, params):
    return dispatch("setup_user_employee", module='base', params={
        'answers': answers,
    }, method='post', **params)


if __name__ == "__main__":
    current_record = simplejson.loads(sys.argv[1])
    params = simplejson.loads(sys.argv[2])
    answers = current_record.get('answers', {})
    record_id = str(current_record.get('record_id') or '')

    if answers.get(STATUS_FIELD) == 'activado':
        response = setup_user_employee(answers, params)
    else:
        response = create_user_account(record_id, answers, params)

    # Un error de sanic aborta el guardado del registro (fase 'before'): se
    # relanza tal cual para que el mensaje le llegue al administrador.
    if response.status_code != 200:
        raise Exception(response.text)

    data = response.json().get('data', {})
    if answers.get(STATUS_FIELD) == 'activado':
        sys.stdout.write(simplejson.dumps({'status': 200}))
    else:
        sys.stdout.write(simplejson.dumps({
            'status': 101,
            'replace_ans': data.get('answers', answers),
            'metadata': {'id': record_id},
        }))
