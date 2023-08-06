import os
from distutils.core import setup

setup(
    name='document',
    description='Wraps dicts in an object for convenient document management',
    long_description=open(os.path.join(os.path.dirname(__file__),
                                       'README.rst')).read(),
    version='1.0',
    py_modules=['document'],
    author='Branko Vukelic',
    author_email='branko@brankovukelic.com',
    url='https://bitbucket.org/brankovukelic/document/',
    download_url='https://bitbucket.org/brankovukelic/document/downloads',
    license='MIT',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
    ],
)
