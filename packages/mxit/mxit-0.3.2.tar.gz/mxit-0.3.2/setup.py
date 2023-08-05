from distutils.core import setup

LONG_DESCRIPTION = None
try:
    LONG_DESCRIPTION = open('README.md').read()
except:
    pass


setup(
    name='mxit',
    version='0.3.2',
    author='Philip Perold',
    author_email='prperold@gmail.com',
    packages=['mxit'],
    url='https://github.com/Mxit/python-mxit',
    license='LICENSE',
    description="Python utility library for accessing Mxit's public APIs.",
    long_description=LONG_DESCRIPTION,
    install_requires=[
        "requests == 2.0.1",
    ],
)

