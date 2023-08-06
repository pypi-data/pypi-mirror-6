from setuptools import setup


setup(
    name='pyRuuviTracker',
    version='0.12',
    author='Kimmo Huoman',
    author_email='kipenroskaposti@gmail.com',
    url='https://github.com/kipe/pyRuuviTracker',
    description='Client library for RuuviTracker in Python',
    long_description='Client library for RuuviTracker server written in Python.\n\nhttp://www.ruuvitracker.fi/',
    packages=['rt_client'],
    install_requires=[
        'requests>=1.2.3',
    ],
)
