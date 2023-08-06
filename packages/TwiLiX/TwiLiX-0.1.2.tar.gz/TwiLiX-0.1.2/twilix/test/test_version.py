import unittest

from twisted.words.protocols.jabber.jid import JID

from twilix.version import MyVersionQuery, ClientVersion
from twilix import errors
from twilix.stanzas import Iq
from twilix.disco import Disco

from twilix.test import hostEmul, dispatcherEmul


class TestVCardQuery(unittest.TestCase):
    
    def setUp(self):
        self.MyVersionQuery = MyVersionQuery(parent=Iq(type_='get'))
        self.MyVersionQuery.host = hostEmul(client_name = 'name', 
                                            client_os = 'os',
                                            client_version = 'version')
    
    def test_getHandler(self):
        res = self.MyVersionQuery.getHandler()
        res = res.children[0]
        host = self.MyVersionQuery.host
        self.assertEqual(res.client_name, host.client_name)
        self.assertEqual(res.client_os, host.client_os)
        self.assertEqual(res.client_version, host.client_version)
        self.assertTrue(isinstance(res.parent, Iq))
    
    def test_setHandler(self):
        self.assertRaises(errors.BadRequestException, self.MyVersionQuery.setHandler)
    
class TestClientVersion(unittest.TestCase):
    
    def setUp(self):
        self.CV = ClientVersion(dispatcher=dispatcherEmul('jid'))
        
    def test_init(self):
        disco = Disco(self.CV.dispatcher)
        self.CV.init(disco=disco)
        self.assertEqual(self.CV.dispatcher._handlers[0],
                         (MyVersionQuery, self.CV))
        self.assertTrue('jabber:iq:version' in \
                        map(unicode, disco.root_info.features))
    
    def test_getVersion(self):
        to = 'to'
        self.CV.getVersion(jid=to)
        result = self.CV.dispatcher.data[0]
        self.assertEqual(result.type_, 'get')
        self.assertEqual(result.to, JID(to))
        self.assertEqual(result.from_, JID('jid'))
        self.assertTrue(isinstance(result, Iq))
