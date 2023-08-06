from setuptools import setup

setup(
    name="notedown",
    version='1.0.3',
    description="Convert markdown to IPython notebook.",
    packages=['notedown'],
    author="Aaron O'Leary",
    author_email='dev@aaren.me',
    url='http://github.com/aaren/notedown',
    install_requires=['ipython', ],
    entry_points={
        'console_scripts': [
            'notedown = notedown:cli',
        ],
    }
)
