import unittest

from livefyre import Livefyre

class LivefyreTestCase(unittest.TestCase):
    NETWORK = 'test.fyre.com';
    NETWORK_KEY = 'testkeytest';
    
    SITE_ID = '1';
    SITE_KEY = 'testkeytest';
    
    def setUp(self):
        pass

    def test_set_user_sync_url(self):
        network = Livefyre.get_network(self.NETWORK, self.NETWORK_KEY)
        with self.assertRaisesRegexp(AssertionError, 'url_template should have {id}.'):
            network.set_user_sync_url('http://thisisa.test.url/')
        
    def test_build_validate_user_token(self):
        network = Livefyre.get_network(self.NETWORK, self.NETWORK_KEY)
        
        with self.assertRaisesRegexp(AssertionError, 'user_id should only contain alphanumeric characters'):
            network.build_user_auth_token('system@blah', 'testName', 86400.0)
        
        token = network.build_user_auth_token('system', 'testName', 86400.0)
        
        self.assertIsNotNone(token)
        self.assertTrue(network.validate_livefyre_token(token))
        
    def test_build_collection_token(self):
        site = Livefyre.get_network(self.NETWORK, self.NETWORK_KEY).get_site(self.SITE_ID, self.SITE_KEY)
        
        with self.assertRaisesRegexp(AssertionError, 'url must be a full domain. ie. http://livefyre.com'):
            site.build_collection_meta_token('title', 'articleId', 'url.com', 'tags', 'reviews')
        
        with self.assertRaisesRegexp(AssertionError, "title's length should be under 255 char"):
            site.build_collection_meta_token('1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456', 'article_id', 'http://url.com', 'tags')
        
        token = site.build_collection_meta_token('title', 'articleId', 'https://www.url.com', 'tags', 'reviews')
        
        self.assertIsNotNone(token)
        

if __name__ == '__main__':
    unittest.main()