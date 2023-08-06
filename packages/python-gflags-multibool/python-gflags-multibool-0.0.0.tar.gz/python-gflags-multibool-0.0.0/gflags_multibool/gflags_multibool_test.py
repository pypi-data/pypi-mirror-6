import gflags
from gflags_multibool import DEFINE_multiboolean
from unittest import TestCase
import sys

FLAGS = gflags.FLAGS

DEFINE_multiboolean('verbose', 0, 'Verbosity', short_name='v')


def fakemain(argv):
    argv = ['fakeprog '] + argv.split()
    argv = FLAGS(argv)[1:]


class GFlagsMultiFlags_Test(TestCase):
    def setUp(self):
        FLAGS.verbose = 0

    def assertVerbosity(self, args, verbosity):
        fakemain(args)
        self.assertEquals(FLAGS.verbose, verbosity)

    def test_none_test(self):
        self.assertVerbosity('', 0)

    def test_negative(self):
        self.assertVerbosity('--noverbose', 0)

    def test_false(self):
        self.assertVerbosity('--verbose=False', 0)

    def test_positive(self):
        self.assertVerbosity('--verbose', 1)

    def test_sequence(self):
        self.assertVerbosity('--verbose --verbose --verbose', 3)

    def test_complex_sequence(self):
        self.assertVerbosity('-v --verbose -v --noverbose --verbose', 3)
