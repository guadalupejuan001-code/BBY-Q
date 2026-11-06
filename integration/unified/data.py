"""Contract transfer curriculum; no held-out answers supplied to inference."""
import random
from .common import C1Data,C1,encoded,digest
from .contracts import RULES

def quantum_rows(split):
    rng=random.Random({'train':2026110701,'validation':2026110702}[split]);rows=[]
    names={'train':['Faro Azul','Nara','Luz del Sur','Iria','Pino Alto','Lago Claro'],
           'validation':['Órbita Neral','Niña Ámbar','Viento Norte','Ñandú Verde','Ébano Lunar','Brisa Nueva']}[split]
    for index,rule in enumerate(RULES):
        for i in range(6):
            # Binary memory, sample seeds and positions have independent values.
            memory=rule.actions[0][0]=='remember' and len(rule.actions)==1
            plan=rule.actions[0][0]=='plan' or rule.actions[0][0]=='cancel' and 'decidas' in rule.pattern
            values={'name':names[i],'kind':names[(i+2)%len(names)],'goal':str(rng.randrange(7)),
                    'a':rng.randrange(2) if memory or rule.actions[0][0]=='feedback' else rng.randrange(7) if plan or rule.actions[0][0]=='mission' else rng.randrange(1000,900000),
                    'b':rng.randrange(7) if plan else rng.randrange(2),'expr':'3'}
            prompt=rule.pattern.format(**values)
            if split=='validation':prompt=prompt[:1].upper()+prompt[1:]+'.'
            rows.append({'input':prompt,'intent':rule.intent,'family':rule.actions[-1][0]})
    unique={}
    for row in rows:
        if row['input'] in unique and row['intent']!=unique[row['input']]['intent']:raise ValueError('Conflicting unified labels')
        unique[row['input']]=row
    return list(unique.values())

def rows(split):
    return [*C1Data.intentions(split),*quantum_rows(split)]

def check_splits():
    train={(row['input'],row.get('previous','')) for row in rows('train')}
    validation={(row['input'],row.get('previous','')) for row in rows('validation')}
    if train&validation:raise ValueError('Unified training/validation overlap')
    return {'train':len(train),'validation':len(validation),'quantum_validation':len(quantum_rows('validation'))}
