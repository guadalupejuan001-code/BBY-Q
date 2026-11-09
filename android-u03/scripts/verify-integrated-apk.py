#!/usr/bin/env python3
"""Static package/ELF/source verification. Does NOT assert device tests passed."""
from hashlib import sha256
from pathlib import Path
import io,json,struct,subprocess,sys,zipfile
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from integration.audit_u03_c00.profile import freeze_assets
BASE='4f1bb3b0b954278f4535af3e3aaeb3d6c6e9660e'

def alignments(raw):
    if raw[:4]!=b'\x7fELF' or raw[4]!=2 or raw[5]!=1:
        raise ValueError('Expected little-endian ELF64')
    offset=struct.unpack_from('<Q',raw,32)[0]
    step,count=struct.unpack_from('<HH',raw,54)
    result=[]
    for i in range(count):
        p=offset+i*step
        if struct.unpack_from('<I',raw,p)[0]==1:
            result.append(struct.unpack_from('<Q',raw,p+48)[0])
    if not result:raise ValueError('ELF has no loadable segments')
    return result

def main():
    apk=Path(sys.argv[1])
    out=Path(sys.argv[2]);out.parent.mkdir(parents=True,exist_ok=True)
    protected=freeze_assets(ROOT)
    if len(protected)!=159:raise AssertionError('Protected count changed')
    for filename,want in protected.items():
        original=subprocess.run(['git','show',BASE+':'+filename],cwd=ROOT,check=True,capture_output=True).stdout
        if sha256(original).hexdigest()!=want:raise AssertionError('Historical file modified: '+filename)
    with zipfile.ZipFile(apk) as z:
        if z.testzip() is not None:raise AssertionError('Broken APK archive')
        files=set(z.namelist())
        libs={name:alignments(z.read(name)) for name in files if name.startswith('lib/') and name.endswith('.so')}
        if not libs:raise AssertionError('No native libraries packaged')
        for name,values in libs.items():
            if min(values)<16384:raise AssertionError('Native ELF is not 16KB aligned: '+name+' '+str(values))
        for abi in ('arm64-v8a','x86_64'):
            if 'lib/'+abi+'/libreverse_os.so' not in libs:raise AssertionError('Missing original XI JNI '+abi)
        guide=z.read('assets/training-guide.html').decode('utf-8')
        if '<svg' not in guide or len(guide)<5000:raise AssertionError('Missing illustrated offline training guide')
        with zipfile.ZipFile(io.BytesIO(z.read('assets/chaquopy/app.imy'))) as modules:
            if 'u03_conversation.pyc' not in modules.namelist():raise AssertionError('Personal conversation adapter missing')
        dex=b''.join(z.read(n) for n in files if n.startswith('classes') and n.endswith('.dex'))
        for name in (b'ModelActivity',b'TrainingActivity',b'UiKit',b'IntegratedActivity'):
            if name not in dex:raise AssertionError('Personal screen missing: '+name.decode())
        manifest=json.loads(z.read('assets/u03/mobile-manifest.json'))
        assert manifest['android_version']=='U03.18.0-personal' and manifest['android_label']=='BBY Q 0'
        raw=z.read('assets/u03/bbyq-u03-runtime.zip')
        if sha256(raw).hexdigest()!=manifest['archive_sha256']:raise AssertionError('Runtime payload hash mismatch')
        with zipfile.ZipFile(io.BytesIO(raw)) as payload:
            for filename,want in protected.items():
                if sha256(payload.read(filename)).hexdigest()!=want:raise AssertionError('Packaged historical source changed: '+filename)
            provenance=json.loads(payload.read('integration/mobile_u03_c16/heads/provenance.json'))
            for cycle,expected in provenance['heads'].items():
                for suffix,key in (('.rvp','checkpoint_sha256'),('.json','report_sha256')):
                    name='integration/mobile_u03_c16/heads/'+cycle+suffix
                    if sha256(payload.read(name)).hexdigest()!=expected[key]:raise AssertionError('Recovered head/report changed: '+name)
        if manifest['experimental_c11_c12_promoted'] or manifest['C13_cache_enabled']:
            raise AssertionError('Unapproved promotion in package')
    report={'static_checks_passed':True,'apk_bytes':apk.stat().st_size,
       'apk_sha256':sha256(apk.read_bytes()).hexdigest(),
       'package':'com.bbyq.u03.training','original_protected_assets':159,
       'all_ELF_load_segments_at_least_16KB':True,'native_library_count':len(libs),
       'ELF_alignment':dict(sorted(libs.items())),
       'original_heads':provenance['heads'],'base_sha':BASE,
       'current_sha':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
       'physical_user_device_tested':False,'android_instrumentation_passed':False,
       'GPU_compute_integrated':False,'auto_model_promotion':False,
       'training_workspace_packaged':True,'offline_illustrated_guide':True,
       'personal_conversation_packaged':True,'personal_model_workspace_packaged':True}
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('ELF_alignment','original_heads')},ensure_ascii=False))
if __name__=='__main__':main()

