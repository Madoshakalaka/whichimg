#!/usr/bin/env python3
import argparse
from typing import List, Dict, Tuple

import numpy as np
from cv2 import cv2


class Procedure:
    def __init__(self, r_c: Tuple[int, int], bgr_color: Tuple[int, int, int], limited_indexes: List[int]):
        """
        if the pixel at row, column <r_c> has color <bgrColor>, then we can shrink our candidates to <limited_indexes>

        :param r_c:
        :param bgr_color:
        :param limited_indexes:
        """
        self.r_c = r_c
        self.bgr_color = bgr_color
        self.limited_indexes = limited_indexes


class ImageTeller:
    def __init__(self, possible_images: List[np.ndarray]):
        """
        An ImageTeller analyzes a list of given images upon creation to know their differences.
        It takes time to analyze. Please only initialize once.
        :param possible_images: a list of numpy images
        """
        self._possible_images = possible_images

        self._shapeToImgIndexes: Dict[Tuple[int, int], List[int]] = dict()

        for index, img in enumerate(possible_images):
            if img.shape[2] != 3:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

            shape_tuple = tuple(img.shape[:2])

            if shape_tuple in self._shapeToImgIndexes:
                self._shapeToImgIndexes[shape_tuple].append(index)
            else:
                self._shapeToImgIndexes[shape_tuple] = [index]

        self._shapeToProcedures: Dict[Tuple[int, int], List[Procedure]] = {shape: [] for shape in
                                                                           self._shapeToImgIndexes.keys()}

        for shape, imgIndexes in self._shapeToImgIndexes.items():
            self._shapeToProcedures[shape] = self._produce_procedures_of_shape(shape)

    def _produce_procedures_of_shape(self, shape):
        procedures = []
        indexes = self._shapeToImgIndexes[shape]
        images = [self._possible_images[i] for i in indexes]

        progress = 0
        while progress < len(indexes) - 1:
            thisIndex = indexes[progress]
            nextIndex = indexes[progress + 1]
            thisPic = images[progress]
            nextPic = images[progress + 1]

            absolute_diff = cv2.absdiff(thisPic, nextPic)
            mask = np.any(absolute_diff != [0,0,0], axis=-1)
            nonzero_r_c = np.where(mask)
            assert np.any(nonzero_r_c), "Got identical images"



def cmd():
    parser = argparse.ArgumentParser(
        description="blazing fast template matching when possible images are all known"
    )

    # parser.add_argument(
    #     "blah",
    #     action="store",
    #     type=str,
    #     help="blah",
    # )

    argv = parser.parse_args()

    # add your command line program here

    print("reserved command line entry for python package whichimg")


def main():
    # add whatever here
    pass


if __name__ == "__main__":
    # just to provide a way to test the cmd entry point
    cmd()
