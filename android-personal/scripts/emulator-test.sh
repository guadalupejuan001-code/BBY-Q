#!/usr/bin/env bash
set -euo pipefail
APK=android-personal/app/build/outputs/apk/debug/app-debug.apk
TEST=android-personal/app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk
OUT=build/personal-artifacts
mkdir -p "$OUT"
cp "$APK" "$OUT/BBYQ-X10-Android-2.0-candidate.apk"
cp "$ANDROID_HOME/build-tools/35.0.0/lib/apksigner.jar" "$OUT/apksigner.jar"
python3 - "$APK" <<'PY_ASSETS'
import hashlib,json,sys,zipfile
with zipfile.ZipFile(sys.argv[1]) as z:
 m=json.loads(z.read('assets/engine/manifest.json'))
 for name,expected in m['files'].items():
  actual=hashlib.sha256(z.read('assets/engine/'+name)).hexdigest()
  assert actual==expected,('Packaged model hash mismatch',name)
 assert len(json.loads(z.read('assets/engine/chat-fixtures.json')))==6
print('All original model assets are present and byte-identical in the APK')
PY_ASSETS
export PATH="$ANDROID_HOME/platform-tools:$PATH"
if [[ -e /dev/kvm ]]; then sudo chmod a+rw /dev/kvm; fi
export ANDROID_AVD_HOME="$(mktemp -d /tmp/bbyq-personal-avd.XXXXXX)"
printf 'no\n' | "$ANDROID_HOME/cmdline-tools/latest/bin/avdmanager" create avd --force -n bbyq-personal -p "$ANDROID_AVD_HOME/bbyq-personal.avd" -k 'system-images;android-35;default;x86_64'
"$ANDROID_HOME/emulator/emulator" -avd bbyq-personal -no-window -no-audio -no-boot-anim -no-snapshot -gpu swiftshader_indirect -memory 3072 > "$OUT/emulator.log" 2>&1 &
EMU=$!
trap 'adb logcat -d > "$OUT/android-logcat.txt" 2>/dev/null || true; kill "$EMU" 2>/dev/null || true' EXIT
adb wait-for-device
ready=0
for i in $(seq 1 150); do
 if [[ "$(adb shell getprop sys.boot_completed | tr -d '\r')" = 1 ]]; then ready=1;break;fi
 sleep 2
done
test "$ready" -eq 1
adb shell settings put global window_animation_scale 0
adb shell settings put global transition_animation_scale 0
adb shell settings put global animator_duration_scale 0
adb install -r "$APK"
adb install -r "$TEST"
adb shell am instrument -w com.bbyq.personalx.test/androidx.test.runner.AndroidJUnitRunner > "$OUT/android-tests.txt"
cat "$OUT/android-tests.txt"
python3 - <<'PY_TESTS'
from pathlib import Path
import re
text=Path('build/personal-artifacts/android-tests.txt').read_text()
match=re.search(r'OK \((\d+) tests?\)',text)
assert match and int(match.group(1))>=12,text
assert not re.search(r'FAILURES|INSTRUMENTATION_FAILED|Process crashed|shortMsg',text),text
PY_TESTS
adb shell am start -n com.bbyq.personalx/com.bbyq.personal.MainActivity
sleep 5
adb exec-out screencap -p > "$OUT/BBYQ-X-Android.png"
adb shell uiautomator dump /sdcard/bbyq-ui.xml >/dev/null
adb exec-out cat /sdcard/bbyq-ui.xml > "$OUT/android-ui.xml"
cp "$APK" "$OUT/BBYQ-X10-Android-2.0.apk"
cp "$ANDROID_HOME/build-tools/35.0.0/lib/apksigner.jar" "$OUT/apksigner.jar"
"$ANDROID_HOME/build-tools/35.0.0/apksigner" verify --verbose --print-certs "$APK" > "$OUT/signature.txt"
"$ANDROID_HOME/build-tools/35.0.0/aapt" dump badging "$APK" > "$OUT/package.txt"
python3 - <<'PY'
from pathlib import Path
import hashlib,json,zipfile,re
out=Path('build/personal-artifacts');p=out/'BBYQ-X10-Android-2.0.apk'
with zipfile.ZipFile(p) as z:
 assert z.testzip() is None
 for n in ['lib/arm64-v8a/libreverse_os.so','lib/x86_64/libreverse_os.so','assets/engine/chat-model.rvpbin','assets/engine/quantum-model.rvpbin']:assert n in z.namelist()
 m=json.loads(z.read('assets/engine/manifest.json'))
 assert m['qubits_per_agent']==1000 and m['quantum_training_episodes_per_agent']==10000
 assert m['concepts']==480
xml=(out/'android-ui.xml').read_text()
assert 'BBY Q' in xml
assert 'com.bbyq.personalx' in (out/'package.txt').read_text()
e={'ok':True,'package':'com.bbyq.personalx','version':'2.0.0-X10','android_api_tested':35,'arm64_compiled':True,'x86_64_native_tested':True,'instrumentation_tests':int(re.search(r'OK \((\d+) tests?\)',(out/'android-tests.txt').read_text()).group(1)),'host_conversation_cases':6,'chat_engine':'X10 Android with preserved X08 XI','quantum_model':'original V3 10000 episodes per agent; no MPS','qchat100':'preserved 49680-update model','qmemory':'keyed binary recall in the shared transaction','new_quantum_conversation_algorithm':False,'apk_bytes':p.stat().st_size,'apk_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'permissions_requested':[]}
(out/'validation.json').write_text(json.dumps(e,indent=2)+'\n');print(json.dumps(e))
PY
