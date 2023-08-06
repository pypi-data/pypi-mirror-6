from distutils.core import setup

setup(
    name='StoreM',
    version='0.0.1',
    author='Michael Imelfort',
    author_email='mike@mikeimelfort.com',
    packages=['storem'],
    scripts=['bin/StoreM'],
    url='http://pypi.python.org/pypi/StoreM/',
    license='GPLv3',
    description='StoreM',
    long_description=open('README.md').read(),
    install_requires=[],
)

