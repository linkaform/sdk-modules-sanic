#!/usr/local/bin/python
# coding: utf-8
import sys, simplejson, lkf_addons
from middleware.auth import dispatch


def _as_list(value):
    if isinstance(value, list):
        return value
    return [value] if value else []

def new_article(params):
    data = params.get("data", {})
    return dispatch("new_article", params={
        'data_article': data.get('data_article', {}),
    }, method='post', **params)

def get_articles(params):
    data = params.get("data", {})
    return dispatch("get_articles", params={
        'location': data.get('location', ''),
        'area': data.get('area', ''),
        'status': data.get('status', ''),
        'dateFrom': data.get('dateFrom', ''),
        'dateTo': data.get('dateTo', ''),
        'filterDate': data.get('filterDate', ''),
    }, method='get', **params)

def update_article(params):
    # El front de devolucion (src/lib/devolucion-concesion.ts) manda el payload
    # plano: record_id, status, state, equipos, quien_entrega, ... Se reenvia
    # completo; data_article_update/folio siguen funcionando para llamadas directas.
    data = params.get("data", {})
    if data.get('data_article_update'):
        data_article = data['data_article_update']
    else:
        data_article = {k: v for k, v in data.items() if k not in ('option', 'script_name')}
    return dispatch("update_article", params={
        'data_article_update': data_article,
        'record_id': data.get('record_id') or data.get('folio'),
    }, method='post', **params)

def delete_article(params):
    data = params.get("data", {})
    return dispatch("delete_article", params={
        'folio': _as_list(data.get('folio')),
    }, method='get', **params)

def catalogo_tipo_concesion(params):
    data = params.get("data", {})
    return dispatch("catalogo_tipo_concesion", params={
        'location': data.get('location', ''),
        'tipo': data.get('tipo', ''),
    }, method='get', **params)


DISPATCHER = {
    "new_article": new_article,
    "get_articles": get_articles,
    "update_article": update_article,
    "delete_article": delete_article,
    "catalogo_tipo_concesion": catalogo_tipo_concesion,
}

if __name__ == "__main__":
    params = simplejson.loads(sys.argv[2])
    data = params.get("data", {})
    option = data.get("option")
    print('..... arranca script articulos_consecionados')
    handler = DISPATCHER.get(option)
    if not handler:
        response = {"error": f"Option '{option}' not supported", "valid_options": list(DISPATCHER.keys())}
        sys.stdout.write(simplejson.dumps(response))
    else:
        response = handler(params)
        body = response.json()
        if response.status_code >= 400:
            # Mismo formato que un LKFException del script viejo: el mini-back
            # lo extrae del stderr y responde success:false con error.exception.
            exception = body if 'msg' in body else {'title': 'Error', 'msg': [body.get('error', str(body))]}
            sys.stderr.write('Exception: ' + simplejson.dumps({'exception': exception}))
            sys.exit(1)
        sys.stdout.write(simplejson.dumps(body))
