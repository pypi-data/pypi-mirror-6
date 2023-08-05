""" Setup file """
import os
import sys

from setuptools import setup, find_packages


HERE = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(HERE, 'README.rst')).read()
CHANGES = open(os.path.join(HERE, 'CHANGES.rst')).read()

REQUIREMENTS = [
    'boto',
    'paste',
    'passlib',
    'pycrypto',
    'pyramid',
    'pyramid_beaker',
    'pyramid_duh>=0.1.1',
    'pyramid_jinja2',
    'pyramid_tm',
    'transaction',
    'zope.sqlalchemy',
]

TEST_REQUIREMENTS = [
    'nose',
    'mock',
    'webtest',
    'requests',
    'httpretty',
    'moto',
]

if sys.version_info[:2] < (2, 7):
    REQUIREMENTS.append('argparse')
    TEST_REQUIREMENTS.append('unittest2')

if __name__ == "__main__":
    setup(
        name='pypicloud',
        version='0.1.0',
        cmdclass={'update_version': None},
        description='Private PyPI backed by S3',
        long_description=README + '\n\n' + CHANGES,
        classifiers=[
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Development Status :: 4 - Beta',
            'Framework :: Pyramid',
            'Intended Audience :: System Administrators',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Topic :: Internet :: WWW/HTTP',
            'Topic :: System :: Systems Administration',
        ],
        license='MIT',
        author='Steven Arcangeli',
        author_email='steven@highlig.ht',
        url='http://pypicloud.readthedocs.org/',
        keywords='pypi s3 cheeseshop package',
        zip_safe=False,
        include_package_data=True,
        packages=find_packages(exclude=('tests',)),
        entry_points={
            'console_scripts': [
                'pypicloud-gen-password = pypicloud.scripts:gen_password',
                'pypicloud-make-config = pypicloud.scripts:make_config',
            ],
            'paste.app_factory': [
                'main = pypicloud:main',
            ],
        },
        install_requires=REQUIREMENTS,
        tests_require=REQUIREMENTS + TEST_REQUIREMENTS,
        test_suite='tests',
    )
