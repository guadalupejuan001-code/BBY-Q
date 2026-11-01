#!/usr/bin/env bash
# C13 emulator smoke: execute real native XI on Android 15 (API 35), not just package.
set -euo pipefail
test "$#" -eq 1 || { echo "Provide the compiled Android APK" >&2; exit 1; }
APK="$1"
test -s "$APK"
export PATH="$ANDROID_HOME/platform-tools:$PATH"
[[ -d "$ANDROID_HOME/emulator" ]] || { echo "Android emulator missing" >&2; exit 1; }
if [[ -e /dev/kvm ]]; then sudo chmod a+rw /dev/kvm; fi
export ANDROID_AVD_HOME="$(mktemp -d /tmp/bbyq-c13-avd.XXXXXX)"
printf 'no\n' | "$ANDROID_HOME/cmdline-tools/latest/bin/avdmanager" create avd --force \
  -n bbyq-c13 -p "$ANDROID_AVD_HOME/bbyq-c13.avd" -k 'system-images;android-35;default;x86_64'
echo 'hw.keyboard=no' >> "$ANDROID_AVD_HOME/bbyq-c13.avd/config.ini"
"$ANDROID_HOME/emulator/emulator" -avd bbyq-c13 -no-window -no-audio \
  -no-boot-anim -no-snapshot -gpu swiftshader_indirect -memory 2048 \
  > android-xi-lab/emulator.log 2>&1 &
EMU=$!
trap 'adb logcat -d > android-xi-lab/emulator-logcat.txt 2>/dev/null || true; kill "$EMU" 2>/dev/null || true' EXIT
adb wait-for-device
ready=0
for i in $(seq 1 150); do
 if [[ "$(adb shell getprop sys.boot_completed | tr -d '\r')" = 1 ]]; then ready=1; break; fi
 sleep 2
done
test "$ready" -eq 1 || { echo "Android failed to boot" >&2; exit 1; }
adb shell settings put global window_animation_scale 0 || true
adb shell settings put global transition_animation_scale 0 || true
adb shell settings put global animator_duration_scale 0 || true
adb install -r "$APK"
adb logcat -c
adb shell am start -n com.bbyq.xilab/com.bbyq.lab.MainActivity
has_marker(){
 adb logcat -d -s 'BBYQ_XI_C13:I' '*:S' | grep -F "$1" >/dev/null
}
await_marker(){
 local label="$1"
 for i in $(seq 1 40); do
  if has_marker "$label"; then echo "PASS $label"; return 0; fi
  sleep 2
 done
 echo "FAILED native Android event: $label" >&2
 adb logcat -d -s 'BBYQ_XI_C13:I' '*:E' | tail -110 >&2 || true
 return 1
}
await_marker BOOT_NATIVE_OK
tap_button(){
 local target="$1" coords=""
 for i in $(seq 1 5); do
  adb shell uiautomator dump /sdcard/bbyq-c13-ui.xml > /dev/null 2>&1 || true
  adb exec-out cat /sdcard/bbyq-c13-ui.xml > android-xi-lab/c13-ui.xml 2>/dev/null || true
  coords="$(python3 - "$target" <<'PY'
import sys,re,xml.etree.ElementTree as ET
from pathlib import Path
try:
 root=ET.fromstring(Path('android-xi-lab/c13-ui.xml').read_bytes())
 for node in root.iter('node'):
  if node.attrib.get('text','').strip().lower()==sys.argv[1].lower():
   match=re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]',node.attrib.get('bounds',''))
   if match:
    x0,y0,x1,y1=map(int,match.groups())
    if x1>x0 and y1>y0:
     print((x0+x1)//2,(y0+y1)//2);break
except (ValueError,ET.ParseError,FileNotFoundError):pass
PY
)"
  if [[ -n "$coords" ]]; then
   read -r x y <<< "$coords"
   adb shell input tap "$x" "$y"
   return 0
  fi
  adb shell input swipe 500 1100 500 350 270
  sleep 2
 done
 echo "Cannot find Android button $target" >&2
 cat android-xi-lab/c13-ui.xml >&2 || true
 return 1
}
tap_button 'entrena xor'
await_marker VQC_TRAIN_OK
tap_button 'clasifica 0 1'
await_marker VQC_CLASSIFY_OK
tap_button 'entrena agente'
await_marker QRL_TRAIN_OK
tap_button 'planea 1 0'
await_marker QRL_PLAN_OK
echo '{"ok":true,"android_api":35,"jni_native":true,"boot":true,"vqc_train":true,"vqc_infer":true,"qrl_train":true,"qrl_plan":true,"full_x10":false}' > android-xi-lab/c13-emulator-evidence.json
cat android-xi-lab/c13-emulator-evidence.json
