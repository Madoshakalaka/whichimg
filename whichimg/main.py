#!/usr/bin/env python3
import argparse
from typing import List, Dict, Tuple, Set

import numpy as np
from cv2 import cv2

# class Procedure:
#     def __init__(self, r_c: Tuple[int, int], this_color: np.array, that_color: np.array, is_this_indexes: Set[int],
#                  is_that_indexes: Set[int], is_neither_indexes: Set[int]):
#         """
#         if the pixel at row, column <r_c> has color <bgrColor>, then we can shrink our candidates to <limited_indexes>.
#
#         :param this_color:
#         :param that_color:
#         :param is_that_indexes:
#         :param is_neither_indexes:
#         :param r_c:
#         :param is_this_indexes:
#         """
#         self._r_c = r_c
#         self._this_color = this_color
#         self._that_color = that_color
#         self._is_this_indexes = is_this_indexes
#         self._is_that_indexes = is_that_indexes
#         self._is_neither_indexes = is_neither_indexes
#
#     def execute_on(self, img):
#         color = img[self._r_c]
#         if np.array_equal(color, self._this_color):
#             return True, self._is_this_indexes.copy()
#         elif np.array_equal(color, self._that_color):
#             return False, self._is_that_indexes.copy()
#         else:
#             return False, self._is_neither_indexes.copy()
#
#     def __repr__(self):
#         return '<Procedure: coords: %s, this color: %s, that color: %s, if this: %s, if that:%s, if neither: %s>' % (
#             self._r_c, self._this_color, self._that_color, self._is_this_indexes, self._is_that_indexes,
#             self._is_neither_indexes)

Procedure = Tuple[Tuple[int, int], np.ndarray, np.ndarray, Set[int],
                  Set[int], Set[int]]


class ImageTeller:
    _shapeToImgIndexes: Dict[Tuple[int, int], List[int]]

    def __init__(self, possible_images: List[np.ndarray], surprises = True):
        """
        An ImageTeller analyzes a list of given images upon creation to know their differences.
        It takes time to analyze. Please only initialize once.

        :param possible_images: a list of numpy images
        :param surprises: whether the image teller will encounter unknown images. Setting it to False will give an roughly 10% performance increase.
        """
        assert len(possible_images) >= 2, "Please provide a list of at least two images as an argument"

        self._surprises = surprises

        self._possible_images = possible_images

        self._shapeToImgIndexes = dict()

        for index, img in enumerate(possible_images):
            if img.shape[2] != 3:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

            shape_tuple = tuple(img.shape[:2])

            if shape_tuple in self._shapeToImgIndexes:
                self._shapeToImgIndexes[shape_tuple].append(index)
            else:
                self._shapeToImgIndexes[shape_tuple] = [index]

        self._shapeToProcedures: Dict[Tuple[int, int], Dict[int, List[Procedure]]] = {shape: dict() for shape in
                                                                                      self._shapeToImgIndexes.keys()}

        for shape, imgIndexes in self._shapeToImgIndexes.items():
            self._shapeToProcedures[shape] = self._produce_procedures_of_shape(
                shape)  # can be empty dict if there's only one image of a single shape

    def tell(self, img: np.array) -> int:
        """
        Analyzes <img> and returns the the index of argument <img> in possible images, -1 if not found
        Note: It will only stably return -1 when keyword argument <surprises> of this teller is set to True. (which is the default)
        If you set it to False. It will still get known images right. But it's possible it will mistaken unexpected images for known ones.

        :param img: the image you want to tell
        """
        # assert isinstance(img, np.ndarray), "only accepts images in form of numpy.ndarray"

        if img.ndim == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        shape = tuple(img.shape[:2])

        if shape not in self._shapeToProcedures:
            return -1

        procedures_for_all_images = self._shapeToProcedures[shape]

        possibilities = self._shapeToImgIndexes[shape]

        if len(procedures_for_all_images) == 0:
            # assert len(possibilities) == 1, "Image Teller internal error"

            the_index = possibilities[0]

            if self._surprises:
                if np.array_equal(img, self._possible_images[the_index]):
                    return the_index
                else:
                    return -1
            else:
                return the_index


        total_possibilities = set(possibilities)

        while total_possibilities:
            index = total_possibilities.pop()
            # print(procedures_for_all_images)
            procedures = procedures_for_all_images[index]

            for procedure in procedures:
                color = img[procedure[0]]
                if np.array_equal(color, procedure[1]):
                    is_possible, possibilities = True, procedure[3]
                elif np.array_equal(color, procedure[2]):
                    is_possible, possibilities = False, procedure[4]
                else:
                    is_possible, possibilities = False, procedure[5]

                total_possibilities &= possibilities

                length = len(total_possibilities)
                if is_possible:
                    if length == 0:
                        if self._surprises:
                            if np.array_equal(img, self._possible_images[index]):
                                return index
                            else:
                                return -1
                        else:
                            return index

                else:
                    if length == 1:
                        surprise = total_possibilities.pop()

                        if self._surprises:
                            if np.array_equal(img, self._possible_images[surprise]):
                                return surprise
                            else:
                                return -1
                        else:
                            return surprise

                    elif length == 0:
                        return -1
                    else:
                        break

    def _produce_procedures_of_shape(self, shape):
        procedures = dict()

        indexes = self._shapeToImgIndexes[shape]

        progress = 0

        if len(indexes) == 1:  # There's only one image in a particular shape
            return []

        while progress < len(indexes):

            procedures_for_progress = []

            this_index = indexes[progress]

            this_possibilities = indexes.copy()

            while True:  # generate procedures that's enough to determine a certain pic

                diff_r, diff_c, this_color, that_color = self._get_diff_rc_color(this_index, this_possibilities)

                that_possibilities = []
                neither_possibilities = []

                for index in indexes:
                    color = self._possible_images[index][diff_r][diff_c]
                    if not np.array_equal(color, this_color):
                        if index in this_possibilities:
                            this_possibilities.remove(index)
                        if np.array_equal(color, that_color):
                            that_possibilities.append(index)
                        else:
                            neither_possibilities.append(index)

                procedures_for_progress.append(
                    ((diff_r, diff_c), this_color, that_color, set(this_possibilities.copy()),
                     set(that_possibilities.copy()),
                     set(neither_possibilities.copy())))

                if len(this_possibilities) == 1:
                    break

            procedures[this_index] = procedures_for_progress

            progress += 1

        return procedures

    def _get_diff_rc_color(self, examined_img_index: int, possibilities: List[int]) -> Tuple[
        int, int, np.array, np.array]:
        """
        pick a random image from <possibilities> that is different than <examined_img>,
        compare those two images and return a random coordinate where they have different colors. The color of <examed_img> at that coordinate.

        :param examined_img_index: the index of the examined image in self._possible_images
        :param possibilities: a list of indexes of the compared images
        :return: row, col, color, color
        """
        that_index = -1
        for possibility in possibilities:
            if possibility != examined_img_index:
                that_index = possibility

        assert that_index != -1
        this_img = self._possible_images[examined_img_index]
        that_img = self._possible_images[that_index]

        absolute_diff = cv2.absdiff(this_img, that_img)
        mask = np.any(absolute_diff != [0, 0, 0], axis=-1)
        nonzero_r_c = np.where(mask)
        # if not np.any(nonzero_r_c):
        #     cv2.imshow('this', this_img)
        #     cv2.imshow('that', that_img)
        #     cv2.waitKey()
        #     cv2.destroyAllWindows()

        assert np.any(nonzero_r_c), "Got identical images"

        diff_r, diff_c = nonzero_r_c[0][0], nonzero_r_c[1][0]
        this_color = this_img[diff_r][diff_c]
        that_color = that_img[diff_r][diff_c]
        return diff_r, diff_c, this_color, that_color


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
