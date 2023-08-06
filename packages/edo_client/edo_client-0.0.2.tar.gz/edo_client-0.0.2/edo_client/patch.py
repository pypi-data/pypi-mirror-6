from pyoauth2 import Client as client
from pyoauth2 import AccessToken
from pyoauth2.libs.base import Base 

class Client(client):

    def get_token(self, **opts):
        self.response = self.request(self.opts['token_method'], self.token_url(), **opts)
        opts.update(self.response.parsed)

        token_info = {}
        if opts.get('return_token_info'):
            token_info = opts.get('token_info', {})
            return AccessToken.from_hash(self, **opts), token_info
        return AccessToken.from_hash(self, **opts)

    @property
    def borrow(self):
        return Borrow(self)


class Borrow(Base):
    def authorize_url(self):
        return NotImplementedError('The authorization endpoint is not used in this strategy')

    def get_token(self, access_token, **opts):
        params = {'grant_type': 'token_borrow',
                  'access_token': access_token,
                 } 

        params.update(self.client_params)
        opts.update(params)
        return self.client.get_token(**opts)

