"""
This just wraps the normal mongrel2 stuff to make it easier to work with websockets
"""

# stdlib
from uuid import uuid4
import logging
from struct import pack # for network byte order

# third party
from mongrel2 import handler, request

__version__ = '0.1'

logger = logging.getLogger(__name__)

# http://tools.ietf.org/html/rfc6455#section-5.2
OP_TEXT = 0x1
OP_CLOSE = 0x8
OP_PING = 0x9
OP_BINARY = 0x2
OP_PONG = 0xA

# the abnormal close errors
# http://tools.ietf.org/html/rfc6455#section-7.4
# http://tools.ietf.org/html/rfc6455#section-11.7
CLOSE_NORMAL = 1000
CLOSE_GOING_AWAY = 1001
CLOSE_PROTOCOL_ERROR = 1002
CLOSE_UNSUPPORTED_DATA = 1003
CLOSE_INVALID_FRAME_DATA = 1007
CLOSE_POLICY_VIOLATION = 1008
CLOSE_TOO_BIG = 1009
CLOSE_INTERNAL_SERVER_ERROR = 1011 # this is the ws equivalent of 500 server error


class WebsocketError(RuntimeError):
    """any problems with the websocket protocol can raise this error"""
    def __init__(self, code, msg):
        '''
        create the error

        code -- integer -- http status code
        msg -- string -- the message you want to accompany your status code
        '''
        self.code = code
        super(WebsocketError, self).__init__(msg)

    def __str__(self):
        """
        http://tools.ietf.org/html/rfc6455#section-5.5.1
        If there is a body, the first two bytes of the body MUST be a 2-byte unsigned integer (in network byte order)
        """
        network_byte_str = pack('!H', self.code)
        return network_byte_str + super(WebsocketError, self).__str__()


class Request(request.Request):
    """wraps the default Mongrel Request and adds websocket only functionality"""
    @property
    def decoded_body(self):
        """
        decodes utf-8 body and moves it into .data so you can still access original body in .body

        normalize the text and make it available in data, sending the right
        error if utf-8 decode fails
        """
        try:
            return self.body.decode('utf-8')

        except UnicodeError, e:
            raise WebsocketError(CLOSE_INVALID_FRAME_DATA, 'invalid UTF')

    def __init__(self, req):
        """
        yes, this is a Request object that takes a parent version of itself to init
        """
        super(Request, self).__init__(req.sender, req.conn_id, req.path, req.headers, req.body)
        if hasattr(req, 'opcode'):
            self.opcode = req.opcode
            self.fin = req.fin
        else:
            self._decode_flags()

    def _decode_flags(self):
        """
        flags is an 8 bit (1 byte) integer representing the first 8 bits of a websocket frame
        because we only get the first 8 bits back, I'm assuming mongrel2 handles the masking and
        concatenating of multiple frames

        We also don't handle opcode 0x0 (continue) or 0xA (pong) since Mongrel handles those

        |F|R|R|R|OPCODE
        |0|0|0|0|0000
        """
        self.opcode = 0
        self.fin = True

        flags = self.headers.get('FLAGS')
        if flags:
            try:
                flags = int(flags, 16)
            except TypeError:
                raise TypeError("flag decode failed from headers {}".format(self.headers))

            self.fin = (flags & 0x80) == 0x80 # mask against 1000 0000 to make sure fin bit is set

            rsvd = flags & 0x70 # mask against 0111 0000 to make sure the bits are all 0
            if rsvd != 0:
                raise WebsocketError(CLOSE_PROTOCOL_ERROR, 'reserved bit was non-zero')

            self.opcode = flags & 0x0f # pull out opcode using 0000 1111

    def is_opcode(self, opcode):
        """return true if self.opcode contains opcode"""
        #return (self.opcode & opcode) != 0
        return self.opcode == opcode

    def is_text(self):
        """return true if text opcode is set"""
        return self.is_opcode(OP_TEXT)

    def is_binary(self):
        """return true if binary opcode received"""
        return self.is_opcode(OP_BINARY)

    def is_close(self):
        """return true if close opcode received"""
        return self.is_opcode(OP_CLOSE)

    def is_ping(self):
        """return true if ping opcode received"""
        return self.is_opcode(OP_PING)

    def is_pong(self):
        """return true if pong opcode received"""
        return self.is_opcode(OP_PONG)

    def is_handshake(self):
        """return true if we are in a websocket upgrade handshake"""
        return self.headers.get('METHOD') == 'WEBSOCKET_HANDSHAKE'

    def is_websocket(self):
        """return true if this is a websocket request"""
        return self.headers.get('METHOD') == 'WEBSOCKET'


class Connection(handler.Connection):
    """A replacement for m2's vanilla Connection class, use this one instead to make
    working with websockets easy-peasy"""
    def __init__(self, sub_addr, pub_addr):
        sender_id = uuid4().hex
        super(Connection, self).__init__(sender_id, sub_addr, pub_addr)
        self.aborted = {}

    def recv_frame(self):
        """
        this wraps frame handling to make it a little easier to deal with
        """
        ws_req = None

        while True:

            m2_req = self.recv()
            logger.info('{} RECEIVED'.format(m2_req.conn_id))

            try:
                ws_req = Request(m2_req)

                if ws_req.is_handshake() or ws_req.is_disconnect():
                    # drop these through so they can be handled
                    pass

                elif not ws_req.is_websocket():
                    self.reply_invalid(ws_req)
                    continue

                elif ws_req.is_close():
                    if self.is_closed(ws_req):
                        logger.info('{} CLOSE HANDSHAKE COMPLETE'.format(ws_req.conn_id))
                        # if the connection id is in aborted, then the close handshake is complete,
                        # we've sent down an OP_CLOSE and received one back
                        del self.aborted[ws_req.conn_id]
                        continue

                    else:
                        # we still want to return this request to give the controller a chance to do other cleanup
                        # even though we have done everything we needed to do to close the connection already
                        self.reply_to_close(ws_req)

                else:

                    if self.is_closed(ws_req):
                        logger.info('{} CLOSED, ignoring opcode {}'.format(ws_req.conn_id, ws_req.opcode))
                        continue

                    elif ws_req.is_ping():
                        self.reply_to_ping(ws_req)
                        continue

                    elif ws_req.is_pong():
                        logger.info('{} PONG'.format(ws_req.conn_id))
                        continue

                    else:
                        # check the remaining opcodes to make sure the opcode is supported
                        # this way code further down the line doesn't need to worry about
                        # invalid opcodes filtering up
                        if not ws_req.is_text() and not ws_req.is_binary():
                            logger.info('{} INVALID OPCODE {}'.format(ws_req.conn_id, ws_req.opcode))
                            raise WebsocketError(
                                CLOSE_PROTOCOL_ERROR,
                                'Unknown or unsupported opcode {}'.format(ws_req.opcode)
                            )

                break

            except Exception, e:
                self.abort(m2_req, e) # we use m2_req since the ws_req creation can fail
                continue

        return ws_req

    def reply_handshake(self, req):
        """reply correctly to a switching protocols request to upgrade to a websocket connection"""

        logger.info('{} WEBSOCKET HANDSHAKE'.format(req.conn_id))

        self.reply_http(
            req,
            body='',
            code=101,
            status='Switching Protocols',
            headers={
                "Upgrade": "websocket",
                "Connection": "Upgrade",
                "Sec-WebSocket-Accept": "{}".format(req.body),
            }
        )

    def reply_invalid(self, req):
        """reply to a non websocket request on a websocket connection"""
        logger.info('{} {} METHOD is Not WEBSOCKET: {}'.format(
            req.conn_id,
            req.headers.get('METHOD', 'UNKNOWN'),
            req.headers
        ))

        self.reply_http(
          req,
          body='',
          code=501,
          status='Not Implemented',
        )
        self.close(req)

    def reply_to_ping(self, req):
        """reply to a ping request with a pong request"""
        logger.info('{} PING -> replying PONG'.format(req.conn_id))
        self.reply_websocket(req, req.body, OP_PONG)

    def reply_to_close(self, req):
        """reply to a close request"""
        logger.info('{} CLIENT CLOSED'.format(req.conn_id))
        # the client has closed on us, we need to send down OP_CLOSE to complete the handshake
        self.reply_websocket(req, req.body, OP_CLOSE)

        self.close(req)

    def reply_to_websocket(self, req, to_conn_id, body, opcode):
        """
        send a reply to a connection

        this is different than reply_websocket() because it allows you to send the
        reply to a different websocket than the one that originally made the request
        """
        orig_conn_id = req.conn_id
        req.conn_id = to_conn_id
        logger.debug("{} -> {} reply_to websocket {}, OPCODE: {}".format(orig_conn_id, to_conn_id, body, opcode))
        self.reply_websocket(req, body, opcode)
        req.conn_id = orig_conn_id

    def forward_websocket(self, req, to_conn_id):
        """
        this just takes the websocket request and sends it to another connection

        this is handy for communication between 2 websockets, say if you were writing
        a chat application or something ;)
        """
        self.reply_to_websocket(req, to_conn_id, req.body, req.opcode)

    def abort(self, req, e=None):
        """
        abnormally close the connection

        this will save the connection and send the OP_CLOSE opcode to the client, if/when
        we get an OP_CLOSE from the client, we will delete the connection
        """
        if self.is_closed(req):
            logger.info('{} already aborted'.format(req.conn_id))
            return

        body = ''
        if e:
            if isinstance(e, WebsocketError):
                body = str(e)
            else:
                ews = WebsocketError(CLOSE_INTERNAL_SERVER_ERROR, str(e))
                body = str(ews)

            logger.info('{} ABORTED'.format(req.conn_id))
            logger.exception(e.message)

        else:
            ews = WebsocketError(CLOSE_NORMAL, 'Normal Abort')
            body = str(ews)

            logger.info('{} NORMAL ABORT'.format(req.conn_id))

        self.reply_websocket(req, body, opcode=OP_CLOSE)
        self.aborted[req.conn_id] = (e, req.sender)

    def is_closed(self, req):
        """return True if this connection has been closed previously"""
        return req.conn_id in self.aborted

