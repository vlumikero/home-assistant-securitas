"""
Securitas platform that offers a control over alarm status.
"""
import logging
import voluptuous as vol

from homeassistant.util import convert
from homeassistant.components.switch import (SwitchEntity)
from homeassistant.const import (STATE_OFF, STATE_ON, CONF_NAME, CONF_SWITCHES)

#import requests
import time

from homeassistant.const import (
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_DISARMED,
    STATE_ALARM_PENDING
)

DOMAIN = 'securitas'
_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_devices, discovery_info=None):


    client = hass.data[DOMAIN]['client']
    name = hass.data[DOMAIN]['name']
    
    switchSecuritas = SecuritasSwitch(hass, name, client)
    add_devices([switchSecuritas])
    add_devices([SecuritasSwitch(hass, name + " Home Mode", client, STATE_ALARM_ARMED_HOME)])


class SecuritasSwitch(SwitchEntity):

    def __init__(self, hass, name, client, mode=STATE_ALARM_ARMED_AWAY):
        _LOGGER.info("Initialized Securitas SWITCH %s", name)
        self._hass = hass
        self._hass.custom_attributes = {}
        self._name = name
        self._icon = 'mdi:lock-open-outline'
        self._state = STATE_ALARM_DISARMED
        self._mode = mode
        self._last_updated = 0
        self._client = client
        self.update()

    def _set_icon(self):
        if self._state == STATE_ALARM_ARMED_AWAY:
            self._icon = 'mdi:shield-key'
        elif self._state == STATE_ALARM_ARMED_HOME:
            self._icon = 'mdi:shield-account'
        elif self._state == STATE_ALARM_PENDING:
            self._icon = 'mdi:shield-half-full'
        else:
            self._icon = 'mdi:shield-off-outline'

        _LOGGER.debug("Update Securitas icon to %s", self._icon)

    def turn_on(self, **kwargs):
        """Turn device on."""
        _LOGGER.debug("Update Securitas SWITCH to on, mode %s ", self._mode)
        self._last_updated = time.time()
        self._client.set_alarm_status(self._mode)
        
    def turn_off(self, **kwargs):
        """Turn device off."""
        _LOGGER.debug("Update Securitas SWITCH to off")
        self._last_updated = time.time()
        self._client.set_alarm_status(STATE_ALARM_DISARMED)

    def update(self):
        _LOGGER.debug("Updated Securitas SWITCH %s", self._name)

        diff = time.time() - self._last_updated        
        if diff > 15:
            self._state = self._client.get_alarm_status()

        attributes = {}
        attributes['state'] = self._state
        self._hass.custom_attributes = attributes
        self._set_icon()
        
    @property
    def is_on(self):
        """Return true if device is switching on or is on."""
        return self._client.target_state == self._mode

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        return self._hass.custom_attributes

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, m):
        self._mode = m

    @property
    def should_poll(self):
        """Polling is needed."""
        return True

