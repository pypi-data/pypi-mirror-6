from setuptools import setup

setup(
    name='qscollect',
    version='1.1',
    packages=['tests', 'qscollect', 'qscollect.scripts', 'qscollect.collectors', 'qscollect.collectors.omnifocus'],
    namespace_packages=['qscollect', 'qscollect.collectors'],
    url='http://bitbucket.org/russellhay/qscollect',
    license='',
    author='Russell Hay',
    author_email='me@russellhay.com',
    description='A system for collecting Quantified Self data',
    entry_points={
        "console_scripts": [
            'qscollectd = qscollect.__main__:main',
            'qsdump = qscollect.scripts.dump:main',
            'qsconfig = qscollect.scripts.config:main',
        ]
    }
)
