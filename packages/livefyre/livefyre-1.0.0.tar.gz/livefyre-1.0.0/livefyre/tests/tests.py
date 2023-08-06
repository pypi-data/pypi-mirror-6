import unittest

from livefyre import Network

class LivefyreTestCase(unittest.TestCase):
    NETWORK = "test.fyre.com";
    NETWORK_KEY = "testkeytest";
    
    SITE_ID = "1";
    SITE_KEY = "testkeytest";
    
    def setUp(self):
        pass

    def test_get_network(self):
        network = Network(self.NETWORK, self.NETWORK_KEY)
        self.assertIsNone(network.set_user_sync_url('http://thisisa.test.url/'), 
                        'should be None as {id} is absent')
        
    def test_build_validate_user_token(self):
        network = Network(self.NETWORK, self.NETWORK_KEY)
        token = network.build_user_auth_token("system", "testName", 86400.0)
        
        self.assertIsNotNone(token)
        self.assertTrue(network.validate_livefyre_token(token))
        
    def test_build_collection_token(self):
        site = Network(self.NETWORK, self.NETWORK_KEY).get_site(self.SITE_ID, self.SITE_KEY)
        token = site.build_collection_token('title', 'articleId', 'url', 'tags')
        
        self.assertIsNotNone(token)
        

if __name__ == '__main__':
    unittest.main()