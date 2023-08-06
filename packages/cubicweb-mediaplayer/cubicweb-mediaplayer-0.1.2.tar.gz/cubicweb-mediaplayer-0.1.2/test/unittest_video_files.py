# -*- coding: utf-8 -*-
import unittest2

from logilab.common.testlib import tag, Tags
from cubicweb import Binary

from cubes.mediaplayer.utils.media import id3infos, flv_meta, _ensure_file

from testlib import MediaPlayerBaseTestCase

class VideoFileTC(MediaPlayerBaseTestCase):

    @tag('meta')
    def test_file_meta(self):
        video = self.add_video_file(self.datapath('video.flv'))
        self.commit()
        video.cw_clear_all_caches()
        self.assertEqual(video.length, 5)
        orig_data = flv_meta(video.data)
        self.assertEqual(orig_data['width'], 352)
        self.assertEqual(orig_data['height'], 288)
        self.assertEqual(orig_data['audiodatarate'], 352)
        self.assertEqual(orig_data['videodatarate'], 200)
        self.assertEqual(orig_data['framerate'],25)
        self.assertEqual(video.width, 512)
        self.assertEqual(video.height, 418)

    @tag('encode')
    def test_encode_flv_video(self):
        video = self.add_video_file(self.datapath('video.flv'))
        self.commit()
        video.cw_clear_all_caches()
        self.assertIsNotNone(video.data_mp4)
        self.assertEqual(video.data_mp4_format, u'video/mp4')
        self.assertIsNotNone(video.data_ogv)
        self.assertEqual(video.data_ogv_format, u'video/ogg')


    def test_idownloadable(self):
        video = self.add_video_file(self.datapath('video.flv'))
        self.commit()
        idownloadable = video.cw_adapt_to('IDownloadable')
        self.assertEqual(idownloadable.download_url(),
                          u'http://testing.fr/cubicweb/%s/%s/raw' % (
            video.__regid__.lower(), video.eid))
        self.assertEqual(idownloadable.download_content_type(), 'video/x-flv')
        mpeg_adaptor = video.cw_adapt_to('MpegIDownloadable')
        self.assertEqual(mpeg_adaptor.download_url(),
                          u'http://testing.fr/cubicweb/%s/%s/mp4' % (
            video.__regid__.lower(), video.eid))
        ogg_adaptor = video.cw_adapt_to('OggIDownloadable')
        self.assertEqual(ogg_adaptor.download_url(),
                         u'http://testing.fr/cubicweb/%s/%s/ogv' % (
            video.__regid__.lower(), video.eid))

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.ERROR)
    unittest2.main()
