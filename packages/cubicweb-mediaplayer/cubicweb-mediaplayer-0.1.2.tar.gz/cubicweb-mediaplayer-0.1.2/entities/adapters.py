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

"""cubicweb-mediaplayer adapters classes"""

from cubicweb.entities import adapters
from cubicweb.predicates import score_entity, is_instance, adaptable
from cubicweb.web.views.idownloadable import DownloadBox

from cubes.mediaplayer import utils

# sound, files adapters ########################################
def formatted_size(session, num):
    _ = session._
    try:
        num = float(num)
    except Exception:
        return _("N/A")
    for x in [_('B'), _('kB'), _('MB'), _('GB')]:
        if num < 1024.0 and num > -1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
    return "%3.1f %s" % (num, _('TB'))


class MediaFileIDownloadableAdapter(adapters.IDownloadableAdapter):
    """ this comes from file """
    __select__ = is_instance('SoundFile', 'VideoFile')
    _format = None

    def download_url(self, **kwargs):
        # include filename in download url for nicer url
        path = '%s/raw' % (self.entity.rest_path())
        return self._cw.build_url(path, **kwargs)

    def download_content_type(self):
        return self.entity.data_format

    def download_encoding(self):
        return self.entity.data_encoding

    def download_file_name(self):
        return self.entity.data_name

    def download_data(self):
        data = self.entity.data
        if data:
            return data.getvalue()

def has_bytes(entity, bytes_attrs):
    return set(bytes_attrs).intersection(entity.__bytes_attributes__)


class FormatedMediaFileIDownloadableAdapter(MediaFileIDownloadableAdapter):
    __abstract__ = True

    def download_content_type(self):
        return getattr(self.entity, 'data_%s_format', self._format)

    def download_data(self):
        data = getattr(self.entity, 'data_%s' % self._format)
        if data:
            return data.getvalue()

    def download_url(self, **kwargs):
        path = '%s/%s' % (self.entity.rest_path(),
                          self._format)
        return self._cw.build_url(path, **kwargs)

    def download_file_name(self):
        return '%s.%s' % (self.entity.data_name, self.download_content_type())

class OggIDownloadableAdapter(FormatedMediaFileIDownloadableAdapter):
    __regid__ = 'OggIDownloadable'
    __abstract__ = True

class SoundFileOggIDownloadableAdapter(OggIDownloadableAdapter):
    __select__ = score_entity(lambda e: has_bytes(e, ('data_oga',)))
    _format = 'oga'

class VideoFileOggIDownloadableAdapter(OggIDownloadableAdapter):
    __select__ = score_entity(lambda e: has_bytes(e, ('data_ogv',)))
    _format = 'ogv'

class MpegIDownloadableAdapter(FormatedMediaFileIDownloadableAdapter):
    __regid__ = 'MpegIDownloadable'
    __abstract__ = True

class SoundFileMpegIDownloadableAdapter(MpegIDownloadableAdapter):
    __select__ = score_entity(lambda e: has_bytes(e, ('data_mp3',)))
    _format = 'mp3'

class VideoFileMpegIDownloadableAdapter(MpegIDownloadableAdapter):
    __select__ = score_entity(lambda e: has_bytes(e, ('data_mp4',)))
    _format = 'mp4'

class WebMIDownloadableAdapter(FormatedMediaFileIDownloadableAdapter):
    __regid__ = 'WebMIDownloadable'
    __select__ = score_entity(lambda e: has_bytes(e, ('data_webm',)))
    _format = 'webm'
