import jwt, unittest

from livefyre import Livefyre

class LivefyreTestCase(unittest.TestCase):
    NETWORK = 'test.fyre.com'
    NETWORK_KEY = 'testkeytest'
    
    SITE_ID = '1'
    SITE_KEY = 'testkeytest'
    
    CHECKSUM = '6e2e4faf7b95f896260fe695eafb34ba'
    
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
        
        token = network.build_livefyre_token()
        
        self.assertIsNotNone(token)
        self.assertTrue(network.validate_livefyre_token(token))
        
    def test_build_collection_token(self):
        site = Livefyre.get_network(self.NETWORK, self.NETWORK_KEY).get_site(self.SITE_ID, self.SITE_KEY)
        
        with self.assertRaisesRegexp(AssertionError, 'url must be a full domain. ie. http://livefyre.com'):
            site.build_collection_meta_token('title', 'articleId', 'url.com', 'tags', 'reviews')
        
        with self.assertRaisesRegexp(AssertionError, "title's length should be under 255 char"):
            site.build_collection_meta_token('1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456', 'article_id', 'http://url.com', 'tags')
        
        with self.assertRaisesRegexp(AssertionError, 'type is not a recognized type. should be liveblog, livechat, livecomments, reviews, sidenotes, or an empty string.'):
            site.build_collection_meta_token('title', 'articleId', 'http://livefyre.com', 'tags', 'bad type')
        
        token = site.build_collection_meta_token('title', 'articleId', 'https://livefyre.com', 'tags')
        
        self.assertIsNotNone(token)
        
        token = site.build_collection_meta_token('title', 'articleId', 'https://livefyre.com', 'tags', 'reviews')
        self.assertEquals(jwt.decode(token, self.SITE_KEY)['type'], 'reviews')
        
        token = site.build_collection_meta_token('title', 'articleId', 'https://livefyre.com', 'tags', 'liveblog')
        self.assertEquals(jwt.decode(token, self.SITE_KEY)['stream_type'], 'liveblog')
        
    def test_build_checksum(self):
        site = Livefyre.get_network(self.NETWORK, self.NETWORK_KEY).get_site(self.SITE_ID, self.SITE_KEY)
        
        with self.assertRaisesRegexp(AssertionError, 'url must be a full domain. ie. http://livefyre.com'):
            site.build_checksum('title', 'url', 'tags')
            
        with self.assertRaisesRegexp(AssertionError, "title's length should be under 255 char"):
            site.build_checksum('1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456', 'http://url.com', 'tags')
       
        checksum = site.build_checksum('title', 'https://www.url.com', 'tags')
        self.assertEquals(self.CHECKSUM, checksum, 'checksum is not correct.')
        
        
if __name__ == '__main__':
    unittest.main()