#!/usr/bin/env bash
# Android 15 end-to-end original U02 XI JNI instrumentation.
set -euo pipefail
OUT=build/android-u03
APK="$OUT/BBY-Q-U03-C15-Android.apk"
TEST=android-u03/app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk
mkdir -p "$OUT"
test -s "$APK" && test -s "$TEST"
export PATH="$ANDROID_HOME/platform-tools:$PATH"
if [[ -e /dev/kvm ]]; then sudo chmod a+rw /dev/kvm; fi
export ANDROID_AVD_HOME="$(mktemp -d /tmp/bbyq-u03-avd.XXXXXX)"
printf 'no\n' | "$ANDROID_HOME/cmdline-tools/latest/bin/avdmanager" create avd   --force -n bbyq-u03 -p "$ANDROID_AVD_HOME/bbyq-u03.avd"   -k 'system-images;android-35;default;x86_64'
"$ANDROID_HOME/emulator/emulator" -avd bbyq-u03 -no-window -no-audio -no-boot-anim   -no-snapshot -gpu swiftshader_indirect -memory 4096 > "$OUT/emulator.log" 2>&1 &
EMU=$!
finish() {
    adb logcat -d > "$OUT/logcat.log" 2>/dev/null || true
    kill "$EMU" 2>/dev/null || true
}
trap finish EXIT
adb wait-for-device
booted=0
for i in $(seq 1 150); do
  if [[ "$(adb shell getprop sys.boot_completed | tr -d '\r')" = "1" ]]; then
    booted=1
    break
  fi
  sleep 2
done
test "$booted" -eq 1 || { echo "Android 15 failed to boot"; tail -70 "$OUT/emulator.log"; exit 1; }
adb shell settings put global window_animation_scale 0
adb shell settings put global transition_animation_scale 0
adb shell settings put global animator_duration_scale 0
adb install -r "$APK"
adb install -r "$TEST"
# Foreground U02 startup for a full UI smoke and instrumentation startup.
adb shell am start -n com.bbyq.u03/com.bbyq.u03.MainActivity
sleep 4
adb shell am instrument -w com.bbyq.u03.test/androidx.test.runner.AndroidJUnitRunner   > "$OUT/android-tests.txt" 2>&1 || {
     cat "$OUT/android-tests.txt"
     adb logcat -d | tail -200
     exit 1
  }
cat "$OUT/android-tests.txt"
python3 - <<'PY'
from pathlib import Path
import re
text=Path('build/android-u03/android-tests.txt').read_text()
assert not re.search(r'FAILURES|INSTRUMENTATION_FAILED|Process crashed|shortMsg|Error in',text),text
match=re.search(r'OK \((\d+) tests?\)',text)
assert match and int(match.group(1))>=4,text
PY
adb shell am force-stop com.bbyq.u03
adb shell am start -n com.bbyq.u03/com.bbyq.u03.MainActivity
sleep 4
adb exec-out screencap -p > "$OUT/android-u03-screen.png"
adb shell uiautomator dump /sdcard/u03-ui.xml >/dev/null || true
adb exec-out cat /sdcard/u03-ui.xml > "$OUT/android-u03-ui.xml" || true
python3 - <<'PY'
from pathlib import Path
import json,re
p=Path('build/android-u03')
doc=json.loads((p/'build.json').read_text())
text=(p/'android-tests.txt').read_text()
doc['android_15_emulator_tested']=True
doc['original_U02_native_XI_instrumentation_tests']=int(re.search(r'OK \((\d+) tests?\)',text).group(1))
doc['test_protocol']='seven SHA banks, C1 math JNI, six-engine mission JNI, exact ID replay, preserved C00-C15'
doc['apk_delivery_verified']=True
(p/'validation.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(doc,ensure_ascii=False))
PY
