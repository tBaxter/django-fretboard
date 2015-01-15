import unittest

def suite():
    return unittest.TestLoader().discover("fretboard.tests", pattern="*.py")
