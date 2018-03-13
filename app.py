import sys
import pdb

from wire import hex2bytes, decode_big_endian, encode_big_endian
from server import ABCIServer
from reader import BytesBuffer

blockchain = {
    'height': 1,
    'uncommited_tx_count': 0,
    'block_0_trans_1_blockchain_parameters': {
        'data': 'def strcode_get_param(params,state):\n key = params[0]\n return state.get(key,None),state\n' +
              'def strcode_set_param(params,state):\n'+
              ' key,val,proof = params\n'+
              ' result = call_address(state.get("param_set_permission_addr",None),'+
                  '"strcode_pset_permission",[proof,])\n'+
              ' if result:\n'+
              '  state.update({key:val})\n'+
              ' return None,state',
        'memory': {'param_set_permission_addr': 'block_0_trans_2_pset_permission',
                   'check_tx_addr': 'block_0_trans_3_check_tx',
                   'deliver_tx_addr': 'block_0_trans_4_deliver_tx'}},
    'block_0_trans_2_pset_permission': {
        'data': 'def strcode_pset_permission(params,state):\n proof = params[0]\n print("genesis pset_permission called: ",proof)\n return True,["None",]',
        'memory': ['None',]},
    'block_0_trans_3_check_tx': {
        'data': 'def strcode_check_tx(params,state):\n tx = params[0]\n print("genesis check_tx called: ",tx)\n return True,["None",]',
        'memory': ['None',]},
    'block_0_trans_4_deliver_tx': {
        'data': 'def strcode_deliver_tx(params,state):\n'+
                ' tx = eval(params[0].decode("utf-8"))\n'+
                ' print("genesis deliver_tx called: ",tx)\n'+
                ' address=tx.get("address",None)\n'+
                ' data=tx.get("data",None)\n'+
                ' if data is not None:\n'+
                '  address = deploy_address(address,data)\n'+
                ' function=tx.get("function",None)\n'+
                ' params=tx.get("params",None)\n'+
                ' if function is not None:\n'+
                '  call_address(address,function,params)\n'+
                ' return True,["None",]',
        'memory': ['None',]}}

def deploy_address(address,data):
    full_addr = 'block_'+str(blockchain['height'])+'_trans_'+str(blockchain['uncommited_tx_count'])+'_'+address
    blockchain.update({full_addr:{'data':data,'memory':['None',]}})
    blockchain['uncommited_tx_count'] += 1
    return full_addr

def call_address(address,function,params):
    function_dict = blockchain.get(address,None)
    function_def = function_dict.get('data',None)
    function_state = function_dict.get('memory',None)
    exec(function_def)
    result,new_state = eval(function+'('+str(params)+','+str(function_state)+')')
    function_dict.update({'memory': new_state})
    blockchain.update({address: function_dict})
    return result

class CounterApplication():

    def echo(self, msg):
        return msg, 0

    def info(self,data):
        return {4:{1:bytearray([123,34,115,105,122,101,34,58,48,125])}}

    def query(self,data):
        value = bytearray(str(blockchain),"utf-8")
        return {7:{4:value,5:bytearray('trust me'.encode("utf8"))}}
        
    def init_chain(self,data):
        return {6:None}

    def begin_block(self,data):
        return {8:None}
        
    def end_block(self,data):
        return {11:None}

    def commit(self,data):
        if blockchain['uncommited_tx_count']>0:
            blockchain['height'] += 1
            blockchain['uncommited_tx_count'] = 0
        return {12:{2:(bytearray(20)+encode_big_endian(blockchain['height']))[-20:]}}

    def deliver_tx(self,data):
        addr = call_address('block_0_trans_1_blockchain_parameters',
            'strcode_get_param',["deliver_tx_addr",])
        result = call_address(addr,'strcode_deliver_tx',[data[1],])
        print("deliver_tx returns ",result)
        return {10:None}

    def check_tx(self,data):
        checktxaddr = call_address('block_0_trans_1_blockchain_parameters',
            'strcode_get_param',["check_tx_addr",])
        result = call_address(checktxaddr,'strcode_check_tx',[data[1],])
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
