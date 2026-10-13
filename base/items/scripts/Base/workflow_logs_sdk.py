#!/usr/local/bin/python
# coding: utf-8
import sys, simplejson, lkf_addons
from middleware.auth import dispatch


def list_workflow_logs(params):
    data = params.get("data", {})
    return dispatch("list_workflow_logs", module='base', params={
        'limit': data.get('limit', 25),
        'skip': data.get('offset', 0),
        'status': data.get('status'),
        'rules': data.get('rules', []),
        'events': data.get('events', []),
        'workflow_names': data.get('workflow_names', []),
        'form_ids': data.get('form_ids', []),
        'user_ids': data.get('user_ids', []),
        'date1': data.get('date1'),
        'date2': data.get('date2'),
    }, method='post', **params)

def get_workflow_log_filters(params):
    return dispatch("get_workflow_log_filters", module='base', params={}, method='get', **params)

def get_workflow_log_detail(params):
    data = params.get("data", {})
    return dispatch("get_workflow_log_detail", module='base', params={
        'log_id': data.get('log_id', ''),
    }, method='post', **params)


DISPATCHER = {
    "list_workflow_logs": list_workflow_logs,
    "get_workflow_log_filters": get_workflow_log_filters,
    "get_workflow_log_detail": get_workflow_log_detail,
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
