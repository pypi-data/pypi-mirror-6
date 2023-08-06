try:
    from setuptools import setup

except ImportError:
    from distutils.core import setup

setup(
    name='virustotal-api',
    test_suite="tests",
    version='1.0.1',
    packages=['virustotal', 'virustotal.test'],
    url='https://github.com/blacktop/virustotal-api',
    license='GPLv3',
    author='blacktop',
    author_email='dev@blacktop.io',
    description='Virus Total Public/Private/Intel API',
    install_requires=[
        "requests >= 2.2.1",
    ],
)
