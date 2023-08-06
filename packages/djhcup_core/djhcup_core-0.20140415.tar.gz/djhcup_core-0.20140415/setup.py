import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='djhcup_core',
    version='0.20140415',
    include_package_data=True,
    description='A django-based interface for warehousing HCUP data',
    long_description=README,
    keywords='HCUP SAS healthcare analysis pandas',
    license='MIT',
    author='T.J. Biel',
    author_email='tbiel@med.umich.edu',
    packages=['djhcup_core'],
    provides=['djhcup_core'],
    classifiers=[
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering',
    ],
    package_data={'djhcup_core': [
                    'templates/*.*',
                    ]
                    },
    requires=[
        'django (>= 1.6)',
        'celery (>= 3.1.0)',
        'pandas (>= 0.11.0)',
        'pyhcup (>= 0.1.6)'
    ],
)