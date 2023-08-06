import logging

from .base import default_ts_skew_in_seconds, HawkAuthority, Resource
from .util import (calculate_mac,
                   parse_authorization_header,
                   validate_credentials)

__all__ = ['Sender']
log = logging.getLogger(__name__)


class Sender(HawkAuthority):

    def __init__(self, credentials,
                 url,
                 method,
                 content='',
                 content_type='text/plain',
                 nonce=None,
                 ext=None,
                 app=None,
                 dlg=None,
                 seen_nonce=None,
                 # For easier testing:
                 _timestamp=None):

        self.reconfigure(credentials)
        self.request_header = None
        self.seen_nonce = seen_nonce

        log.debug('generating request header')
        self.req_resource = Resource(url=url,
                                     credentials=self.credentials,
                                     ext=ext,
                                     app=app,
                                     dlg=dlg,
                                     nonce=nonce,
                                     method=method,
                                     content=content,
                                     timestamp=_timestamp,
                                     content_type=content_type)

        mac = calculate_mac('header', self.req_resource)
        self.request_header = self._make_header(self.req_resource, mac)

    def accept_response(self,
                        response_header,
                        content='',
                        content_type='text/plain',
                        localtime_offset_in_seconds=0,
                        timestamp_skew_in_seconds=default_ts_skew_in_seconds,
                        _timestamp=None,
                        **auth_kw):
        log.debug('accepting response {header}'
                  .format(header=response_header))

        parsed_header = parse_authorization_header(response_header)

        resource = Resource(ext=parsed_header.get('ext', None),
                            nonce=parsed_header['nonce'],
                            timestamp=_timestamp or parsed_header['ts'],
                            content=content,
                            content_type=content_type,
                            # The following response attributes must match
                            # our request:
                            url=self.req_resource.url,
                            method=self.req_resource.method,
                            app=self.req_resource.app,
                            dlg=self.req_resource.dlg,
                            credentials=self.credentials,
                            seen_nonce=self.seen_nonce)

        self._authorize('response', parsed_header, resource,
            timestamp_skew_in_seconds=timestamp_skew_in_seconds,
            localtime_offset_in_seconds=localtime_offset_in_seconds,
            **auth_kw)

    def reconfigure(self, credentials):
        validate_credentials(credentials)
        self.credentials = credentials
