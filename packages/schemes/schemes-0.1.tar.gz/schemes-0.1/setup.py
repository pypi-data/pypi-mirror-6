import codecs
import os

from setuptools import setup

with codecs.open(os.path.join(os.path.dirname(__file__), 'README.rst'),
                 'r', 'utf8') as f:
    long_description = f.read()

setup(
    name='schemes',
    version='0.1',
    url='https://bitbucket.org/tawmas/schemes',
    license='MIT License',
    author='Tommaso R. Donnarumma',
    author_email='tawmas@tawmas.net',
    install_requires=[],
    description='Easy input validation and data manipulation.',
    long_description=long_description,
    packages=['schemes', 'schemes.libs'],
    include_package_data=True,
    platforms='any',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    extras_require={
        'testing': ['pytest>=2.5.2', 'pytest-cov>=1.6']
    }
)
