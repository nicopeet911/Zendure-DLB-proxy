#!/usr/bin/env python3
"""Apply the Gast777 -> standalone DLB adapter to a future Gast777 flow export.
Usage: python apply_gast777_dlb_adapter.py input.json output.json
The script refuses to patch when the expected semantic handover point is absent.
"""
import json, copy, sys
LINK_IN='dlbstandalone100linkin'; LINK_CALL='dlbadapter100linkcall'
SPLITTER_JS='const batch=Array.isArray(msg.dlb_batch)?msg.dlb_batch:[];\nconst out=[null,null,null];\nbatch.forEach(m=>{\n    const i=Number(m.dlb_device_index||0)-1;\n    if(i>=0 && i<3) out[i]=m;\n});\nreturn out;'
ADAPTER_TAIL='// ============================================================================\n// DLB STANDALONE ADAPTER v1.0 — stable handover point\n// ============================================================================\n// Package Gast777\'s already calculated per-device messages into one transaction.\n// The standalone DLB approves inputLimit values before any Zendure HTTP write.\nif (msg1) msg1.dlb_device_index = 1;\nif (msg2) msg2.dlb_device_index = 2;\nif (msg3) msg3.dlb_device_index = 3;\nmsg.dlb_batch = [msg1, msg2, msg3].filter(Boolean);\nmsg.dlb_adapter_request = true;\nmsg.dlb_adapter_version = "20260701-NL-Gast777-DLB-Adapter-v1.0-TEST";\nreturn [null, msg, null, null, null, null, null];\n'

def patch(flow):
    flow=copy.deepcopy(flow); by={n.get('id'):n for n in flow if n.get('id')}
    posts=[n for n in flow if n.get('type')=='function' and n.get('name')=='POST Request handling']
    if len(posts)!=1: raise RuntimeError(f'Expected one POST Request handling node, found {len(posts)}')
    post=posts[0]; marker='// Return both messages (to the two HTTP request outputs)'; pos=post.get('func','').find(marker)
    if pos<0: raise RuntimeError('Compatible Gast777 final return marker not found; manual review required')
    if 'dlb_adapter_version' in post.get('func',''): raise RuntimeError('Flow already appears to contain the DLB adapter')
    post['func']=post['func'][:pos]+ADAPTER_TAIL
    old=copy.deepcopy(post.get('wires',[])); z=post['z']
    dash={i:next(n['id'] for n in flow if n.get('z')==z and n.get('type')=='function' and n.get('name')==f'Zendure {i} POST to dashboard') for i in (1,2,3)}
    rates=[]
    for idx in (4,5,6): rates.append(next((oid for oid in old[idx] if by.get(oid,{}).get('type')=='delay'),None))
    if not all(rates): raise RuntimeError('Could not identify original three POST rate-limit nodes')
    post['wires']=[old[0],[LINK_CALL],[],[],[],[],[]]
    flow.extend([
      {'id':'dlbadapter100comment','type':'comment','z':z,'name':'DLB STANDALONE ADAPTER v1.0 TEST — do not bypass','info':'','x':660,'y':1460,'wires':[]},
      {'id':LINK_CALL,'type':'link call','z':z,'name':'Call standalone DLB for approval','links':[LINK_IN],'linkType':'static','timeout':'30','x':700,'y':1510,'wires':[['dlbadapter100splitter']]},
      {'id':'dlbadapter100splitter','type':'function','z':z,'name':'DLB adapter — split approved batch','func':SPLITTER_JS,'outputs':3,'timeout':0,'noerr':0,'initialize':'','finalize':'','libs':[],'x':1000,'y':1510,'wires':[[dash[1],rates[0]],[dash[2],rates[1]],[dash[3],rates[2]]]}
    ])
    return flow

if __name__=='__main__':
    if len(sys.argv)!=3: raise SystemExit('Usage: python apply_gast777_dlb_adapter.py input.json output.json')
    src=json.load(open(sys.argv[1],encoding='utf-8')); out=patch(src)
    json.dump(out,open(sys.argv[2],'w',encoding='utf-8'),indent=2,ensure_ascii=False)
    print('Adapter applied:',sys.argv[2])
