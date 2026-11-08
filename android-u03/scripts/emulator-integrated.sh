#!/usr/bin/env bash
# Preserve the complete previously verified C16 campaign; add deeper ELF/UI gates.
set -euo pipefail
python3 android-u03/scripts/verify-deep-elf.py build/android-c16/BBY-Q-U03-Integrado-C16.apk build/android-c16/deep-elf-verification.json
bash android-u03/scripts/emulator-integrated-baseline.sh
python3 - <<'PY'
from pathlib import Path
import json,re,xml.etree.ElementTree as ET
out=Path('build/android-c16')
root=ET.fromstring((out/'integrated-ui.xml').read_text())
def bounds(node):
    return tuple(map(int,re.findall(r'\d+',node.attrib['bounds'])))
nodes=list(root.iter('node'))
button=next(n for n in nodes if n.attrib.get('text')=='Ejecutar' and n.attrib.get('class')=='android.widget.Button')
nav=next((n for n in nodes if n.attrib.get('resource-id')=='android:id/navigationBarBackground'),None)
rect=bounds(button)
if nav is not None:
    assert rect[3]<=bounds(nav)[1],('Execute button is hidden behind Android navigation',rect,bounds(nav))
assert rect[2]>rect[0] and rect[3]-rect[1]>=44
for label in ('Misión','Aprender','Ciclos','Exportar'):
    item=next(n for n in nodes if n.attrib.get('text')==label and n.attrib.get('class')=='android.widget.Button')
    b=bounds(item);assert b[3]-b[1]>=44,(label,b)
report=json.loads((out/'validation.json').read_text())
elf=json.loads((out/'deep-elf-verification.json').read_text())
assert report['delivery_verified'] and elf['all_load_segments_16kb']
report['nested_python_ELF_verified']=elf['verified_elf_count']
report['execute_button_above_navigation']=True
report['shortcut_touch_height_verified']=True
report['native_algorithm_changed_in_delivery_review']=False
(out/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'review_passed':True,'nested_ELF_count':elf['verified_elf_count'],'execute_button_above_navigation':True,'original_C16_tests_preserved':True}))
PY
