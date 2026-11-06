#!/usr/bin/env python3
"""Run the repaired native workspace from source; no APK is built."""
import argparse,json
from pathlib import Path
from workspace import Workspace

def main():
    p=argparse.ArgumentParser();p.add_argument('database',type=Path);p.add_argument('request_id');p.add_argument('text');p.add_argument('--readers',type=Path)
    args=p.parse_args()
    with Workspace(args.database,args.readers) as workspace:result=workspace.turn(args.request_id,args.text)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
