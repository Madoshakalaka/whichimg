import glob
import os
import subprocess
import sys
import unittest
from os import path
from cv2 import cv2

from whichimg import main
from whichimg.main import ImageTeller


def get_fixture_img(name):
    return cv2.imread(path.join('fixtures', name + '.png'))


class MyTestCase(unittest.TestCase):
    oldDir = ""

    def setUp(self) -> None:
        MyTestCase.oldDir = os.getcwd()
        os.chdir(os.path.dirname(__file__))

    def test_shapeToIndex(self):
        # 10: phages 15: emerald 20: bloody_sea
        a = get_fixture_img('phage')
        b = get_fixture_img('phage_blue_face')
        c = get_fixture_img('emerald')
        d = get_fixture_img('bloody_sea')
        e = get_fixture_img('phage_bw')

        t = ImageTeller([a, b, c, d, e])
        answer = {(10, 10): [0, 1, 4], (15, 15): [2], (20, 20): [3]}
        index_dict = t._shapeToImgIndexes
        for shape, indexes in index_dict.items():
            self.assertIn(shape, answer)
            self.assertEqual(indexes, answer[shape])



    def test_stuff(self):
        a = get_fixture_img('phage')

        b = get_fixture_img('phage_blue_face')

        absdiff = cv2.absdiff(b, a)
        print(absdiff)
        cv2.imshow('lmao', absdiff)
        cv2.waitKey()
        cv2.destroyAllWindows()

    def test_cmd(self):
        cmd = ' '.join((sys.executable, path.join('..', 'whichimg', 'main.py')))
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, _ = p.communicate()

        res = stdout.decode(encoding='utf-8').strip()
        print("command line result:", res)

    def tearDown(self) -> None:
        os.chdir(MyTestCase.oldDir)


def generate_grey_scale_fixtures():
    files = [file for file in glob.glob(path.join('fixtures', '*.png')) if not (file.endswith('bw.png'))]
    images = [cv2.imread(file, cv2.IMREAD_GRAYSCALE) for file in files]
    print(len(images), 'non bw images is going to be converted to greyscale')
    for i in range(len(images)):
        cv2.imwrite(files[i].split('.')[0] + '_bw.png', images[i])


if __name__ == '__main__':
    unittest.main()
