from setuptools import setup


setup(
    author='Alex Clark',
    author_email='aclark@aclark.net',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ],
    description="Make a temp dir",
    entry_points={
        'console_scripts': 'tmp=tmp:print_tmp',
    },
    keywords="temp temporary files directory",
    license='GPL',
    long_description=(
        open('README.rst').read() + '\n' +
        open('CHANGES.rst').read()),
    name='tmp',
    py_modules=[
        'tests',
        'tmp',
    ],
    test_suite='tests.TestCase',
    url='https://github.com/aclark4life/tmp',
    version='0.0.2',
    zip_safe=False,
)
