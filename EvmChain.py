import sys
from state import Blockchain
import pdb

from wire import encode_big_endian
from server import ABCIServer

class CounterApplication():

    def __init__(self):
        self.blockchain = Blockchain()
        
    def echo(self, msg):
        return msg, 0

    def info(self,data):
        return {4:{1:bytearray([123,34,115,105,122,101,34,58,48,125])}}

    def query(self,data):
        value = bytearray(repr(self.blockchain),"utf-8")
        return {7:{4:value,5:bytearray('trust me'.encode("utf8"))}}
        
    def init_chain(self,data):
        return {6:None}

    def begin_block(self,data):
        return {8:None}
        
    def end_block(self,data):
        return {11:None}

    def commit(self,data):
        if self.blockchain.uncommited_tx_count>0:
            self.blockchain.height += 1
            self.blockchain.uncommited_tx_count = 0
        return {12:{2:(bytearray(20)+encode_big_endian(self.blockchain.height))[-20:]}}

    def deliver_tx(self,data):
        result = self.blockchain.deliver_tx(data[1])
        print("deliver_tx returns ",result)
        return {10:None}

    def check_tx(self,data):
        result = self.blockchain.check_tx(data[1])
        print("check_tx returns ",result)
        return {9:None}


if __name__ == '__main__':
    l = len(sys.argv)
    if l == 1:
        port = 46658
    elif l == 2:
        port = int(sys.argv[1])
    else:
        print("too many arguments")
        quit()

    print('ABCI Demo APP (Python)')

    app = CounterApplication()
    server = ABCIServer(app, port)
    server.main_loop()
