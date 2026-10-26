#!/usr/bin/env bash
# E010 test TRANSPORT. All intelligence/learning/planning runs in owner XI.
# No host training models, hardcoded AI answers or imported vocabularies.
set -euo pipefail
R="$1"
seed_state="$2"
B=7200000000000000000
mkdir -p evidence
cp "$seed_state" state.rvp
cp state.rvp evidence/original-E009-before-school.rvp
"$R" run ai/xi/school/birth.xi state.rvp born.rvp > evidence/birth.jsonl
mv born.rvp state.rvp
reg() {
  grep -m1 "\"register\":\"$2\"" "$1" | sed -n 's/.*"value":\([0-9][0-9]*\).*/\1/p'
}
emit_word() {
  local offset="$1" word="$2" i=0 n
  printf 'store8 %s %s\n' "$((B+offset))" "$(printf %s "$word" | wc -c)"
  for n in $(printf %s "$word" | od -An -tu1); do
    printf 'store8 %s %s\n' "$((B+offset+1+i))" "$n"
    i=$((i+1))
  done
}
decode() {
  local value oct character result=""
  while read -r value; do
    printf -v oct '%03o' "$value"
    printf -v character '%b' "\\$oct"
    result+="$character"
  done < <(grep '"register":"' "$1" | sed -n 's/.*"value":\([0-9][0-9]*\).*/\1/p')
  printf '%s' "$result"
}
stage() {
  local program="$1"
  "$R" run lesson.xi state.rvp incoming.rvp > /dev/null
  "$R" run "ai/xi/school/$program.xi" incoming.rvp executed.rvp > "evidence/last-$program.jsonl"
  mv executed.rvp state.rvp
}
teach() {
  local d="$1" x="$2" y="$3" z="$4" es="$5" en="$6"
  {
    echo '#!reverse-pc-machine-v1'
    printf 'store8 %s 1\n' "$((B+100))"
    printf 'store8 %s %s\n' "$((B+101))" "$d"
    printf 'store8 %s %s\n' "$((B+102))" "$x"
    printf 'store8 %s %s\n' "$((B+103))" "$y"
    printf 'store8 %s %s\n' "$((B+104))" "$z"
    emit_word 105 "$es"
    emit_word 115 "$en"
  } > lesson.xi
  stage learn
}
setlang() {
  local lang="$1"
  printf '#!reverse-pc-machine-v1\nstore8 %s %s\n' "$((B+80))" "$lang" > lesson.xi
  stage set-language
}
observe() {
  local d="$1" x="$2" y="$3" z="$4" slot="$5" es="$6" en="$7" label="$8"
  {
    echo '#!reverse-pc-machine-v1'
    printf 'store8 %s 2\n' "$((B+100))"
    printf 'store8 %s %s\n' "$((B+101))" "$d"
    printf 'store8 %s %s\n' "$((B+102))" "$x"
    printf 'store8 %s %s\n' "$((B+103))" "$y"
    printf 'store8 %s %s\n' "$((B+104))" "$z"
  } > lesson.xi
  "$R" run lesson.xi state.rvp incoming.rvp > /dev/null
  "$R" run ai/xi/school/recognize.xi incoming.rvp classified.rvp > "evidence/$label-classified.jsonl"
  "$R" run ai/xi/school/name.xi classified.rvp unchanged.rvp > "evidence/$label-spoken.jsonl"
  cmp classified.rvp unchanged.rvp
  local actual expected
  actual="$(decode "evidence/$label-spoken.jsonl")"
  if [ "$mode" = es ];then expected="$es";else expected="$en";fi
  if [ "$actual" != "$expected" ];then
    echo "E010 recognition mismatch $label: got [$actual] expected [$expected]" >&2;exit 1
  fi
  # The independent examiner reveals the answer only AFTER prediction.
  printf '#!reverse-pc-machine-v1\nstore8 %s 1\nstore8 %s %s\n' \
    "$((B+300))" "$((B+301))" "$slot" > feedback.xi
  "$R" run feedback.xi classified.rvp graded-input.rvp > /dev/null
  "$R" run ai/xi/school/grade.xi graded-input.rvp scored.rvp > "evidence/$label-score.jsonl"
  test "$(reg "evidence/$label-score.jsonl" r11)" -eq 1
  mv scored.rvp state.rvp
  echo "$mode|$label|$actual" >> evidence/bilingual-transcript.psv
}
operator_example() {
  local op="$1" before="$2" amount="$3" after="$4"
  printf '#!reverse-pc-machine-v1\nstore8 %s 1\nstore8 %s %s\nstore8 %s %s\nstore8 %s %s\nstore8 %s %s\n' \
    "$((B+340))" "$((B+341))" "$op" "$((B+342))" "$before" \
    "$((B+343))" "$amount" "$((B+344))" "$after" > lesson.xi
  stage learn-operation
}
math_case() {
  local before="$1" amount="$2" op="$3" expected_count="$4" es="$5" en="$6" label="$7"
  printf '#!reverse-pc-machine-v1\nstore8 %s 1\nstore8 %s %s\nstore8 %s %s\nstore8 %s %s\n' \
    "$((B+320))" "$((B+321))" "$before" "$((B+322))" "$amount" \
    "$((B+323))" "$op" > lesson.xi
  "$R" run lesson.xi state.rvp equation.rvp > /dev/null
  "$R" run ai/xi/school/calculate.xi equation.rvp result.rvp > "evidence/$label-equation.jsonl"
  "$R" run ai/xi/school/name.xi result.rvp unchanged.rvp > "evidence/$label-result.jsonl"
  cmp result.rvp unchanged.rvp
  local actual expected
  actual="$(decode "evidence/$label-result.jsonl")"
  if [ "$mode" = es ];then expected="$es";else expected="$en";fi
  if [ "$actual" != "$expected" ];then
    echo "E010 operation mismatch $label: got [$actual] expected [$expected]" >&2;exit 1
  fi
  printf '#!reverse-pc-machine-v1\nstore8 %s 1\nstore8 %s %s\n' \
    "$((B+350))" "$((B+351))" "$expected_count" > feedback.xi
  "$R" run feedback.xi result.rvp scoring.rvp > /dev/null
  "$R" run ai/xi/school/grade-math.xi scoring.rvp evaluated.rvp > "evidence/$label-grade.jsonl"
  test "$(reg "evidence/$label-grade.jsonl" r10)" -eq 1
  mv evaluated.rvp state.rvp
  echo "$mode|$label|$actual" >> evidence/bilingual-transcript.psv
}
# The first curriculum provides 22 observations. Repeat without cloning memory
# to require at least two consistent witnesses for recognition.
for pass in 1 2; do
  while IFS='|' read -r d x y z es en; do
    [[ "$d" != \#* && -n "$d" ]] || continue
    teach "$d" "$x" "$y" "$z" "$es" "$en"
  done < ai/xi/school/data/observations-v1.psv
done
"$R" run ai/xi/school/audit.xi state.rvp audited.rvp > evidence/initial-audit.jsonl
cmp state.rvp audited.rvp
cp state.rvp evidence/learned-bilingual-concepts.rvp
# Contradiction guard: never silently overwrite 'rojo/red' with 'azul/blue'.
{
  echo '#!reverse-pc-machine-v1'
  printf 'store8 %s 1\n' "$((B+100))"
  printf 'store8 %s 1\n' "$((B+101))"
  printf 'store8 %s 237\n' "$((B+102))"
  printf 'store8 %s 34\n' "$((B+103))"
  printf 'store8 %s 27\n' "$((B+104))"
  emit_word 105 azul
  emit_word 115 blue
} > lesson.xi
"$R" run lesson.xi state.rvp contradicted.rvp > /dev/null
if "$R" run ai/xi/school/learn.xi contradicted.rvp illegal.rvp > /dev/null;then
  echo "Conflicting bilingual label was accepted!" >&2;exit 1
fi
test ! -f illegal.rvp
: > evidence/bilingual-transcript.psv
for mode in es en; do
  lang=1
  if [ "$mode" = en ];then lang=2;fi
  setlang "$lang"
  n=0
  while IFS='|' read -r d x y z slot es en; do
    [[ "$d" != \#* && -n "$d" ]] || continue
    n=$((n+1))
    observe "$d" "$x" "$y" "$z" "$slot" "$es" "$en" "$n-$mode"
  done < ai/xi/school/data/holdout-v1.psv
done
"$R" run ai/xi/school/next.xi state.rvp next.rvp > evidence/recognition-milestone.jsonl
test "$(reg evidence/recognition-milestone.jsonl r12)" -eq 1
mv next.rvp state.rvp
# Introduce effects as OBSERVED interventions, not answers in a lookup table.
operator_example 1 2 1 3
operator_example 1 4 2 6
operator_example 2 6 2 4
operator_example 2 7 3 4
# Wrong evidence must not overwrite an operator model.
printf '#!reverse-pc-machine-v1\nstore8 %s 1\nstore8 %s 1\nstore8 %s 3\nstore8 %s 2\nstore8 %s 1\n' \
  "$((B+340))" "$((B+341))" "$((B+342))" "$((B+343))" "$((B+344))" > lesson.xi
"$R" run lesson.xi state.rvp inconsistent.rvp > /dev/null
if "$R" run ai/xi/school/learn-operation.xi inconsistent.rvp wrong-math.rvp > /dev/null;then
  echo "Contradictory operation was accepted!" >&2;exit 1
fi
test ! -f wrong-math.rvp
for mode in en es; do
  lang=1
  if [ "$mode" = en ];then lang=2;fi
  setlang "$lang"
  math_case 3 2 1 5 cinco five "new-3plus2-$mode"
  math_case 5 4 1 9 nueve nine "new-5plus4-$mode"
  math_case 9 2 2 7 siete seven "new-9minus2-$mode"
  math_case 5 3 2 2 dos two "new-5minus3-$mode"
  math_case 9 3 1 255 '?' '?' "unknown-9plus3-$mode"
done
"$R" run ai/xi/school/next.xi state.rvp next.rvp > evidence/milestone-final.jsonl
test "$(reg evidence/milestone-final.jsonl r12)" -eq 2
mv next.rvp state.rvp
"$R" run ai/xi/school/audit.xi state.rvp audited.rvp > evidence/final-audit.jsonl
cmp state.rvp audited.rvp
"$R" run ai/xi/e008/audit-organism.xi state.rvp old-audit.rvp > /dev/null
cmp state.rvp old-audit.rvp
"$R" run ai/xi/language/audit.xi state.rvp lang-audit.rvp > /dev/null
cmp state.rvp lang-audit.rvp
cp state.rvp evidence/BBYQ_E010_ES_EN_Development.rvp
echo 'E010 PASS: 22 concepts, 60 independent naming tests in ES/EN, 10 new arithmetic tests, original E009 unchanged' | tee evidence/final-summary.txt
