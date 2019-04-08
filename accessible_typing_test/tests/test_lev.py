from unittest import TestCase
import accessible_typing_test

class TestLevenshteinDistance(TestCase):
	"""Ensure that our formula for calculating typing accuracy is working."""

	def test_accurate_typing(self):
		"""When everything is typed correctly."""
		distance = accessible_typing_test.lev.levenshteinDistance(
			"The quick red fox jumped over the lazy brown dog.",
			"The quick red fox jumped over the lazy brown dog."
			)
		self.assertEqual(distance, 0)

	def test_inaccurate_typing(self):
		"""When characters are missing, added, case shifted, or swapped."""
		distance = accessible_typing_test.lev.levenshteinDistance(
			"The quick red fox jumped over the lazy brown dog.",
			"The Quick read fox jumped ovre the lazy brown dog"
			)
		self.assertEqual(distance, 5)

	def test_ints(self):
		"""What happens when the arguments are integers?"""
		with self.assertRaises(TypeError):
			distance = accessible_typing_test.lev.levenshteinDistance(0, 1)
