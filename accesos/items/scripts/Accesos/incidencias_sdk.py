#!/usr/local/bin/python
# coding: utf-8
import sys, simplejson, lkf_addons
from middleware.auth import dispatch


def nueva_incidencia(params):
    data = params.get("data", {})
    return dispatch("nueva_incidencia", params={
        'data_incidence': data.get('data_incidence', {}),
    }, method='post', **params)

def _filtros_incidencias(data):
    # El front manda 'location' (texto o lista); el back espera 'locations'.
    return {
        'locations': data.get('locations') or data.get('location') or [],
        'area': data.get('area', ''),
        'dateFrom': data.get('dateFrom', ''),
        'dateTo': data.get('dateTo', ''),
        'filterDate': data.get('filterDate', ''),
        'estatus': data.get('estatus') or data.get('status') or '',
        'facets': data.get('facets', []),
    }

def get_incidences(params):
    data = params.get("data", {})
    return dispatch("get_incidences", params={
        **_filtros_incidencias(data),
        'prioridades': data.get('prioridades', []),
        'limit': data.get('limit'),
        'skip': data.get('skip', 0),
    }, method='post', **params)

def get_search_fields(params):
    return dispatch("get_search_fields_incidencias", params={}, method='get', **params)

def get_search_counts(params):
    data = params.get("data", {})
    return dispatch("get_search_counts_incidencias", params={
        **_filtros_incidencias(data),
        'candidates': data.get('candidates', []),
    }, method='post', **params)

def update_incidence(params):
    data = params.get("data", {})
    return dispatch("update_incidence", params={
        'data_incidence_update': data.get('data_incidence_update', {}),
        'folio': data.get('folio', ''),
    }, method='post', **params)

def update_incidence_seguimiento(params):
    data = params.get("data", {})
    return dispatch("update_incidence_seguimiento", params={
        'folio': data.get('folio', ''),
        'seguimientos_incidencia': data.get('seguimientos_incidencia', []),
        'estatus': data.get('estatus', ''),
        'location': data.get('location', ''),
        'area': data.get('area', ''),
    }, method='post', **params)

def delete_incidence(params):
    data = params.get("data", {})
    folio = data.get('folio')
    return dispatch("delete_incidence", params={
        'folio': folio if isinstance(folio, list) else ([folio] if folio else []),
    }, method='get', **params)

def catalogo_area_empleado(params):
    data = params.get("data", {})
    return dispatch("catalogo_area_empleado_incidencias", params={
        'location': data.get('location', ''),
    }, method='get', **params)

def catalogo_incidencias_plano(params):
    # Todos los tipos con su categoría/subcategoría en una sola llamada.
    return dispatch("catalogo_incidencias_plano", params={}, method='get', **params)

def get_pdf(params):
    data = params.get("data", {})
    return dispatch("get_pdf", params={
        'qr_code': data.get('qr_code', ''),
        'template_id': data.get('template_id', ''),
    }, method='get', **params)


DISPATCHER = {
    "nueva_incidencia": nueva_incidencia,
    "get_search_fields": get_search_fields,
    "get_search_counts": get_search_counts,
    "get_incidences": get_incidences,
    "update_incidence": update_incidence,
    "update_incidence_seguimiento": update_incidence_seguimiento,
    "delete_incidence": delete_incidence,
    "catalogo_area_empleado": catalogo_area_empleado,
    "catalogo_incidencias_plano": catalogo_incidencias_plano,
    "get_pdf": get_pdf,
}

if __name__ == "__main__":
    params = simplejson.loads(sys.argv[2])
    data = params.get("data", {})
    option = data.get("option")
    print('..... arranca script incidencias')
    handler = DISPATCHER.get(option)
    if not handler:
        response = {"error": f"Option '{option}' not supported", "valid_options": list(DISPATCHER.keys())}
        sys.stdout.write(simplejson.dumps(response))
    else:
        response = handler(params)
        sys.stdout.write(simplejson.dumps(response.json()))
