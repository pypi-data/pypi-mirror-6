from distutils.core import setup


setup(
    name='djhcup_staging',
    version='0.20140415.3dev',
    description='Staging module for the Django-HCUP Hachoir (djhcup)',
    #long_description=open('README.rst').read(),
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
