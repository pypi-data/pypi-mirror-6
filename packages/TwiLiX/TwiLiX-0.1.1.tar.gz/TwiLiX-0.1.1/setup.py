from distutils.core import setup

setup(
    name='TwiLiX',
    version='0.1.1',
    author='Sergey Dobrov',
    author_email='binary@jrudevels.org',
    packages=['twilix'],
    url='https://github.com/jbinary/twilix',
    license='LICENSE.txt',
    description='ORM based XMPP library for Twisted',
    install_requires=[
        "Twisted >= 13.2.0",
    ],
)
