# -*- coding: utf-8 -*-
# Override de ScriptLogs (lkf_addons.base.app) para probar correcciones en
# caliente, sin rebuild. Lo carga base_routes.py via loader (CUSTOM_MODULE_PATHS).
#
# Vacio a proposito: la correccion de fechas (ScriptLogs._iso) ya vive en
# addons/base/app.py. Agrega aqui solo lo que estes probando; al validarlo,
# llevalo a app.py y vuelve a vaciar este archivo.
from lkf_addons.base.app import ScriptLogs as _ScriptLogs


class ScriptLogs(_ScriptLogs):
    pass
