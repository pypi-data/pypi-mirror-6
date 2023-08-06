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

"""cubicweb-mediafile views/players for web ui"""

from logilab.mtconverter import xml_escape

from cubicweb.predicates import is_instance
from cubicweb.view import EntityView
from cubicweb.web import httpcache
from cubicweb.utils import make_uid, json_dumps

from cubes.mediaplayer.views.loader import TemplateBasedMixIn
from cubes.mediaplayer.utils.media import VIDEO_SIZE

_ = unicode

class JPlayerStreamingView(TemplateBasedMixIn, EntityView):
    __abstract__ = True
    templatable = False
    http_cache_manager = httpcache.NoHTTPCacheManager
    javascripts = [
        'cubes.mediaplayer.js',
        'jplayer/js/jquery.jplayer.min.js',
        ]

    stylesheets = [
        'jplayer/skin/simple.css',
        ]

class MultiJPlayerStreamingView(JPlayerStreamingView):
    __abstract__ = True

    javascripts = JPlayerStreamingView.javascripts + ['jplayer/js/jplayer.playlist.min.js']

    stylesheets = [
        'jplayer/skin/blue.monday/jplayer.blue.monday.css',
        ]

    # html
    track_html = ("<div id='track%(eid)s' class='%(css)s' rel='popover' "
                  "data-original-title='%(track)s' data-content='%(html)s'>"
                  "%(title)s <span class='jp-details'>(%(duration)s)</span></div>")

    supplied_formats = {
        # map format (e.g. "mp3") -> adapter'ids (e.g. "MpegIDownloadable")
        }

    def init_popover(self):
        self._cw.add_onload('''$('body').popover({delay: {show: 100, hide: 100}, placement:'top', selector: '[rel="popover"]',trigger: 'hover', html: true})''')

    def load_resources(self):
        self._cw.add_js(self.javascripts)
        self._cw.add_css(self.stylesheets)

    def jplayer_custom_settings(self):
        return {
            'supplied': ', '.join(self.supplied_formats)
            }

    @property
    def _uid(self):
        return make_uid()

    def track_definition(self, tracknum, entity):
        _ = self._cw._
        duration = entity.formatted_duration or u"<div class='error'>%s</div>" % _('N/A')
        trackdef = {
            'title': self.track_html % {
                'eid': entity.eid,
                'html': xml_escape(self.build_info(entity)),
                'css': '', 'track': xml_escape(entity.dc_title()),
                'title': xml_escape('%s.%s' % (tracknum, entity.dc_title())),
                'duration': duration
                },
            }
        for media_format, adapter_id in self.supplied_formats.items():
            adapted = entity.cw_adapt_to(adapter_id)
            trackdef[media_format] = adapted.download_url() if adapted else ''
        return trackdef

    def build_info(self, entity):
        return entity.dc_title()

    def build_context(self, row=0, col=0):
        _ = self._cw._
        self.load_resources()
        self.init_popover()
        uid = self._uid
        divid = 'jplayer_%s' % uid
        cssa = 'jplayer_container_%s' % uid
        playlist = []
        for rowidx, soundfile in enumerate(self.cw_rset.entities()):
            playlist.append(self.track_definition(rowidx+1, soundfile))
        self._cw.add_onload('cw.mediaplayer.initPlaylist(%s, %s, %s, %s);' % (
                json_dumps(divid),
                json_dumps(cssa),
                json_dumps(playlist),
                json_dumps(self.jplayer_custom_settings())
                ))
        return {'idplayer': divid, 'idcontainer': cssa}


class AbstractMultiJPlayerStreamingVideoView(MultiJPlayerStreamingView):
    template = 'multi-jplayer-video.html'
    video_options = '''size: {
			height: "%(height)spx",
			width: "%(width)spx",
			cssClass: "jp-video-%(height)sp"
		},'''
    video_size = VIDEO_SIZE
    styles_options = 'style="width:%(width)spx"'
    play_styles_options = 'style="height: %(height)spx; margin-top: -%(height)spx"'

    supplied_formats = {
        'm4v': 'MpegIDownloadable',
        'ogv': 'OggIDownloadable',
        'webm': 'WebmIDownloadable',
        }

    def track_definition(self, tracknum, entity):
        options = super(AbstractMultiJPlayerStreamingVideoView, self).track_definition(tracknum, entity)
        poster = entity.preferred_image()
        options['poster'] = poster.cw_adapt_to('IDownloadable').download_url() if poster else u''
        return options

    def jplayer_custom_settings(self):
        width, height = self.guess_player_dimensions()
        return {
            'supplied': 'm4v, ogv, webm',
            'size': {
                'width': '%spx' % width,
                'height': '%spx' % height,
                'cssClass': 'jp-video-%sp' % height,
                }
            }

    def build_context(self, col=0, row=0):
        context = super(AbstractMultiJPlayerStreamingVideoView, self).build_context()
        context.update(self.compute_styles())
        return context

    def guess_player_dimensions(self):
        mediafiles = list(self.cw_rset.entities())
        width, height = 0, 0
        if mediafiles:
            width = [mediafile.width for mediafile in mediafiles]
            width = max(width) if width else 0
            height = [mediafile.height for mediafile in mediafiles]
            height = max(height) if height else 0
        if not width or height:
            width, height = self.video_size
        return [width, height]

    def compute_styles(self):
        width, height = self.guess_player_dimensions()
        if width and height:
            styles = {
                'video_otions': self.video_options % {'height': height, 'width': width},
                'styles': self.styles_options % {'height': height, 'width': width},
                'play_styles': self.play_styles_options % {'height': height, 'width': width},
                }
        else:
            styles = {
                'styles': '',
                'video_options': '',
                'play_styles': 'style="display:none"',
                }
        return styles

class MultiJPlayerStreamingVideoView(AbstractMultiJPlayerStreamingVideoView):
    __regid__ = 'multi-jplayer-video'
    __select__ = AbstractMultiJPlayerStreamingVideoView.__select__ & is_instance('VideoFile')

class AbstractMultiJPlayerStreamingAudioView(MultiJPlayerStreamingView):
    template = 'multi-jplayer-audio.html'
    supplied_formats = {
        'm3v': 'MpegIDownloadable',
        'oga': 'OggIDownloadable',
        }


class MultiJPlayerStreamingAudioView(AbstractMultiJPlayerStreamingAudioView):
    __regid__ = 'multi-jplayer-audio'
    __select__ = AbstractMultiJPlayerStreamingAudioView.__select__ & is_instance('SoundFile')


class JPlayerStreamingAudioView(JPlayerStreamingView):
    __select__ = JPlayerStreamingView.__select__ & is_instance('SoundFile')
    __regid__ = 'jplayer-audio'
    template = 'jplayer-audio.html'

    def build_context(self, row=0, col=0):
        entity = self.cw_rset.get_entity(row, col)
        self._cw.add_js(('jplayer/js/jquery.jplayer.min.js',))
        self._cw.add_js('cubes.mediaplayer.js')
        self._cw.add_css(('jplayer/skin/simple.css',))
        divid = 'jplayer_%s' % entity.eid
        cssa = 'jplayer_container_%s' % entity.eid
        self._cw.add_onload('cw.mediaplayer.initAudioPlayer(%s, %s, %s, %s);'
                            % (json_dumps(divid),
                               json_dumps(cssa),
                               json_dumps(entity.cw_adapt_to('MpegIDownloadable').download_url()),
                               json_dumps(entity.cw_adapt_to('OggIDownloadable').download_url())))
        return {'idplayer': divid,
                'idcontainer': cssa,
                'title': xml_escape(entity.dc_title()),
                }
