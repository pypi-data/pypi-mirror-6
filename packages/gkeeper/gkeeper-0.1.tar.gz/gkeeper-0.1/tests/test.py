import unittest
import tempfile
import os

from gkeeper.version_manager import VersionManager

class VersionManagerTest(unittest.TestCase):
    def setUp(self):
        self.path = tempfile.mkdtemp()
        self.vm = VersionManager(self.path)
        self.temp_file = open(self.path + '/' + 'data.txt', 'w')
        self.temp_file.write('One' + os.linesep)
        self.temp_file.close()

    def test_add_file(self):
        self.vm.add_file(self.temp_file.name)

if __name__ == '__main__':
    unittest.main()
