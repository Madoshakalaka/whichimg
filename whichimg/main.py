#!/usr/bin/env python3
import argparse

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