#!/usr/bin/env bash
set -euo pipefail
OUT=build/android-c17
APK="$OUT/BBY-Q-U03-Entrenamiento-C17.apk"
TEST=android-u03/app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk
PKG=com.bbyq.u03.training
TRAINING_EVIDENCE=(training-test-proof.json training-workspace-ui.png training-guide-ui.png
  training-restart-seed.json training-restart-verify.json)
mkdir -p "$OUT"
test -s "$APK" && test -s "$TEST"
export PATH="$ANDROID_HOME/platform-tools:$PATH"
if [[ -e /dev/kvm ]]; then sudo chmod a+rw /dev/kvm; fi
export ANDROID_AVD_HOME="$(mktemp -d /tmp/bbyq-c17-avd.XXXXXX)"
printf 'no\n' | "$ANDROID_HOME/cmdline-tools/latest/bin/avdmanager" create avd --force -n bbyq-c17 \
  -p "$ANDROID_AVD_HOME/bbyq-c17.avd" -k 'system-images;android-35;default;x86_64'
"$ANDROID_HOME/emulator/emulator" -avd bbyq-c17 -no-window -no-audio -no-boot-anim \
  -no-snapshot -gpu swiftshader_indirect -memory 4096 > "$OUT/emulator.log" 2>&1 &
EMU=$!
finish(){
  local result=$? name partial
  # Preserve completed test receipts/screenshots even when a later assertion fails.
  # A missing file must not replace valid evidence with run-as error output.
  for name in "${TRAINING_EVIDENCE[@]}"; do
    partial="$OUT/$name.partial"
    if timeout 8s adb shell run-as "$PKG" test -s "files/$name" >/dev/null 2>&1 &&
       timeout 8s adb exec-out run-as "$PKG" cat "files/$name" > "$partial" 2>/dev/null && test -s "$partial"; then
      mv "$partial" "$OUT/$name"
    else
      rm -f "$partial"
    fi
  done
  timeout 10s adb logcat -d > "$OUT/android-logcat.log" 2>/dev/null || true
  timeout 8s adb exec-out run-as "$PKG" cat files/startup-diagnostic.json > "$OUT/startup-diagnostic.txt" 2>/dev/null || true
  kill "$EMU" 2>/dev/null || true
  exit "$result"
}
trap finish EXIT
adb wait-for-device
booted=0
for i in $(seq 1 150); do
  if [[ "$(adb shell getprop sys.boot_completed | tr -d '\r')" = 1 ]]; then booted=1;break;fi
  sleep 2
done
test "$booted" -eq 1 || { tail -80 "$OUT/emulator.log";exit 1; }
adb shell getconf PAGE_SIZE > "$OUT/emulator-page-size.txt"
adb shell settings put global window_animation_scale 0
adb shell settings put global transition_animation_scale 0
adb shell settings put global animator_duration_scale 0
adb install -r "$APK"
adb install -r "$TEST"
adb shell am start -W -n "$PKG/com.bbyq.u03.IntegratedActivity" > "$OUT/launcher.txt"
# User-facing learning is tested through original XI, not canned lab answers.
adb shell am instrument -w -e class com.bbyq.u03.TrainingWorkspaceTest \
  "$PKG.test/androidx.test.runner.AndroidJUnitRunner" > "$OUT/training-tests.txt" 2>&1
cat "$OUT/training-tests.txt"
python3 - <<'PYTEST'
from pathlib import Path
import re
text=Path('build/android-c17/training-tests.txt').read_text()
m=re.search(r'OK \((\d+) tests?\)',text)
assert m and int(m.group(1))>=5,text
assert not re.search(r'FAILURES|INSTRUMENTATION_FAILED|Process crashed|shortMsg|Error in ',text),text
PYTEST

adb shell am instrument -w \
  -e class com.bbyq.u03.U03NativeTest,com.bbyq.u03.IntegratedCyclesTest \
  "$PKG.test/androidx.test.runner.AndroidJUnitRunner" > "$OUT/android-tests.txt" 2>&1
cat "$OUT/android-tests.txt"
python3 - <<'PY'
from pathlib import Path
import re
text=Path('build/android-c17/android-tests.txt').read_text()
m=re.search(r'OK \((\d+) tests?\)',text)
assert m and int(m.group(1))>=16,text
assert not re.search(r'FAILURES|INSTRUMENTATION_FAILED|Process crashed|shortMsg|Error in ',text),text
PY
# These are TWO different Android processes, not close/reopen on one Python object.
for phase in seed verify; do
  adb shell am force-stop "$PKG"
  adb shell am instrument -w -e class com.bbyq.u03.ProcessRestartTest -e persistence_phase "$phase" \
    "$PKG.test/androidx.test.runner.AndroidJUnitRunner" > "$OUT/restart-$phase.txt" 2>&1
  cat "$OUT/restart-$phase.txt"
  python3 - "$OUT/restart-$phase.txt" <<'PY'
from pathlib import Path
import sys,re
text=Path(sys.argv[1]).read_text()
assert re.search(r'OK \(1 test\)',text),text
assert not re.search(r'FAILURES|INSTRUMENTATION_FAILED|Process crashed|shortMsg|Error in ',text),text
PY
done
# Training checkpoints and the selected model must survive a process death.
for phase in seed verify; do
  adb shell am force-stop "$PKG"
  adb shell am instrument -w -e class com.bbyq.u03.TrainingRestartTest -e training_phase "$phase" \
    "$PKG.test/androidx.test.runner.AndroidJUnitRunner" > "$OUT/training-restart-$phase.txt" 2>&1
  cat "$OUT/training-restart-$phase.txt"
  python3 - "$OUT/training-restart-$phase.txt" <<'PYTEST'
from pathlib import Path
import sys,re
text=Path(sys.argv[1]).read_text()
assert re.search(r'OK \(1 test\)',text),text
assert not re.search(r'FAILURES|INSTRUMENTATION_FAILED|Process crashed|shortMsg|Error in ',text),text
PYTEST
done
for name in "${TRAINING_EVIDENCE[@]}"; do
  adb exec-out run-as "$PKG" cat "files/$name" > "$OUT/$name"
done

# Export measured Android laboratory outputs, not just copied Linux results.
mkdir -p "$OUT/lab"
for name in transport persistence c11 c12 cache profile stress candidate; do
  adb exec-out run-as "$PKG" cat "files/sessions/laboratory/$name-last.json" > "$OUT/lab/$name.json"
done
adb shell am start -W -n "$PKG/com.bbyq.u03.IntegratedActivity" >> "$OUT/launcher.txt"
sleep 3
adb exec-out screencap -p > "$OUT/integrated-ui.png"
adb shell uiautomator dump /sdcard/c17-ui.xml >/dev/null
adb exec-out cat /sdcard/c17-ui.xml > "$OUT/integrated-ui.xml"
python3 - <<'PY'
from pathlib import Path
import json,re
out=Path('build/android-c17')
report=json.loads((out/'static-verification.json').read_text())
text=(out/'android-tests.txt').read_text()
report['android_instrumentation_passed']=True
report['android_instrumentation_test_count']=int(re.search(r'OK \((\d+) tests?\)',text).group(1))
report['training_instrumentation_passed']=True
report['training_instrumentation_test_count']=int(re.search(r'OK \((\d+) tests?\)',(out/'training-tests.txt').read_text()).group(1))
report['training_external_restart_verified']=True
report['training_restart_evidence']={phase:json.loads((out/f'training-restart-{phase}.json').read_text()) for phase in ('seed','verify')}
assert all(evidence.get('passed') is True for evidence in report['training_restart_evidence'].values())
restart=report['training_restart_evidence']['verify']
assert restart['real_process_restart'] is True and restart['seed_pid']!=restart['verify_pid']
report['training_test_evidence']=json.loads((out/'training-test-proof.json').read_text())
training_cases=report['training_test_evidence']['cases']
assert set(training_cases)=={'native_lessons_activation_restore','joint_native_feedback','invalid_and_stale_actions','portable_export','training_ui_and_guide'}
assert all(case.get('passed') is True for case in training_cases.values())
report['android_api_tested']=35
report['emulator_page_size']=int((out/'emulator-page-size.txt').read_text().strip())
report['external_force_stop_restart_verified']=True
report['physical_user_device_tested']=False
report['cycle_labs']={}
for f in sorted((out/'lab').glob('*.json')):
    lab=json.loads(f.read_text())
    assert lab.get('personal_database_writes')==0,(f,lab)
    if f.stem!='candidate':assert lab.get('passed') is True,(f,lab)
    report['cycle_labs'][f.stem]={'executed_on_android':True,'personal_writes':0,'wall_ms':lab['experiment_wall_ms']}
assert set(report['cycle_labs'])=={'transport','persistence','c11','c12','cache','profile','stress','candidate'}
assert 'BBY Q' in (out/'integrated-ui.xml').read_text()
report['delivery_verified']=True
(out/'validation.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('ELF_alignment','original_heads')},ensure_ascii=False))
PY

