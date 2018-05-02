
from evm.vm import vm_execute, Message
from evm import utils

import math
import pdb

GenesisParams = '\
pragma solidity ^0.4.21;\n\
\n\
import "./GenesisPermission.sol";\n\
\n\
contract GenesisParams {\n\
\n\
    mapping (bytes32 => uint160) parameters;\n\
\n\
    function GenesisParams() public {\n\
        parameters["param_set_permission_addr"] = 2;\n\
        parameters["check_tx_addr"] = 3;\n\
        parameters["deliver_tx_addr"] = 4;\n\
    }\n\
\n\
    function get_param(bytes32 name) public view returns(uint160) {\n\
        return parameters[name];\n\
    }\n\
\n\
    function set_param(bytes32 name, uint160 param, bytes proof) public {\n\
        uint160 address_num = parameters["param_set_permission_addr"];\n\
        GenesisPermission gp = GenesisPermission(address(address_num));\n\
        if(gp.CheckPermission(name,param,proof)) {\n\
            parameters[name] = param;\n\
        }\n\
    }\n\
}'

GenesisParamsBytes = bytes.fromhex('608060405234801561001057600080fd5b5060026000807f706172616d5f7365745f7065726d697373696f6e5f616464720000000000000060001916815260200190815260200160002060006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff16021790555060036000807f636865636b5f74785f616464720000000000000000000000000000000000000060001916815260200190815260200160002060006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff16021790555060046000807f64656c697665725f74785f61646472000000000000000000000000000000000060001916815260200190815260200160002060006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff1602179055506103e1806101826000396000f30060806040526004361061004c576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff168063045d4b7d1461005157806387f7bb64146100c2575b600080fd5b34801561005d57600080fd5b506100806004803603810190808035600019169060200190929190505050610159565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b3480156100ce57600080fd5b506101576004803603810190808035600019169060200190929190803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803590602001908201803590602001908080601f016020809104026020016040519081016040528093929190818152602001838380828437820191505050505050919291929050505061019d565b005b6000806000836000191660001916815260200190815260200160002060009054906101000a900473ffffffffffffffffffffffffffffffffffffffff169050919050565b6000806000807f706172616d5f7365745f7065726d697373696f6e5f616464720000000000000060001916815260200190815260200160002060009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1691508190508073ffffffffffffffffffffffffffffffffffffffff1663efbcfa8b8686866040518463ffffffff167c01000000000000000000000000000000000000000000000000000000000281526004018084600019166000191681526020018373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200180602001828103825283818151815260200191508051906020019080838360005b838110156102c65780820151818401526020810190506102ab565b50505050905090810190601f1680156102f35780820380516001836020036101000a031916815260200191505b50945050505050602060405180830381600087803b15801561031457600080fd5b505af1158015610328573d6000803e3d6000fd5b505050506040513d602081101561033e57600080fd5b8101908080519060200190929190505050156103ae5783600080876000191660001916815260200190815260200160002060006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff1602179055505b50505050505600a165627a7a72305820fee9bd6a50a6d4c6757f7f1382547a963131b1f7ac816a120c4a5df6ceee9ef60029')

GenesisPermission = '\
pragma solidity ^0.4.21;\n\
\n\
contract GenesisPermission {\n\
\n\
    function CheckPermission(bytes32 name, uint160 param, bytes proof) public pure returns(bool) {\n\
        return name>0 || param > 0 || proof.length>0;\n\
    }\n\
}'

GenesisCheckTx = '\
pragma solidity ^0.4.21;\n\
\n\
contract GenesisCheckTx {\n\
\n\
    function CheckTx(bytes _tx) public pure returns(bool) {\n\
        return _tx.length>0;\n\
    }\n\
}'

GenesisCheckTxBytes = bytes.fromhex('608060405234801561001057600080fd5b5060fb8061001f6000396000f300608060405260043610603f576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff168063d17c247d146044575b600080fd5b348015604f57600080fd5b5060a8600480360381019080803590602001908201803590602001908080601f016020809104026020016040519081016040528093929190818152602001838380828437820191505050505050919291929050505060c2565b604051808215151515815260200191505060405180910390f35b60008082511190509190505600a165627a7a72305820b3fe654b33c421c739352007c22da9056142e27078c00cf74d7b77a7b7b098f00029')

GenesisDeliverTx = '\
pragma solidity ^0.4.21;\n\
\n\
contract GenesisDeliverTx {\n\
\n\
    function DeliverTx(bytes32[] _tx) public pure returns(bytes32 from, bytes32 to, bytes32[] data) {\n\
        from = _tx[0];\n\
        to = _tx[1];\n\
        uint l = _tx.length;\n\
        data = new bytes32[](l-2);\n\
        for(uint i = 0; i < l-2; ++i) {\n\
            data[i] = _tx[i+2];\n\
        }\n\
    }\n\
}'

GenesisDeliverTxBytes = bytes.fromhex('608060405234801561001057600080fd5b50610269806100206000396000f300608060405260043610610041576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff168063f9a6b89514610046575b600080fd5b34801561005257600080fd5b506100b4600480360381019080803590602001908201803590602001908080602002602001604051908101604052809392919081815260200183836020028082843782019150505050505091929192908035906020019092919050505061015c565b60405180856bffffffffffffffffffffffff19166bffffffffffffffffffffffff19168152602001846bffffffffffffffffffffffff19166bffffffffffffffffffffffff1916815260200180602001838152602001828103825284818151815260200191508051906020019060200280838360005b8381101561014557808201518184015260208101905061012a565b505050509050019550505050505060405180910390f35b600080606060008086600081518110151561017357fe5b90602001906020020151945086600181518110151561018e57fe5b90602001906020020151935060408603915060028751036040519080825280602002602001820160405280156101d35781602001602082028038833980820191505090505b509250600090505b60028751038110156102335786600282018151811015156101f857fe5b90602001906020020151838281518110151561021057fe5b9060200190602002019060001916908160001916815250508060010190506101db565b50929591945092505600a165627a7a723058208fae37c2f52dbe28a47928b1a43196aa159da9c8ad9341de3770f684a4d3bee90029')

addr0 = bytes.fromhex('0000000000000000000000000000000000000000')
addr1 = bytes.fromhex('0000000000000000000000000000000000000001')
addr2 = bytes.fromhex('0000000000000000000000000000000000000002')
addr3 = bytes.fromhex('0000000000000000000000000000000000000003')
addr4 = bytes.fromhex('0000000000000000000000000000000000000004')
check_tx_addr_req = bytes.fromhex('045d4b7d636865636b5f74785f6164647200000000000000000000000000000000000000')
check_tx_call_prefix = bytes.fromhex('d17c247d0000000000000000000000000000000000000000000000000000000000000020')
deliver_tx_addr_req = bytes.fromhex('045d4b7d64656c697665725f74785f616464720000000000000000000000000000000000')
deliver_tx_call_prefix = bytes.fromhex('f9a6b8950000000000000000000000000000000000000000000000000000000000000040')

class Blockchain():

    def __init__(self):
        self.block_prevhash = 0
        self.block_coinbase = 0
        self.block_timestamp = 0
        self.block_number = 0
        self.block_difficulty = 0
        self.block_gas_limit = 0
        self.tx_origin = b'0' * 40
        self.tx_gasprice = 0

        self.storage = {}
        self.height = 1
        self.uncommited_tx_count = 0
        self.nonce = 5
        
        result,gas,memory = vm_execute(self,Message(addr0,addr1),GenesisParamsBytes)
        self.code = {addr1:bytes(memory)}
        result,gas,memory = vm_execute(self,Message(addr0,addr3),GenesisCheckTxBytes)
        self.code.update({addr3:bytes(memory)})
        result,gas,memory = vm_execute(self,Message(addr0,addr4),GenesisDeliverTxBytes)
        self.code.update({addr4:bytes(memory)})

    def __repr__(self):
        return str({"code":self.code,"storage":self.storage})
        
    def get_code(self, addr):
        print('\n**** get_code ****\n')
        return self.code.get(bytes.fromhex(addr),b'')
        
    def get_balance(self, addr):
        print('\n**** get_balance ****\n')
        return 0
        
    def set_balance(self, addr, balance):
        print('\n**** set_balance ****\n')
        return 0
        
    def set_storage_data(self, addr, key, value):
        print('\n**** set_storage_data ****')
        a=self.storage.get(addr,{})
        a.update({key:value})
        self.storage.update({addr:a})
        print(self.storage)
        print('**** set_storage_data ****\n')

    def get_storage_data(self, addr, key):
        print('\n**** get_storage_data ****')
        a=self.storage.get(addr,{})
        b=a.get(key,0)
        print(addr,key,b)
        print('**** get_storage_data ****\n')
        return b

    def log_storage(self, addr):
        print('\n**** log_storage ****\n')
        return 0

    def add_suicide(self, addr):
        print('\n**** add_suicide ****\n')
        return 0

    def add_refund(self, x):
        print('\n**** add_refund ****\n')
        return 0

    def log(self, addr, topics, data):
        print('\n**** log ****\n')
        return 0

    def create(self, msg):
        print('\n**** create ****\n')
        return 0, 0, 0

    def call(self, msg):
        print('\n**** call ****\n')
        return 0, 0, 0

    def sendmsg(self, msg):
        print('\n**** sendmsg ****\n')
        return 0, 0, 0

    def account_exists(self,addr):
        print('\n**** account_exists ****\n')
        return addr in self.code

    def msg(self, inmsg):
        print('\n**** msg ****\n')
        code = self.code.get(inmsg.code_address,None)
        return vm_execute(self,inmsg,code)

    def call_address(self, fromAddr, toAddr, data):
        code = self.code.get(toAddr,None)
        if(code != None):
            result,gas,memory = vm_execute(self,Message(fromAddr,toAddr,data=data),code)
        return memory
        
    def check_tx(self,data):
        result = self.call_address(addr0,addr1,check_tx_addr_req)
        checktxaddr = bytes(result[12:32])
        bdata = bytearray.fromhex(data.decode("utf-8"))
        call_data = check_tx_call_prefix+utils.encode_int32(len(bdata))+bdata
        result = self.call_address(addr0,checktxaddr,call_data)
        return utils.bytearray_to_int(result)

    def deliver_tx(self,data):
        # get deliver_tx address
        result = self.call_address(addr0,addr1,deliver_tx_addr_req)
        delivertxaddr = bytes(result[12:32])
        
        # call deliver_tx
        bdata = bytearray.fromhex(data.decode("utf-8"))
        call_data = deliver_tx_call_prefix+utils.encode_int32(len(bdata))+utils.encode_int32(math.ceil(len(bdata)/32))+bdata
        result = self.call_address(addr0,delivertxaddr,call_data)
        
        # get transaction data
        fromAddr = bytes(result[0:20])
        toAddr = bytes(result[32:52])
        length = utils.bytearray_to_int(result[96:128])
        codeData = bytes(result[160:160+length])
        
        # execute transaction
        if(toAddr==addr0):
            new_address = utils.int_to_addr(self.nonce)
            self.nonce += 1
            result,gas,memory = vm_execute(self,Message(fromAddr,new_address),codeData)
            self.code.update({new_address:bytes(memory)})
            result = new_address
        else:
            result = self.call_address(fromAddr,toAddr,call_data)
        self.uncommited_tx_count += 1
            
        return result
