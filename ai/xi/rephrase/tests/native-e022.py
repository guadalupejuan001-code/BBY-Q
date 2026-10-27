#!/usr/bin/env python3
"""Continue E021 with native learned query rewrites; examiner stays external."""
import argparse,base64,gzip,hashlib,importlib.util,json,statistics,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[2]
N=8100000000000000000
PARENT_SHA='3246c34cb2d51037476f206020c55d8453a3060a4d2c511887c4b3fb3bdb4b1b'
spec=importlib.util.spec_from_file_location('e021',ROOT.parent/'lingua/tests/native-e021.py')
e021=importlib.util.module_from_spec(spec);spec.loader.exec_module(e021)
e019,e018,e017=e021.e019,e021.e018,e021.e017
snapshot,stores,frame=e017.snapshot,e017.stores,e017.frame
U,K,C=e017.U,e017.K,e017.C
Session,decode_result=e017.Session,e017.decode_result
RULES=json.loads((ROOT/'data/rules.json').read_text())
CHECKPOINT='BBYQ_E022_Compositional_Requests_ES_EN.rvp'


class Examiner(e021.Examiner):
    def __init__(self,runtime,parent,out):
        e018.Examiner.__init__(self,runtime,parent,out,expected_parent=PARENT_SHA)
        for name in ['rephrase-teach','rephrase-seal','rephrase-audit']:
            self.programs[name]=subprocess.check_output(['bash',str(ROOT.parent/'knowledge/link.sh'),name],text=True).split('\n',1)[1]

    def pair(self,rule,labels,source,target,language=1,reject=False):
        roles={r for r in ['S','P','O'] if labels.get(r,0)}
        intent=1 if roles=={'S','P'} else (8 if roles=={'S'} else (2 if roles=={'S','P','O'} else 5))
        fields=[(N+16,rule['id']),(N+17,rule['mode']),(N+18,rule['scope']),(N+19,0),(N+20,len(target.encode())),
                (U+176,rule['id']),(U+177,intent),(U+178,0)]
        fields+=e017.wide(U+180,labels.get('S',0))+e017.wide(U+182,labels.get('P',0))+e017.wide(U+184,labels.get('O',0))
        fields += [(N+512+i,b) for i,b in enumerate(target.encode())]
        self.run(frame(source,language)+stores(fields).split('\n',1)[1]+self.programs['rephrase-teach'],reject=reject)

    def model_audit(self):
        before=self.state.read_bytes();out=self.run('#!reverse-pc-machine-v1\n'+self.programs['rephrase-audit'])
        assert self.state.read_bytes()==before
        return [json.loads(x) for x in out.splitlines() if x.startswith('{')]


def u32(m,a):return sum(m.get(a+i,0)<<(8*i) for i in range(4))


def train(e):
    started=time.perf_counter();e.run((ROOT/'birth.xi').read_text())
    lex,_=e021.lang.vocabulary(snapshot(e.state)[1]);next_id=e017.u16(snapshot(e.state)[1],U+4);added=[]
    for rule in RULES:
        for text in [rule['source'],rule['target']]:
            for word in text.split():
                if word.startswith('{') or word in lex:continue
                e.word(next_id,3,1,word);lex[word]=(next_id,3,1);added.append(word);next_id+=1
    for rule in RULES:
        has_s='{S}' in rule['source'];has_p='{P}' in rule['source']
        english=rule['source'].split()[0] in ['and','as','which','what','give','can','could','tell','please','a','briefly','about','of','in']
        for s,p in ([(5,25),(71,28)] if has_s or has_p else [(5,25)]):
            labels={}
            if has_s:labels['S']=s
            if has_p:labels['P']=p
            values={'S':('cat' if s==5 else 'plant') if english else ('gato' if s==5 else 'planta'),
                    'P':('need' if p==25 else 'use') if english else ('necesita' if p==25 else 'utiliza')}
            e.pair(rule,labels,rule['source'].format(**values),rule['target'].format(**values),2 if english else 1)
        m=snapshot(e.state)[1]
        for bank in [10000,20000]:
            a=N+bank+(rule['id']-1)*96
            assert m.get(a+2)==1,('unresolved rewrite',rule['id'],bank,rule)
    e018.restore_context(e)
    core,m,bindings=snapshot(e.state);assert core==e.original[0] and bindings==e.original[2]
    assert all(m.get(a,0)==v for a,v in e.original[1].items() if a not in {U+4,U+5,U+6,U+7})
    old_count=e017.u16(e.original[1],U+6);old_next=e017.u16(e.original[1],U+4)
    def allowed(a):return (N<=a<N+100000 or a in {U+4,U+5,U+6,U+7} or U+100000+old_count*40<=a<U+100000+e017.u16(m,U+6)*40 or U+20000+old_next<=a<U+20000+e017.u16(m,U+4))
    assert all(allowed(a) for a,v in m.items() if v!=e.original[1].get(a,0)), 'undeclared learned-state change'
    assert u32(m,N+8)==sum(2 if '{S}' in f['source'] or '{P}' in f['source'] else 1 for f in RULES)
    e.run('#!reverse-pc-machine-v1\n'+e.programs['rephrase-seal']);e.model_audit()
    return e.state.read_bytes(),{'training_seconds':time.perf_counter()-started,'paired_examples':u32(m,N+8),'learned_rewrite_rules':len(RULES),'new_lexical_entries':len(added),'new_words':added,'old_training_replayed':False}


def smoke(e,binary,learned):
    with Session(binary,e.state,e.program) as ss:
        e.lesson('aprende que neral es clasea',session=ss)
        e.lesson('aprende que alterna es claseb',session=ss)
        cases=[('puedes hablarme un poco de neral',1,'definition'),('podrías explicarme un poco sobre neral',1,'definition'),
               ('give me some information about neral',2,'definition'),('can you tell me a little about neral',2,'definition'),
               ('y hablando de neral qué requiere',1,'require'),('qué es lo que requiere neral',1,'require'),
               ('me interesa conocer lo que requiere neral',1,'require'),('which resources does neral require',2,'require'),
               ('say what neral requires in other words',2,'require'),('oye, qué requiere neral',1,'require')]
        for q,l,kind in cases:
            expected=e021.answer('neral',l,kind);e.check(q,expected,l,session=ss)
            print('E022_PASS',q,'->',expected,flush=True)
    e.state.write_bytes(learned)



def expected_answer(subject,language,kind):
    if kind=='reach':return e021.SURFACE[8,language]+' '+subject.capitalize()+(' alcanza destino022.' if language==1 else ' reaches destino022.')
    return e021.answer(subject,language,kind)


def pct(times):return {'median':statistics.median(times),'p95':sorted(times)[max(0,(len(times)*95+99)//100-1)]}


def transfer(e,binary,learned,dialogs):
    cases=json.loads((ROOT/'data/heldout-compositions.json').read_text());before=e.checks;times=[]
    with Session(binary,e.state,e.program) as ss:
        for i in range(dialogs):
            subject=f'compuesto{i:03d}';e.lesson(f'aprende que {subject} es clasea',session=ss)
            e.lesson(f'aprende que {subject} alcanza destino022',session=ss)
            for j,c in enumerate(cases):
                q=c['text'].format(S=subject);q=q.upper() if i%3==1 else q
                if i%2:q+='?'
                e.check(q,expected_answer(subject,c['language'],c['kind']),c['language'],session=ss);times.append(e.times[-1])
            if i%2==1:print('E022_COMPOSITION_TRANSFER',i+1,'DIALOGUES',e.checks-before,flush=True)
        metrics=ss.metrics()
    e.model_audit();e.state.write_bytes(learned)
    return {'dialogues':dialogs,'held_out_complete_formulations':len(cases),'queries':dialogs*len(cases),'checks':e.checks-before,
            'held_out_scope':'whole compositions and subjects; request pieces supervised separately, variable predicates transfer to requires/reaches',
            'query_ms':pct(times),'session_metrics':metrics}


def guards(e,binary,learned):
    before=e.checks;rows=[]
    with Session(binary,e.state,e.program) as ss:
        e.lesson('aprende que principal es clasea',session=ss);e.lesson('aprende que alterno es claseb',session=ss)
        rejected=[
          ('puedes hablarme un poco de desconocido',1),('puedes hablarme un poco de principal y alterno',1),
          ('no puedes hablarme un poco de principal',1),('háblame un poco sobre principal sininventarverbo',1),
          ('qué es lo que requiere utiliza principal',1),('qué es lo que requiere principal agua',1),
          ('y hablando de desconocido qué requiere',1),('me interesa conocer lo que inventaverbo principal',1),
          ('puedes hablarme un poco de aprende que falso es clasea',1),
          ('could you tell me a little about unknownbeing',2),('give me some information about principal and alterno',2),
          ('can you not tell me a little about principal',2),('what is it that principal requires uses',2),
          ('which resources does principal study',2),('which resources does unknownbeing require',2),
          ('which resources does principal require water',2),('say what principal requires of unknownobject in other words',2),
          ('can you tell me a little about learn that falseword is clasea',2),
          ('puedes hablarme un poco de 7',1),('could you tell me a little about one',2),
          ('1,000 por dos',1),('1,5 mas dos',1)]
        for q,l in rejected:
            old=e021.knowledge(e.state);names_before=e017.lexicon(snapshot(e.state)[1]);raw,ms=ss.request(q,l);out=decode_result(raw)
            allowed=[e021.SURFACE[4,l],e021.SURFACE[11,l],e017.conversation.ACTS[3,l],e019.CLARIFY[l]]
            assert out in allowed,(q,out,allowed)
            assert e021.knowledge(e.state)==old and e017.lexicon(snapshot(e.state)[1])==names_before
            rows.append({'input':q,'output':out,'language':l,'ms':ms});e.checks+=1
        # Query-looking lessons cannot allocate a new term or write a claim.
        for q,l in [('aprende que falso es clasea?',1),('learn that falseword is clasea?',2),('aprende, que falso es clasea?',1),('learn, that falseword is clasea?',2)]:
            old=e021.knowledge(e.state);raw,_=ss.request(q,l);assert decode_result(raw)==e021.SURFACE[4,l]
            assert e021.knowledge(e.state)==old;e.checks+=1
        # Actual explicit teaching and corrections keep their original route.
        e.lesson('aprende que principal no requiere agua',session=ss)
        e.check('which resources does principal require',e021.SURFACE[4,2],2,session=ss)
        e.check('principal requires water?',e021.SURFACE[8,2]+' Principal does not require water.',2,session=ss)
        e.lesson('aprende que principal requiere agua',session=ss)
        e.check('qué es lo que requiere principal',e021.SURFACE[5,1],session=ss)
    e.state.write_bytes(learned)
    # Public client, persistence, and atomic rollback for rewritten requests.
    with Session(binary,e.state,e.program) as ss:
        e.lesson('aprende que persiste022 es clasea',session=ss)
        e.check('puedes hablarme un poco de persiste022',e021.answer('persiste022',1,'definition'),session=ss)
    with Session(binary,e.state,e.program) as ss:
        e.check('can you tell me a little about persiste022',e021.answer('persiste022',2,'definition'),2,session=ss)
        pending=Path(str(e.state)+'.pending');pending.mkdir();seed=e.state.read_bytes()
        try:
            try:ss.request('could you tell me a little about persiste022');raise AssertionError('save failure accepted')
            except RuntimeError as error:assert 'cannot write state' in str(error)
            assert e.state.read_bytes()==seed
        finally:pending.rmdir()
        e.check('por qué',e021.SURFACE[9,1]+' Persiste022 es clasea.',session=ss)
    cli=['bash',str(ROOT.parent/'knowledge/text.sh'),e.runtime,str(e.state)]
    got=subprocess.check_output(cli+['puedes hablarme un poco de persiste022','es'],text=True).strip()
    assert got==e021.answer('persiste022',1,'definition');e.checks+=1
    e.state.write_bytes(learned);e.model_audit()
    print('E022_UNCERTAINTY_VETOES_CARDINALITY_NEGATION_RESTART_AND_ROLLBACK_PASS',e.checks-before,flush=True)
    return {'checks':e.checks-before,'rejected_queries':rows,'no_question_writes':True,'new_query_public_client':True,'restart_rollback':True}


def learning_controls(e,binary,learned):
    def reset(*rules):
        e.state.write_bytes(learned);m=snapshot(e.state)[1];total=u32(m,N+8);fields=[(N+3,0)]
        for f in rules:
            i=f['id']-1;total-=e017.u16(m,N+30002+i*8)
            fields += [(N+b+i*96+j,0) for b in [10000,20000] for j in range(96)]
            fields += [(N+30000+i*8+j,0) for j in range(8)]+[(N+40000+i*512+j,0) for j in range(512)]
        fields += [(N+8+j,(total>>(j*8))&255) for j in range(4)];e.run(stores(fields))
    f=RULES[16];reset(f)
    for _ in range(4):e.pair(f,{'S':5,'P':25},'y hablando de gato qué necesita','qué necesita gato')
    for bank in [10000,20000]:assert snapshot(e.state)[1].get(N+bank+(f['id']-1)*96+2,0)==0
    e.run('#!reverse-pc-machine-v1\n'+e.programs['rephrase-seal'],reject=True)
    e.state.write_bytes(learned);e.pair(RULES[0],{},RULES[0]['source'],RULES[0]['target'],reject=True)
    reset(f);e.pair(f,{'S':5,'P':25},'y hablando de gato qué necesita','',reject=True)
    for target in ['gato','aprende que']:
        fbad=RULES[5];reset(fbad)
        for _ in range(2):e.pair(fbad,{},fbad['source'],target,2)
        e.run('#!reverse-pc-machine-v1\n'+e.programs['rephrase-seal'],reject=True)
    fbad=RULES[20];reset(fbad)
    for cid,word in [(5,'cat'),(71,'plant')]:e.pair(fbad,{'S':cid},f'which resources does {word} require',f'what does {word} need',2)
    e.run('#!reverse-pc-machine-v1\n'+e.programs['rephrase-seal'],reject=True)
    # Conflicting equally specific replacements fail closed.
    e.state.write_bytes(learned);fextra={'id':len(RULES)+1,'mode':1,'scope':1,'source':RULES[5]['source']}
    e.run(stores([(N+3,0)]));e.pair(fextra,{},fextra['source'],'háblame de',2)
    e.run('#!reverse-pc-machine-v1\n'+e.programs['rephrase-seal'])
    with Session(binary,e.state,e.program) as ss:
        e.lesson('aprende que ambiguo022 es clasea',session=ss)
        e.check('give me some information about ambiguo022',e017.conversation.ACTS[3,2],2,session=ss)
    # Wrong supervision changes interpretation with the same code and facts.
    f=RULES[5];reset(f);e.pair(f,{},f['source'],'háblame de',2)
    e.run('#!reverse-pc-machine-v1\n'+e.programs['rephrase-seal'])
    with Session(binary,e.state,e.program) as ss:
        e.lesson('aprende que contraprueba es clasea',session=ss)
        e.check('give me some information about contraprueba',e017.conversation.ACTS[3,2],2,session=ss)
    # Even an explicitly taught cycle must terminate and preserve original text.
    left=next(f for f in RULES if f['source']=='brevemente');right=next(f for f in RULES if f['source']=='briefly')
    reset(left,right);e.pair(left,{},'brevemente','briefly');e.pair(right,{},'briefly','brevemente')
    e.run('#!reverse-pc-machine-v1\n'+e.programs['rephrase-seal'])
    with Session(binary,e.state,e.program) as ss:
        e.lesson('aprende que ciclotema es clasea',session=ss)
        e.check('puedes hablarme brevemente sobre ciclotema',e017.conversation.ACTS[3,1],session=ss)
    e.state.write_bytes(learned);e.model_audit()
    print('E022_REPETITION_QUERY_ONLY_PROMOTION_CONFLICT_COUNTERFACTUAL_AND_CYCLE_CONTROLS_PASS',flush=True)


def comparisons(e,binary,learned):
    cases=json.loads((ROOT/'data/heldout-compositions.json').read_text());transcript=[];versions=[]
    for name,file in [('E020','BBYQ_E020_Million_Arithmetic_ES_EN.rvp.gz.b64'),('E021','BBYQ_E021_Language_Dialogue_ES_EN.rvp.gz.b64'),('E022',None)]:
        seed=learned if file is None else gzip.decompress(base64.b64decode((REPO/'ai/checkpoints'/file).read_bytes()))
        e.state.write_bytes(seed);score=dev=0;times=[]
        with Session(binary,e.state,e.program) as ss:
            ss.request('aprende que compone es clasea');ss.request('aprende que compone alcanza destino022')
            for c in cases:
                q=c['text'].format(S='compone');l=c['language'];expected=expected_answer('compone',l,c['kind']);raw,ms=ss.request(q,l);out=decode_result(raw)
                ok=out.partition(' [')[0]==expected;score+=ok;times.append(ms)
                transcript.append({'version':name,'suite':'unseen_compositions','input':q,'language':l,'output':out,'expected':expected,'pass':ok,'ms':ms})
            for text,l,kind in e021.FREE_PROMPTS:
                q=text.format(s='compone');expected=e021.answer('compone',l,kind);raw,ms=ss.request(q,l);out=decode_result(raw);ok=out.partition(' [')[0]==expected;dev+=ok
                transcript.append({'version':name,'suite':'development_16','input':q,'language':l,'output':out,'expected':expected,'pass':ok,'ms':ms})
            common=0;ct=[]
            for _ in range(8):
                for q,expected in [('hola',e017.conversation.ACTS[1,1]),('gato es mamífero?','Un gato es un mamífero.'),('dos mas tres',e017.conversation.ACTS[5,1]+' cinco.'),('ocho menos tres',e017.conversation.ACTS[5,1]+' cinco.')]:
                    raw,ms=ss.request(q);common+=decode_result(raw)==expected;ct.append(ms)
            assert common==32,(name,common)
        m=snapshot(e.state)[1]
        versions.append({'version':name,'checkpoint_sha256':hashlib.sha256(seed).hexdigest(),'checkpoint_bytes':len(seed),'heldout_compositions':{'correct':score,'total':len(cases)},'development_16':{'correct':dev,'total':16},'shared_32':{'correct':common,'total':32},'new_query_ms':pct(times),'shared_query_ms':pct(ct)})
        print('E022_COMPARISON',name,'COMPOSITIONS',score,'/'+str(len(cases)),'DEVELOPMENT',dev,'/16',flush=True)
    assert versions[-1]['heldout_compositions']['correct']==len(cases)
    assert versions[-1]['development_16']['correct']==16
    e.state.write_bytes(learned)
    return {'scope':'110 fresh whole compositions, outside paired lessons and the separate development64; functional pieces supervised. Development16 and development64 guided engineering; no general-conversation score.','method':'same native runtime, source, question fixtures and oracle, varying learned checkpoint','versions':versions,'transcript':transcript}

def main():
    p=argparse.ArgumentParser();p.add_argument('runtime');p.add_argument('session_binary');p.add_argument('--out',default='evidence/e022');p.add_argument('--smoke',action='store_true');a=p.parse_args()
    out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
    parent=out/'parent.rvp';parent.write_bytes(gzip.decompress(base64.b64decode((REPO/'ai/checkpoints/BBYQ_E021_Language_Dialogue_ES_EN.rvp.gz.b64').read_bytes())))
    e=Examiner(a.runtime,parent,out);binary=Path(a.session_binary).resolve()
    learned,training=train(e);(out/CHECKPOINT).write_bytes(learned)
    print('E022_TRAINED',hashlib.sha256(learned).hexdigest(),len(learned),training,flush=True)
    smoke(e,binary,learned)
    if a.smoke:return
    report={'training':training,'composition_transfer':transfer(e,binary,learned,8)}
    report['query_guards']=guards(e,binary,learned)
    learning_controls(e,binary,learned)
    comparison=comparisons(e,binary,learned)
    report['e021_transfer']=e021.text_transfer(e,binary,learned,4)
    report['e021_topics']=e021.topic_and_integrity(e,binary,learned)
    report['e019_transfer']=e019.novel_dialogues(e,binary,learned,4)
    report['e018_transfer']=e018.novel_dialogues(e,binary,learned,20)
    e018.controls(e,binary,learned);e018.interfaces_and_rollback(e,binary,learned);e018.retention(e,binary,learned)
    e019.controls(e,binary,learned);e019.restart_and_reset(e,binary,learned)
    spec=importlib.util.spec_from_file_location('e020',ROOT.parent/'scale/tests/native-e020.py');e020=importlib.util.module_from_spec(spec);spec.loader.exec_module(e020)
    report['arithmetic_retention']=e020.independent_text_exam(e,binary,learned)
    e.state.write_bytes(learned);e017.audit(e);stats=e.model_audit()
    e.run((ROOT.parent/'scale/audit.xi').read_text());e.run((ROOT.parent/'lingua/audit.xi').read_text())
    report.update({'stage':'E022','parent_sha256':PARENT_SHA,'checkpoint_sha256':hashlib.sha256(learned).hexdigest(),'checkpoint_bytes':len(learned),
        'checks':e.checks,'old_learned_records_preserved':True,'new_world_facts_in_release':0,'open_conversation_achieved':False,
        'memory_stats':stats,'comparison':comparison['versions'],'limits':{'input_bytes':255,'tokens':15,'rewrite_steps':8,'rules':64,'topics':8},
        'intelligence':'XI; paired supervision for query rewrites; unchanged owner runtime and original state authority'})
    (out/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    (out/'comparisons.json').write_text(json.dumps(comparison,ensure_ascii=False,indent=2)+'\n')
    (out/'raw.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in e.transcript))
    e.state.write_bytes(learned);print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':main()
