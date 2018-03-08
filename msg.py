import math
import pdb

# map type_byte to message name
message_types = {
    2: "echo",
    3: None, #"flush"
    4: {
        1: bytearray # version
        }, #"info"
    5: "set_option",
    6: {
        1: {
            1: bytearray, # pub_key
            2: int # power
            }, # validator
        }, # "init_chain"
    7: {
        1: bytearray, # data
        2: bytearray, # path
        3: int, # height
        4: int # prove
        }, # query
    8: {
        1: bytearray, # hash
        2: {
            1: bytearray, #chain_id
            2: int, # height
            3: int, #time
            4: int, #num_txs
            5: {
                1: bytearray, # hash
                2: {
                    1: int, # total
                    2: bytearray # hash
                    } # parts
                }, # last_block_id
            6: bytearray, # last_commit_hash
            7: bytearray, # data_hash
            8: bytearray, # validators_hash
            9: bytearray, # app_hash
            }, # header
        3: int, # absent_validators
        4: {
            1: bytearray, # pub_key
            2: int # height
            } # byzantine_validators
        }, # begin_block
    9: {
        1: bytearray #tx
        }, # check_tx
    11: {
        1: int # height
        }, # end_block
    12: None, # commit
    19: {
        1: bytearray #tx
        } # deliver_tx
}

message_names = {
    2: "echo",
    3: "flush",
    4: "info",
    5: "set_option",
    6: "init_chain",
    7: "query",
    8: "begin_block",
    9: "check_tx",
    11: "end_block",
    12: "commit",
    19: "deliver_tx",
}
# return the decoded arguments of abci messages

class Decoder():

    def __init__(self, reader):
        self.reader = reader

    def decode_big_end(self):
        val = int(self.reader.read(1)[0])
        if val < 0x80:
            return val
        return (self.decode_big_end()<<7)+(val&0x7f)

    def decode_varint(self):
        val = self.decode_big_end()
# negative numbers representation is not clear. I saw tendermint sending size 123 as 123
#        if val > 0:
#            bits = int(math.log(val,2))+1
#            if (bits%7)==0:
#                val -= math.pow(2,bits)
        return val
            
    def decode(self,dec_dict,size):
        start = self.reader.count()
        ret_val = {}
        while self.reader.count()-start < size:
            typeByte = self.decode_varint()
            req_num = typeByte>>3
            type_num = typeByte & 0x07
            expected = dec_dict[req_num]
            if expected is None:
                zero = int(self.reader.read(1)[0])
                if zero != 0:
                    print("unexpected value when None")
                ret_val.update({req_num:None})
            elif expected == bytearray:
                length = self.decode_varint()
                ret_val.update({req_num:self.reader.read(length)})
            elif expected == int:
                val = self.decode_varint()
                ret_val.update({req_num:val})
            elif type(expected) == dict:
                length = self.decode_varint()
                ret_val.update({req_num:self.decode(expected,length)})
        return ret_val

