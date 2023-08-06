# -*- coding: utf-8 -*-
import os.path as osp
import unittest2
import tempfile

from cubicweb import Binary

from logilab.common.testlib import tag, Tags
from cubicweb.devtools.testlib import CubicWebTC

class MediaPlayerBaseTestCase(CubicWebTC):
    test_db_id = 'mediplayer-base'
    tags = CubicWebTC.tags | Tags('MP')

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        if self.config._cubes is None:
            self.config.init_cubes(self.config.expand_cubes(('mediaplayer', )))
        self.set_option('media-dir', self.tempdir)
        self.config._cubes = None # hack to avoid troubles in default setUp
        super(MediaPlayerBaseTestCase, self).setUp()

    def add_sound(self, filepath=None, data_format=u'audio/mpeg', data_name=u''):
        if filepath is None:
            filepath = self.datapath('eminem.mp3')
        filepath = unicode(filepath)
        return self.request().create_entity('SoundFile',
                                            data=Binary(file(filepath).read()),
                                            title=unicode(osp.basename(filepath)),
                                            data_name=unicode(osp.basename(filepath)),
                                            )
    def add_video_file(self, filepath=None, data_format=u'audio/mpeg', data_name=u''):
        if filepath is None:
            filepath = self.datapath('eminem.mp3')
        filepath = unicode(filepath)
        return self.request().create_entity('VideoFile',
                                            data=Binary(file(filepath).read()),
                                            title=unicode(osp.basename(filepath)),
                                            data_name=unicode(osp.basename(filepath)),
                                            )


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.ERROR)
    unittest2.main()
