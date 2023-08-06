import urllib, urllib2, jwt, time, base64, json, re


class Network(object):
    DEFAULT_USER = 'system'
    DEFAULT_EXPIRES = 86400
    
    def __init__(self, network_name, network_key):
        self.network_name = network_name
        self.network_key = network_key
    
    
    def set_user_sync_url(self, url_template):
        assert '{id}' in url_template, 'url_template should have {id}.'
        token = self.build_user_auth_token()
        
        url = 'http://{0!s}/'.format(self.network_name)
        data = urllib.urlencode({'actor_token' : token,
                                 'pull_profile_url'  : url_template})
        status = urllib2.urlopen(url=url, data=data).getcode()
        return status is 204
        
        
    def sync_user(self, user_id):
        url = 'http://{0!s}/api/v3_0/user/{1!s}/refresh'.format(self.network_name, user_id)
        data = urllib.urlencode({'lftoken' : self.build_user_auth_token()})
        status = urllib2.urlopen(url=url, data=data).getcode()
        return status is 200
    
    
    def build_user_auth_token(self, user_id=None, display_name=None, expires=None):
        if user_id is None:
            user_id = self.DEFAULT_USER
        else:
            assert user_id.isalnum(), 'user_id should only contain alphanumeric characters'
        if display_name is None:
            display_name = self.DEFAULT_USER
        if expires is None:
            expires = self.DEFAULT_EXPIRES
        return jwt.encode({
                'domain': self.network_name,
                'user_id': user_id,
                'display_name': display_name,
                'expires': int(time.time()) + expires},
            self.network_key)
    
    
    def validate_livefyre_token(self, lf_token):
        token_attr = jwt.decode(lf_token, self.network_key)
        return (token_attr['domain'] == self.network_name
            and token_attr['user_id'] == self.DEFAULT_USER
            and token_attr['expires'] >= int(time.time()))
        
    
    def get_site(self, site_id, site_key):
        return Site(self.network_name, site_id, site_key)


class Site(object):
    def __init__(self, network_name, site_id, site_key):
        self.network_name = network_name
        self.site_id = site_id
        self.site_key = site_key
    
    
    def build_collection_meta_token(self, title, article_id, url, tags, stream=''):
        assert re.match(r'^http[s]{0,1}://[a-zA-Z\d-]{,63}(\.[a-zA-Z\d-]{,63})*$', url), 'url must be a full domain. ie. http://livefyre.com'
        assert len(title) <= 255, "title's length should be under 255 char"
        return jwt.encode({
                'title': title,
                'url': url,
                'tags': tags,
                'articleId': article_id,
                'type': stream
                },
            self.site_key)
    
    
    def get_collection_content(self, article_id):
        url = 'http://bootstrap.{0!s}/bs3/{0!s}/{1!s}/{2!s}/init' \
            .format(self.network_name, self.site_id, base64.b64encode(str(article_id)))
        response = urllib2.urlopen(url=url)
        
        status = response.getcode()
        if status == 200:
            return json.load(response)
        return ''
