from setuptools import setup

setup(name="accessible_typing_test",
	version="1.0",
	description="Typing speed and accuracy test which is accessible.",
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
	zip_safe=False
	)