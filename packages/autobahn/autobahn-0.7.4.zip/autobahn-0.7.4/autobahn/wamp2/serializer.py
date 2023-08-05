###############################################################################
##
##  Copyright (C) 2013 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

__all__ = ['WampSerializer',
           'JsonSerializer',
           'WampJsonSerializer']


from zope.interface import implementer

from interfaces import ISerializer
from error import WampProtocolError
from message import WampMessageHello, \
                    WampMessageHeartbeat, \
                    WampMessageRoleChange, \
                    WampMessageSubscribe, \
                    WampMessageSubscription, \
                    WampMessageSubscribeError, \
                    WampMessageUnsubscribe, \
                    WampMessagePublish, \
                    WampMessageEvent, \
                    WampMessageMetaEvent, \
                    WampMessageProvide, \
                    WampMessageUnprovide, \
                    WampMessageCall, \
                    WampMessageCancelCall, \
                    WampMessageCallProgress, \
                    WampMessageCallResult, \
                    WampMessageCallError



class WampSerializer:
   """
   WAMP serializer is the core glue between parsed WAMP message objects and the
   bytes on wire (the transport).
   """

   MESSAGE_TYPE_MAP = {
      ## Session
      WampMessageHello.MESSAGE_TYPE:            WampMessageHello,
      WampMessageHeartbeat.MESSAGE_TYPE:        WampMessageHeartbeat,
      WampMessageRoleChange.MESSAGE_TYPE:       WampMessageRoleChange,

      ## PubSub
      WampMessageSubscribe.MESSAGE_TYPE:        WampMessageSubscribe,
      WampMessageSubscription.MESSAGE_TYPE:     WampMessageSubscription,
      WampMessageSubscribeError.MESSAGE_TYPE:   WampMessageSubscribeError,

      WampMessageUnsubscribe.MESSAGE_TYPE:      WampMessageUnsubscribe,
      WampMessagePublish.MESSAGE_TYPE:          WampMessagePublish,
      WampMessageEvent.MESSAGE_TYPE:            WampMessageEvent,
      WampMessageMetaEvent.MESSAGE_TYPE:        WampMessageMetaEvent,

      ## RPC
      WampMessageProvide.MESSAGE_TYPE:          WampMessageProvide,
      WampMessageUnprovide.MESSAGE_TYPE:        WampMessageUnprovide,
      WampMessageCall.MESSAGE_TYPE:             WampMessageCall,
      WampMessageCancelCall.MESSAGE_TYPE:       WampMessageCancelCall,
      WampMessageCallProgress.MESSAGE_TYPE:     WampMessageCallProgress,
      WampMessageCallResult.MESSAGE_TYPE:       WampMessageCallResult,
      WampMessageCallError.MESSAGE_TYPE:        WampMessageCallError,
   }


   def __init__(self, serializer):
      """
      Constructor.

      :param serializer: The wire serializer to use for WAMP wire processing.
      :type serializer: An object that implements :class:`autobahn.interfaces.ISerializer`.
      """
      self._serializer = serializer


   def serialize(self, wampMessage):
      """
      Serializes a WAMP message to bytes to be sent to a transport.

      :param wampMessage: An instance of a subclass of :class:`autobahn.wamp2message.WampMessage`.
      :type wampMessage: obj
      :returns str -- A byte string.
      """
      return wampMessage.serialize(self._serializer), self._serializer.isBinary


   def unserialize(self, bytes, isBinary):
      """
      Unserializes bytes from a transport and parses a WAMP message.

      :param bytes: Byte string from wire.
      :type bytes: str or bytes
      :returns obj -- An instance of a subclass of :class:`autobahn.wamp2message.WampMessage`.
      """
      if isBinary != self._serializer.isBinary:
         raise WampProtocolError("invalid serialization of WAMP message [binary = %s, but expected %s]" % (isBinary, self._serializer.isBinary))

      try:
         raw_msg = self._serializer.unserialize(bytes)
      except Exception as e:
         raise WampProtocolError("invalid serialization of WAMP message [%s]" % e)

      if type(raw_msg) != list:
         raise WampProtocolError("invalid type %s for WAMP message" % type(raw_msg))

      if len(raw_msg) == 0:
         raise WampProtocolError("missing message type in WAMP message")

      message_type = raw_msg[0]

      if type(message_type) != int:
         raise WampProtocolError("invalid type %d for WAMP message type" % type(message_type))

      Klass = self.MESSAGE_TYPE_MAP.get(message_type)

      if Klass is None:
         raise WampProtocolError("invalid WAMP message type %d" % message_type)

      msg = Klass.parse(raw_msg)

      return msg



import json

@implementer(ISerializer)
class JsonSerializer:

   isBinary = False

   def serialize(self, obj):
      return json.dumps(obj, separators = (',',':'))


   def unserialize(self, bytes):
      return json.loads(bytes)



class WampJsonSerializer(WampSerializer):

   SERIALIZER_ID = "json"

   def __init__(self):
      WampSerializer.__init__(self, JsonSerializer())



try:
   import msgpack
except:
   pass
else:
   @implementer(ISerializer)
   class MsgPackSerializer:

      isBinary = True

      def serialize(self, obj):
         return msgpack.packb(obj, use_bin_type = True)


      def unserialize(self, bytes):
         return msgpack.unpackb(bytes, encoding = 'utf-8')

   __all__.append('MsgPackSerializer')


   class WampMsgPackSerializer(WampSerializer):

      SERIALIZER_ID = "msgpack"

      def __init__(self):
         WampSerializer.__init__(self, MsgPackSerializer())

   __all__.append('WampMsgPackSerializer')
