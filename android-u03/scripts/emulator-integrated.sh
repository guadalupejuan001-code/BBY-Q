#!/usr/bin/env bash
set -euo pipefail
OUT=build/android-c19
APK="$OUT/BBY-Q-0-Chats.apk"
TEST=android-u03/app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk
BASELINE=build/chat-upgrade-fixture/C18-upgrade-baseline.apk
PKG=com.bbyq.u03.training
TRAINING_EVIDENCE=(training-test-proof.json training-workspace-ui.png training-guide-ui.png
  training-guide-diagram-ui.png training-guide-diagram-2-ui.png training-guide-diagram-3-ui.png
  training-restart-seed.json training-restart-verify.json)
mkdir -p "$OUT"
test -s "$APK" && test -s "$TEST" && test -s "$BASELINE"
export PATH="$ANDROID_HOME/platform-tools:$PATH"
if [[ -e /dev/kvm ]]; then sudo chmod a+rw /dev/kvm; fi
export ANDROID_AVD_HOME="$(mktemp -d /tmp/bbyq-c19-avd.XXXXXX)"
printf 'no\n' | "$ANDROID_HOME/cmdline-tools/latest/bin/avdmanager" create avd --force -n bbyq-c19 \
  -p "$ANDROID_AVD_HOME/bbyq-c19.avd" -k 'system-images;android-36;default;x86_64'
"$ANDROID_HOME/emulator/emulator" -avd bbyq-c19 -no-window -no-audio -no-boot-anim \
  -no-snapshot -gpu swiftshader_indirect -memory 4096 > "$OUT/emulator.log" 2>&1 &
EMU=$!
capture_personal(){
  local name partial
  while IFS= read -r name; do
    [[ "$name" =~ ^(personal|chat)-[[:alnum:]_.-]+$ ]] || continue
    partial="$OUT/$name.partial"
    if timeout 8s adb exec-out run-as "$PKG" cat "files/$name" > "$partial" 2>/dev/null && test -s "$partial"; then
      mv "$partial" "$OUT/$name"
    else rm -f "$partial"; fi
  done < <(timeout 8s adb shell run-as "$PKG" ls files 2>/dev/null | tr -d '\r')
}
finish(){
  local result=$? name partial
  capture_personal || true
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
adb shell getprop ro.build.version.sdk > "$OUT/emulator-api.txt"
adb shell settings put secure show_ime_with_hard_keyboard 1
adb shell settings put global window_animation_scale 0
adb shell settings put global transition_animation_scale 0
adb shell settings put global animator_duration_scale 0
adb install -r "$BASELINE" > "$OUT/chat-upgrade-install-old.txt"
adb install -r "$TEST"
# Seed real C18 data, then let Android preserve that data through install -r.
for phase in seed verify; do
  if [[ "$phase" = verify ]]; then
    adb shell am force-stop "$PKG"
    adb install -r "$APK" > "$OUT/chat-upgrade-install-new.txt"
  fi
  adb shell am instrument -w -e class com.bbyq.u03.ChatUpgradeTest -e chat_upgrade_phase "$phase" \
    "$PKG.test/androidx.test.runner.AndroidJUnitRunner" > "$OUT/chat-upgrade-$phase.txt" 2>&1
  cat "$OUT/chat-upgrade-$phase.txt"
  python3 - "$OUT/chat-upgrade-$phase.txt" <<'PYUPGRADE'
from pathlib import Path
import sys,re
text=Path(sys.argv[1]).read_text()
assert re.search(r'OK \(1 test\)',text),text
assert not re.search(r'FAILURES|INSTRUMENTATION_FAILED|Process crashed|shortMsg|Error in ',text),text
PYUPGRADE
done
capture_personal
adb shell am start -W -n "$PKG/com.bbyq.u03.LauncherActivity" > "$OUT/launcher.txt"
# Real touch targets are checked against Android system bars and the visible IME.
adb shell am instrument -w -e class com.bbyq.u03.PersonalInterfaceTest \
  "$PKG.test/androidx.test.runner.AndroidJUnitRunner" > "$OUT/personal-interface-tests.txt" 2>&1
cat "$OUT/personal-interface-tests.txt"
capture_personal
python3 - <<'PYUI'
from pathlib import Path
import re
text=Path('build/android-c19/personal-interface-tests.txt').read_text()
m=re.search(r'OK \((\d+) tests?\)',text)
assert m and int(m.group(1))>=5,text
assert not re.search(r'FAILURES|INSTRUMENTATION_FAILED|Process crashed|shortMsg|Error in ',text),text
PYUI

# Check the rendered transcript, chat switching/drafts and thread-scoped context.
adb shell am instrument -w -e class com.bbyq.u03.ChatContinuityTest \
  "$PKG.test/androidx.test.runner.AndroidJUnitRunner" > "$OUT/chat-continuity-tests.txt" 2>&1
cat "$OUT/chat-continuity-tests.txt"
capture_personal
python3 - <<'PYCHAT'
from pathlib import Path
import re
text=Path('build/android-c19/chat-continuity-tests.txt').read_text()
m=re.search(r'OK \((\d+) tests?\)',text)
assert m and int(m.group(1))>=4,text
assert not re.search(r'FAILURES|INSTRUMENTATION_FAILED|Process crashed|shortMsg|Error in ',text),text
PYCHAT

# User-facing learning is tested through original XI, not canned lab answers.
adb shell am instrument -w -e class com.bbyq.u03.TrainingWorkspaceTest \
  "$PKG.test/androidx.test.runner.AndroidJUnitRunner" > "$OUT/training-tests.txt" 2>&1
cat "$OUT/training-tests.txt"
python3 - <<'PYTEST'
from pathlib import Path
import re
text=Path('build/android-c19/training-tests.txt').read_text()
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
text=Path('build/android-c19/android-tests.txt').read_text()
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
capture_personal
for name in "${TRAINING_EVIDENCE[@]}"; do
  adb exec-out run-as "$PKG" cat "files/$name" > "$OUT/$name"
done

# Export measured Android laboratory outputs, not just copied Linux results.
mkdir -p "$OUT/lab"
for name in transport persistence c11 c12 cache profile stress candidate; do
  adb exec-out run-as "$PKG" cat "files/sessions/laboratory/$name-last.json" > "$OUT/lab/$name.json"
done
adb shell am start -W -n "$PKG/com.bbyq.u03.LauncherActivity" >> "$OUT/launcher.txt"
sleep 3
adb exec-out screencap -p > "$OUT/integrated-ui.png"
adb shell uiautomator dump /sdcard/c19-ui.xml >/dev/null
adb exec-out cat /sdcard/c19-ui.xml > "$OUT/integrated-ui.xml"
python3 - <<'PY'
from pathlib import Path
import json,re
out=Path('build/android-c19')
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
assert all(restart.get(name) is True for name in (
    'conversation_survived_process_restart','conversation_exact_request_replayed',
    'conversation_retry_no_duplicate_messages','conversation_query_was_read_only',
    'multiple_conversations_survived_process_restart','active_conversation_survived_process_restart',
    'thread_drafts_survived_process_restart','conversation_ui_history_survived_process_restart',
    'thread_context_survived_process_restart','thread_context_isolated_after_restart',
    'replay_kept_active_conversation'))
report['training_test_evidence']=json.loads((out/'training-test-proof.json').read_text())
training_cases=report['training_test_evidence']['cases']
assert set(training_cases)=={'native_lessons_activation_restore','joint_native_feedback','invalid_and_stale_actions','portable_export','training_ui_and_guide'}
assert all(case.get('passed') is True for case in training_cases.values())
report['android_api_tested']=int((out/'emulator-api.txt').read_text().strip())
report['personal_interface_test_count']=int(re.search(r'OK \((\d+) tests?\)',(out/'personal-interface-tests.txt').read_text()).group(1))
report['personal_interface_evidence']=json.loads((out/'personal-interface-proof.json').read_text())
personal_cases=report['personal_interface_evidence']['cases']
assert set(personal_cases)=={'P01_threeButtonAndKeyboard','P02_gestureAndKeyboard','P03_landscapeLargeFontAndSideBars','P04_nativeConversationHistoryAndRecreation','P05_modelTrainingAndIllustratedGuide'}
assert all(case.get('passed') is True for case in personal_cases.values())
assert report['personal_interface_evidence']['android_api']==report['android_api_tested']
report['personal_interface_verified']=True
report['chat_continuity_test_count']=int(re.search(r'OK \((\d+) tests?\)',(out/'chat-continuity-tests.txt').read_text()).group(1))
report['chat_continuity_evidence']=json.loads((out/'chat-continuity-proof.json').read_text())
chat_cases=report['chat_continuity_evidence']['cases']
assert set(chat_cases)=={'C01_threeTurnsKeepSixRealBubbles','C02_threadNavigationDraftsRenameArchiveAndRecreation',
    'C03_contextUsesOnlyItsConversation','C04_c18SparseViewsAndPendingRequestMigrate'}
assert all(case.get('passed') is True for case in chat_cases.values())
report['chat_continuity_verified']=True
report['chat_upgrade_evidence']={phase:json.loads((out/f'chat-upgrade-{phase}.json').read_text()) for phase in ('seed','verify')}
report['chat_upgrade_authentication']=json.loads((out/'chat-upgrade-authentication.json').read_text())
assert report['chat_upgrade_authentication']['authenticated'] is True
assert report['chat_upgrade_authentication']['only_ci_signature_changed'] is True
assert report['chat_upgrade_authentication']['all_three_ci_certificates_identical'] is True
assert all(evidence.get('passed') is True for evidence in report['chat_upgrade_evidence'].values())
upgrade=report['chat_upgrade_evidence']['verify']
assert all(upgrade.get(name) is True for name in (
    'actual_apk_upgrade','distinct_process','personal_snapshot_unchanged',
    'all_legacy_views_recovered','all_legacy_messages_preserved','exact_legacy_request_replayed',
    'replay_kept_active_conversation','no_duplicate_messages','migrated_thread_context_works'))
report['actual_C18_to_C19_upgrade_verified']=True
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

