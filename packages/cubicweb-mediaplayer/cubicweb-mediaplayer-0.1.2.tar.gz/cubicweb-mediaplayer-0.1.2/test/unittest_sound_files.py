# -*- coding: utf-8 -*-
import unittest2

from logilab.common.testlib import tag, Tags
from cubicweb import Binary

from cubes.mediaplayer.utils.media import id3infos, flv_meta, _ensure_file

from testlib import MediaPlayerBaseTestCase

class MediaPlayerSoundFileTC(MediaPlayerBaseTestCase):

    @tag('length')
    def test_sound_length(self):
        sound = self.add_sound(self.datapath('beep.mp3'))
        self.commit()
        sound.cw_clear_all_caches()
        self.assertEqual(sound.length, 303)
        self.assertEqual(sound.formatted_duration, '0:05:03')

    @tag('id3', 'update', 'title')
    def test_id3_update_title(self):
        sound = self.add_sound(self.datapath('beep.mp3'))
        self.assertEqual(sound.title, 'beep.mp3')
        sound.cw_set(data=Binary(file(self.datapath('eminem.mp3')).read()))
        self.commit()
        sound.cw_clear_all_caches()
        self.assertEqual(sound.title, 'Oh My Darling  Prod By Dr Dre')

    @tag('id3',)
    def test_id3_format(self):
        sound = self.add_sound(self.datapath('beep.mp3'))
        self.assertDictEqual(dict(id3infos(sound)),
                          dict(id3infos(Binary(file(self.datapath('eminem.mp3')).read()))))

    @tag('encode')
    def test_encode_mp3_sound(self):
        sound = self.add_sound(self.datapath('beep.mp3'))
        self.commit()
        sound.cw_clear_all_caches()
        self.assertIsNotNone(sound.data_mp3)
        self.assertEqual(sound.data_mp3_format, u'audio/mp3')
        self.assertIsNotNone(sound.data_oga)
        self.assertEqual(sound.data_oga_format, u'audio/oga')

    @tag('encode')
    def test_flv_meta(self):
        sound = self.add_sound(self.datapath('beep.mp3'))
        self.commit()
        meta = flv_meta(sound)
        self.assertEqual(meta['length'], 303)
        self.assertEqual(meta['audiodatarate'], 64)

    def test_idownloadable(self):
        sound = self.add_sound(self.datapath('beep.mp3'))
        self.commit()
        idownloadable = sound.cw_adapt_to('IDownloadable')
        self.assertEqual(idownloadable.download_url(),
                          u'http://testing.fr/cubicweb/%s/%s/raw' % (
            sound.__regid__.lower(), sound.eid))
        self.assertEqual(idownloadable.download_content_type(), 'audio/mpeg')
        mpeg_adaptor = sound.cw_adapt_to('MpegIDownloadable')
        self.assertEqual(mpeg_adaptor.download_url(),
                          u'http://testing.fr/cubicweb/%s/%s/mp3' % (
            sound.__regid__.lower(), sound.eid))
        ogg_adaptor = sound.cw_adapt_to('OggIDownloadable')
        self.assertEqual(ogg_adaptor.download_url(),
                         u'http://testing.fr/cubicweb/%s/%s/oga' % (
            sound.__regid__.lower(), sound.eid))


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.ERROR)
    unittest2.main()
