from setuptools import setup

from setuputils import find_version

setup(
    name='ged',
    version=find_version('ged.py'),
    description='A simple script runner.',
    py_modules=['ged', 'setuputils'],
    entry_points={'console_scripts': ['ged=ged:main']},
    author='Berker Peksag',
    author_email='berker.peksag@gmail.com',
    url='https://github.com/berkerpeksag/ged',
    license='Mozilla Public License, v. 2.0',
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
    ],
)
