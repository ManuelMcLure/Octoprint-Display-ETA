# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
from octoprint.util import RepeatedTimer
import time
import datetime
import logging
from babel.dates import format_date, format_datetime, format_time

_logger = logging.getLogger('octoprint.plugins.display_eta')

class DisplayETAPlugin(octoprint.plugin.ProgressPlugin,
                       octoprint.plugin.TemplatePlugin,
                       octoprint.plugin.AssetPlugin,
                       octoprint.plugin.EventHandlerPlugin,
                       octoprint.plugin.SettingsPlugin,
                       octoprint.plugin.StartupPlugin):
##    def get_template_configs(self):
##        return [
##            dict(type="settings")
##        ]
##
##    def get_template_vars(self):
##        return dict(
##            time24hr=self._settings.get(["time24hr"]),
##            sendToPrinter=self._settings.get(["sendToPrinter"])
##        )
##
    def on_after_startup(self):
        format_24hr = self._settings.get(["time24hr"])
        _logger.debug('24hrFormat ')
        _logger.debug(self._settings.get(["time24hr"]))

    def get_settings_defaults(self):
        return dict(
            time24hr=False,
            sendToPrinter=True
        )

    def __init__(self):
        self.eta_string = "-"
        self.timer = RepeatedTimer(15.0, DisplayETAPlugin.fromTimer, args=[self], run_first=True,)
        _logger.debug('reached end of __init__')

    def fromTimer(self):
        self.eta_string = self.calculate_ETA()
        self._plugin_manager.send_plugin_message(self._identifier, dict(eta_string=self.eta_string))
        
        
    def calculate_ETA(self):
        _logger.debug('calculate_ETA called')
        currentData = self._printer.get_current_data()
        if not currentData["progress"]["printTimeLeft"]:
            return "-"
        current_time = datetime.datetime.today()
        finish_time = current_time + datetime.timedelta(0,currentData["progress"]["printTimeLeft"])
        strtime = format_time(finish_time)
        strdate = ""
        if finish_time.day > current_time.day:
            if finish_time.day == current_time.day + 1:
                strdate = " Tomorrow"
            else:
                strtime = " " + format_date(finish_time,"EEE d")
        _logger.debug('reached end of calculate_ETA')
        return strtime + strdate
            
        
        
    def on_print_progress(self,storage, path, progress):
        _logger.debug('on_print_progress called')
        self.eta_string = self.calculate_ETA()
        self._printer.commands("M117 ETA is {}".format(self.eta_string))
        self._plugin_manager.send_plugin_message(self._identifier, dict(eta_string=self.eta_string))
        _logger.debug('reached end of on_print_progress')
        
    def on_event(self,event, payload):
        _logger.debug('on_event called')
        _logger.debug('event is')
        _logger.debug(event)
        if event.startswith('Print'):
            _logger.debug('event starts with Print')
            if event not in {"PrintStarted","PrintResumed"}:
                self.eta_string="-"
                self.timer.cancel()
                _logger.debug('event is not equal to PrintStarted or PrintResumed.')
            else:
                _logger.debug('event is equal to PrintStarted or PrintResumed. Calling calculate_ETA')
                self.eta_string = self.calculate_ETA()
                self.timer.cancel()
                self.timer = RepeatedTimer(10.0, DisplayETAPlugin.fromTimer, args=[self], run_first=True,)
                self.timer.start()
            self._plugin_manager.send_plugin_message(self._identifier, dict(eta_string=self.eta_string))
            _logger.debug('reached end of on_event')
            
    def get_assets(self):
        return {
            "js": ["js/display_eta.js"]
        } 


    def get_update_information(self):
        return dict(
            display_eta=dict(
            #Octoprint-Display-ETA=dict(
                displayName=self._plugin_name,
                displayVersion=self._plugin_version,
                type="github_release",
                current=self._plugin_version,
                user="AlexVerrico",
                repo="Octoprint-Display-ETA",
                pip="https://github.com/AlexVerrico/Octoprint-Display-ETA/archive/{target}.zip"
            )
        )

__plugin_name__ = "Octoprint-Display-ETA"
__plugin_identifier__ = "display_eta"
__plugin_version__ = "1.0.6"
__plugin_description__ = "Show finish time (ETA) for current print."
__plugin_implementation__ = DisplayETAPlugin()
__plugin_pythoncompat__ = ">=2.7,<4"

__plugin_hooks__ = {
    "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
}

