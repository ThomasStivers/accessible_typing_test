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

from setuptools import setup
from accessible_typing_test import __version__

def readme():
	with open("README.md") as f:
		return f.read()

setup(name="accessible_typing_test",
	version=__version__,
	description="Typing speed and accuracy test which is accessible.",
	long_description=readme(),
	url="https://github.com/thomas.stivers/accessible_typing_test/",
	author="Thomas Stivers",
	author_email="thomas.stivers@gmail.com",
	license="GPL",
	packages=["accessible_typing_test"],
	install_requires=[
		"openpyxl",
		"pyttsx3",
		"sphinx",
		"sqlalchemy",
		"wxpython",
		],
		tests_require=["nose"],
		test_suite="nose.collector",
		include_package_data=True,
	zip_safe=False
	)
