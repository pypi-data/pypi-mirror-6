from distutils.core import setup

setup(
    name='zoro',
    description='Build tool written in Python, works with anything',
    long_description=open('README.rst').read(),
    version='1.0',
    py_modules=['zoro'],
    include_package_data=True,
    author='Branko Vukelic',
    author_email='branko@brankovukelic.com',
    url='https://bitbucket.org/brankovukelic/zoro/',
    download_url='https://bitbucket.org/brankovukelic/zoro/downloads',
    license='MIT',
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
    ],
)

