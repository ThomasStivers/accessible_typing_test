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
		"sphinx",
		"sqlalchemy",
		"wxpython",
		],
		tests_require=["nose"],
		test_suite="nose.collector",
		include_package_data=True,
	zip_safe=False
	)
	