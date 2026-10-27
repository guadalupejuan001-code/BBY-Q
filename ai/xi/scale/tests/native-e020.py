#!/usr/bin/env python3
"""Validate a million-example XI campaign, publish the learned state, examine it.

All expected results are examiner-only. Text inference receives raw bytes and
output language, and consults the independently learned concept records in XI.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import statistics
import subprocess

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[2]
spec=importlib.util.spec_from_file_location('scale',ROOT/'tests/native-scale.py')
scale=importlib.util.module_from_spec(spec);spec.loader.exec_module(scale)
e019=scale.e019;e018=e019.e018;e017=e019.e017
M,D=scale.M,e017.D
snapshot,stores=scale.snapshot,e017.stores
Session,decode_result=e017.Session,e017.decode_result
CHECKPOINT='BBYQ_E020_Million_Arithmetic_ES_EN.rvp'
TRAINING_ROWS=2097152


def put32(address,value):return [(address+i,(value>>(8*i))&255) for i in range(4)]


def result(value,language):
    names={1:['cero','uno','dos','tres','cuatro','cinco','seis','siete','ocho','nueve'],
           2:['zero','one','two','three','four','five','six','seven','eight','nine']}
    number=names[language][value] if 0<=value<=9 else str(value)
    return e017.conversation.ACTS[5,language]+' '+number+'.'


def word(e,concept,language,text,reject=False):
    data=('dos '+text+' tres').encode()
    fields=[(D+16,1),(D+17,len(data)),(M+24,concept),(M+25,language)]
    fields += [(D+128+i,b) for i,b in enumerate(data)]
    program=subprocess.check_output(['bash',str(ROOT.parent/'dialogue/link.sh'),'scale-word'],text=True).split('\n',1)[1]
    e.run(stores(fields)+program,reject=reject)


def audit(e):
    before=e.state.read_bytes();_,raw=e.run((ROOT/'audit.xi').read_text())
    assert e.state.read_bytes()==before
    return [json.loads(line) for line in raw.splitlines() if line.startswith('{')]


def finish_training(e,training):
    assert training['training_examples']==TRAINING_ROWS
    e.processed=TRAINING_ROWS;mem=e.preserve()
    assert scale.u32(mem,M+12)==0
    for concept,family in scale.FAMILIES.items():
        a=M+128+(concept-1)*64
        assert mem[a]==1<<(family-1) and scale.u32(mem,a+4)==262144
    e.run((ROOT/'seal.xi').read_text(),reject=True)
    for concept,_,language,text in scale.rows():word(e,int(concept),int(language),text)
    assert e.preserve()[M+4]==20
    word(e,2,1,'por')
    word(e,3,1,'por',reject=True)
    word(e,4,1,'dos',reject=True)
    word(e,4,1,'mas',reject=True)
    # These a/b ranges do not overlap the training grid for any concept.
    training_fields={a:b for a,b in mem.items() if M+128<=a<M+640}
    for concept,family in sorted(scale.FAMILIES.items()):
        observations=[scale.teacher(family,700+i,1100+3*i) for i in range(256)]
        e.batch(concept,observations,mode=1)
    mem=e.preserve();assert scale.u32(mem,M+12)==2048
    assert all(mem.get(a,0)==b for a,b in training_fields.items() if (a-M-128)%64<16)
    # Incorrect labels must roll back the entire batch, including an earlier
    # correct row and all temporary transport writes.
    e.batch(4,[(600,800,1400),(601,801,999)],mode=1,reject=True)
    e.run(stores([(M+17,9),(M+18,1)])+e.batch_code,reject=True)
    e.run(stores([(M+17,1),(M+18,1),(M+19,4)])+e.batch_code,reject=True)
    audit(e)
    e.run((ROOT/'seal.xi').read_text());mem=e.preserve()
    for concept,family in scale.FAMILIES.items():
        a=M+128+(concept-1)*64
        assert mem[a+2]==family and scale.u32(mem,a+16)==256
    assert mem[M+3]==1
    e.batch(2,[(7,2,14)],reject=True)
    stats=audit(e)
    return e.state.read_bytes(),stats


def independent_text_exam(e,binary,learned):
    before=e.checks;timings=[]
    with Session(binary,e.state,e.program) as session:
        for concept,family,language,text in scale.rows():
            family,language=int(family),int(language)
            a,b=(8,2) if family==4 else (7,2)
            value=scale.teacher(family,a//b,b)[2] if family==4 else scale.teacher(family,a,b)[2]
            e.check(f'{a} {text} {b}',result(value,language),language,session=session)
        for concept,family in sorted(scale.FAMILIES.items()):
            aliases=[text for c,_,_,text in scale.rows() if int(c)==concept]
            for i in range(128):
                if family==3:a,b=513+17*i,2+i%7
                elif family==4:a,b=(513+i)*(2+i%7),2+i%7
                elif family==1:a,b=5000+17*i,513+i
                elif family==5:a,b=7000+13*i,513+i
                else:a,b=1000+13*i,513+3*i
                # Independently constructed result; never sent into inference.
                value={1:lambda:a-b,2:lambda:a+b,3:lambda:a*b,4:lambda:a//b,
                       5:lambda:a%b,6:lambda:min(a,b),7:lambda:max(a,b),8:lambda:abs(a-b)}[family]()
                text=f'{a} {aliases[i%len(aliases)]} {b}'
                if i%3==0:text=text.upper()+'?'
                language=1+i%2
                e.check(text,result(value,language),language,session=session);timings.append(e.times[-1])
        for text,value,language in [('dos por tres',6,1),('eight times nine',72,2),
                                   ('ocho dividido dos',4,1),('nueve mínimo dos',2,1),
                                   ('7 maximum dos',7,2),('tres por cuatro mas dos',14,1),
                                   ('dividido dos',7,1),('distancia 20',13,1),
                                   ('42 resto 5 por 3',6,1)]:
            e.check(text,result(value,language),language,session=session)
        for text in ['cinco dividido dos','8 dividido 0','8 resto 0','65535 por 65535',
                     '65535 suma uno','dos inventado tres','dos mas tres por cuatro',
                     'two plus three times four','mas uno']:
            e.check(text,e017.conversation.ACTS[3,1],session=session)
        metrics=session.metrics()
    e.state.write_bytes(learned)
    print('E020_UNSEEN_TEXT_ARITHMETIC_AND_CHAINING_PASS',e.checks-before,flush=True)
    return {'text_checks':e.checks-before,'unseen_numeric_queries':1024,
            'query_ms':{'median':statistics.median(timings),'p95':sorted(timings)[int(.95*len(timings))-1]},
            'session_metrics':metrics}


def writer_lifecycle(e,binary,learned):
    e.state.write_bytes(learned)
    with Session(binary,e.state,e.program) as owner:
        e.check('7 por 2',result(14,1),session=owner)
        with Session(binary,e.state,e.program) as blocked:
            try:blocked.request('hola');raise AssertionError('second writer accepted')
            except RuntimeError as error:assert 'active writer' in str(error)
        cli=['bash',str(ROOT.parent/'knowledge/text.sh'),e.runtime,str(e.state),'7 por 2','es']
        blocked=subprocess.run(cli,capture_output=True,text=True)
        assert blocked.returncode!=0 and 'active writer' in blocked.stderr
    # Kernel ownership must disappear even if a process cannot run destructors.
    owner=Session(binary,e.state,e.program)
    try:
        owner.request('7 por 2');owner.process.kill()
    finally:owner.close()
    with Session(binary,e.state,e.program) as restarted:
        e.check('dividido dos',result(7,1),session=restarted)
    for _ in range(50):
        with Session(binary,e.state,e.program) as restarted:
            e.check('7 por 2',result(14,1),session=restarted)
    assert not Path(str(e.state)+'.lock').exists()
    assert Path(str(e.state)+'.writer').is_file()
    legacy=Path(str(e.state)+'.lock');legacy.mkdir()
    try:
        with Session(binary,e.state,e.program) as blocked:
            try:blocked.request('hola');raise AssertionError('foreign lock ignored')
            except RuntimeError as error:assert 'active writer' in str(error)
        assert legacy.is_dir()
    finally:legacy.rmdir()
    e.state.write_bytes(learned)
    print('E020_KERNEL_WRITER_EXCLUSION_50_RESTARTS_AND_KILLED_OWNER_PASS',flush=True)


def experimental_controls(runtime,binary,learned,program,out):
    # Same spelling and same XI source, different supplied consequences.
    c=scale.Campaign(runtime,out/'counterfactual');c.state.write_bytes(learned)
    c.processed=TRAINING_ROWS-262144
    a=M+128+64
    fields=[(M+3,0)]+[(a+i,0) for i in range(64)]+[(a,255)]
    fields+=put32(M+8,c.processed)+put32(M+12,2048-256)
    c.run(stores(fields))
    for offset in [0,1024]:
        c.batch(2,[scale.teacher(6,i//512,i%512+1) for i in range(offset,offset+1024)])
    c.batch(2,[scale.teacher(6,700+i,1100+3*i) for i in range(256)],mode=1)
    c.preserve();c.run((ROOT/'seal.xi').read_text());audit(c)
    with Session(binary,c.state,program) as session:
        raw,_=session.request('siete por dos');assert decode_result(raw)==result(2,1)
    # Unique fit to one repeated pair is insufficient for promotion.
    c=scale.Campaign(runtime,out/'repeated');c.state.write_bytes(learned)
    c.processed=TRAINING_ROWS-262144;c.run(stores(fields))
    c.batch(2,[(2,3,6)]*1024);c.batch(2,[(2,3,6)]*1024)
    c.batch(2,[(2,3,6)]*256,mode=1)
    assert snapshot(c.state)[1].get(a+3,0)==0
    c.run((ROOT/'seal.xi').read_text(),reject=True)
    print('E020_COUNTERFACTUAL_WORD_MEANING_AND_REPETITION_CONTROLS_PASS',flush=True)


def diagnostic(e,binary,learned,parent):
    rows=[];scores={}
    for stage,state in [('before',parent),('after',learned)]:
        e.state.write_bytes(state);correct=0
        with Session(binary,e.state,e.program) as session:
            for _,family,language,text in scale.rows():
                family,language=int(family),int(language)
                a,b=(8,2) if family==4 else (7,2)
                value=a//b if family==4 else scale.teacher(family,a,b)[2]
                q=f'{a} {text} {b}';raw,ms=session.request(q,language);answer=decode_result(raw)
                ok=answer==result(value,language);correct+=ok
                rows.append({'stage':stage,'input':q,'language':language,'output':answer,'expected':result(value,language),'pass':ok,'ms':ms})
        scores[stage]={'correct':correct,'total':20}
    e.state.write_bytes(learned)
    return {'score':scores,'scope':'20 operator spellings; not a general intelligence score','transcript':rows}


def main():
    p=argparse.ArgumentParser();p.add_argument('runtime');p.add_argument('binary');p.add_argument('trained_state');p.add_argument('training_report')
    p.add_argument('--out',default='evidence/e020');p.add_argument('--smoke',action='store_true');args=p.parse_args()
    training=json.loads(Path(args.training_report).read_text());out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
    school=scale.Campaign(args.runtime,out/'school');school.state.write_bytes(Path(args.trained_state).read_bytes())
    learned,stats=finish_training(school,training);checkpoint=out/CHECKPOINT;checkpoint.write_bytes(learned)
    sha=hashlib.sha256(learned).hexdigest()
    print('TRAINED_E020',sha,len(learned),flush=True)
    e=e018.Examiner(args.runtime,checkpoint,out/'exam',expected_parent=sha);binary=Path(args.binary).resolve()
    writer_lifecycle(e,binary,learned)
    report=independent_text_exam(e,binary,learned)
    experimental_controls(args.runtime,binary,learned,e.program,out)
    diag=diagnostic(e,binary,learned,school.parent)
    if not args.smoke:
        e019.controls(e,binary,learned)
        report['e019_context_regression']=e019.novel_dialogues(e,binary,learned,4)
        e019.restart_and_reset(e,binary,learned)
        report['e018_regression']=e018.novel_dialogues(e,binary,learned,20)
        e018.interfaces_and_rollback(e,binary,learned)
        e018.retention(e,binary,learned)
        e017.audit(e)
    e.state.write_bytes(learned)
    report.update({'stage':'E020','parent_sha256':scale.PARENT_SHA,'learned_sha256':sha,'checkpoint_bytes':len(learned),
        'training':training,'validation_examples':2048,'training_grid':[512,512],'independent_validation':True,
        'opaque_numerical_concepts':8,'new_operator_spellings':20,'new_primitive_families':6,
        'candidate_primitives_are_designed':True,'spelling_to_primitive_is_learned':True,
        'previous_all_logical_bytes_unchanged':True,'complete_corpus_rows_retained':0,
        'first_input_pairs_retained_for_diversity':8,'memory_stats':stats,
        'query_checks':e.checks,'limits':{'integer_min':0,'integer_max':65535,'effects_per_expression':7,
            'batch_rows':1024,'batch_input_bytes':10240,'operand_1_training':'u32','consequence_training':'i32'},
        'open_conversation_achieved':False,'intelligence':'XI only; same RVPC2 and pinned REVERSE-PC/Mundo X',
        'data':'synthetic labeled numerical experiences; not millions of conversations or world facts',
        'diagnostic_score':diag['score']})
    for file,data in [('results.json',report),('diagnostic.json',diag)]:
        (out/file).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    (out/'raw.jsonl').write_text(''.join(json.dumps(row,ensure_ascii=False)+'\n' for row in e.transcript))
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':main()
