import socket
import select
import sys
import logging
import pdb

from wire import decode_varint, encode
from reader import BytesBuffer
from msg import Decoder, message_types, message_names

# hold the asyncronous state of a connection
# ie. we may not get enough bytes on one read to decode the message

logger = logging.getLogger(__name__)

class Connection():

    def __init__(self, fd, app):
        self.fd = fd
        self.app = app
        self.recBuf = BytesBuffer(bytearray())
        self.msgLength = 0
        self.decoder = Decoder(self.recBuf)
        self.inProgress = False  # are we in the middle of a message

    def recv(this):
        data = this.fd.recv(1024)
        if not data:  # what about len(data) == 0
            raise IOError("dead connection")
#        print("recv",list(data))
        this.recBuf.write(data)

    def send(self,buf):
        self.fd.send(buf)

# ABCI server responds to messges by calling methods on the app

class ABCIServer():

    def __init__(self, app, port=5410):
        self.app = app
        # map conn file descriptors to (app, reqBuf, resBuf, msgDecoder)
        self.appMap = {}

        self.port = port
        self.listen_backlog = 10

        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.setblocking(0)
        self.listener.bind(('', port))

        self.listener.listen(self.listen_backlog)

        self.shutdown = False

        self.read_list = [self.listener]
        self.write_list = []
        self.enc=[]

    def handle_new_connection(self, r):
        new_fd, new_addr = r.accept()
        new_fd.setblocking(1)  # non-blocking
        new_fd.settimeout(1)
        self.read_list.append(new_fd)
        self.write_list.append(new_fd)
        print('new connection to', new_addr)

        self.appMap[new_fd] = Connection(new_fd, self.app)

    def handle_conn_closed(self, r):
        self.read_list.remove(r)
        self.write_list.remove(r)
        r.close()
        print("connection closed")

    def handle_recv(self, r):
        #  app, recBuf, resBuf, conn
        conn = self.appMap[r]
        while True:
            try:
                # check if we need more data first
                if conn.inProgress:
                    if (conn.msgLength == 0 or conn.recBuf.size() < conn.msgLength):
                        conn.recv()
                else:
                    if conn.recBuf.size() == 0:
                        conn.recv()

                conn.inProgress = True

                # see if we have enough to get the message length
                if conn.msgLength == 0:
                    ll = conn.recBuf.peek()
                    if conn.recBuf.size() < 1 + ll:
                        # we don't have enough bytes to read the length yet
                        continue
                    conn.msgLength = decode_varint(conn.recBuf)

                # see if we have enough to decode the message
                if conn.recBuf.size() < conn.msgLength:
                    continue

                # now we can decode the message

#                pdb.set_trace()
                d = conn.decoder.decode(message_types,conn.msgLength)
                req_type = list(d)[0]
                req_args = d[req_type]
#                print("recv", req_args)
                req_type = message_names[req_type]

                # done decoding message
                conn.msgLength = 0
                conn.inProgress = False

                # send only after flush
                if req_type == "flush":
                    for enc in self.enc:
                        length = len(enc)
                        len_bytes = length.to_bytes((length.bit_length() + 7) // 8, 'big')
                        header = bytes([len(len_bytes)])+len_bytes
                        conn.send(header+enc)
                    # send flush
                    conn.send(bytes([1,2,26,0]))
                    self.enc=[]
                    return
                else:
                    req_f = getattr(conn.app, req_type)
                    res = req_f(req_args)
#                    print("send",res)
                    self.enc += (encode(res),)

            except IOError as e:
                print("IOError on reading from connection:", e)
                if isinstance(e,socket.timeout):
                    continue
                self.handle_conn_closed(r)
                return
            except Exception as e:
                logger.exception("error reading from connection")
                self.handle_conn_closed(r)
                return

    def main_loop(self):
        while not self.shutdown:
            r_list, w_list, _ = select.select(
                self.read_list, self.write_list, [], 2.5)

            for r in r_list:
                if (r == self.listener):
                    try:
                        self.handle_new_connection(r)
                        # undo adding to read list ...
                    except NameError as e:
                        print("Could not connect due to NameError:", e)
                    except TypeError as e:
                        print("Could not connect due to TypeError:", e)
                    except:
                        print("Could not connect due to unexpected error:", sys.exc_info()[0])
                else:
                    self.handle_recv(r)

    def handle_shutdown(self):
        for r in self.read_list:
            r.close()
        for w in self.write_list:
            try:
                w.close()
            except Exception as e:
                print(e)  # TODO: add logging
        self.shutdown = True
