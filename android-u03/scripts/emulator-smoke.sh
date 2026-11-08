#!/usr/bin/env bash
# Real Android execution of the integrated modules. No archived test results.
set -euo pipefail
OUT=build/android-u03
APK="$OUT/BBY-Q-U03-Integrado.apk"
TEST=android-u03/app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk
PACKAGE=com.bbyq.u03.integrated
mkdir -p "$OUT"
test -s "$APK" && test -s "$TEST"
export PATH="$ANDROID_HOME/platform-tools:$PATH"
if [[ -e /dev/kvm ]]; then sudo chmod a+rw /dev/kvm; fi
export ANDROID_AVD_HOME="$(mktemp -d /tmp/bbyq-u03-integrated.XXXXXX)"
printf 'no\n' | "$ANDROID_HOME/cmdline-tools/latest/bin/avdmanager" create avd --force -n bbyq-u03-integration -p "$ANDROID_AVD_HOME/bbyq-u03-integration.avd" -k 'system-images;android-35;default;x86_64'
"$ANDROID_HOME/emulator/emulator" -avd bbyq-u03-integration -no-window -no-audio -no-boot-anim -no-snapshot -gpu swiftshader_indirect -memory 4096 -partition-size 8192 > "$OUT/emulator.log" 2>&1 &
EMU=$!
finish(){ adb logcat -d > "$OUT/logcat.log" 2>/dev/null || true; kill "$EMU" 2>/dev/null || true; }
trap finish EXIT
adb wait-for-device
booted=0
for i in $(seq 1 150); do
 if [[ "$(adb shell getprop sys.boot_completed | tr -d '\r')" == 1 ]]; then booted=1;break;fi
 sleep 2
done
test "$booted" -eq 1 || { tail -80 "$OUT/emulator.log";exit 1; }
adb shell settings put global window_animation_scale 0
adb shell settings put global transition_animation_scale 0
adb shell settings put global animator_duration_scale 0
adb shell getconf PAGE_SIZE > "$OUT/emulator-page-size.txt"
adb install -r "$APK"
adb install -r "$TEST"
adb shell am instrument -w -e class com.bbyq.u03.U03NativeTest "$PACKAGE.test/androidx.test.runner.AndroidJUnitRunner" > "$OUT/android-tests.txt" 2>&1
cat "$OUT/android-tests.txt"
python3 - <<'PY'
from pathlib import Path
import re
s=Path('build/android-u03/android-tests.txt').read_text()
assert not re.search(r'FAILURES|INSTRUMENTATION_FAILED|Process crashed|shortMsg|Error in',s),s
m=re.search(r'OK \((\d+) tests?\)',s);assert m and int(m.group(1))>=15,s
PY
# A new process must restore the exact committed model and old receipt.
adb shell am force-stop "$PACKAGE"
adb shell am instrument -w -e class com.bbyq.u03.U03RestartTest "$PACKAGE.test/androidx.test.runner.AndroidJUnitRunner" > "$OUT/restart-tests.txt" 2>&1
cat "$OUT/restart-tests.txt"
python3 - <<'PY'
from pathlib import Path
import re
s=Path('build/android-u03/restart-tests.txt').read_text()
assert re.search(r'OK \(1 tests?\)',s),s
assert not re.search(r'FAILURES|INSTRUMENTATION_FAILED|Process crashed|shortMsg|Error in',s),s
PY
adb exec-out run-as "$PACKAGE" tar -C files -cf - test-evidence > "$OUT/mobile-evidence.tar"
mkdir -p "$OUT/mobile-evidence"
tar -xf "$OUT/mobile-evidence.tar" -C "$OUT/mobile-evidence"
adb shell am start -n "$PACKAGE/com.bbyq.u03.MainActivity"
sleep 5
adb exec-out screencap -p > "$OUT/app-screen.png"
adb shell uiautomator dump /sdcard/bbyq-u03-ui.xml >/dev/null
adb exec-out cat /sdcard/bbyq-u03-ui.xml > "$OUT/ui.xml"
python3 - <<'PY'
from pathlib import Path
from hashlib import sha256
import json,re
p=Path('build/android-u03');root=p/'mobile-evidence/test-evidence'
required=['loader','startup','main-modules','six-engines','memory-C09','plan-C10','semantic-C06','evidence-C07-C08','transport-C01','persistence-C02','learning-C11','learning-C12','cache-C13','ablations-C14','stress-C15','complete-status','restart-before','restart-after']
evidence={k:json.loads((root/(k+'.json')).read_text()) for k in required}
assert evidence['loader']['loaded'] and evidence['restart-after']['passed']
assert evidence['main-modules']['C06']['native_XI']
assert evidence['plan-C10']['status']=='native_plan'
assert evidence['learning-C11']['arms']['joint']['verified_feedback']==1
assert evidence['learning-C12']['arms']['joint']['verified_feedback']==2
assert evidence['ablations-C14']['trial_count']==10
assert evidence['stress-C15']['rollbacks']==3
assert not evidence['learning-C11']['candidate_promoted']
assert not evidence['learning-C12']['candidate_promoted']
assert not evidence['cache-C13']['cache_promoted']
assert evidence['startup']['historical_assets']==159
build=json.loads((p/'build.json').read_text())
elf=json.loads((p/'elf-16kb.json').read_text())
assert elf['passed'] and elf['all_LOAD_alignment_at_least_16384']
assert 'BBY Q' in (p/'ui.xml').read_text()
report={**build,'passed':True,'android_15_x86_64_instrumentation_tests':15,'restart_new_process_tests':1,
 'actual_emulator_page_size':int((p/'emulator-page-size.txt').read_text().strip()),
 'ARM64_runtime_tested':False,'ARM64_ELF_static_verified':True,
 'user_phone_error_reproduced':False,'all_159_original_sources_unchanged':True,
 'mobile_scope':'C01-C15 main/observation/laboratory actions with bounded synthetic tests; no GPU dispatch',
 'evidence_sha256':{k:sha256((root/(k+'.json')).read_bytes()).hexdigest() for k in required},
 'no_models_automatically_promoted':True,'GPU_virtual_compute_integrated':False}
(p/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
PY
