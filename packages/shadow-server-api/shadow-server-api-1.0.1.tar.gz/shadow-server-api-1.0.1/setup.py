try:
    from setuptools import setup

except:
    from distutils.core import setup

setup(
    name='shadow-server-api',
    test_suite="tests",
    version='1.0.1',
    packages=['shadowserver', 'shadowserver.test'],
    url='https://github.com/blacktop/shadow-server-api',
    license='GPLv3',
    author='blacktop',
    author_email='dev@blacktop.io',
    description='Shadow Server - Binary Whitelist and MD5/SHA1 AV Service API',
    install_requires=[
        "requests >= 2.2.1",
    ],
)
