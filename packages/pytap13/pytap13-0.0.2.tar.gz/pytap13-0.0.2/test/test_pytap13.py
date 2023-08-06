import unittest

import sys
import os
sys.path.append(os.path.realpath(os.path.join(os.path.split(__file__)[0], '../')))
import pytap13

class TAP13_data_ok(unittest.TestCase):

    def test_basic(self):
        test_data = """
            TAP version 13
            1..2
            ok 1 Input file opened
            not ok 2 First line invalid
          """
        t = pytap13.TAP13()
        t.parse(test_data)

        self.assertEqual(t.tests_planned, 2)
        self.assertEqual(len(t.tests), t.tests_planned)

        tx = t.tests[0]
        self.assertEqual(tx.result, 'ok')
        self.assertEqual(tx.description, 'Input file opened')
        self.assertEqual(tx.directive, None)
        self.assertEqual(tx.comment, None)
        self.assertEqual(tx.yaml, None)

        tx = t.tests[1]
        self.assertEqual(tx.result, 'not ok')
        self.assertEqual(tx.description, 'First line invalid')

    def test_missing_id(self):
        test_data = """
            TAP version 13
            1..3
            ok 1 Input file opened
            not ok 2 First line invalid
            ok Third result
          """
        t = pytap13.TAP13()
        t.parse(test_data)

        self.assertEqual(t.tests_planned, 3)
        self.assertEqual(len(t.tests), t.tests_planned)

        tx = t.tests[2]
        self.assertEqual(tx.id, 3)
        self.assertEqual(tx.description, 'Third result')

    def test_missing_result_at_the_end(self):
        test_data = """
            TAP version 13
            1..4
            ok 1 Input file opened
            not ok 2 First line invalid
            ok Third result
          """
        t = pytap13.TAP13()
        t.parse(test_data)

        tx = t.tests[3]
        self.assertEqual(tx.id, 4)
        self.assertEqual(tx.result, 'not ok')

    def test_missing_result_in_between(self):
        test_data = """
            TAP version 13
            1..4
            ok 1 Input file opened
            not ok 2 First line invalid
            ok 4 Fourth result
          """
        t = pytap13.TAP13()
        t.parse(test_data)

        tx = t.tests[2]
        self.assertEqual(tx.id, 3)
        self.assertEqual(tx.result, 'not ok')

    def test_yaml(self):
        test_data = """
            TAP version 13
            1..2
            ok 1 Input file opened
            not ok 2 First line of the input valid
                ---
                message: 'First line invalid'
                data:
                    got:
                        - 1
                        - 2
                    expect:
                        - 2
                        - 2
                ...
          """
        t = pytap13.TAP13()
        t.parse(test_data)

        yaml_data = {"message": "First line invalid",
                "data": {
                        "got": [1,2],
                        "expect": [2,2]
                        }
                }
        self.assertEqual(t.tests[1].yaml, yaml_data)

    def test_multiline_yaml_string(self):
        test_data = """
            TAP version 13
            1..2
            ok 1 Input file opened
            not ok 2 First line of the input valid
                ---
                message: |-
                    First line
                    Second line
                ...
        """
        t = pytap13.TAP13()
        t.parse(test_data)
        yaml_data = {"message":"First line\nSecond line"}

        self.assertEqual(t.tests[1].yaml, yaml_data)


    def test_directive(self):
        test_data = """
        TAP version 13
        1..3
        not ok # ToDo not implemented
        not ok # SkiP arch is not ARM
        not ok # just a comment
        """
        t = pytap13.TAP13()
        t.parse(test_data)

        self.assertEqual(t.tests[0].directive, "TODO")
        self.assertEqual(t.tests[0].comment, "not implemented")
        self.assertEqual(t.tests[1].directive, "SKIP")
        self.assertEqual(t.tests[2].directive, None)
        self.assertEqual(t.tests[2].comment, "just a comment")

if __name__ == "__main__":
    unittest.main()
