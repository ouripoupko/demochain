import urllib.parse
import requests
import codecs
import pprint
import pdb

def commit(address,data=None,function=None,prms=None):
    d={'address':address}
    if data is not None:
        d.update({'data':data})
    if function is not None:
        d.update({'function':function, 'params':prms})
    s=urllib.parse.quote(str(d),safe='').replace("%22","%27")
    addr='http://localhost:46657/broadcast_tx_commit?tx="'+s+'"'
    r=requests.get(addr)
    print(r.text)

def query():
    r=requests.get('http://localhost:46657/abci_query?data="abcd"')
    pprint.pprint(eval(codecs.decode(r.json()['result']['response']['value'],'hex_codec').decode()))

if __name__ == '__main__':
    community = ('def init_community(params,state):\\n'+
                 ' return True,[]\\n'+
                 'def get_community(params,state):\\n'+
                 ' return state,state\\n'+
                 'def register_to_community(params,state):\\n'+
                 ' persona = params[0]\\n'+
                 ' state.append(persona)\\n'+
                 ' return True,state')
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
#    pdb.set_trace()
    query()
    print(community)
    commit('community',community,'init_community','[]')
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
