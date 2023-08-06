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

"""cubicweb-mediaplayer entity's classes"""
from os.path import join

import datetime
from logilab.mtconverter import guess_mimetype_and_encoding

from cubicweb import Binary
from cubicweb.entities import AnyEntity, fetch_config
from cubicweb.predicates import is_instance

from cubicweb.server.repository import Repository

from cubes.mediaplayer.utils import media

def fs_encoding(repo, etype, attr):
    # XXX fspath computation should be done here. (or in the adapters).
    storage = repo.system_source.storage(etype, attr)
    return storage.fsencoding

Repository.fs_encoding = fs_encoding
del fs_encoding

def _get_repo(appobject):
    if hasattr(appobject._cw, 'repo'):
        return appobject._cw.repo
    elif hasattr(appobject._cw.cnx, '_repo'):
        return appobject._cw.cnx._repo
    else:
        assert False, 'no repo found from %s' % appobject

class MediaMixIn(object):
    """those methods basically come from File"""
    __bytes_attributes__ = ()

    def dc_title(self):
        if self.title:
            return '%s (%s)' % (self.title, self.data_name)
        return self.data_name

    def set_format_and_encoding(self):
        """try to set format and encoding according to known values (filename,
        file content, format, encoding).

        This method must be called in a before_[add|update]_entity hook else it
        won't have any effect.
        """
        assert 'data' in self.cw_edited, "missing mandatory attribute data"
        if self.cw_edited.get('data'):
            if hasattr(self.data, 'filename') \
                   and not self.cw_edited.get('data_name'):
                self.cw_edited['data_name'] = self.data.filename
        else:
            self.cw_edited['data_format'] = None
            self.cw_edited['data_encoding'] = None
            self.cw_edited['data_name'] = None
            return
        if 'data_format' in self.cw_edited:
            format = self.cw_edited.get('data_format')
        else:
            format = None
        if 'data_encoding' in self.cw_edited:
            encoding = self.cw_edited.get('data_encoding')
        else:
            encoding = None
        if not (format and encoding):
            format, encoding = guess_mimetype_and_encoding(
                data=self.cw_edited.get('data'),
                # use get and not get_value since data has changed, we only want
                # to consider explicitly specified values, not old ones
                filename=self.cw_edited.get('data_name'),
                format=format, encoding=encoding,
                fallbackencoding=self._cw.encoding)
            if format:
                self.cw_edited['data_format'] = unicode(format)
            if encoding:
                self.cw_edited['data_encoding'] = unicode(encoding)

    @property
    def formatted_duration(self):
        if self.length:
            return str(datetime.timedelta(seconds=self.length))
        return '00:00'

    def read(self, size=-1):
        return self.data.read(size)

    def seek(self, pos, *args, **kwargs):
        return self.data.seek(pos, *args, **kwargs)

    def tell(self):
        return self.data.tell()

    def icon_url(self):
        config = self._cw.vreg.config
        for rid in (self.data_format.replace('/', '_', 1),
                    self.data_format.split('/', 1)[0],
                    'default'):
            iconfile = rid + '.ico'
            rpath, iconfile = config.locate_resource(join('icons', iconfile))
            if rpath is not None:
                return self._cw.data_url(iconfile)

    def fspath(self, attr=None):
        rql = 'Any fspath(D) WHERE X eid %%(x)s, X %s D' % (attr)
        rset = self._cw.execute(rql, {'x': self.eid})
        if rset:
            path = rset[0][0]
            # XXX we need unicode to avoid standard str / unicode mix
            # mess, use storage's fsencoding to decode.
            if path is not None:
                fs_encoding = _get_repo(self).fs_encoding(self.__regid__, attr)
                path = unicode(path.getvalue(), fs_encoding)
        else:
            path = None
        return path


class SoundFile(MediaMixIn, AnyEntity):
    __regid__ = 'SoundFile'
    __bytes_attributes__ = ('data', 'data_mp3', 'data_oga')

    fetch_attrs, cw_fetch_order = fetch_config(
        ['data_name', 'title', 'length',
         'data_mp3_name', 'data_oga_name'])

    def reencode(self):
        """ Re-encode the file in .mp3 and .oga formats"""
        if self._cw.transaction_data.get('fs_importing', None) is None:
            self._cw.transaction_data['fs_importing'] = False
        outputs = self.reencode_sound()
        self.update_entity(outputs)

    def reencode_sound(self):
        outputs = media.get_sound_formats(self)
        return media.reencode_sound(self, outputs)

    def update_entity(self, outputs):
        for _format, binary_data in outputs.iteritems():
            media.set_bytes_attr(self,
                                'data_%s' % _format,
                                 binary_data,
                                 u'audio/%s' % _format # XXX do it from ffmpeg
                           )

class VideoFile(MediaMixIn, AnyEntity):
    __regid__ = 'VideoFile'
    __bytes_attributes__ = ('data', 'data_mp4', 'data_ogv', 'data_webm')

    fetch_attrs, cw_fetch_order = fetch_config(
        ['data_name', 'title', 'length', 'width', 'height',
         'data_mp4_name', 'data_ogv_name', 'data_webm_name'])

    def reencode(self):
        """Re-encode the video in all appropriate format.

        This methode update format attribut in place"""
        outputs = self.reencode_video()
        self.update_entity(outputs)

    def reencode_video(self):
        self.size = None
        formats = media.video_filter_format(self)
        outputs = {}
        for fmt in formats:
            attr = 'data_%s' % fmt[0]
            outputs[fmt[0]] = fmt
            self.size = fmt[3]
        if outputs:
            return media.reencode_video(self, outputs)
        return None

    def update_entity(self, results):
        attrs = {}
        for attr, (fmt, binary_data) in results.iteritems():
            attr = 'data_%s' % attr
            attrs[attr] = binary_data
            attrs['%s_name' % attr] = self.data_name
            attrs['%s_format' % attr] = u'video/%s' % fmt # XXX check ffmpeg output
        if self.size:
            attrs['width'] = self.size['x']
            attrs['height'] = self.size['y']
        if attrs:
            self.cw_set(**attrs)

    def poster(self):
        return self.reverse_poster_of if self.poster else None

