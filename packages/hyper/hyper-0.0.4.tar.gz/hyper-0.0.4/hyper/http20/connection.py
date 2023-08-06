# -*- coding: utf-8 -*-
"""
hyper/http20/connection
~~~~~~~~~~~~~~~~~~~~~~~

Objects that build hyper's connection-level HTTP/2.0 abstraction.
"""
from .hpack import Encoder, Decoder
from .stream import Stream
from .tls import wrap_socket
from .frame import (
    DataFrame, HeadersFrame, SettingsFrame, Frame, WindowUpdateFrame,
    GoAwayFrame
)
from .window import FlowControlManager

import logging
import socket

log = logging.getLogger(__name__)


class HTTP20Connection(object):
    """
    An object representing a single HTTP/2.0 connection to a server.

    This object behaves similarly to the Python standard library's
    HTTPConnection object, with a few critical differences.

    Most of the standard library's arguments to the constructor are irrelevant
    for HTTP/2.0 or not supported by hyper.

    :param host: The host to connect to. This may be an IP address or a
        hostname, and optionally may include a port: for example,
        ``'twitter.com'``, ``'twitter.com:443'`` or ``'127.0.0.1'``.
    :param port: (optional) The port to connect to. If not provided and one also
        isn't provided in the ``host`` parameter, defaults to 443.
    :param window_manager: (optional) The class to use to manage flow control
        windows. This needs to be a subclass of the
        :class:`BaseFlowControlManager <hyper.http20.window.BaseFlowControlManager>.
        If not provided,
        :class:`FlowControlManager <hyper.http20.window.FlowControlManager>`
        will be used.
    """
    def __init__(self, host, port=None, *, window_manager=None, **kwargs):
        """
        Creates an HTTP/2.0 connection to a specific server.
        """
        if port is None:
            try:
                self.host, self.port = host.split(':')
                self.port = int(self.port)
            except ValueError:
                self.host, self.port = host, 443
        else:
            self.host, self.port = host, port

        # Create the mutable state.
        self.__wm_class = window_manager or FlowControlManager
        self.__init_state()

        return

    def __init_state(self):
        """
        Initializes the 'mutable state' portions of the HTTP/2.0 connection
        object.

        This method exists to enable HTTP20Connection objects to be reused if
        they're closed, by resetting the connection object to its basic state
        whenever it ends up closed. Any situation that needs to recreate the
        connection can call this method and it will be done.

        This is one of the only methods in hyper that is truly private, as
        users should be strongly discouraged from messing about with connection
        objects themselves.
        """
        # Streams are stored in a dictionary keyed off their stream IDs. We
        # also save the most recent one for easy access without having to walk
        # the dictionary.
        self.streams = {}
        self.recent_stream = None
        self.next_stream_id = 1

        # Header encoding/decoding is at the connection scope, so we embed a
        # header encoder and a decoder. These get passed to child stream
        # objects.
        self.encoder = Encoder()
        self.decoder = Decoder()

        # Values for the settings used on an HTTP/2.0 connection.
        self._settings = {
            SettingsFrame.INITIAL_WINDOW_SIZE: 65535,
        }

        # The socket used to send data.
        self._sock = None

        # The inbound and outbound flow control windows.
        self._out_flow_control_window = 65535

        # Instantiate a window manager.
        self.window_manager = self.__wm_class(65535)

        return

    def request(self, method, url, body=None, headers={}):
        """
        This will send a request to the server using the HTTP request method
        ``method`` and the selector ``url``. If the ``body`` argument is
        present, it should be string or bytes object of data to send after the
        headers are finished. Strings are encoded as UTF-8. To use other
        encodings, pass a bytes object. The Content-Length header is set to the
        length of the body field.

        :returns: A stream ID for the request.
        :param method: The request method, e.g. ``'GET'``.
        :param url: The URL to contact, e.g. ``'/path/segment'``.
        :param body: (optional) The request body to send. Must be a bytestring
            or a file-like object.
        :param headers: (optional) The headers to send on the request.
        """
        stream_id = self.putrequest(method, url)

        for name, value in headers.items():
            self.putheader(name, value, stream_id)

        # Convert the body to bytes if needed.
        if isinstance(body, str):
            body = body.encode('utf-8')

        self.endheaders(message_body=body, final=True, stream_id=stream_id)

        return stream_id

    def getresponse(self, stream_id=None):
        """
        Should be called after a request is sent to get a response from the
        server. If sending multiple parallel requests, pass the stream ID of
        the request whose response you want. Returns a HTTPResponse instance.
        If you pass no stream_id, you will receive the oldest HTTPResponse
        still outstanding.

        :param stream_id: (optional) The stream ID of the request for which to
            get a response.
        :returns: A HTTP response object.
        """
        stream = (self.streams[stream_id] if stream_id is not None
                  else self.recent_stream)
        return stream.getresponse()

    def connect(self):
        """
        Connect to the server specified when the object was created. This is a
        no-op if we're already connected.

        :returns: Nothing.
        """
        if self._sock is None:
            sock = socket.create_connection((self.host, self.port), 5)
            sock = wrap_socket(sock, self.host)
            assert sock.selected_npn_protocol() == 'HTTP-draft-09/2.0'
            self._sock = sock

            # We need to send the connection header immediately on this
            # connection, followed by an initial settings frame.
            sock.send(b'PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n')
            f = SettingsFrame(0)
            f.settings[SettingsFrame.ENABLE_PUSH] = 0
            self._send_cb(f)

            # The server will also send an initial settings frame, so get it.
            self._recv_cb()

        return

    def close(self):
        """
        Close the connection to the server.

        :returns: Nothing.
        """
        # Todo: we should actually clean ourselves up if possible by sending
        # GoAway frames and closing all outstanding streams. For now this will
        # do.
        if self._sock is not None:
            self._sock.close()
            self.__init_state()

    def putrequest(self, method, selector, **kwargs):
        """
        This should be the first call for sending a given HTTP request to a
        server. It returns a stream ID for the given connection that should be
        passed to all subsequent request building calls.

        :param method: The request method, e.g. ``'GET'``.
        :param selector: The path selector.
        :returns: A stream ID for the request.
        """
        # Create a new stream.
        s = self._new_stream()

        # To this stream we need to immediately add a few headers that are
        # HTTP/2.0 specific. These are: ":method", ":scheme", ":authority" and
        # ":path". We can set all of these now.
        s.add_header(":method", method)
        s.add_header(":scheme", "https")  # We only support HTTPS at this time.
        s.add_header(":authority", self.host)
        s.add_header(":path", selector)

        # Save the stream.
        self.streams[s.stream_id] = s
        self.recent_stream = s

        return s.stream_id

    def putheader(self, header, argument, stream_id=None):
        """
        Sends an HTTP header to the server, with name ``header`` and value
        ``argument``.

        Unlike the httplib version of this function, this version does not
        actually send anything when called. Instead, it queues the headers up
        to be sent when you call ``endheaders``.

        :param header: The name of the header.
        :param argument: The value of the header.
        :param stream_id: (optional) The stream ID of the request to add the
            header to.
        :returns: Nothing.
        """
        stream = (self.streams[stream_id] if stream_id is not None
                  else self.recent_stream)

        stream.add_header(header, argument)

        return

    def endheaders(self, message_body=None, final=False, stream_id=None):
        """
        Sends the prepared headers to the server. If the ``message_body``
        argument is provided it will also be sent to the server as the body of
        the request, and the stream will immediately be closed. If the
        ``final`` argument is set to True, the stream will also immediately
        be closed: otherwise, the stream will be left open and subsequent calls
        to ``send()`` will be required.

        :param message_body: (optional) The body to send. May not be provided
            assuming that ``send()`` will be called.
        :param final: (optional) If the ``message_body`` parameter is provided,
            should be set to ``True`` if no further data will be provided via
            calls to ``send()``.
        :param stream_id: (optional) The stream ID of the request to finish
            sending the headers on.
        :returns: Nothing.
        """
        self.connect()

        stream = (self.streams[stream_id] if stream_id is not None
                  else self.recent_stream)

        # Close this if we've been told no more data is coming and we don't
        # have any to send.
        stream.open(final and message_body is None)

        # Send whatever data we have.
        if message_body is not None:
            stream.send_data(message_body, final)

        return

    def send(self, data, final=False, stream_id=None):
        """
        Sends some data to the server. This data will be sent immediately
        (excluding the normal HTTP/2.0 flow control rules). If this is the last
        data that will be sent as part of this request, the ``final`` argument
        should be set to ``True``. This will cause the stream to be closed.

        :param data: The data to send.
        :param final: (optional) Whether this is the last bit of data to be
            sent on this request.
        :param stream_id: (optional) The stream ID of the request to send the
            data on.
        :returns: Nothing.
        """
        stream = (self.streams[stream_id] if stream_id is not None
                  else self.recent_stream)

        stream.send_data(data, final)

        return

    def receive_frame(self, frame):
        """
        Handles receiving frames intended for the stream.
        """
        if isinstance(frame, WindowUpdateFrame):
            self._out_flow_control_window += frame.window_increment
        elif isinstance(frame, SettingsFrame):
            if 'ACK' not in frame.flags:
                self._update_settings(frame)

                # Need to return an ack.
                f = SettingsFrame(0)
                f.flags.add('ACK')
                self._send_cb(f)
        elif isinstance(frame, GoAwayFrame):
            # If we get GoAway with error code zero, we are doing a graceful
            # shutdown and all is well. Otherwise, throw an exception.
            self.close()

            if frame.error_code != 0:
                raise RuntimeError("Encountered error %d, extra data %s." % (frame.error_code, frame.additional_data))
        else:
            raise ValueError("Unexpected frame %s." % frame)

    def _update_settings(self, frame):
        """
        Handles the data sent by a settings frame.
        """
        if SettingsFrame.HEADER_TABLE_SIZE in frame.settings:
            new_size = frame.settings[SettingsFrame.HEADER_TABLE_SIZE]

            self._settings[SettingsFrame.HEADER_TABLE_SIZE] = new_size
            self.encoder.header_table_size = new_size

        if SettingsFrame.INITIAL_WINDOW_SIZE in frame.settings:
            newsize = frame.settings[SettingsFrame.INITIAL_WINDOW_SIZE]
            oldsize = self._settings[SettingsFrame.INITIAL_WINDOW_SIZE]
            delta = newsize - oldsize

            for stream in self.streams.values():
                stream._out_flow_control_window += delta

            # Update our own window manager's window size. If the delta is
            # negative this is treated specially: we adjust the window size,
            # and then call self._adjust_receive_window with a zero-sized frame.
            # This will potentially result in the emission of a WINDOWUPDATE
            # frame.
            self.window_manager.initial_window_size = newsize
            self.window_manager.window_size += delta
            if delta < 0:
                self._adjust_receive_window(0)

            self._settings[SettingsFrame.INITIAL_WINDOW_SIZE] = newsize

    def _new_stream(self):
        """
        Returns a new stream object for this connection.
        """
        window_size = self._settings[SettingsFrame.INITIAL_WINDOW_SIZE]
        s = Stream(
            self.next_stream_id, self._send_cb, self._recv_cb,
            self._close_stream, self.encoder, self.decoder,
            self.__wm_class(window_size)
        )
        self.next_stream_id += 2

        return s

    def _close_stream(self, stream_id):
        """
        Called by a stream when it would like to be 'closed'.
        """
        del self.streams[stream_id]

    def _send_cb(self, frame):
        """
        This is the callback used by streams to send data on the connection.

        It expects to receive a single frame, and then to serialize that frame
        and send it on the connection. It does so obeying the connection-level
        flow-control principles of HTTP/2.0.
        """
        # Maintain our outgoing flow-control window.
        if (isinstance(frame, DataFrame) and
            not isinstance(frame, HeadersFrame)):

            # If we don't have room in the flow control window, we need to look
            # for a Window Update frame.
            while self._out_flow_control_window < len(frame.data):
                self._recv_cb()

            self._out_flow_control_window -= len(frame.data)

        data = frame.serialize()

        log.info(
            "Sending frame %s on stream %d",
            frame.__class__.__name__,
            frame.stream_id
        )

        self._sock.send(data)

    def _adjust_receive_window(self, frame_len):
        """
        Adjusts the window size in response to receiving a DATA frame of length
        ``frame_len``. May send a WINDOWUPDATE frame if necessary.
        """
        increment = self.window_manager._handle_frame(frame_len)

        if increment:
            f = WindowUpdateFrame(0)
            f.window_increment = increment
            self._send_cb(f)

        return

    def _recv_cb(self):
        """
        This is the callback used by streams to read data from the connection.

        It expects to read a single frame, and then to deserialize that frame
        and pass it to the relevant stream. This is generally called by a
        stream, not by the connection itself, and it's likely that streams will
        read a frame that doesn't belong to them. That's ok: streams need to
        make a decision to spin around again.
        """
        # Begin by reading 8 bytes from the socket.
        header = self._sock.recv(8)

        # Parse the header.
        frame, length = Frame.parse_frame_header(header)

        # Read the remaining data from the socket.
        if length:
            data = self._sock.recv(length)
        else:
            data = b''

        frame.parse_body(data)

        log.info(
            "Received frame %s on stream %d",
            frame.__class__.__name__,
            frame.stream_id
        )

        # Maintain our flow control window. We do this by delegating to the
        # chosen WindowManager.
        if (isinstance(frame, DataFrame) and
            not isinstance(frame, HeadersFrame)):
            # Inform the WindowManager of how much data was received. If the
            # manager tells us to increment the window, do so.
            self._adjust_receive_window(len(frame.data))

        # Work out to whom this frame should go.
        if frame.stream_id != 0:
            self.streams[frame.stream_id].receive_frame(frame)
        else:
            self.receive_frame(frame)


    # The following two methods are the implementation of the context manager
    # protocol.
    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.close()
        return False  # Never swallow exceptions.
