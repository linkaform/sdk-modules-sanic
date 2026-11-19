#!/usr/local/bin/python
# coding: utf-8
# Override de rutas del modulo Base. loader.extend_routes('Base', ...) busca
# `base_routes.py`, y las rutas que repitan un URI del blueprint original lo
# sustituyen (las demas se conservan).
#
# Aqui solo se sobrescribe /base/list_script_logs para que use ScriptLogs de
# base_service.py (con la correccion de fechas). Cuando la correccion viva en
# addons/base/app.py, este archivo y base_service.py se pueden eliminar.
from sanic import Blueprint
from sanic.request import Request
from sanic.response import json

from config.account_settings import *

from loader import CUSTOM_MODULE_PATHS, find_module_file, load_class_from_file


def _load_script_logs():
    """ScriptLogs de base_service.py; si no aparece, la clase original."""
    path, _ = find_module_file(CUSTOM_MODULE_PATHS, 'Base', ['base_service.py'])
    cls = load_class_from_file(path, 'ScriptLogs') if path else None
    if cls is None:
        print('>>> base_service.py no disponible, usando ScriptLogs original')
        from lkf_addons.base.app import ScriptLogs as cls
    return cls


script_logs_service = _load_script_logs()(settings)

base_bp = Blueprint("base", url_prefix="/base")
# loader.load_blueprint_from_file() busca por default el atributo `accesos_bp`
# (blueprint_name no se pasa desde extend_routes), asi que se expone con ese
# nombre tambien.
accesos_bp = base_bp


def _payload(request: Request) -> dict:
    try:
        if request.json:
            return request.json
    except Exception:
        pass
    return {}


@base_bp.post("/list_script_logs")
async def post_list_script_logs(request: Request):
    p = _payload(request)
    response = script_logs_service.list_script_logs(
        limit=p.get('limit', 25),
        skip=p.get('skip', 0),
        status=p.get('status'),
        script_ids=p.get('script_ids'),
        script_name=p.get('script_name', ''),
        user_ids=p.get('user_ids'),
        user_name=p.get('user_name', ''),
        date1=p.get('date1'),
        date2=p.get('date2'),
        min_duration=p.get('min_duration'),
        max_duration=p.get('max_duration'),
        run_success=p.get('run_success'),
    )
    return json({"data": response}, status=200)
