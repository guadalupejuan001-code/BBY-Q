"""Original RVPC2 JNI transport with C01 code libraries and real packet telemetry.

No learned state or output is cached. Baseline mode reconstructs the identical
full source and uses the original execute call. ContextVars isolate benchmarks.
"""
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
import json
import re
import time
from java import jclass
Native=jclass('com.bbyq.personal.XiSession')
_TRACE=ContextVar('u03_mobile_packet_trace',default=None)
_LIBRARY=ContextVar('u03_mobile_code_library',default=True)

@contextmanager
def trace_scope(library=True):
    stats={'opens':0,'executes':0,'registered_libraries':0,'cache_hits':0,
           'source_bytes':0,'jni_source_bytes':0,'packets':[]}
    a=_TRACE.set(stats);b=_LIBRARY.set(bool(library))
    try: yield stats
    finally: _LIBRARY.reset(b);_TRACE.reset(a)

class XiSession:
    def __init__(self,binary,state):
        path=Path(state)
        if not path.is_file():raise FileNotFoundError('Original XI state missing: '+str(path))
        self.handle=Native.open(path.read_bytes())
        if not self.handle:raise RuntimeError('Original JNI XI could not restore RVPC2')
        self.bank=path.stem;self._libraries={};self.execute_count=0
        if _TRACE.get() is not None:_TRACE.get()['opens']+=1
    def execute(self,source):
        if self.handle is None:raise RuntimeError('Closed XI session')
        if not isinstance(source,str):raise TypeError('XI requires source text')
        start=time.perf_counter_ns();stats=_TRACE.get();sent=0
        head,marker,library=source.partition('\nhalt\n')
        if _LIBRARY.get() and marker and len(library.encode('utf-8'))>=512:
            index=self._libraries.get(library)
            if index is None:
                index=Native.registerLibrary(self.handle,library)
                if index<=0:raise RuntimeError('XI code library registration failed')
                self._libraries[library]=index;sent+=len(library.encode('utf-8'))
                if stats is not None:stats['registered_libraries']+=1
            elif stats is not None:stats['cache_hits']+=1
            prefix=head+marker;sent+=len(prefix.encode('utf-8'))
            raw=bytes(Native.executeRef(self.handle,index,prefix))
        else:
            sent+=len(source.encode('utf-8'));raw=bytes(Native.execute(self.handle,source))
        end=time.perf_counter_ns()
        events=[json.loads(line) for line in raw.decode('utf-8').splitlines() if line.startswith('{')]
        self.execute_count+=1
        if stats is not None:
            from integration.bench_u03_c14.native_packets import packet_owner
            calls=re.findall(r'(?m)^\s*call\s+([a-zA-Z0-9_]+)\s*$',head if marker else source)
            stats['executes']+=1;stats['source_bytes']+=len(source.encode('utf-8'));stats['jni_source_bytes']+=sent
            stats['packets'].append({'bank':self.bank,'owner':packet_owner(self.bank,calls),
                'calls':calls,'start_ns':start,'end_ns':end,'wall_ms':(end-start)/1e6,
                'source_bytes':len(source.encode('utf-8')),'jni_source_bytes':sent})
        return events,(end-start)/1e6
    def save(self,destination):
        if self.handle is None:raise RuntimeError('Closed XI session')
        p=Path(destination);p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(bytes(Native.checkpoint(self.handle)))
    def metrics(self):return {'xi_jni_invocations':self.execute_count,'native_cpu_ms':None}
    def close(self):
        if self.handle is not None:Native.release(self.handle);self.handle=None;self._libraries.clear()
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
