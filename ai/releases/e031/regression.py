#!/usr/bin/env python3
import importlib.util,runpy,shutil,sys,types
from pathlib import Path
runtime,source,out=sys.argv[1:4];source=Path(source);out=Path(out);out.mkdir(parents=True,exist_ok=True)
shutil.copy2(source/'dictionary.rxe',out/'BBY-Q.rxe')
shutil.copy2(source/'controller.rvp',out/'controller.rvp')
module=types.ModuleType('build');module.build=lambda runtime,out:None
sys.modules['build']=module;sys.argv=[sys.argv[0],runtime,str(out)]
runpy.run_path('ai/releases/e025/test.py',run_name='__main__')
