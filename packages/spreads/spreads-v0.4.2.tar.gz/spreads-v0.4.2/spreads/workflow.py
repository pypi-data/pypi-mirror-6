# -*- coding: utf-8 -*-

# Copyright (c) 2013 Johannes Baiter. All rights reserved.
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
spreads workflow object.
"""

from __future__ import division, unicode_literals

import logging
import time

import spreads.vendor.confit as confit
from concurrent.futures import ThreadPoolExecutor
from spreads.vendor.pathlib import Path

from spreads.plugin import get_pluginmanager, get_devices
from spreads.util import check_futures_exceptions, DeviceException


class Workflow(object):
    path = None
    step = None
    step_done = False
    capture_start = None
    _pages_shot = 0

    _devices = None
    _pluginmanager = None

    def __init__(self, path, config=None, step=None, step_done=None):
        self.logger = logging.getLogger('Workflow')
        self.step = step
        self.step_done = step_done
        if not isinstance(path, Path):
            path = Path(path)
        self.path = path
        if not self.path.exists():
            self.path.mkdir()
        # See if supplied `config` is already a valid Configuration object
        if isinstance(config, confit.Configuration):
            self.config = config
        else:
            self.config = self._load_config(config)

    @property
    def plugins(self):
        if self._pluginmanager is None:
            self._pluginmanager = get_pluginmanager(self.config)
        return [ext.obj for ext in self._pluginmanager]

    @property
    def devices(self):
        if self._devices is None:
            self._devices = get_devices(self.config)
        if not self._devices:
            raise DeviceException("Could not find any compatible devices!")
        return self._devices

    @property
    def images(self):
        # Get fresh image list if number of pages has changed
        raw_path = self.path / 'raw'
        if not raw_path.exists():
            return None
        return sorted(raw_path.iterdir())

    @property
    def out_files(self):
        out_path = self.path / 'out'
        if not out_path.exists():
            return None
        else:
            return sorted(out_path.iterdir())

    def _load_config(self, value):
        # Load default configuration
        config = confit.Configuration('spreads')
        cfg_file = self.path / 'config.yml'
        if value is None and cfg_file.exists():
            # Load workflow-specific configuration from file
            config.set(confit.ConfigSource({}, unicode(cfg_file)))
        elif value is not None:
            # Load configuration from supplied ConfigSource or dictionary
            config.set(value)
        return config

    def _run_hook(self, hook_name, *args):
        self.logger.debug("Running '{0}' hooks".format(hook_name))
        for plugin in self.plugins:
            getattr(plugin, hook_name)(*args)

    def _get_next_filename(self, target_page=None):
        """ Get next filename that a capture should be stored as.

        If the workflow is shooting with two devices, this will select a
        filename that matches the device's target page (odd/even).

        :param target_page: target page of file ('odd/even')
        :type target_page:  str/unicode/None if not applicable
        :return:            absolute path to next filename
                            (e.g. /tmp/proj/003.jpg)
        :rtype:             pathlib.Path
        """
        base_path = self.path / 'raw'
        if not base_path.exists():
            base_path.mkdir()

        try:
            last_num = int(self.images[-1].stem)
        except IndexError:
            last_num = -1

        if target_page is None:
            return base_path / "{03:0}".format(self._pages_shot)

        next_num = (last_num+2 if target_page == 'odd' else last_num+1)
        return base_path / "{0:03}".format(next_num)

    def prepare_capture(self):
        self.logger.info("Preparing capture.")
        self.step = 'capture'
        if any(dev.target_page is None for dev in self.devices):
            raise DeviceException(
                "Target page for at least one of the devicescould not be"
                "determined, please run 'spread configure' to configure your"
                "your devices.")
        with ThreadPoolExecutor(len(self.devices)) as executor:
            futures = []
            self.logger.debug("Preparing capture in devices")
            for dev in self.devices:
                futures.append(executor.submit(dev.prepare_capture, self.path))
        check_futures_exceptions(futures)

        flip_target = ('flip_target_pages' in self.config['device'].keys()
                       and self.config['device']['flip_target_pages'].get())
        if flip_target:
            (self.devices[0].target_page,
             self.devices[1].target_page) = (self.devices[1].target_page,
                                             self.devices[0].target_page)
        self._run_hook('prepare_capture', self.devices, self.path)

    def capture(self, retake=False):
        if self.capture_start is None:
            self.capture_start = time.time()
        self.logger.info("Triggering capture.")
        parallel_capture = ('parallel_capture' in self.config['device'].keys()
                            and self.config['device']['parallel_capture'].get()
                            )
        num_devices = 1 if not parallel_capture else 2

        if retake:
            # Remove last n images, where n == len(self.devices)
            map(lambda x: x.unlink(), self.images[-num_devices:])

        with ThreadPoolExecutor(num_devices) as executor:
            futures = []
            self.logger.debug("Sending capture command to devices")
            for dev in self.devices:
                img_path = self._get_next_filename(dev.target_page)
                futures.append(executor.submit(dev.capture, img_path))
        check_futures_exceptions(futures)
        self._run_hook('capture', self.devices, self.path)
        self._pages_shot += len(self.devices)

    def finish_capture(self):
        self.step_done = True
        self._run_hook('finish_capture', self.devices, self.path)

    def process(self):
        self.step = 'process'
        self.step_done = False
        self.logger.info("Starting postprocessing...")
        self._run_hook('process', self.path)
        self.logger.info("Done with postprocessing!")
        self.step_done = True

    def output(self):
        self.logger.info("Generating output files...")
        self.step = 'output'
        self.step_done = False
        out_path = self.path / 'out'
        if not out_path.exists():
            out_path.mkdir()
        self._run_hook('output', self.path)
        self.logger.info("Done generating output files!")
        self.step_done = True
