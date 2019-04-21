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

"""Standalone function to calculate the Levenshtein distance between 2 strings.

For more information on the Levenshtein distance see:
https://en.wikipedia.org/wiki/Levenshtein_distance
"""

def levenshteinDistance(shorter: str, longer: str) -> int:
	"""Calculate the Levenshtein Distance aka edit distance between 2 strings.
	
	Args:
		shorter (str): First string to compare.
		longer (str): Second string to compare.

	Returns:
		int: The number of edits required to convert s2 into s1.
	"""
	# Swap the strings if the lengths aren't as expected.
	if len(shorter) > len(longer):
		shorter, longer = longer, shorter

	# Create an integer list 1 longer than the length of the shorter string.
	distances = range(len(shorter) + 1)
	
	# Iterate over the longer string keeping track of position within the string.
	for position_longer, character_longer in enumerate(longer):
		
		# Create a list with 1 integer with the position of the next character.
		distances_ = [position_longer+1]
		# Iterate over the shorter string keeping track of position within the string.
		for position_shorter, character_shorter in enumerate(shorter):
			if character_shorter == character_longer:
				distances_.append(distances[position_shorter])
			else:
				distances_.append(
					1 + min((distances[position_shorter], distances[position_shorter + 1], distances_[-1]))
					)
		distances = distances_
	return distances[-1]
