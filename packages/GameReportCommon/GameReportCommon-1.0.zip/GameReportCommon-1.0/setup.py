from distutils.core import setup

setup(
    name='GameReportCommon',
    version='1.0',
    author='Sebastien Tolron',
    author_email='sebastien@tolron',
    packages=['GameReportCommon', ],
    scripts=['bin/event.py'],
    url='http://pypi.python.org/pypi/GameReportCommon/',
    license='LICENSE.txt',
    description='Common library for GameReport project',
    long_description=open('README.txt').read(),
)

