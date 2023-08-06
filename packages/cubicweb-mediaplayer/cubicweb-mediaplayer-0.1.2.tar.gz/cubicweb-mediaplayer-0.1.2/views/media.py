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

"""cubicweb-mediaplayer views/media for web ui"""

from logilab.mtconverter import BINARY_ENCODINGS, xml_escape
from cubicweb.web.views.idownloadable import DownloadView
from cubicweb.predicates import adaptable, is_instance
from cubicweb.view import EntityView

from cubicweb.web import component

_ = unicode

class MediaPlayerDownloadView(DownloadView):
    __abstract__ = True

    def adapter(self, entity):
        raise NotImplementedError

    def set_request_content_type(self):
        """overriden to set the correct filetype and filename"""
        entity = self.cw_rset.complete_entity(self.cw_row or 0, self.cw_col or 0)
        encoding = self.adapter(entity).download_encoding()
        if encoding in BINARY_ENCODINGS:
            contenttype = 'application/%s' % encoding
            encoding = None
        else:
            contenttype = self.adapter(entity).download_content_type()
        req = self._cw
        req.set_header('Accept-Ranges', 'bytes')
        req.set_header('Content-Range', 'bytes=0-20000')
        req.set_header('Access-Control-Allow-Header', 'range, accept-encoding')
        self._cw.set_content_type(contenttype or self.content_type,
                                  filename=self.adapter(entity).download_file_name(),
                                  encoding=encoding,
                                  disposition='attachment')
    def call(self):
        entity = self.cw_rset.complete_entity(self.cw_row or 0, self.cw_col or 0)
        self.w(self.adapter(entity).download_data())

class DownloadOggView(MediaPlayerDownloadView):
    __regid__ = 'download_ogg'
    __select__ = DownloadView.__select__ & adaptable('OggIDownloadable')

    def adapter(self, entity):
        return entity.cw_adapt_to('OggIDownloadable')

class DownloadMpegView(MediaPlayerDownloadView):
    __regid__ = 'download_mpeg'
    __select__ = DownloadView.__select__ & adaptable('MpegIDownloadable')

    def adapter(self, entity):
        return entity.cw_adapt_to('MpegIDownloadable')

class DownloadWenMView(MediaPlayerDownloadView):
    __regid__ = 'download_webm'
    __select__ = DownloadView.__select__ & adaptable('WebMIDownloadable')

    def adapter(self, entity):
        return entity.cw_adapt_to('WebMIDownloadable')


class StreamingAudioView(EntityView):
    __select__ = (EntityView.__select__ &
                  is_instance('SoundFile'))
    __regid__ = 'streaming-audio'
    with_info_html = ("<div id='track%(eid)s' class='track-info' rel='popover' "
                      "data-original-title='%(title)s' data-content='%(html)s'>"
                      "%(title)s <span class='jp-details'>(%(duration)s)</span></div>")
    without_info_html = ("<div id='track%(eid)s' class='track-info'>%(title)s</div>")

    def cell_call(self, row, col, display_info=False, **kwargs):
        entity = self.cw_rset.get_entity(row, col)
        data = {'title': xml_escape(entity.dc_title()),
                'eid': entity.eid,
                'duration': entity.formatted_duration}
        if display_info:
            self._cw.add_onload('''$('body').popover({delay: {show: 100, hide: 100}, placement:'top', selector: '[rel="popover"]',trigger: 'hover', html: true})''')
            data.update({'html': self.build_info(entity)})
            html = self.with_info_html
        else:
            html = self.without_info_html
        self.w(html % data)
        entity.view('jplayer-audio', w=self.w)

    def build_info(self, entity):
        raise NotImplementedError

class StreamingVideoView(EntityView):
    __select__ = (EntityView.__select__ &
                  is_instance('VideoFile'))
    __regid__ = 'streaming-video'
    with_info_html = ("<div id='track%(eid)s' class='track-info' rel='popover' "
                      "data-original-title='%(title)s' data-content='%(html)s'>"
                      "%(title)s <span class='jp-details'>(%(duration)s)</span></div>")
    without_info_html = ("<div id='track%(eid)s' class='track-info'>%(title)s</div>")

    def cell_call(self, row, col, **kwargs):
        self.wview('multi-jplayer-video', self.cw_rset, row=row, col=col)

class SoundFileStreamingBox(component.EntityCtxComponent):
    """add streaming box"""
    __regid__ = 'streaming_box'
    __select__ = (component.EntityCtxComponent.__select__ &
                  is_instance('SoundFile'))

    order = 9
    title = _('streaming')

    def render_body(self, w):
        self.entity.view('streaming-audio', w=w)
