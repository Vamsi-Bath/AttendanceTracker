import unittest
from code import greet

class TestGreeting(unittest.TestCase):
    def test_normal_name(self):
        self.assertEqual(greet("Alice"), "Hello, Alice!")

    def test_trim_spaces(self):
        self.assertEqual(greet("  Bob  "), "Hello, Bob!")

    def test_empty_name(self):
        self.assertEqual(greet("   "), "Hello, Guest!")

if __name__ == "__main__":
    unittest.main()
