import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='djhcup_staging',
    version='0.20140415',
    description='Staging module for the Django-HCUP Hachoir (djhcup)',
    long_description=README,
    license='MIT',
    author='T.J. Biel',
    author_email='tbiel@med.umich.edu',
    packages=['djhcup_staging'],
    provides=['djhcup_staging'],
    classifiers=[
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering',
    ],
    package_data={'djhcup_staging': [
                    'templates/*.*',
                    'utils/*.*',
                    ]
                    },
    requires=[
        'djhcup_core (>= 0.20140415)',
    ],
)
