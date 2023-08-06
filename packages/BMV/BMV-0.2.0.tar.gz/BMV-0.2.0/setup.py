from distutils.core import setup

setup(
    name='BMV',
    version='0.2.0',
    author='jepefe',
    maintainer='Nick Otter',
    maintainer_email='otternq@gmail.com',
    packages=['bmv', 'bmv.test'],
    scripts=['bin/bmv_mon.py'],
    url='https://github.com/otternq/bmvmonitor',
    license='LICENSE',
    description='A python script to record data from Victron BMV-600S and BMV-602S',
    long_description=open('README.md').read(),
    install_requires=[
        "pyserial",
        "nose"
    ],
)