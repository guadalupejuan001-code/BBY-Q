#!/usr/bin/env python3
"""Reuse the exact E025/W4u regression oracle against the new capsule."""
import importlib.util,runpy,sys
from pathlib import Path
runtime,out=sys.argv[1:3]
spec=importlib.util.spec_from_file_location('build',Path('ai/releases/e025/build.py'))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
def candidate_build(runtime,out):
 import shutil,subprocess
 subprocess.run(['node','ai/releases/e030/build.mjs',runtime,str(out)],check=True)
 shutil.copy2(out/'BBY-Q.rxe',out/'authentic-E025.rxe')
 shutil.copy2(out/'learned.rxe',out/'BBY-Q.rxe')
module.build=candidate_build;sys.modules['build']=module
runpy.run_path('ai/releases/e025/test.py',run_name='__main__')
