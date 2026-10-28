#!/usr/bin/env node
// Native black-box tests: the expected records are independent of XI code.
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';

const [runtimeArg, capsulesArg, outputArg] = process.argv.slice(2);
if (!runtimeArg || !capsulesArg || !outputArg) throw Error('usage: node test.mjs RUNTIME CAPSULES OUT');
const runtime = path.resolve(runtimeArg), capsules = path.resolve(capsulesArg), out = path.resolve(outputArg);
fs.mkdirSync(out, { recursive: true });
const state = path.join(out, 'live.rvp');
fs.copyFileSync(path.join(capsules, 'controller.rvp'), state);
const app = path.join(capsules, 'candidate.rxe');
let checks = 0, turns = 0;
function ask(input, language = 'es') {
  turns++;
  return execFileSync(runtime, ['app-turn', app, state, state, language, input],
    { encoding: 'utf8', maxBuffer: 1024 * 1024 }).trimEnd();
}
function check(condition, label) { assert.ok(condition, label); checks++ }
function equals(actual, expected, label) { assert.equal(actual, expected, label); checks++ }
function digest() { return crypto.createHash('sha256').update(fs.readFileSync(state)).digest('hex'); }

equals(ask('hola').trim(), 'Hola. Soy BBY Q.', 'E025 original greeting still works');
check(ask('hello', 'en').includes('BBY Q'), 'E025 English remains available');
check(ask('aprende que tatuy es animal').includes('Aprendí'), 'E025 native learning');
check(ask('que es tatuy').toLowerCase().includes('animal'), 'E025 factual retrieval');

const stateBytesBeforeContext = fs.statSync(state).size;
const appendStartNs = process.hrtime.bigint();
const records = [];
for (let i = 0; i < 200; i++) {
  const marker = 'ref_' + String(i).padStart(3, '0');
  const line = ('Registro ' + marker + ' | información de largo plazo; ' +
    'este fragmento documenta memoria verificable y persistencia. ').padEnd(210, 'z');
  check(Buffer.byteLength(line, 'utf8') <= 224, 'individual XI fragment limit');
  const output = ask('@ctx add ' + line);
  equals(output, 'CTX guardado #' + String(i).padStart(3, '0'), 'append stores sequential segment '+i);
  records.push(line);
}
const appendMilliseconds = Number(process.hrtime.bigint() - appendStartNs) / 1e6;
const stateBytesWithContext = fs.statSync(state).size;
const bytes = records.reduce((s, row) => s + Buffer.byteLength(row, 'utf8'), 0);
equals(ask('@ctx status'), 'CTX n=200 bytes=' + String(bytes).padStart(6,'0') + ' limite=114688', 'persisted live byte count');
for (const i of [0, 37, 100, 199]) {
  equals(ask('@ctx get ' + i), '#' + String(i).padStart(3, '0') + ' ' + records[i], 'byte-accurate indexed recall '+i);
}
equals(ask('@ctx find REF_037'), '#037 ' + records[37], 'ASCII case-insensitive search');
equals(ask('@ctx find ref_199'), '#199 ' + records[199], 'most recent long-range retrieval');
equals(ask('@ctx find sin_existencia_783'), 'CTX sin coincidencia.', 'unknown query abstains');
equals(ask('@ctx get 511'), 'CTX segmento inexistente.', 'out-of-range read abstains');
const beforeStatus = ask('@ctx status');
const beforeLast = ask('@ctx get 199');
equals(ask('@ctx add ' + 'L'.repeat(225)), 'CTX limite; no guardado.', 'oversize input is not accepted');
equals(ask('@ctx status'), beforeStatus, 'rejection preserves logical context byte count');
equals(ask('@ctx get 199'), beforeLast, 'rejection preserves the last stored fragment');
const scrub = path.join(out, 'audit-mailbox.xi');
fs.writeFileSync(scrub, '#!reverse-pc-machine-v1\\n' +
  'set r0 0\\nset r1 0\\nlabel scan_mail\\ncmp r0 255\\njge mail_done\\n' +
  'set r7 7400000000000000128\\nadd r7 r0\\nload8 r2 $r7\\nadd r1 r2\\nadd r0 1\\njmp scan_mail\\n' +
  'label mail_done\\nprint r1\\nload8 r3 7400000000000000017\\nprint r3\\nhalt\\n');
const scrubOutput=execFileSync(runtime,['run',scrub,state,state],{encoding:'utf8'});
const scrubValues=scrubOutput.split('\\n').filter(t=>t.startsWith('{')).map(t=>JSON.parse(t).value);
equals(JSON.stringify(scrubValues), JSON.stringify([0,0]), 'XI mailbox scrubbed after context commands');
equals(ask('@ctx get 000'), '#000 ' + records[0], 'leading-zero index works');
equals(ask('@ctx add puente'), 'CTX guardado #200', 'first half of boundary phrase');
equals(ask('@ctx add azul'), 'CTX guardado #201', 'second half of boundary phrase');
equals(ask('@ctx find PUENTEAZUL'), '#200 puente', 'contiguous search crosses segment boundary');
const utf8 = 'Café, piñata, ángeles y 東京.';
equals(ask('@ctx add ' + utf8), 'CTX guardado #202', 'UTF-8 fragment accepted');
equals(ask('@ctx get 202'), '#202 ' + utf8, 'UTF-8 bytes recalled exactly');
check(ask('que es tatuy').toLowerCase().includes('animal'), 'normal XI factual query survives 200+ context writes');
equals(ask('@ctx clear'), 'CTX vaciado.', 'clear command executed');
equals(ask('@ctx status'), 'CTX n=000 bytes=000000 limite=114688', 'clear resets metadata');
equals(ask('@ctx find ref_000'), 'CTX sin coincidencia.', 'cleared text cannot be retrieved');
check(ask('que es tatuy').toLowerCase().includes('animal'), 'clearing context preserves knowledge');

const fullBytesBeforeClear = bytes + Buffer.byteLength('puenteazul' + utf8, 'utf8');
const audit = path.join(out, 'audit-clear.xi');
fs.writeFileSync(audit, '#!reverse-pc-machine-v1\n' +
  'set r0 0\nset r1 0\nlabel audit_loop\ncmp r0 '+fullBytesBeforeClear+'\njge audit_end\n' +
  'set r7 8900000000000100000\nadd r7 r0\nload8 r2 $r7\nadd r1 r2\nadd r0 1\njmp audit_loop\n' +
  'label audit_end\nprint r1\nhalt\n');
const auditOutput = execFileSync(runtime,['run', audit, state, state],{encoding:'utf8'});
const auditNumbers = auditOutput.split('\n').filter(s => s.startsWith('{')).map(s=>JSON.parse(s).value);
equals(JSON.stringify(auditNumbers), JSON.stringify([0]), 'clear physically overwrites stored data');
const report = {
  version:'E027-Context-1-dev', checks, app_turns:turns, archived_records:200,
  tested_context_bytes:bytes, capacity_bytes:114688,
  append_elapsed_ms:Math.round(appendMilliseconds),
  serialized_state_bytes_before_context:stateBytesBeforeContext,
  serialized_state_bytes_after_200_records:stateBytesWithContext,
  evaluated:['original greeting', 'persistent original facts', '200 append cycles',
   'indexed retrieval across process restarts', 'case-insensitive byte search',
   'search across segment boundary', 'UTF-8', 'oversize rejection', 'physical erase',
   'knowledge isolation'],
  limitation:'No semantic synthesis of whole history; lexical retrieval is an explicit operation.',
  source:'Native pinned XI runtime, fresh disposable state for every CI test.'
};
fs.writeFileSync(path.join(out,'tests.json'), JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
