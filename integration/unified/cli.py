"""One front door for language, tools, quantum tasks and verified learning."""
import argparse,json,sys
from pathlib import Path
from .common import ROOT
from .session import Session

def main():
    parser=argparse.ArgumentParser(description='BBY Q: one native entity; no Android build')
    parser.add_argument('--database',type=Path,default=ROOT/'build/unified/personal.sqlite')
    parser.add_argument('--readers',type=Path,default=ROOT/'integration/unified/release')
    commands=parser.add_subparsers(dest='command',required=True)
    commands.add_parser('init');commands.add_parser('status');commands.add_parser('history')
    turn=commands.add_parser('turn');turn.add_argument('--id',required=True);turn.add_argument('--payload',type=Path);turn.add_argument('text')
    args=parser.parse_args()
    try:
        with Session(args.database,args.readers) as session:
            if args.command=='turn':result=session.turn(args.id,args.text,json.loads(args.payload.read_text()) if args.payload else None)
            elif args.command=='history':result=session.history()
            else:result={'entity':'U01','components':['C1','VQC3','QRL3','QMemory','QChat100','E02'],'snapshot':session.snapshot(),'apk_built':False}
        print(json.dumps(result,ensure_ascii=False,indent=2))
        if isinstance(result,dict) and result.get('ok') is False:sys.exit(2)
    except (ValueError,RuntimeError) as error:
        print(json.dumps({'ok':False,'error':str(error)},ensure_ascii=False),file=sys.stderr);sys.exit(2)
