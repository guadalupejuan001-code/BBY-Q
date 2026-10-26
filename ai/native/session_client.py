#!/usr/bin/env python3
"""Framed byte transport and display only; the native XI program answers."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time


def decode_result(raw):
    result=[]
    for row in raw.splitlines():
        if not row.startswith('{'):continue
        item=json.loads(row)
        if item.get('register') in ('r14','r9'):result.append(item['value'])
    return bytes(result).decode('utf-8')


class Session:
    def __init__(self,binary,state,program):
        self.stderr=tempfile.TemporaryFile()
        self.process=subprocess.Popen([str(binary),str(state),str(program)],stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE,stderr=self.stderr)
        self.usage=None

    def request(self,text,language=1):
        data=text.encode('utf-8') if isinstance(text,str) else text
        if len(data)>255 or language not in (1,2):raise ValueError('invalid transport frame')
        started=time.perf_counter_ns()
        self.process.stdin.write(f'{language} {len(data)}\n'.encode()+data)
        self.process.stdin.flush()
        header=self.process.stdout.readline().decode().strip().split()
        if len(header)!=2:
            self.stderr.seek(0);raise RuntimeError(self.stderr.read().decode())
        length=int(header[1]);assert 0<=length<=16*1024*1024
        payload=self.process.stdout.read(length)
        if len(payload)!=length:raise RuntimeError('truncated response')
        elapsed=(time.perf_counter_ns()-started)/1e6
        if header[0]!='OK':raise RuntimeError(payload.decode())
        return payload.decode(),elapsed

    def rss_kib(self):
        try:
            rows=Path(f'/proc/{self.process.pid}/status').read_text().splitlines()
            return int(next(x for x in rows if x.startswith('VmRSS:')).split()[1])
        except (OSError,StopIteration):return None

    def metrics(self):
        self.process.stdin.write(b'METRICS\n');self.process.stdin.flush()
        header=self.process.stdout.readline().decode().strip().split()
        if len(header)!=2 or header[0]!='OK':raise RuntimeError('invalid metrics response')
        length=int(header[1]);assert 0<=length<=4096
        return json.loads(self.process.stdout.read(length))

    def close(self):
        if self.usage is not None:return self.process.returncode
        self.process.stdin.close()
        _,status,self.usage=os.wait4(self.process.pid,0)
        self.process.returncode=os.waitstatus_to_exitcode(status)
        self.process.stdout.close();self.stderr.close()
        return self.process.returncode

    def __enter__(self):return self
    def __exit__(self,*_):self.close()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('binary');parser.add_argument('state');parser.add_argument('--language',choices=['es','en'],default='es')
    parser.add_argument('--compact',action='store_true',help='Keep the original compact answer protocol')
    args=parser.parse_args();root=Path(__file__).resolve().parents[1]/'xi/knowledge'
    with tempfile.TemporaryDirectory(prefix='bbyq-session-') as temp:
        program=Path(temp)/'combined.xi'
        program.write_bytes(subprocess.check_output(['bash',str(root/'link.sh'),'combined' if args.compact else 'conversation']))
        with Session(Path(args.binary).resolve(),Path(args.state).resolve(),program) as session:
            for line in sys.stdin:
                raw,_=session.request(line.rstrip('\n'),1 if args.language=='es' else 2)
                print(decode_result(raw),flush=True)


if __name__=='__main__':main()
