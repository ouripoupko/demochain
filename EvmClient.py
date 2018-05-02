import urllib.parse
import requests
import codecs
import pdb

def commit(fromAddr,toAddr,data):
    padding = "000000000000000000000000"
    addr='http://localhost:46657/broadcast_tx_commit?tx="'+fromAddr+padding+toAddr+padding+data+'"'
    r=requests.get(addr)
    print(r.text)

def nice_print(v,pad):
    if type(v)==dict:
        for key, val in v.items():
            nice_print(key,pad)
            nice_print(val,pad+' ')
    elif type(v)==bytes:
        print(pad,v[:100].hex())
    elif type(v)==bytearray:
        print(pad,v[:100].hex())
    else:
        print(pad,v)

def query():
    r=requests.get('http://localhost:46657/abci_query?data="abcd"')
    nice_print(eval(codecs.decode(r.json()['result']['response']['value'],'hex_codec').decode()),'')

if __name__ == '__main__':
    community = '\
pragma solidity ^0.4.21;\n\
\n\
contract Community {\n\
\n\
    address[] persona_list;\n\
    \n\
    function get_community() public view returns(address[]) {\n\
        return persona_list;\n\
    }\n\
\n\
    function register_to_community(address persona) public {\n\
        persona_list.push(persona);\n\
    }\n\
}'
    community_str = '608060405234801561001057600080fd5b50610223806100206000396000f30060806040526004361061004c576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff1680633bf47e8614610051578063b4bb3a3d146100bd575b600080fd5b34801561005d57600080fd5b50610066610100565b6040518080602001828103825283818151815260200191508051906020019060200280838360005b838110156100a957808201518184015260208101905061008e565b505050509050019250505060405180910390f35b3480156100c957600080fd5b506100fe600480360381019080803573ffffffffffffffffffffffffffffffffffffffff16906020019092919050505061018e565b005b6060600080548060200260200160405190810160405280929190818152602001828054801561018457602002820191906000526020600020905b8160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001906001019080831161013a575b5050505050905090565b60008190806001815401808255809150509060018203906000526020600020016000909192909190916101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff16021790555050505600a165627a7a72305820bb9c4f06c8dc95c6b43906f2b4b23d3a217be029ce1097c6e43dde3ea3c100eb0029'

    persona = ('def register_persona(params,state):\\n'+
               ' call_address(\\"block_1_trans_0_community\\",\\"register_to_community\\",params)\\n'+
               ' return True,params\\n'+
               'def sign_tx(params,state):\\n'+
               ' signature = params[0]+params[1]+state[0]\\n'+
               ' return signature,state')
    voting = ('def voting_init(params,state):\\n'+
              ' return True,{}\\n'+
              'def strcode_pset_permission(params,state):\\n'+
              ' print(\\"strcode_pset_permission\\")\\n'+
              ' key,val,proof = params\\n'+
              ' data = key+val\\n'+
              ' community = call_address(\\"block_1_trans_0_community\\",\\"get_community\\",[None,])\\n'+
              ' counter = 0\\n'+
              ' print(\\"before if\\")\\n'+
              ' if isinstance(proof,dict):\\n'+
              '  print(\\"is dict\\")\\n'+
              '  for key in community:\\n'+
              '   print(\\"key:\\",key)\\n'+
              '   val = proof.get(key,None)\\n'+
              '   if val is not None:\\n'+
              '    print(\\"val: \\",val)\\n'+
              '    if val == data+key:\\n'+
              '     print(\\"data:\\",data)\\n'+
              '     counter += 1\\n'+
              ' thresh = len(community)//2\\n'+
              ' return counter>thresh,state\\n'+
              'def vote_block0_change(params,state):\\n'+
              ' key,val,persona = params\\n'+
              ' signature = call_address(persona,\\"sign_tx\\",[key,val])\\n'+
              ' if signature is not None:\\n'+
              '  stored = state.get(key+val,{})\\n'+
              '  stored.update({persona:signature})\\n'+
              '  state.update({key+val:stored})\\n'+
              ' return None,state\\n'+
              'def commit_block0_change(params,state):\\n'+
              ' print(\\"commit_block0_change\\")\\n'+
              ' sigs = state.get(params[0]+params[1],None)\\n'+
              ' if sigs is not None:\\n'+
              '  call_address(\\"block_0_trans_1_blockchain_parameters\\",\\"strcode_set_param\\",(params[0],params[1],sigs))\\n'+
              ' return True,state')
    pdb.set_trace()
    query()
    print(community)
    commit(b'community_owner_addr'.hex(),'0000000000000000000000000000000000000000',community_str)
    query()
    print(persona)
    commit('persona_Udi',persona)
    commit('block_2_trans_0_persona_Udi',None,'register_persona','[\\"block_2_trans_0_persona_Udi\\"]')
    commit('persona_Ouri',persona)
    commit('block_3_trans_0_persona_Ouri',None,'register_persona','[\\"block_3_trans_0_persona_Ouri\\"]')
    commit('persona_Nimrod',persona)
    commit('block_4_trans_0_persona_Nimrod',None,'register_persona','[\\"block_4_trans_0_persona_Nimrod\\"]')
    query()
    print(voting)
    commit('voting',voting,'voting_init','None')
    query()
    commit('block_0_trans_1_blockchain_parameters',None,'strcode_set_param','(\\"param_set_permission_addr\\",\\"block_5_trans_0_voting\\",\\"Trust me!\\")')
    query()
    commit('block_0_trans_1_blockchain_parameters',None,'strcode_set_param','(\\"some_new_parameter\\",\\"some_new_value\\",\\"Trust me!\\")')
    query()
    commit('block_5_trans_0_voting',None,'vote_block0_change','[\\"some_new_parameter\\",\\"some_new_value\\",\\"block_2_trans_0_persona_Udi\\"]')
    commit('block_5_trans_0_voting',None,'vote_block0_change','[\\"some_new_parameter\\",\\"some_new_value\\",\\"block_3_trans_0_persona_Ouri\\"]')
    query()
    commit('block_5_trans_0_voting',None,'commit_block0_change','[\\"some_new_parameter\\",\\"some_new_value\\"]')
    query()
