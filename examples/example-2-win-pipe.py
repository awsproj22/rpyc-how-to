#!/usr/bin/env python3
# example-2-win-pipe.py
#  derived from test_win32pipes.py

from rpyc.lib.compat import BYTES_LITERAL
from rpyc.core.stream import PipeStream, NamedPipeStream
import rpyc
import sys
import time
import logging


class Test_Pipes(object):
    def __init__(self):
        if sys.platform != "win32":
            raise RuntimeError("Rquires windows")

    def test_basic_io(self):
        p1, p2 = PipeStream.create_pair()
        p1.write(BYTES_LITERAL("hello"))
        assert p2.poll(0)
        assert p2.read(5) == BYTES_LITERAL("hello")
        assert not p2.poll(0)
        p2.write(BYTES_LITERAL("world"))
        assert p1.poll(0)
        assert p1.read(5) == BYTES_LITERAL("world")
        assert not p1.poll(0)
        p1.close()
        p2.close()

    def test_rpyc(self):
        p1, p2 = PipeStream.create_pair()
        client = rpyc.connect_stream(p1)
        server = rpyc.connect_stream(p2)
        server_thread = rpyc.spawn(server.serve_all)
        assert client.root.get_service_name() == "VOID"
        t = rpyc.BgServingThread(client)
        assert server.root.get_service_name() == "VOID"
        t.stop()
        client.close()
        server.close()
        server_thread.join()


class Test_NamedPipe(object):
    def __init__(self):
        if sys.platform != "win32":
            raise RuntimeError("Rquires windows")

    def setUp(self):
        self.pipe_server_thread = rpyc.spawn(self.pipe_server)
        time.sleep(1)  # make sure server is accepting already
        self.np_client = NamedPipeStream.create_client("floop")
        self.client = rpyc.connect_stream(self.np_client)

    def tearDown(self):
        self.client.close()
        self.server.close()
        self.pipe_server_thread.join()

    def pipe_server(self):
        self.np_server = NamedPipeStream.create_server("floop")
        self.server = rpyc.connect_stream(self.np_server)
        self.server.serve_all()

    def test_rpyc(self):
        assert self.client.root.get_service_name() == "VOID"
        t = rpyc.BgServingThread(self.client)
        assert self.server.root.get_service_name() == "VOID"
        t.stop()


if __name__ == "__main__":
    test_step = "init"
    try:
        test_step = "test1 create"
        test1 = Test_Pipes()
        test_step = "test1 basic_io"
        test1.test_basic_io()
        test_step = "test1 rpyc"
        test1.test_rpyc()
        test1 = None

        test_step = "test2 create"
        test2 = Test_NamedPipe()
        test_step = "test2 setUp"
        test2.setUp()
        test_step = "test2 rpyc"
        test2.test_rpyc()
        test_step = "test2 tearDown"
        test2.tearDown()
        test2 = None

        print(" all passed ")

    except Exception as e:
        print("Exception: ")
        print("    test step: ", test_step)
        print("    exception: ", repr(e))
        logging.exception(" user exception log ")
        pass

'''
python 3.9.5 win10
    Package    Version Location
    ---------- ------- -----------------------------------------
    pip        21.1.1
    plumbum    1.6.9
    pywin32    300
    rpyc       4.1.5   \rpyc
    setuptools 56.0.0
pywin32==300: 
  File "example-2-win-pipe.py", line 64, in pipe_server
    self.server.serve_all()
  File "\rpyc\core\protocol.py", line 408, in serve_all
    self.serve(None)
  File "\rpyc\core\protocol.py", line 382, in serve
    data = self._channel.poll(timeout) and self._channel.recv()
  File "\rpyc\core\channel.py", line 57, in recv
    data = self.stream.read(length + len(self.FLUSHER))[:-len(self.FLUSHER)]
  File "\rpyc\core\stream.py", line 588, in read
    self.close()
  File "\rpyc\core\stream.py", line 558, in close
    win32file.FlushFileBuffers(self.outgoing)
pywin32==306: 
  all passed
'''


