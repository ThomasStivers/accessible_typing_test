# accessible_typing_test
# Copyright (C) 2019 Thomas Stivers

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
