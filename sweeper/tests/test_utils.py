__author__ = 'fer'

import unittest
import sweeper.utils


class UtilsTest(unittest.TestCase):
    def test(self):
        def count():
            for i in range(1000000):
                pass
            return True
        sweeper.utils.wait_for(count)

        def count(time):
            print 'time={0}'.format(time)
            for i in range(time):
                pass
            return True
        sweeper.utils.wait_for(count, time=9000000)


if __name__ == '__main__':
    unittest.main()
