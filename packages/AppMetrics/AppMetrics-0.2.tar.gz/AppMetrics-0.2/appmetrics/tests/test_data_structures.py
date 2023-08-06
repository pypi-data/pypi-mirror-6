import operator
import random

from nose.tools import assert_equal

from .. import data_structures as mm

class TestSkipList(object):
    def setUp(self):
        self.random_state = random.getstate()
        random.seed(42)

        self.sl = mm.SkipList()

    def tearDown(self):
        random.setstate(self.random_state)

    def _test_plain(self):
        import math
        #print
        for iii in (10, 20, 50, 100, 200, 400, 2000, 5000):
            self.sl = mm.SkipList()
            values = [random.randint(1, 100) for _ in range(iii)]
            #values = [5,3,2,4,1]

            ops = 0
            logs = 0
            for i, value in enumerate(values):
                #print "*****", i, value
                op = self.sl.insert(value)
                ops += op
                logs += math.log(i+1, 2)

                #print op, i+1, math.log(i+1, 2)
            #print len(values), ops, logs, ops/logs, self.sl.levels, math.log(len(values), 2)

            #print self.sl
            assert_equal(list(self.sl), sorted(values))


