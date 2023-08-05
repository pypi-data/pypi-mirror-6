import unittest
from pyprotobuf.generators.go import Go
from pyprotobuf.main import parse_and_generate


class ProtorpcTest(unittest.TestCase):
    def check_expected_output(self, name):
        inputproto ='pyprotobuf/testdata/%s' % name
        string = parse_and_generate(open(inputproto).read(), inputproto , Go)
        self.assertMultiLineEqual(open('pyprotobuf/testdata/%s.go' % name).read(), string)

    def test_enum(self):
        """ Test simple evaluation
        """
        self.maxDiff = 16732
        self.check_expected_output('go.proto')


if __name__ == '__main__':
    unittest.main()
