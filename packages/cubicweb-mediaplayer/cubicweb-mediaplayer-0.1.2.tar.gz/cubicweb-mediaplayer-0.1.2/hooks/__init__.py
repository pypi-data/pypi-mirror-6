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

"""cubicweb-mediaplayer specific hooks and operations"""

from cubicweb.predicates import is_instance, has_related_entities
from cubicweb.server.hook import Hook, Operation, DataOperationMixIn, match_rtype

from cubes.mediaplayer.utils.media import SOUND_FORMATS, \
     flv_meta, id3infos

def hook_implements(*etypes):
    return Hook.__select__ & is_instance(*etypes)

class SetMediaFormatHook(Hook):
    __regid__ = 'mediaplayer.media-format'
    __select__ = hook_implements('SoundFile', 'VideoFile')
    events = ('before_add_entity', 'before_update_entity',)

    def __call__(self):
        entity = self.entity
        if 'data' in entity.cw_edited:
            self.entity.set_format_and_encoding()

class UpdateMediaTitleHook(Hook):
    __regid__ = 'mediaplayer.update-media-title'
    __select__ = hook_implements('SoundFile', 'VideoFile')
    events = ('after_update_entity',)

    def __call__(self):
        entity = self.entity
        if not 'title' in entity.cw_edited:
            SetMediaTitleOp.get_instance(self._cw).add_data(entity.eid)

class SetMediaTitleOp(DataOperationMixIn, Operation):
    """ set video or audio title"""
    def precommit_event(self):
        session = self.session
        for entity_eid in self.get_data():
            entity = session.entity_from_eid(entity_eid)
            try:
                infos = id3infos(entity)
                entity.cw_set(title=unicode(infos.title))
            except Exception, err:
                continue

class AddEncodeSoundHook(Hook):
    __regid__ = 'mediaplayer.encode-sound'
    __select__ = hook_implements('SoundFile')
    events = ('after_add_entity', 'after_update_entity')

    def __call__(self):
        entity = self.entity
        if 'data' in entity.cw_edited:
            try:
                entity.cw_set(length=flv_meta(entity)['length'])
            except Exception, ex:
                self.error("unable to extract sound length for %s:\n%s", entity, ex)
            entity.reencode()

class AddEncodeVideoHook(Hook):
    __regid__ = 'mediaplayer.encode-video'
    __select__ = hook_implements('VideoFile')
    events = ('after_add_entity', 'after_update_entity')

    def __call__(self):
        if 'data' in self.entity.cw_edited:
            if len(self.entity.cw_edited['data'].getvalue()):
                   ComputeVideoLenOp.get_instance(self._cw).add_data(self.entity.eid)
            ReencodeVideoOp.get_instance(self._cw).add_data(self.entity.eid)

class ComputeVideoLenOp(DataOperationMixIn, Operation):
    """ set video length"""
    def precommit_event(self):
        session = self.session
        for entity_eid in self.get_data():
            entity = session.entity_from_eid(entity_eid)
            meta = flv_meta(entity.data)
            new_meta = dict([(a, v) for a, v in meta.iteritems() if hasattr(entity, a)])
            if new_meta:
                entity.cw_set(**new_meta)

class ReencodeVideoOp(DataOperationMixIn, Operation):
    """set entity 'width', 'height' from a compressed file"""
    def precommit_event(self):
        session = self.session
        for entity_eid in self.get_data():
            entity = session.entity_from_eid(entity_eid)
            if not entity.data_mp4:
                entity.reencode()
            try:
                meta = flv_meta(entity.data_mp4)
                self.warning(u'Unable to get the %s video size' % entity.dc_title())
            except Exception:
                continue
            for attr in ('width', 'height'):
                data = meta.get(attr, None)
                if data:
                    entity.cw_set(**{attr:data})
