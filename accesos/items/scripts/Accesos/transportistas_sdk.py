#!/usr/local/bin/python
# coding: utf-8
import warnings
# couchdb (importado transitivamente por lkf_addons/linkaform_api) emite un
# UserWarning de pkg_resources en el import -- el runner de Django trata
# cualquier escritura a stderr como fallo (success=False, HTTP 400) aunque
# la respuesta sea correcta. Debe ir ANTES de cualquier otro import.
warnings.filterwarnings('ignore', category=UserWarning, module='couchdb')
import sys, simplejson, lkf_addons
from linkaform_api import settings
from account_settings import *
from middleware.auth import dispatch_with_api_key


def create_pass_transportista(api_key, params, payload):
    return dispatch_with_api_key("create_pass_transportista", api_key, params={'payload': payload}, method='post', **params)

def create_visit_transportista(api_key, params, payload):
    return dispatch_with_api_key("create_visit_transportista", api_key, params={'payload': payload}, method='post', **params)

def generate_submit_token_transportista(api_key, params, record_id):
    return dispatch_with_api_key("generate_submit_token_transportista", api_key, params={'record_id': record_id}, method='post', **params)

def get_andenes(api_key, params):
    return dispatch_with_api_key("get_andenes", api_key, params={}, method='get', **params)

def get_bitac_transportista_record(api_key, params, record_id):
    return dispatch_with_api_key("get_bitac_transportista_record", api_key, params={'record_id': record_id}, method='get', **params)

BITAC_RECORDS_FILTERS = (
    "date_from", "date_to", "tipo_de_vehiculo", "proveedor_cliente", "anden_asignado",
    "estatus", "tipo_de_operacion", "conductor", "material", "search",
    "skip", "limit", "pagination", "facets",
)

def get_bitac_transportista_records(api_key, params, data):
    filters = {k: data[k] for k in BITAC_RECORDS_FILTERS if data.get(k) is not None}
    return dispatch_with_api_key("get_bitac_transportista_records", api_key, params=filters, method='post', **params)

def get_horarios_data(api_key, params, dia):
    return dispatch_with_api_key("get_horarios_data", api_key, params={'dia': dia}, method='get', **params)

def get_pass_transportista(api_key, params, record_id, token, folio):
    query = {k: v for k, v in {'record_id': record_id, 'token': token, 'folio': folio}.items() if v}
    return dispatch_with_api_key("get_pass_transportista", api_key, params=query, method='get', **params)

def get_users_data(api_key, params, locations):
    return dispatch_with_api_key("get_users_data_transportista", api_key, params={'locations': locations}, method='get', **params)

def get_location_data(api_key, params, location):
    return dispatch_with_api_key("get_location_data", api_key, params={'location': location}, method='get', **params)

def get_proveedores_transportista(api_key, params):
    return dispatch_with_api_key("get_proveedores_transportista", api_key, params={}, method='get', **params)

def validate_token(api_key, params, record_id, token):
    return dispatch_with_api_key("validate_token_transportista", api_key, params={'record_id': record_id, 'token': token}, method='get', **params)

def update_information_transportista(api_key, params, payload):
    return dispatch_with_api_key("update_information_transportista", api_key, params={'payload': payload}, method='post', **params)

def save_bitac_transportista_record(api_key, params, record_id, payload):
    return dispatch_with_api_key("save_bitac_transportista_record", api_key, params={'record_id': record_id, 'payload': payload}, method='post', **params)

def delete_bitac_transportista_items(api_key, params, record_id, payload):
    return dispatch_with_api_key("delete_bitac_transportista_items", api_key, params={'record_id': record_id, 'payload': payload}, method='post', **params)

def save_inspecciones(api_key, params, record_id, inspecciones):
    return dispatch_with_api_key("save_inspecciones", api_key, params={'record_id': record_id, 'inspecciones': inspecciones}, method='post', **params)

def save_inspecciones_sello(api_key, params, record_id, inspecciones):
    return dispatch_with_api_key("save_inspecciones_sello", api_key, params={'record_id': record_id, 'inspecciones': inspecciones}, method='post', **params)

def get_search_fields(api_key, params):
    return dispatch_with_api_key("get_search_fields_transportistas", api_key, params={}, method='get', **params)

def get_search_counts(api_key, params, data):
    query = {k: data.get(k) for k in ("date_from", "date_to", "facets", "candidates") if data.get(k) is not None}
    return dispatch_with_api_key("get_search_counts_transportistas", api_key, params=query, method='post', **params)

def get_inspeccion_record(api_key, params, record_id, tipo):
    return dispatch_with_api_key("get_inspeccion_record", api_key, params={'record_id': record_id, 'tipo': tipo}, method='get', **params)

def get_fotografias(api_key, params, registros):
    return dispatch_with_api_key("get_fotografias_transportista", api_key, params={'registros': registros}, method='post', **params)

def get_form_fields(api_key, params, form_ids):
    return dispatch_with_api_key("get_form_fields_transportista", api_key, params={'form_ids': form_ids}, method='post', **params)

def get_config_flujo_transportistas(api_key, params):
    return dispatch_with_api_key("get_config_flujo_transportistas", api_key, params={}, method='get', **params)

def get_formas_inspeccion_transportista(api_key, params, ubicacion):
    query = {'ubicacion': ubicacion} if ubicacion else {}
    return dispatch_with_api_key("get_formas_inspeccion_transportista", api_key, params=query, method='get', **params)

def send_aviso_correo_transportista(api_key, params, record_id, email_to):
    return dispatch_with_api_key("send_aviso_correo_transportista", api_key, params={'record_id': record_id, 'email_to': email_to}, method='post', **params)


if __name__ == "__main__":
    params = simplejson.loads(sys.argv[2])
    data = params.get('data', {})
    api_key = data.get('api_key') or config.get('APIKEY')
    option = data.get("option", '')
    inspecciones = data.get("inspecciones", [])
    payload = data.get("payload", {})
    record_id = data.get("record_id", None)
    token = data.get("token", None)
    locations = data.get("locations", None)
    location = data.get("location", None)
    print('..... arranca script transportistas')

    dispatcher = {
        "create_pass_transportista": lambda: create_pass_transportista(api_key, params, payload),
        "create_visit_transportista": lambda: create_visit_transportista(api_key, params, payload),
        "generate_submit_token_transportista": lambda: generate_submit_token_transportista(api_key, params, record_id),
        "get_andenes": lambda: get_andenes(api_key, params),
        "get_bitac_transportista_record": lambda: get_bitac_transportista_record(api_key, params, record_id),
        "get_bitac_transportista_records": lambda: get_bitac_transportista_records(api_key, params, data),
        "get_horarios_data": lambda: get_horarios_data(api_key, params, data.get('dia')),
        "get_pass_transportista": lambda: get_pass_transportista(api_key, params, record_id, token, data.get("folio")),
        "get_users_data": lambda: get_users_data(api_key, params, locations),
        "get_location_data": lambda: get_location_data(api_key, params, location),
        "get_proveedores_transportista": lambda: get_proveedores_transportista(api_key, params),
        "validate_token": lambda: validate_token(api_key, params, record_id, token),
        "update_information_transportista": lambda: update_information_transportista(api_key, params, payload),
        "save_bitac_transportista_record": lambda: save_bitac_transportista_record(api_key, params, record_id, payload),
        "delete_bitac_transportista_items": lambda: delete_bitac_transportista_items(api_key, params, record_id, payload),
        "save_inspecciones": lambda: save_inspecciones(api_key, params, record_id, inspecciones),
        "save_inspecciones_sello": lambda: save_inspecciones_sello(api_key, params, record_id, inspecciones),
        "get_search_fields": lambda: get_search_fields(api_key, params),
        "get_search_counts": lambda: get_search_counts(api_key, params, data),
        "get_inspeccion_record": lambda: get_inspeccion_record(api_key, params, record_id, data.get('tipo', '')),
        "get_fotografias": lambda: get_fotografias(api_key, params, data.get("registros", [])),
        "get_form_fields": lambda: get_form_fields(api_key, params, data.get("form_ids", [])),
        "get_config_flujo_transportistas": lambda: get_config_flujo_transportistas(api_key, params),
        "get_formas_inspeccion_transportista": lambda: get_formas_inspeccion_transportista(api_key, params, data.get("ubicacion")),
        "send_aviso_correo_transportista": lambda: send_aviso_correo_transportista(api_key, params, record_id, data.get("email_to")),
    }

    action = dispatcher.get(option)
    if not action:
        response_json = {"error": "Opción no válida"}
        sys.stdout.write(simplejson.dumps(response_json))
    else:
        response = action()
        sys.stdout.write(simplejson.dumps(response.json()))
