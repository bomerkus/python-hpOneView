# -*- coding: utf-8 -*-
###
# (C) Copyright (2012-2016) Hewlett Packard Enterprise Development LP
#
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
###

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from future import standard_library

standard_library.install_aliases()

__title__ = 'firmware-bundles'
__version__ = '0.0.1'
__copyright__ = '(C) Copyright (2012-2016) Hewlett Packard Enterprise ' \
                ' Development LP'
__license__ = 'MIT'
__status__ = 'Development'

from hpOneView.resources.resource import ResourceClient
from hpOneView.resources.task_monitor import TaskMonitor

from hpOneView.exceptions import HPOneViewException

import os


class FirmwareBundles(object):
    URI = '/rest/firmware-bundles'

    def __init__(self, con):
        self._connection = con
        self._client = ResourceClient(con, self.URI)
        self._task_monitor = TaskMonitor(con)

    def upload(self, file_path, timeout=-1):
        """
        Upload an SPP ISO image file or a hotfix file to the appliance.
        The API supports upload of one hotfix at a time into the system.
        For the successful upload of a hotfix, ensure its original name and extension are not altered.

        Args:
            file_path: Full path to firmware.
            timeout:
                Timeout in seconds. Wait task completion by default. The timeout does not abort the operation
                in OneView, just stops waiting for its completion.

        Returns:
          dict: Information about the updated firmware bundle.

        """
        upload_file_name = os.path.basename(file_path)
        response, body = self._connection.post_multipart(self.URI, None, file_path, upload_file_name)
        if response.status >= 400:
            raise HPOneViewException(body.get('message'))

        return self._task_monitor.wait_for_task(body, timeout)
