import glob
import os
import random
import subprocess
import sys
import time
import unittest
from os import path
from typing import List, Tuple, Dict

import numpy as np
from cv2 import cv2

from whichimg import main
from whichimg.main import ImageTeller

FILE_DIR = os.path.dirname(__file__)

NAMES = np.array([path.splitext(path.basename(file))[0] for file in glob.glob(path.join(FILE_DIR, 'fixtures', '*'))])
ALL_IMAGES = [cv2.imread(file) for file in glob.glob(path.join(FILE_DIR, 'fixtures', '*'))]



def get_fixture_img(name):
    return cv2.imread(path.join(os.path.dirname(__file__), 'fixtures', name + '.png'))



def get_random_images(number) -> List[np.array]:
    return random.sample(ALL_IMAGES, number)

def get_teller_surprise_images_pair(total_image_count) -> Tuple[Dict[int, np.ndarray], Dict[int, np.ndarray]]:
    # print(total_image_count)
    assert total_image_count >= 2
    max_surprise = total_image_count - 2

    training_indeces = random.sample(range(2, len(ALL_IMAGES)), total_image_count)
    training = {ind: ALL_IMAGES[ind] for ind in training_indeces}

    surprise_indeces = random.sample(training_indeces, random.randint(0, len(training_indeces)-2))

    surprises = dict()
    for i in surprise_indeces:
        surprises[i] = training.pop(i)

    return training, surprises

def get_training_images(image_count) -> Dict[int, np.ndarray]:
    assert image_count >= 2
    training_indeces = random.sample(range(2, len(ALL_IMAGES)), image_count)
    return {ind: ALL_IMAGES[ind] for ind in training_indeces}

phage = get_fixture_img('phage')
phage_blue_face = get_fixture_img('phage_blue_face')
phage_blue_face_bw = get_fixture_img('phage_blue_face_bw')
phage_demon_horns = get_fixture_img('phage_demon_horns')


rainbow_1_bw = get_fixture_img('rainbow_1_bw')

# [phage_blue_face, phage_demon_horns, rainbow_1_bw]

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

    def test_instance_creation(self):
        repeat = 5
        for i in range(2, len(ALL_IMAGES)):
            for j in range(repeat):
                images = get_random_images(i)
                t = ImageTeller(images)
                del t

    def test_img_telling_wo_surises(self):
        repeat = 30

        for i in range(2,len(ALL_IMAGES)-1):
            for j in range(repeat):

                training= get_training_images(i)
                # print(NAMES[list(training.keys())])

                training_images = list(training.values())
                t = ImageTeller(training_images, surprises=False)

                for dd, img in enumerate(training_images):

                    self.assertEqual(t.tell(img), dd)

    def test_img_telling_w_surprises(self):
        repeat = 30

        for i in range(2,len(ALL_IMAGES)-1):
            for j in range(repeat):

                training, surprises = get_teller_surprise_images_pair(i)
                # print(NAMES[list(training.keys())])

                training_images = list(training.values())
                t = ImageTeller(training_images, surprises=True)

                for s in surprises.values():
                    self.assertEqual(t.tell(s), -1)

                for dd, img in enumerate(training_images):
                    # telling = t.tell(img)
                    self.assertEqual(t.tell(img), dd)



    def test_cmd(self):
        cmd = ' '.join((sys.executable, path.join('..', 'whichimg', 'main.py')))
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, _ = p.communicate()

        res = stdout.decode(encoding='utf-8').strip()
        print("command line result:", res)

    def tearDown(self) -> None:
        os.chdir(MyTestCase.oldDir)


def generate_grey_scale_fixtures():
    files = [file for file in glob.glob(path.join(FILE_DIR, 'fixtures', '*.png')) if not (file.endswith('bw.png'))]
    images = [cv2.imread(file, cv2.IMREAD_GRAYSCALE) for file in files]
    print(len(images), 'non bw images is going to be converted to greyscale')
    for i in range(len(images)):
        cv2.imwrite(path.join(FILE_DIR, files[i].split('.')[0] + '_bw.png'), images[i])

def naive_tell(images, sample_img):
    for i, img in enumerate(images):
        if np.array_equal(img, sample_img):
            return i
    return -1



def compare_shit_w_surprise():
    repeat = 20
    length = len(ALL_IMAGES)

    pairs = []

    for i in range(2, length - 1):
        for j in range(repeat):

            training, surprises = get_teller_surprise_images_pair(i)

            pairs.append((list(training.values()), surprises.values()))


    tellers = []
    for training_images, _ in pairs:
        tellers.append(ImageTeller(training_images,surprises=True))

    time1 = time.time()
    for training_images, surprise_images in pairs:

            for s in surprise_images:
                naive_tell(training_images, s)
            for img in training_images:
                naive_tell(training_images, img)

    print(time.time()-time1)

    time2 = time.time()
    lll = 0
    for training_images, surprise_images in pairs:
        t = tellers[lll]
        for s in surprise_images:
            t.tell(s)

        for img in training_images:
            t.tell(img)
        lll += 1
    print(time.time() - time2)


def compare_shit_wo_surprise():
    repeat = 18
    length = len(ALL_IMAGES)

    training_image_sets = []

    for i in range(2, length - 1):
        for j in range(repeat):

            training = get_training_images(i)

            training_image_sets.append(list(training.values()))


    tellers = []
    for training_images in training_image_sets:
        tellers.append(ImageTeller(training_images,surprises=False))

    time1 = time.time()
    # print(len(training_images))
    for training_images in training_image_sets:

            for img in training_images:
                naive_tell(training_images, img)

    print(time.time()-time1)

    time2 = time.time()
    lll = 0
    for training_images in training_image_sets:
        t = tellers[lll]

        for img in training_images:
            t.tell(img)
        lll += 1
    print(time.time() - time2)



if __name__ == '__main__':
    unittest.main()
    # pass
