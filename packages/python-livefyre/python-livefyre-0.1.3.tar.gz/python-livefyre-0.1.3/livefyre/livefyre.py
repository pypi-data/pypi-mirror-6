# -*- coding: utf-8 -*-

"""
.. module:: livefyre
   :platform: Unix, Windows
   :synopsis: Defines a REST API wrapper for Livefyre's (livefyre.com) v3
        commenting system.

.. moduleauthor:: Jason Novinger <jnovinger@gmail.com>
"""

import hashlib
import json
import os
from urllib import urlencode
import urlparse

import requests

from .utils import create_auth_token, jid, jwt_encode, validate_url


# grab info from environment if needed
DEFAULT_LIVEFYRE_NETWORK = os.environ.get('LIVEFYRE_NETWORK')
DEFAULT_LIVEFYRE_NETWORK_SECRET = os.environ.get('LIVEFYRE_NETWORK_SECRET')
DEFAULT_LIVEFYRE_SITE_ID = os.environ.get('LIVEFYRE_SITE_ID')
DEFAULT_LIVEFYRE_SITE_SECRET = os.environ.get('LIVEFYRE_SITE_SECRET')

# define API endpoints
LIVEFYRE_API_BASE = 'http://quill.{network}.fyre.co/api/v3.0/site/{site_id}'
LIVEFYRE_API_USER_BASE = 'http://{network}.fyre.co/api/v3_0'
LIVEFYRE_API_BARE = 'http://{network}.fyre.co/'

# suppoert HTTP methods
HTTP_METHODS = ['GET', 'POST']


class Livefyre(object):
    """A Livefyre v3 API client."""

    ENDPOINTS = {
        'COLLECTIONS': {
            '_base': 'collection',
            'create': 'create',
        },
        'USER': {
            '_base': 'user',
            'ping_to_pull': '{user_id}/refresh',
        },
    }

    def __init__(self,
        network=None,
        network_secret=None,
        site_id=None,
        site_secret=None,
        system_token=None):

        """Initializes a Livefyre API wrapper instance.

        :param str network:
            Required, the Livefyre "network_" assigned to you.
        :param str network_secret:
            Required, super secret API key associated with your network.
        :param str site_id:
            Optional, but required for some operations like :meth:`create_collection`.
        :param str site_secret:
            Optional, but required for any operations that also require
            :param:`site_id`.
        :param str system_token:
            Optional, provides the ability to supply a pre-generated
            `system@{network}` JWT auth token.
        :returns:
            None

        .. _network: https://github.com/Livefyre/livefyre-docs/wiki/Livefyre-concepts#data-model
        """

        super(Livefyre, self).__init__()

        self.network = network or DEFAULT_LIVEFYRE_NETWORK

        if ".fyre.co" in self.network:
            self.network = self.network.replace(".fyre.co", "")

        self.network_secret = network_secret or DEFAULT_LIVEFYRE_NETWORK_SECRET
        self.site_id = site_id or DEFAULT_LIVEFYRE_SITE_ID
        self.site_secret = site_secret or DEFAULT_LIVEFYRE_SITE_SECRET

        self.base_api = LIVEFYRE_API_BASE.format(network=self.network,
                                            site_id=self.site_id)
        self.bare_api = LIVEFYRE_API_BARE.format(network=self.network)
        self.user_api = LIVEFYRE_API_USER_BASE.format(network=self.network)

        self._system_token = system_token

        self.session = requests.session()

    def _get_system_token(self):
        """Returns the token for the `system@{network}` user."""
        if self._system_token:
            return self._system_token

        # if one was not passed in, create one for the "system" user
        system_token = self._create_auth_token(user_id='system')
        return system_token
    token = property(_get_system_token)

    def _make_jid(self, user_id):
        return jid(user_id, self.network)

    def _create_auth_token(self, user_id='system', display_name="", expires=None):
        """ Generate a JSON Web Token for a user id."""
        return create_auth_token(
            user_id=user_id,
            network=self.network,
            network_secret=self.network_secret,
            display_name=display_name,
        )

    def list_sites(self):
        params = {'actor_token': self.token}
        params = urlencode(params)

        response = self.send_data(
            endpoint='/sites?{}'.format(params),
            payload={},
            api='http://quill.{}.fyre.co/'.format(self.network),
        )
        return response.content, response

    def create_collection(self, title, url, article_id, stream_type, tags):
        collection = Collection(
            title, url, article_id, stream_type, tags, self.site_secret)
        response = self.send_data(
            endpoint='/collection/create',
            payload=collection.payload()
        )

        return collection, response

    def ping_to_pull(self, user_id, token=None):
        """Calls to the Livefyre Ping To Pull API

        Tells Livefyre that a user profile has changed and that they should
        hit our pre-registered API point to grab new information about the
        profile.

        If :param:`user_id` is not a string, it is assumed to be an object with
        a :var:`livefyre_id` attribute. See:
        [django-coversate](https://github.com/dailydot/django-conversate).

        If no token is passed, then one will be generated based on exisiting
        known credentials.
        """

        if not isinstance(user_id, basestring):
            user_id = user_id.livefyre_id

        # use a token if presented, else one presented at object instantiation
        # else one generated from the user_id
        token = (token or
                 self.token or
                 self._create_auth_token())

        endpoint = '/user/{user_id}/refresh'.format(user_id=user_id)
        payload = {'lftoken': token}
        return self.send_data(endpoint, payload, api=self.user_api)

    def register_profile_pull_interface(self, url, token=None):

        assert 'http' in url, "The Pull URL must be a valide HTTP(s) URL."
        params = {
            'actor_token': token or self.token,
            'pull_profile_url': url,
        }
        endpoint = '?{}'.format(urlencode(params))

        return self.send_data(endpoint, payload={}, api=self.bare_api)


    def send_data(self, endpoint, payload, method="POST", api=None):
        if api is None:
            api = self.base_api
        url = '{}{}'.format(api, endpoint)

        assert method in HTTP_METHODS, "Sorry, we only support {} as HTTP methods".format(HTTP_METHODS)

        method_ = getattr(self.session, method.lower())

        return method_(url, data=payload)


class Collection(object):
    """Represents a Livefyre StreamHub Collection"""

    TYPES = ['livecomments', 'liveblog', 'livechat']

    def __init__(self,
            title,
            url,
            article_id,
            stream_type='livecomments',
            tags=None,
            site_secret=None):

        assert title, 'title may not be empty.'
        assert article_id, 'article_id may not be empty'

        _url = urlparse.urlparse(url)
        assert 'http' in _url.scheme, 'The URL must be a fully qualified url whose scheme is either "http" or "https".'

        assert stream_type in self.TYPES, 'stream_type must be one of {}'.format(self.TYPES)

        _collection = {
            'title': title if len(title) < 256 else title[:255],
            'url': url,
            'articleId': article_id if len(article_id) < 256 else article_id[:255],
            'stream_type': stream_type,
            'tags': self._tagify(tags),
        }
        self.collection = _collection
        self.site_secret = site_secret

    def _tagify(self, tags):
        if tags:
            return tags.split(',')
        return []

    def meta(self):
        return jwt_encode(self.collection, self.site_secret)

    def checksum(self):
        hash_ = hashlib.md5()
        hash_.update(self.meta())
        return hash_.hexdigest()

    def payload(self):
        payload_ = json.dumps({
            'collectionMeta': self.meta(),
            'type': self.collection['stream_type'],
            'checksum': self.checksum(),
        })
        return payload_
