import random
import unittest
import subprocess
import os
import sys
sys.path.insert(0, os.path.join(os.path.split(__file__)[0], ".."))
print os.path.join(os.path.split(__file__)[0], "..")
from pync import TerminalNotifier



class TestNotificationFunctions(unittest.TestCase):
    def setUp(self):
        self.Notifier = TerminalNotifier.TerminalNotifier()

    def test_execute_tool_with_given_options(self):
        bin_path = TerminalNotifier.TerminalNotifier().bin_path
        output = subprocess.Popen([bin_path,] + ["-message", "test message"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # print output
        self.assertFalse(output.returncode)

    def test_basic_notify(self):
        output = self.Notifier.notify("HELLO")
        print("AAA", output.communicate())
        self.assertEqual(output.communicate()[0], '* Notification delivered.\n')

    #     # should raise an exception for an immutable sequence
    #     self.assertRaises(TypeError, random.shuffle, (1,2,3))

    # def test_choice(self):
    #     element = random.choice(self.seq)
    #     self.assertTrue(element in self.seq)

    # def test_sample(self):
    #     with self.assertRaises(ValueError):
    #         random.sample(self.seq, 20)
    #     for element in random.sample(self.seq, 5):
    #         self.assertTrue(element in self.seq)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestNotificationFunctions)
    unittest.TextTestRunner(verbosity=2).run(suite)
