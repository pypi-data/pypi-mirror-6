from  ise.pfgfieldpermission.testing import ISE_PFGFIELDPERMISSION_FUNCTIONAL_TESTING
from plone.testing import layered
import robotsuite
import unittest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite("robot_test.txt"),
                layer=ISE_PFGFIELDPERMISSION_FUNCTIONAL_TESTING)
    ])
    return suite