// F004 build-time XI transformation. No inference or model responses occur in JS.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
export const CAPACITY=4096;
export const BYTE_CAPACITY=CAPACITY*224;
const sha=s=>createHash('sha256').update(s).digest('hex');
export function patchMemory(original){
 const changes=[];let src=original;
 function rep(before,after,n=1){const found=src.split(before).length-1;assert.equal(found,n,'patch anchor count: '+before);src=src.split(before).join(after);changes.push({before,after,count:n});}
 // Two-byte fact identifiers use CAPACITY as an out-of-range sentinel.
 for(const address of ['9000000000000000401','9000000000000000403']){
  rep(`store8 ${address} 2`,`store8 ${address} 16`);
  rep(`load8 r3 ${address}\ncmp r3 2`,`load8 r3 ${address}\ncmp r3 16`,2);
 }
 rep('cmp r4 512\njge e28_scan_done','cmp r4 4096\njge e28_scan_done');
 rep('cmp r8 512\njne e28_duplicate_compare','cmp r8 4096\njne e28_duplicate_compare',2);
 rep('cmp r4 512\njge lctx_full','cmp r4 4096\njge lctx_full');
 rep('cmp r10 114688','cmp r10 917504');
 rep('set r5 114688','set r5 917504');rep('cmp r5 114688','cmp r5 917504');
 // Enlarged metadata [1024,17408) would overlap the old find scratch table at 5000.
 // Relocate only this scratch area to [80000,80256), below the data area at 100000.
 rep('8900000000000005000','8900000000000080000',4);
 rep('cmp r10 81\njgt e28_scan_next','cmp r10 225\njgt e28_scan_next');
 rep('cmp r10 80\njgt e28_scan_next','cmp r10 224\njgt e28_scan_next');
 rep('label lctx_get\nset r4 0\nset r0 9\ncmp r9 12','label lctx_get\nset r4 0\nset r0 9\ncmp r9 13');
 const print=s=>[...s].map(c=>`set r14 ${c.charCodeAt(0)}\nprint r14`).join('\n');
 rep(print('limite=114688'),print('limite=917504'));
 // Keep all existing 3-digit IDs stable; render a fourth digit only at >=1000.
 const a=src.indexOf('label e28_scan_init'),b=src.indexOf('label lctx_finish\n');
 assert.ok(a>0&&b>a);let body=src.slice(a,b),i=0;
 const pattern='mov r0 r4\nmov r8 r0\ndiv r8 100';
 assert.equal(body.split(pattern).length-1,4);
 body=body.replaceAll(pattern,()=>{const label=`f004_id_${i++}`;return `mov r0 r4\ncmp r0 1000\njlt ${label}\nmov r8 r0\ndiv r8 1000\nadd r8 48\nmov r14 r8\nprint r14\nmod r0 1000\nlabel ${label}\nmov r8 r0\ndiv r8 100`;});
 src=src.slice(0,a)+body+src.slice(b);
 changes.push({kind:'four_digit_ids',sites:i});
 return {source:src,audit:{capacity_before:512,capacity_after:CAPACITY,bytes_before:114688,bytes_after:BYTE_CAPACITY,record_bytes:224,input_bytes:255,subject_bytes:48,reader_value_before:80,reader_value_after:224,find_scratch_before:'8900000000000005000',find_scratch_after:'8900000000000080000',original_sha256:sha(original),patched_sha256:sha(src),changes}};
}
