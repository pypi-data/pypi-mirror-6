import os
from distutils.core import setup

setup(
    name='FlaskWarts',
    description='Assortment of various utilities for Flask applications',
    long_description=open(os.path.join(os.path.dirname(__file__),
                                       'README.rst')).read(),
    version='0.1a5',
    packages=['utils'],
    requires=[
        'Flask (>=0.10)',
        'FormEncode (>=1.3.0a1)',
        'Jinja2 (>=2.7)'
    ],
    author='Branko Vukelic',
    author_email='branko@brankovukelic.com',
    url='https://bitbucket.org/brankovukelic/FlaskWarts/',
    download_url='https://bitbucket.org/brankovukelic/FlaskWarts/downloads',
    license='MIT',
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Flask',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
    ],
)
