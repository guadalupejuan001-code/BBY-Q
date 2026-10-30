import {test} from 'node:test';
import assert from 'node:assert/strict';
import {parseState,comparePreservation} from './state.mjs';

function state(entries,extra='MXIM1 0',counter=1) {
  const kernel = Buffer.from('fixed-kernel');
  const body = Buffer.from(`MXIM2 ${counter}\n${extra}\n`+entries.map(([address,value]) => `O ${address} ${value}\n`).join(''));
  const header = Buffer.alloc(29);header.write('RVPC2');header.writeBigUInt64LE(BigInt(kernel.length),5);header.writeBigUInt64LE(BigInt(body.length),13);
  return parseState(Buffer.concat([header,kernel,body]));
}
const contract={allowed_additions:[{name:'new bank',start:'9180000000000000000',end_exclusive:'9180000000001000000',requires_empty_baseline:true,requires_nonempty_candidate:true}],must_be_zero:[{name:'scratch',start:'9180000000001000000',end_exclusive:'9180000000002000000'}],allowed_serializer_counters:['MXIM2']};
const original=['7100000000000001000',7],newCell=['9180000000000000000',88];
test('permits an added bank while preserving old data and serializer metadata',()=>assert.equal(comparePreservation(state([original]),state([original,newCell],'MXIM1 0',2),contract).ok,true));
test('rejects replacement or removal of an original learned byte',()=>{
  for(const candidate of [state([[original[0],8],newCell]),state([newCell])])assert.ok(comparePreservation(state([original]),candidate,contract).errors.some(x=>x.kind==='historical_state_changed'));
});
test('rejects filling an implicit zero in an existing historical namespace',()=>assert.ok(comparePreservation(state([original]),state([original,newCell,['7100000000000001001',1]]),contract).errors.some(x=>x.kind==='historical_state_changed')));
test('rejects an occupied baseline range, missing installation and leftover scratch',()=>{
  assert.ok(comparePreservation(state([original,newCell]),state([original,newCell]),contract).errors.some(x=>x.kind==='new_region_already_occupied'));
  assert.ok(comparePreservation(state([original]),state([original]),contract).errors.some(x=>x.kind==='new_region_not_installed'));
  assert.ok(comparePreservation(state([original]),state([original,newCell,['9180000000001000000',1]]),contract).errors.some(x=>x.kind==='dirty_scratch'));
});
test('rejects changes to opaque state records and counter resets',()=>{
  assert.ok(comparePreservation(state([original]),state([original,newCell],'MXIM1 1'),contract).errors.some(x=>x.kind==='non_override_records_changed'));
  assert.ok(comparePreservation(state([original],'MXIM1 0',2),state([original,newCell]),contract).errors.some(x=>x.kind==='serializer_counter_changed'));
});
test('rejects duplicate overrides, truncation and ranges outside signed XI pointers',()=>{
  assert.throws(()=>state([original,original]),/duplicate/);
  assert.throws(()=>parseState(state([original]).bytes.subarray(0,40)),/length/);
  assert.throws(()=>comparePreservation(state([original]),state([original,newCell]),{allowed_additions:[{name:'out-of-range',start:'9300000000000000000',end_exclusive:'9300000000001000000'}]}),/signed XI/);
});
