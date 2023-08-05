import unittest

import pytest
import spreads.vendor.confit as confit
from mock import call, MagicMock as Mock, patch

import spreads.plugin as plugin
from spreads.util import DeviceException


class TestPlugin(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_driver(self):
        assert "dummy" in plugin.get_driver("dummy").names()

    @patch('spreads.plugin.get_driver')
    def test_get_devices(self, get_driver):
        cfg = Mock()
        cfg.keys.return_value = ["driver"]
        driver = Mock()
        usb_mock = Mock()
        plugin.usb.core.find = Mock(return_value=[usb_mock])
        get_driver.return_value = driver
        plugin.get_driver = get_driver
        plugin.get_devices(cfg)
        assert call(cfg["device"], usb_mock) in driver.driver.call_args_list
        assert driver.driver.match.call_args_list == [call(usb_mock)]

    @patch('spreads.plugin.get_driver')
    def test_no_devices(self, get_driver):
        cfg = Mock()
        driver = Mock()
        driver.driver.match = Mock(return_value=False)
        usb_mock = Mock()
        plugin.usb.core.find = Mock(return_value=[usb_mock])
        get_driver.return_value = driver
        plugin.get_driver = get_driver
        with pytest.raises(DeviceException) as excinfo:
            plugin.get_devices(cfg)
