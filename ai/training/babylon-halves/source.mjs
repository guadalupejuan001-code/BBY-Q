import fs from 'node:fs';import assert from 'node:assert/strict';import {sha} from './archive.mjs';
export const PDF_SHA='76b620d86a163a1934aebeea997f75c1c685d0ecd877f4a0854f0ab3e0e29b69';
export function bookSource(text,pdf){
 assert.equal(sha(pdf),PDF_SHA,'exact source PDF');
 const raw=text.split('\f');if(!raw.at(-1).trim())raw.pop();assert.equal(raw.length,122);
 const pages=raw.map((s,i)=>({page:i+1,half:i<61?'A':'B',text:s.replace(/[\x00-\x08\x0b\x0e-\x1f]/g,'-').replace(/\s+/g,' ').trim()}));
 const records=[];
 for(const p of pages){
  const chunks=[];let chunk='';
  for(const word of p.text.split(' ')){
   assert.ok(Buffer.byteLength(word)<=205,'word too long');
   const next=chunk?chunk+' '+word:word;if(Buffer.byteLength(next)>205){chunks.push(chunk);chunk=word;}else chunk=next;
  }if(chunk)chunks.push(chunk);
  assert.equal(chunks.join(' '),p.text,'full normalized page reconstructed');
  chunks.forEach((chunk,i)=>records.push({id:`book-p${String(p.page).padStart(3,'0')}-s${String(i+1).padStart(3,'0')}`,page:p.page,half:p.half,kind:'source_text_en',text:`bbl p${String(p.page).padStart(3,'0')} s${String(i+1).padStart(3,'0')} ${chunk}`,chunk,source_language:'en',text_sha256:sha(Buffer.from(chunk))}));
  p.sha256=sha(Buffer.from(p.text));p.chunks=chunks.length;
 }
 for(const r of records)assert.ok(Buffer.byteLength(r.text)<=224);
 return {pages,records,coverage:{source_pdf_sha256:PDF_SHA,source_page_count:122,half_A:[1,61],half_B:[62,122],page_coverage:122,normalized_text_bytes:pages.reduce((a,p)=>a+Buffer.byteLength(p.text),0),raw_text_records:records.length,normalization:'Preserves all extracted page text including front matter and footers; collapses whitespace; C0 nonwhitespace control characters become hyphens. Figures are not learned. Full original PDF included.',meaning_claim:'Complete textual ingestion is not complete understanding or numerical reasoning.',pages:pages.map(({text,...rest})=>rest)}};
}
