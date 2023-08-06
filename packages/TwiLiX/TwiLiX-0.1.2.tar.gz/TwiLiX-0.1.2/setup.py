from distutils.core import setup

setup(
    name='TwiLiX',
    version='0.1.2',
    author='Sergey Dobrov',
    author_email='binary@jrudevels.org',
    packages=[
        'twilix',
        'twilix.base',
        'twilix.bytestreams',
        'twilix.bytestreams.socks5',
        'twilix.bytestreams.ibb',
        'twilix.ft',
        'twilix.muc',
        'twilix.patterns',
        'twilix.pubsub',
        'twilix.pubsub.payloads',
        'twilix.roster',
        'twilix.test',
    ],
    url='https://github.com/jbinary/twilix',
    license='LICENSE.txt',
    description='ORM based XMPP library for Twisted',
    install_requires=[
        "Twisted >= 13.2.0",
    ],
)
