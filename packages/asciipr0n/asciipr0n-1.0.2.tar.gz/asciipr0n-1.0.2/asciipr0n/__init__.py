'''
Output random pinups from asciipr0n.com
'''

from random import randint
import os


def output():
    which = randint(1, 48)

    filename = "%s/data/pinup%.2d.txt" % \
        (os.path.dirname(os.path.realpath(__file__)), which)

    with open(filename, "r") as f:
        print f.read()
