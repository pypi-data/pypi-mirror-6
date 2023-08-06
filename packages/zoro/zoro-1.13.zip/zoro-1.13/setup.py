import os
from distutils.core import setup

setup(
    name='zoro',
    description='Build tool written in Python, works with anything',
    long_description=open(os.path.join(os.path.dirname(__file__),
                                       'README.rst')).read(),
    version='1.13',
    py_modules=['zoro'],
    author='Branko Vukelic',
    author_email='branko@brankovukelic.com',
    url='https://bitbucket.org/brankovukelic/zoro/',
    download_url='https://bitbucket.org/brankovukelic/zoro/downloads',
    license='MIT',
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
    ],
)

