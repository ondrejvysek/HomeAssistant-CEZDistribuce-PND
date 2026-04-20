import appdaemon.plugins.hass.hassapi as hass

class InitHelper(hass.Hass):
    def initialize(self):
        self.fire_event("APPDAEMON_READY")
