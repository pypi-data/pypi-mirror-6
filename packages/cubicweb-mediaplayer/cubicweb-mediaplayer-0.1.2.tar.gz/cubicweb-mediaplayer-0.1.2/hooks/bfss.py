# -*- coding: utf-8 -*-
# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-mediaplayer specific bfss hooks and operations"""

import os

from cubicweb.server.hook import Hook
from cubicweb.server.sources.storages import BytesFileSystemStorage

class MediaPlayerServerStartupHook(Hook):
    __regid__ = 'mediaplayer.server-startup-hook'
    events = ('server_startup', 'server_maintenance')

    def __call__(self):
        # NOTE: defaultdirectory passed to ImageFileSystemStorage is actually
        #       not used for now since we always recompute output directory path
        bfss_root = self.repo.vreg.config['media-dir']
        if not os.path.isdir(bfss_root):
            os.makedirs(bfss_root)
        bfss_root = bfss_root.encode('utf-8') # work around a bug in BFSS
        storage = BytesFileSystemStorage(bfss_root)
        for etype_name in ('SoundFile', 'VideoFile'):
            etype = self.repo.vreg['etypes'].etype_class(etype_name)
            for attr in etype.__bytes_attributes__:
                self.repo.system_source.set_storage(etype_name, attr, storage)
