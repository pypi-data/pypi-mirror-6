from setuptools import setup
import os
import re
 
 
def read_file(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()
 
 
def read_first_line(file_name):
    with open(os.path.join(os.path.dirname(__file__), file_name)) as f:
        return f.readline().strip()
 
invalid = re.compile("\s*(#|--|\s+$)")


def read_dependencies(file_name):
    return [
        dep.strip() for dep in open(file_name).readlines() if not invalid.match(dep.strip())
    ]

REQUIREMENTS = read_dependencies('requirements.txt')
TEST_REQUIREMENTS = read_dependencies('requirements-dev.txt')

setup(
    name='simpyple',
    version=read_first_line('version_number.txt'),
    description="A bunch of utilities for simpy",
    long_description=read_file('README.md'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering'
    ],
    keywords='simpy simulation',
    author='Piergiuliano Bossi',
    author_email='',
    url='https://github.com/thinkingbox/simpyple',
    license='',
    package_dir={'simpyple': ''},
    packages=['simpyple'],
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIREMENTS,
    test_suite='nose.collector',
    tests_require=TEST_REQUIREMENTS
)
