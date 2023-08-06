# -*- coding: utf-8 -*-

'''

  canteen: JSONRPC protocol
  ~~~~~~~~~~~~~~~~~~~~~~~~~

  :author: Sam Gammon <sg@samgammon.com>
  :copyright: (c) Sam Gammon, 2014
  :license: This software makes use of the MIT Open Source License.
            A copy of this license is included as ``LICENSE.md`` in
            the root of the project.

'''

# stdlib
import json

# canteen base & core
from canteen.core import runtime
from canteen.base import protocol


## Globals
_content_types = (
  'application/json',
  'application/x-javascript',
  'text/javascript',
  'text/x-javascript',
  'text/x-json',
  'text/json'
)


with runtime.Library('protorpc') as (library, protorpc):

  # submodules
  protojson = library.load('protojson')


  @protocol.Protocol.register('jsonrpc', _content_types)
  class JSONRPC(protocol.Protocol, protojson.ProtoJson):

    '''  '''

    class JSONMessageCodec(protojson.MessageJSONEncoder):

      '''  '''

      skipkeys = True
      ensure_ascii = True
      check_circular = True
      allow_nan = True
      sort_keys = False
      indent = None
      separators = (',', ':')
      encoding = 'utf-8'

    def encode_message(self, message):

      '''  '''

      message.check_initialized()
      result = json.dumps(message, **{
        'cls': self.JSONMessageCodec,
        'skipkeys': self.JSONMessageCodec.skipkeys,
        'ensure_ascii': self.JSONMessageCodec.ensure_ascii,
        'check_circular': self.JSONMessageCodec.check_circular,
        'allow_nan': self.JSONMessageCodec.allow_nan,
        'sort_keys': self.JSONMessageCodec.sort_keys,
        'indent': self.JSONMessageCodec.indent,
        'encoding': self.JSONMessageCodec.encoding,
        'separators': self.JSONMessageCodec.separators,
        'protojson_protocol': self
        })

      return result

    def decode_message(self, message_type, encoded_message):

      '''  '''

      return protojson.ProtoJson().decode_message(message_type, encoded_message)
