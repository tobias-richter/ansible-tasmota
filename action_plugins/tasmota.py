#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import requests
import json

from ansible.module_utils._text import to_native
from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleOptionsError

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()

class ActionModule(ActionBase):
    TRANSFERS_FILES = False

    def __init__(self, task, connection, play_context, loader, templar, shared_loader_obj):
        super(ActionModule, self).__init__(task, connection, play_context, loader, templar, shared_loader_obj)
        self._task_vars = None

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        # uncomment to enable request debugging
        #try:
        #    import http.client as http_client
        #except ImportError:
        #    # Python 2
        #    import httplib as http_client
        #    http_client.HTTPConnection.debuglevel = 1
##
        #logLevel = logging.DEBUG
        #logging.basicConfig()
        #logging.getLogger().setLevel(logLevel)
        #requests_log = logging.getLogger("requests.packages.urllib3")
        #requests_log.setLevel(logLevel)
        #requests_log.propagate = True

        result = super(ActionModule, self).run(tmp, task_vars)

        self._task_vars = task_vars
        changed = False

        display.v("args: %s" % (self._task.args))

        try:
            # Get the tasmota host
            tasmota_host = self._get_arg_or_var('tasmota_host', task_vars['ansible_host'])
            command = self._get_arg_or_var('command')
            incoming_value = self._get_arg_or_var('value')

        except Exception as err:
            display.v("got an exception: %s" % (err))
            display.v("got an exception: "+err.message)
            return self._fail_result(result, "error during retrieving parameter '%s'" % (err.message))

        endpoint_uri = "http://%s/cm" % (tasmota_host)
        status_params = {'cmnd' : command }

        # execute command
        status_response = requests.get(url = endpoint_uri, params = status_params)
        # get response data
        data = status_response.json()
        display.v("data: %s" % (data))
        existing_value = unicode(data.get(command))

        if (command.startswith('Rule')):
            display.vv("rule found!")
            existing_once = data.get("Once")
            existing_rules = data.get("Rules")
            existing_rule = data.get(command)
            existing_stop_on_error = data.get("StopOnError")
            if incoming_value in ["0","1","2"]:
                display.vv("disable, enable, toggle rule found")
                existing_value = self._translateResultStr(existing_value)
            elif incoming_value in ["4","5"]:
                display.vv("disable, enable oneshot")
                existing_value = self._translateResultStr(existing_once, "4", "5")
            elif incoming_value.startswith("on"):
                display.vv("rule value found")
                existing_value = existing_rules
        elif (command.startswith('SetOption')):
            existing_value = self._translateResultStr(existing_value)
        elif (command.startswith('PowerRetain')):
            existing_value = self._translateResultStr(existing_value)

        display.v("[%s] command: %s, existing_value: '%s', incoming_value: '%s'" % (tasmota_host, command, existing_value, incoming_value))



        display.v("[%s] existing_uri: %s" % (tasmota_host, endpoint_uri))
        if existing_value != incoming_value:
            changed = True
            change_params = { 'cmnd' : ("%s %s" % (command, incoming_value)) }
            change_response = requests.get(url = endpoint_uri, params = change_params)

        result["changed"] = changed
        result["command"] = command
        result["tasmota_host"] = tasmota_host
        result["raw_data"] = data
        result["endpoint_uri"] = endpoint_uri
        result["incoming_value"] = incoming_value
        result["existing_value"] = existing_value

        return result

    @staticmethod
    def _fail_result(result, message):
        display.v("_fail_result")
        result['failed'] = True
        result['msg'] = message
        return result

    def _get_arg_or_var(self, name, default=None, is_required=True):
        display.v("%s, %s, %s" % (name, default, is_required))
        ret = self._task.args.get(name, self._task_vars.get(name, default))
        ret = self._templar.template(ret)
        if is_required and ret == None:
            raise AnsibleOptionsError("parameter %s is required" % name)
        else:
            return ret

    def _translateResultStr(self, translate, offValue = "0", onValue = "1"):
      if (translate == "OFF"):
        return offValue
      if (translate == "ON"):
        return onValue
      return translate

