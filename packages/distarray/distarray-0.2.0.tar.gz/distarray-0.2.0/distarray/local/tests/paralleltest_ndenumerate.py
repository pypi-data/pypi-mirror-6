# encoding: utf-8
# ---------------------------------------------------------------------------
#  Copyright (C) 2008-2014, IPython Development Team and Enthought, Inc.
#  Distributed under the terms of the BSD License.  See COPYING.rst.
# ---------------------------------------------------------------------------

from __future__ import print_function

import unittest

from distarray.local.localarray import LocalArray, ndenumerate
from distarray.testing import MpiTestCase


class TestNDEnumerate(MpiTestCase):
    """Make sure we generate indices compatible with __getitem__."""

    def test_ndenumerate(self):
        a = LocalArray((16, 16, 2), dist=('c', 'b', 'n'), comm=self.comm)
        for global_inds, value in ndenumerate(a):
            a.global_index[global_inds] = 0.0


if __name__ == '__main__':
    try:
        unittest.main()
    except SystemExit:
        pass
