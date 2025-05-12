"""
Securitas platform that offers a control over alarm status.
"""
import logging
import voluptuous as vol

from homeassistant.util import convert
from homeassistant.components.alarm_control_panel import (AlarmControlPanelEntity)
from homeassistant.const import (STATE_OFF, STATE_ON, CONF_NAME, CONF_SWITCHES)

#import requests
import time

from homeassistant.const import (
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_DISARMED,
    STATE_ALARM_PENDING,
)

DOMAIN = 'securitas'
_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_devices, discovery_info=None):


    client = hass.data[DOMAIN]['client']
    name = hass.data[DOMAIN]['name']
    
    add_devices([SecuritasAlarmPanel(name, client)])


class SecuritasAlarmPanel(AlarmControlPanelEntity):

    def __init__(self, name, client, mode=STATE_ALARM_ARMED_AWAY):
        _LOGGER.info("Initialized Securitas SWITCH %s", name)
        self._name = name
        self._state = STATE_ALARM_DISARMED
        self._last_updated = 0
        self._client = client
        self.update()

    #@property
    #def supported_features(self) -> int:
        """Return the list of supported features."""
    #    return SUPPORT_ALARM_ARM_HOME | SUPPORT_ALARM_ARM_AWAY

    def update(self):
        _LOGGER.debug("Updated Securitas SWITCH %s", self._name)

        diff = time.time() - self._last_updated        
        if diff > 15:
            self._state = self._client.get_alarm_status()

    @property
    def state(self):
        """Return the state of the alarm."""
        return self._state

    def alarm_arm_home(self, code=None):
        """ Try to arm home. """
        self._last_updated = time.time()
        self._client.set_alarm_status(STATE_ALARM_ARMED_HOME)
        self._state = STATE_ALARM_PENDING

    def alarm_disarm(self, code=None):
        self._last_updated = time.time()
        self._client.set_alarm_status(STATE_ALARM_DISARMED)
        self._state = STATE_ALARM_PENDING

    def alarm_arm_away(self, code=None):
        self._last_updated = time.time()
        self._client.set_alarm_status(STATE_ALARM_ARMED_AWAY)
        self._state = STATE_ALARM_PENDING

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def code_format(self):
        return None

    #@property
    #def should_poll(self):
        """Polling is needed."""
    #    return True

