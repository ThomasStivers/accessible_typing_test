from setuptools import setup

def readme():
	with open("README.md") as f:
		return f.read()

setup(name="accessible_typing_test",
	version="1.0",
	description="Typing speed and accuracy test which is accessible.",
	long_description=readme(),
	url="https://github.com/thomas.stivers/accessible_typing_test/",
	author="Thomas Stivers",
	author_email="thomas.stivers@gmail.com",
	license="GPL",
	packages=["accessible_typing_test"],
	install_requires=[
		"openpyxl",
		"sqlalchemy",
		"wxpython",
		],
		tests_require=["nose"],
		test_suite="nose.collector",
		include_package_data=True,
	zip_safe=False
	)
	