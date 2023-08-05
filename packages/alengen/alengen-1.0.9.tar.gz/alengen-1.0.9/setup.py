import sys
import os.path

from setuptools import setup, find_packages

import alengen


here = os.path.dirname(__file__)

setup(
    name='alengen',
    description='Automatic model code generator for SQLAlchemy',
    version=alengen.version,
    author='Ashot Seropian',
    author_email='ashot.seropyan@gmail.com',
    url='https://github.com/massanchik/alengen',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Environment :: Console',
        'Topic :: Database',
        'Topic :: Software Development :: Code Generators',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ],
    keywords='sqlalchemy, alengen, generator, generate, autocode, entity, model',
    license='MIT',
    packages=find_packages(exclude=['tests']),
    install_requires=(
        'SQLAlchemy >= 0.6.0'
    ),
    test_suite='nose.collector',
    tests_require=['nose', 'sqlalchemy'],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'alengen=alengen.main:main'
        ]
    }
)
