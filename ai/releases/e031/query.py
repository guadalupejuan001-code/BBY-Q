#!/usr/bin/env python3
"""Transport only: XI requests a page; copy that entire byte page unchanged."""
import argparse,json,struct,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('runtime');p.add_argument('bundle');p.add_argument('state');p.add_argument('language',choices=['es','en']);p.add_argument('word');a=p.parse_args()
runtime=str(Path(a.runtime).resolve());root=Path(a.bundle).resolve();state=Path(a.state).resolve()
U=7400000000000000000;B=8700000000000000000
prep=Path('ai/releases/e031/request.xi').read_text();q=('@lex '+a.word).encode();assert len(q)<=255
def run(code):
 f=state.with_suffix('.transport.xi');f.write_text(code)
 return subprocess.check_output([runtime,'run',str(f),str(state),str(state)],text=True)
fields=[(U+16,1),(U+17,len(q)),(U+3,1 if a.language=='es' else 2)]+[(U+128+i,v) for i,v in enumerate(q)]
raw=run('#!reverse-pc-machine-v1\n'+''.join('store8 %d %d\n'%x for x in fields)+prep.split('\n',1)[1])
key=[json.loads(x)['value'] for x in raw.splitlines() if x.startswith('{')][-1]
page=root/'banks'/(str(key)+'.bin');data=page.read_bytes() if page.exists() else b''
# Native metadata gives the old byte length; host does not examine dictionary entries.
raw=run('#!reverse-pc-machine-v1\nload8 r0 %d\nprint r0\nload8 r0 %d\nprint r0\nload8 r0 %d\nprint r0\nhalt\n'%(B+16,B+17,B+18))
vals=[json.loads(x)['value'] for x in raw.splitlines() if x.startswith('{')];last=sum(v<<(8*i) for i,v in enumerate(vals))
code='#!reverse-pc-machine-v1\nset r0 0\nlabel clear\ncmp r0 %d\njge copy\nset r7 %d\nadd r7 r0\nstore8 $r7 0\nadd r0 1\njmp clear\nlabel copy\n'%(last,B+1024)
fields=[(B+1024+i,v) for i,v in enumerate(data)]+[(B+16+i,(len(data)>>(8*i))&255) for i in range(3)]+[(B+8+i,(key>>(8*i))&255) for i in range(3)]
run(code+''.join('store8 %d %d\n'%x for x in fields)+'halt\n')
print(subprocess.check_output([runtime,'app-turn',str(root/'dictionary.rxe'),str(state),str(state),a.language,q.decode()],text=True),end='')
