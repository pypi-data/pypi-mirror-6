#coding=utf8
__author__ = 'Alexander.Li'
import logging
import socket
import time
import tornado.ioloop
import tornado.iostream
from tornado.iostream import StreamClosedError
from TorCast import STATUS_REPLY,INTEGER_REPLY,BULK_REPLY,MULTI_BULK_REPLY

def tob(s, enc='utf8'):
    return s.encode(enc) if isinstance(s, unicode) else bytes(s)

class Connection(object):
    def __init__(self, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        stream = tornado.iostream.IOStream(sock)
        stream.connect((host, port))
        self.stream = stream
        self.channels = []
        self.when_data = None
        self.processor = None

    def subscribe(self, *channels):
        for chn in channels:
            if chn not in self.channels:
                self.channels.append(chn)


    def regist_trigger(self, on_data):
        self.when_data = on_data


    def write(self, command):
        self.stream.write(command)

    def recive(self):
        self.processor = ReplyProcessor(self.stream, self.when_data)


class ReplyProcessor(object):
    def __init__(self, stream, callback):
        self.stream = stream
        self.callback = callback
        self.wait_header()
        self.multi_bulk = False
        self.multi_bulk_count = -1
        self.multi_bulk_cache = []

    def wait_bytes(self, byte_count):
        if not self.multi_bulk and byte_count<0:
            self.callback(BULK_REPLY, None)
            self.wait_header()
            return
        self.stream.read_bytes(byte_count+2, self.on_bulk)

    def on_bulk(self, data):
        data = data[:-2]
        if not self.multi_bulk:
            self.callback(BULK_REPLY, data)
        else:
            self.multi_bulk_cache.append(data)
            if len(self.multi_bulk_cache)==self.multi_bulk_count:
                self.callback(MULTI_BULK_REPLY, self.multi_bulk_cache)
                self.multi_bulk = False
                self.multi_bulk_count = -1
        self.wait_header()

    def wait_header(self):
        self.stream.read_until("\r\n", self.on_header)

    def on_header(self, data):
        logging.error("%s" % data)
        data = data[:-2]
        if data[0] in ["+", "-"]:
            self.callback(STATUS_REPLY, data[1:])
            self.wait_header()
        if data[0]==":":
            self.callback(INTEGER_REPLY, int(data[1:]))
            self.wait_header()
        if data[0]=="$":
            self.wait_bytes(int(data[1:]))
        if data[0]=="*":
            if data[1:3] == "-1":
                self.callback(MULTI_BULK_REPLY, [])
                self.wait_header()
                return
            self.multi_bulk = True
            self.multi_bulk_count = int(data[1:])
            del self.multi_bulk_cache[:]
            self.wait_header()


def parse_command(*argv):
    output = [["*", str(len(argv)), "\r\n"]] + [["$", str(len(p)), "\r\n", p, "\r\n"] for p in map(str, argv)]
    return "".join(reduce(lambda i1, i2: i1+i2, output))



class Blocker(object):
    def __init__(self, host, port, db):
        self.conn = None
        self.conn_params = (host, port, db)
        self.callbacks = {}
        self.state_ok = False
        self.reconnect(*self.conn_params)


    def reconnect(self, host, port, db):
        def on_line(type, data):
            self.on_data(type, data)
        self.conn = Connection(host, port)
        self.conn.regist_trigger(on_line)
        self.conn.write(parse_command("SELECT", str(db)))
        self.state_ok = True
        self.conn.recive()


    def on_data(self, chunk_type, data):
        logging.error(u"type:%s data:%s" % (chunk_type, data))
        if chunk_type == MULTI_BULK_REPLY and data and data[0] in self.callbacks:
            key = data[0]
            callback, timeout = self.callbacks[key]
            callback(data[1])
            del self.callbacks[key]

    def _send_block(self, key, callback, timeout):
        try:
            self.conn.write(parse_command("blpop", key, timeout))
        except Exception, e:
            logging.error(str(e))
            self.reconnect(*self.conn_params)
            callback({})
            del self.callbacks[key]


    def blpop(self, key, callback, timeout=1800):
        if key in self.callbacks:
            last_callback, last_update = self.callbacks
            self.callbacks[key] = (callback, time.time())
            if time.time()-last_update >= timeout:
                self._send_block(key, callback, timeout)
                return
            else:
                return
        else:
            self.callbacks[key] = (callback, time.time())
            self._send_block(key, callback, timeout)


class Subscriber(object):
    def __init__(self, host, port, db):
        self.conn = None
        self.send_conn = None
        self.conn_params = (host,port,db)
        self.data_pool = []
        self.param_len = -1
        self.callback = None
        self.channels = None
        self.state_ok = False
        self.reconnect(*self.conn_params)

    def listen_on(self, channels, callback):
        self.conn.write(parse_command("subscribe", *channels))
        self.callback = callback
        self.channels = channels

    def reconnect(self, host, port, db):
        def on_line(type, data):
            self.on_data(type, data)
        def silent(type, data):
            pass
        self.conn = Connection(host, port)
        self.conn.regist_trigger(on_line)
        self.conn.write(parse_command("SELECT", str(db)))
        self.conn.recive()
        self.send_conn = Connection(host, port)
        self.send_conn.regist_trigger(silent)
        self.send_conn.write(parse_command("SELECT", str(db)))
        self.send_conn.recive()
        self.state_ok = True


    def on_data(self, chunk_type, data):
        if chunk_type == MULTI_BULK_REPLY and data[0] == "message":
            self.callback(data[1], data[2])


    def check_connection(self):
        if not self.state_ok:
            self.reconnect(*self.conn_params)
            self.conn.write(parse_command("subscribe", *self.channels))


    def notify_all(self, channel, message):
        if channel not in self.channels:
            return False
        try:
            self.send_conn.write(parse_command("publish", channel, tob(message)))
        except StreamClosedError, e:
            logging.error(e.message)
            self.state_ok = False
            return False
        return True
