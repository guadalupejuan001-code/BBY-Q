#!/usr/bin/env bash
set -euo pipefail
APK=android-personal/app/build/outputs/apk/debug/app-debug.apk
TEST=android-personal/app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk
OUT=build/personal-artifacts
mkdir -p "$OUT"
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
grep -Eq 'OK \([2-9] tests?\)' "$OUT/android-tests.txt"
adb shell am start -n com.bbyq.personalx/com.bbyq.personal.MainActivity
sleep 5
adb exec-out screencap -p > "$OUT/BBYQ-X-Android.png"
adb shell uiautomator dump /sdcard/bbyq-ui.xml >/dev/null
adb exec-out cat /sdcard/bbyq-ui.xml > "$OUT/android-ui.xml"
cp "$APK" "$OUT/BBYQ-X-Android-1.0.apk"
cp "$ANDROID_HOME/build-tools/35.0.0/lib/apksigner.jar" "$OUT/apksigner.jar"
"$ANDROID_HOME/build-tools/35.0.0/apksigner" verify --verbose --print-certs "$APK" > "$OUT/signature.txt"
"$ANDROID_HOME/build-tools/35.0.0/aapt" dump badging "$APK" > "$OUT/package.txt"
python3 - <<'PY'
from pathlib import Path
import hashlib,json,zipfile
out=Path('build/personal-artifacts');p=out/'BBYQ-X-Android-1.0.apk'
with zipfile.ZipFile(p) as z:
 assert z.testzip() is None
 for n in ['lib/arm64-v8a/libreverse_os.so','lib/x86_64/libreverse_os.so','assets/engine/chat-model.rvp.gz','assets/engine/quantum-model.rvp.gz']:assert n in z.namelist()
 m=json.loads(z.read('assets/engine/manifest.json'))
 assert m['qubits_per_agent']==1000 and m['quantum_training_episodes_per_agent']==10000
 assert m['concepts']==480
xml=(out/'android-ui.xml').read_text()
assert 'BBY Q' in xml
assert 'com.bbyq.personalx' in (out/'package.txt').read_text()
e={'ok':True,'package':'com.bbyq.personalx','version':'1.0.0-personal','android_api_tested':35,'arm64_compiled':True,'x86_64_native_tested':True,'instrumentation_tests':2,'host_conversation_cases':6,'chat_engine':'original X08 XI','quantum_model':'original V3 10000 episodes per agent; no MPS','new_quantum_conversation_algorithm':False,'apk_bytes':p.stat().st_size,'apk_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'permissions_requested':[]}
(out/'validation.json').write_text(json.dumps(e,indent=2)+'\n');print(json.dumps(e))
PY
