#!/usr/bin/env python3
# example-3-win-pipe-service.py
#  derived example-2-win-pipe.py

from rpyc.lib.compat import BYTES_LITERAL
from rpyc.core.stream import PipeStream, NamedPipeStream
import rpyc
import sys
import time
import logging


class EchoService(rpyc.Service):
    def on_connect(self, conn):
        pass

    def on_disconnect(self, conn):
        pass

    def exposed_echo(self, message):
        if message == "Echo":
            return "Echo Reply"
        else:
            return "Parameter Problem"


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
        self.server = rpyc.connect_stream(self.np_server, service=EchoService)
        self.server.serve_all()

    def test_rpyc(self):
        # check server service name from the client
        svr_svc_name = self.client.root.get_service_name()
        assert svr_svc_name == "ECHO"

        # check client service name from the server
        t = rpyc.BgServingThread(self.client)
        clnt_svc_name = self.server.root.get_service_name()
        assert clnt_svc_name == "VOID"

        # send "Echo" from client to server and get the return to check
        snd_msg = "Echo"
        ret_msg = self.client.root.echo(snd_msg)
        assert ret_msg == snd_msg + " Reply"

        # send not an "Echo" and check returned value
        snd_msg = "abcdefggg"
        ret_msg = self.client.root.echo(snd_msg)
        assert ret_msg != snd_msg

        # stop client service thread
        t.stop()


if __name__ == "__main__":
    test_step = "init"
    try:
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


