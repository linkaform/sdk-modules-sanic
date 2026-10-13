#!/usr/local/bin/python
# coding: utf-8
import sys, simplejson, lkf_addons
from middleware.auth import dispatch


def list_script_logs(params):
    data = params.get("data", {})
    return dispatch("list_script_logs", module='base', params={
        'limit': data.get('limit', 25),
        'skip': data.get('offset', 0),
        'status': data.get('status'),
        'script_ids': data.get('script_ids', []),
        'script_name': data.get('script_name', ''),
        'user_ids': data.get('user_ids', []),
        'user_name': data.get('user_name', ''),
        'date1': data.get('date1'),
        'date2': data.get('date2'),
        'min_duration': data.get('min_duration'),
        'max_duration': data.get('max_duration'),
        'run_success': data.get('run_success'),
    }, method='post', **params)

def get_script_log_filters(params):
    return dispatch("get_script_log_filters", module='base', params={}, method='get', **params)

def get_script_log_content(params):
    data = params.get("data", {})
    return dispatch("get_script_log_content", module='base', params={
        'log_url': data.get('log_url', ''),
    }, method='post', **params)


DISPATCHER = {
    "list_script_logs": list_script_logs,
    "get_script_log_filters": get_script_log_filters,
    "get_script_log_content": get_script_log_content,
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
