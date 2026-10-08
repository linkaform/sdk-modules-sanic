#!/usr/local/bin/python
# coding: utf-8
import sys, simplejson, lkf_addons
from middleware.auth import dispatch

if __name__ == "__main__":
    params = simplejson.loads(sys.argv[2])
    print('..... arranca script close_rondines')
    response = dispatch("close_rondines", params={}, method='post', **params)
    sys.stdout.write(simplejson.dumps(response.json()))
