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

from os import stat
from time import time
import os.path as osp

HERE = osp.abspath(osp.dirname(__file__))
TEMPLATE_DIR = osp.join(HERE, 'htmltemplates')


class TemplateBasedMixIn(object):
    """template's filename (supposed to be found in the templates
    directory)"""
    template = None

    @classmethod
    def load_template(cls):
        assert cls.template is not None, "mixed-in class must define their template"
        fname = osp.join(TEMPLATE_DIR, cls.template)
        # avoid stat call outside DEBUG mode
        last_load_time, mtime = getattr(cls, '_load_time', 0), stat(fname)[-1]
        if last_load_time < mtime:
            cls.info('loading %s (%s < %s)', fname, last_load_time, mtime)
            cls._template = file(fname).read().decode('utf-8')
            cls._load_time = time()
        return cls._template

    @classmethod
    def set_template(cls, template):
        cls.template = template

    def call(self, *args, **kwargs):
        self._render(*args, **kwargs)

    def cell_call(self, *args, **kwargs):
        self._render(*args, **kwargs)

    def _render(self, *args, **kwargs):
        self.w(self.load_template() % self.build_context(*args, col=0, row=0))
