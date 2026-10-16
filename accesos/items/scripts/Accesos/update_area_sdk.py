#!/usr/local/bin/python
# coding: utf-8
import sys, simplejson, lkf_addons
from middleware.auth import dispatch


def exception_from_response(body):
    """Arma el dict de LKFException a partir de la respuesta de error de Sanic.

    La ruta /update_area responde {"exception": {...}} en sus validaciones; si el
    servicio lanza LKFException, el error handler de Sanic responde el dict
    interno (con "msg"); y un error no controlado llega como {"error": "..."}.
    """
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
        exception['msg'] = [exception['msg']]  # LKFException manda msg como lista
    return exception


def write_response(response):
    """Escribe la respuesta de Sanic. Si es un error (>= 400), el script falla
    igual que LKFException: el hook muestra el mensaje y, desde el front, el
    mini-back responde success:false con error.exception (lo lee errorMsj)."""
    try:
        body = response.json()
    except ValueError:
        body = {'error': f'Respuesta inválida del servidor (HTTP {response.status_code}).'}
    if response.status_code >= 400:
        sys.stderr.write('Exception: ' + simplejson.dumps({'exception': exception_from_response(body)}))
        sys.exit(1)
    sys.stdout.write(simplejson.dumps(body))


def create_area(params):
    data = params.get("data", {})
    return dispatch("create_area", params={
        'ubicacion': data.get('ubicacion', ''),
        'nombre': data.get('nombre', ''),
        'tipo_de_area': data.get('tipo_de_area', ''),
        'foto_area': data.get('foto_area', []),
        'qr_area': data.get('qr_area', ''),
        'geolocalizacion': data.get('geolocalizacion'),
        'multiple_ubicacion': data.get('multiple_ubicacion', 'no'),
        'direccion': data.get('direccion', ''),
        'usos': data.get('usos', []),
    }, method='post', **params)


def update_full_area(params):
    # Solo se reenvían las llaves que manda el front: el back parcha esas.
    data = params.get("data", {})
    campos = ('record_id', 'nombre', 'ubicacion', 'direccion', 'tipo_de_area', 'area_status', 'area_state',
              'qr_area', 'foto_area', 'geolocalizacion', 'multiple_ubicacion', 'usos')
    return dispatch("update_full_area", params={
        k: data[k] for k in campos if k in data
    }, method='post', **params)


# Llamadas desde el front (runScript con option). Sin option se comporta como
# el hook de la forma Configuracion de Area.
DISPATCHER = {
    "create_area": create_area,
    "update_full_area": update_full_area,
}


if __name__ == "__main__":
    params = simplejson.loads(sys.argv[2])
    handler = DISPATCHER.get(params.get("data", {}).get("option", ""))
    if handler:
        # Desde el front el record (argv[1]) llega vacio.
        write_response(handler(params))
        sys.exit(0)

    current_record = simplejson.loads(sys.argv[1])
    print('..... arranca hook update_area')
    response = dispatch("update_area", params={
        'current_record': current_record,
    }, method='post', **params)
    write_response(response)
