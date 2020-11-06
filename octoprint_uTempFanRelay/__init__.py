# coding=utf-8
from __future__ import absolute_import

### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.

import octoprint.plugin
import octoprint.util
from octoprint.server import user_permission
from flask import make_response, jsonify

class UtempfanrelayPlugin(octoprint.plugin.StartupPlugin,
                          octoprint.plugin.SettingsPlugin,
                          octoprint.plugin.AssetPlugin,
                          octoprint.plugin.EventHandlerPlugin,
                          octoprint.plugin.SimpleApiPlugin,
                          octoprint.plugin.TemplatePlugin):

    def on_startup(self, *args, **kwargs):
        try:
            global GPIO
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            self._hasGPIO = True
        except (ImportError, RuntimeError):
            self._hasGPIO = False

        self.read_settings()
        self.init_fan_pin()

        self.progress = '0%'
        self.totalLayer = '0'
        self.currentLayer = '0'
        self.printTimeLeft = '0'

        self._logger.info("about to start...")

        self.timer = octoprint.util.RepeatedTimer(10, self.updateLCD, run_first=True)
        self.timer.start()

        self._logger.info("uTempFanRelay STARTED!")

    def hook(self, comm_instance, line, *args, **kwargs):

        if 'enabled' not in self.__dict__:
            self._logger.info("TOO EARLY!!!")
            return line

        if not self.enabled:
            if not self.is_fan_ON():
                self.turn_fan_on()
            return line

        heaters = self._printer.get_current_temperatures()
        for heater, entry in heaters.items():
            if not heater.startswith("tool"):
                continue

            actual = entry.get("actual")
            target = entry.get("target")
            if actual is None:
                # heater doesn't exist in fw
                continue

            try:
                actu = float(actual)
                targ = float(target)
            except ValueError:
                # not a float for some reason, skip it
                continue

            # Cooling: if heater is off AND tool temperature is below threshold, turn off FAN
            if targ == 0 and actu < self.tempSwitch and self.is_fan_ON():
                self.turn_fan_off()
                self._logger.info("Switching OFF: Temp=%s, Target=%s, Threshold=%s" % (actu, targ, self.tempSwitch))

            # Heating: if heater is on OR tool is above the threshold: turn on FAN!!!
            elif (actu < targ or actu > self.tempSwitch) and not self.is_fan_ON():
                self.turn_fan_on()
                self._logger.info("Switching ON: Temp=%s, Target=%s, Threshold=%s" % (actu, targ, self.tempSwitch))

        return line

    def updateLCD(self):
        self._logger.info("inside updateLCD")
        self.lcdText = "M117 " + self.progress + "% " + self.currentLayer + "/" + self.totalLayer + " " + self.printTimeLeft
        self._logger.info(lcdText)
        self._logger.info(self.tempEnclosureSerial)

        try:
            fileName = "/sys/bus/w1/devices/" + self.tempEnclosureSerial + "/w1_slave"
            self._logger.info(fileName)
            with open(fileName, 'r') as file:
                data = file.read().split("=")
                self._logger.info(data)
                tempEnclosure = int(float(data[-1]) / 1000 + 0.5)
                self._logger.info(tempEnclosure)
                self.lcdText += " " + tempEnclosure
                self._logger.info(lcdText)
        except ValueError:
            self._logger.info("ERROR - No sensor for temperature found")

        self._printer.commands(self.lcdText)

    def on_event(self, event, payload):
        if event == "DisplayLayerProgress_layerChanged":
            self.progress = payload['progress']
            self.totalLayer = payload['totalLayer']
            self.currentLayer = payload['currentLayer']
            self.printTimeLeft, *secs = payload['printTimeLeft'].split("m")
            self._logger.info("About to update LCD, on_event...")
            self.updateLCD()
            self._logger.info("done...")


    def get_settings_defaults(self):
        return dict(
            enabled = False,
            fanPin = 14,
            pinInverted = True,
            tempSwitch = 40.0,
            tempEnclosureSerial = ""
        )

    def get_settings_version(self):
        return 1

    def read_settings(self):

        self.tempEnclosureSerial = self._settings.get(["tempEnclosureSerial"])
        self._logger.info("tempEnclosureSerial= %s" % self.tempEnclosureSerial)

        self.enabled = self._settings.get_boolean(["enabled"])
        self._logger.info("enabled      = %s" % self.enabled)

        self.fanPin = self._settings.get_int(["fanPin"])
        self._logger.info("fanPin      = %s" % self.fanPin)

        self.tempSwitch = self._settings.get_float(["tempSwitch"])
        self._logger.info("tempSwitch  = %s" % self.tempSwitch)

        self.pinInverted = self._settings.get_boolean(["pinInverted"])
        self._logger.info("pinInverted = %s" % self.pinInverted)

        self.fanOff = self.pinInverted
        self.fanOn = not self.fanOff
        self._logger.info("fanOn       = %s" % self.fanOn)
        self._logger.info("fanOff      = %s" % self.fanOff)

    def on_settings_save(self, data):
        oldFanPin = self.fanPin
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

        self.read_settings()
        if self.fanPin != oldFanPin:
            self.init_fan_pin()

    def init_fan_pin(self):
        if self._hasGPIO:
            try:
                GPIO.setup(self.fanPin, GPIO.OUT, initial=self.fanOn)
                self.allOk = True
            except (ImportError, RuntimeError):
                self.allOk = False
        self._logger.info("fan pin init = %s" % self.allOk)

    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=False)
            ]

	##~~ ApiPlugin mixin

    def get_api_commands(self):
        return dict(
            enable=[],
            disable=[],
            getFanState=[]
        )

    def on_api_get(self, request):
        return self.on_api_command(request.args['command'], [])

    def on_api_command(self, command, data):
        if not user_permission.can():
            return make_response("Insufficient rights", 403)

        self._logger.info("Command via API=%s" % command)
        if command == 'disable':
            self.enabled = False
            self.turn_fan_on()
            self._logger.info("Disabling plugin")
        elif command == 'enable':
            self.enabled = True
            self.turn_fan_on()
            self._logger.info("Enabling plugin")

        isFO = self.is_fan_ON()
        self._logger.info("isFanOn via API=%s" % isFO)
        return jsonify(isFanOn=isFO)

    def turn_fan_on(self):
        GPIO.output(self.fanPin, self.fanOn)

    def turn_fan_off(self):
        GPIO.output(self.fanPin, self.fanOff)

    def is_fan_ON(self):
        # Read FAN status from GPIO
        return GPIO.input(self.fanPin) ^ self.pinInverted

	##~~ Softwareupdate hook

    def get_update_information(self):
        return dict(
            uTempFanRelay=dict(
                displayName="uTempFanRelay Plugin",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="umbacos",
                repo="uTempFanRelay",
                current=self._plugin_version,

                # update method: pip
                pip="https://github.com/umbacos/uTempFanRelay/archive/master.zip"
            )
        )

__plugin_name__ = "uTempFanRelay"
__plugin_pythoncompat__ = ">=3,<4"
__plugin_implementation__ = UtempfanrelayPlugin()
__plugin_hooks__ = {
            "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
            "octoprint.comm.protocol.gcode.received": __plugin_implementation__.hook
            }
