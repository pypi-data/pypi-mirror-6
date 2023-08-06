try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='max7301',
    version='1.0.3',
    description='MAX7301 driver',
    author='Tobias Schneider',
    author_email='schneider@xtort.eu',
    url='https://github.com/muccc/py-max7301',
    packages=['max7301'],
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 2",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='max7301',
    license='GPLv3+',
    install_requires=['spidev'],
    scripts=['scripts/py-max7301-rpi-spi-setup']
)
