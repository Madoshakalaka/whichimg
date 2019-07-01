import os
import subprocess
import sys
import unittest
from os import path

from whichimg import main


class MyTestCase(unittest.TestCase):
    oldDir = ""

    def setUp(self) -> None:
        MyTestCase.oldDir = os.getcwd()
        os.chdir(os.path.dirname(__file__))

    def test_stuff(self):
        pass


    def test_cmd(self):
        cmd = ' '.join((sys.executable, path.join('..','whichimg','main.py')))
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, _ = p.communicate()

        res = stdout.decode(encoding='utf-8').strip()
        print("command line result:", res)


    def tearDown(self) -> None:

        os.chdir(MyTestCase.oldDir)

if __name__ == '__main__':
    unittest.main()
