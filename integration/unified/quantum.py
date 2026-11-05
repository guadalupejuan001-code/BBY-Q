"""Native quantum stages over a transaction's shared session banks.

The host transports typed data and persists provenance. XI computes the
classification, association, goal, policy, confidence, words and gradients.
"""
import math,struct
from .common import ROOT,C1,Entity,XiSession,A,Q,M,E,encoded,digest,key,run,metrics,integer,floating,material,stage_bytes

def natural(value,maximum):
    text=str(value)
    if not text.isdecimal() or not 0<=int(text)<=maximum:raise ValueError('Integer outside supported range')
    return int(text)

def observations(values):
    if not isinstance(values,list) or len(values)!=1000:raise ValueError('Exactly 1000 observations are required')
    if any(type(v) not in (int,float) for v in values):raise ValueError('Observations must be finite numbers')
    try:converted=[float(v) for v in values]
    except (OverflowError,ValueError):raise ValueError('Observations must be finite numbers') from None
    if any(not math.isfinite(v) for v in converted):raise ValueError('Observations must be finite numbers')
    return converted

class Quantum:
    def __init__(self,sessions,metadata,directory,project):
        self.sessions=sessions;self.meta=metadata;self.directory=directory;self.project=project;self.trace=[]

    def stage(self,bank,body,operation,**details):
        events=run(self.sessions[bank],body)
        self.trace.append({'bank':bank,'operation':operation,'native':True,**details})
        return events

    def remember(self,name,bit):
        bit=natural(bit,1);canonical=key(name);records=self.meta.setdefault('associations',{})
        if canonical not in records:
            if len(records)>=250:raise ValueError('Quantum association capacity reached')
            records[canonical]={'slot':len(records),'display':name}
        slot=records[canonical]['slot'];site=20000+4*slot
        self.stage('memory',f'qprepare {site} 4\n'+(f'x {site+1}\n' if bit else '')+f'set r14 {site}\nset r7 {site+1}\nfload f5 {M+64}\ncall qm_exchange','qm_exchange',slot=slot,qubits=4)
        # This is explicit user supervision, kept out of the inference metadata.
        return {'kind':'remember','status':1,'name':name,'slot':slot,'supervision':bit}

    def recall(self,name,erased=False):
        record=self.meta.get('associations',{}).get(key(name))
        if record is None:return {'kind':'recall','status':0,'name':name,'reason':'Unknown quantum association'}
        site=20000+4*record['slot']
        body=(f'qprepare {site} 4\n' if erased else '')+f'fexpect f0 Z:{site}\nfset f1 1\nfsub f1 f0\nfdiv f1 2\nfemit probability f1'
        p=float(metrics(self.stage('memory',body,'qm_read',slot=record['slot'],qubits=4))['probability'])
        return {'kind':'recall','status':1,'name':name,'slot':record['slot'],'probability':p,'value':int(p>=.5)}

    def observe(self,name,seed=None,payload=None):
        if seed is not None:
            if payload is not None:raise ValueError('Use either a synthetic sample or 1000 external observations')
            seed=natural(seed,2147483647);spec={'kind':'synthetic','seed':seed,'noise':.1}
        elif payload is not None:
            spec={'kind':'external','values':observations(payload)}
        else:
            spec=self.meta.get('observations',{}).get(key(name))
            if spec is None:return {'kind':'observe','status':0,'name':name,'reason':'No observations supplied'}
        self.meta.setdefault('observations',{})[key(name)]=spec
        return self.classify(name,spec)

    def input_body(self,spec):
        if spec['kind']=='synthetic':return f'store64 {A+256} {spec["seed"]}\nstore64 {A+272} 0\nfstore {A+296} {spec["noise"]}\ncall vqc_sample\n'
        return ''.join(f'fstore {A+300000+8*i} {value!r}\n' for i,value in enumerate(observations(spec['values'])))

    def classify(self,name,spec,ablated=False):
        sha=digest(encoded(spec))
        body=self.input_body(spec)+f'store64 {A} 0\nstore64 {A+280} {int(ablated)}\ncall select_agent\ncall forward\nfemit probability f21'
        p=float(metrics(self.stage('v3',body,'vqc_forward',qubits=1000,input_sha256=sha))['probability'])
        projection=self.project(name,int(p>=.5),p,sha)
        return {'kind':'observe','status':1,'name':name,'class':int(p>=.5),'probability':p,'input_sha256':sha,'observations':1000,'symbolic_projection':projection}

    def policy(self,position,goal,ablated=False):
        position=natural(position,6);goal=natural(goal,6)
        body=f'store64 {A+280} 0\nstore64 {A+344} {position}\nstore64 {A+352} {goal}\nstore64 {A+360} 0\nstore64 {A+312} 12\nstore64 {A+320} 2\ncall qrl_step'
        if ablated:
            # Counterfactual control modifies native policy parameters in a
            # disposable transaction, rather than choosing a host-side action.
            body=''.join(f'fstore {A+210000+8*i} 0\n' for i in range(1000))+f'fstore {A+5016} -12\n'+body
        result=metrics(self.stage('v3',body,'qrl_step',qubits=1000,position=position,goal=goal))
        return {'kind':'plan','status':1,'position':position,'goal':goal,'action':2 if result['terminal'] else int(result['action']),'probability_right':float(result.get('probability_right',.5)),'terminal':bool(result['terminal'])}

    def say(self,values,ablated=False):
        value=Entity.Entity.voice(self,values,mode=int(ablated))
        self.trace.append({'bank':'voice','operation':'qchat_encode/qchat_next','native':True,'qubits':100,'tokens':len(value['ids'])})
        body=Entity.workspace({**values,592:len(value['ids'])})+''.join(f'store8 {E+600+i} {token}\n' for i,token in enumerate(value['ids']))+'call entity_voice_check'
        self.stage('entity',body,'entity_voice_check')
        value['faithful']=bool(integer(self.sessions['entity'],E+144))
        return value

    def mission(self,name,rule,position,control=None):
        position=natural(position,6);start=len(self.trace)
        memory=self.recall(rule,erased=control=='memory-erased')
        spec=self.meta.get('observations',{}).get(key(name));observed=None
        if spec is not None:observed=self.classify(name,spec,ablated=control=='vqc-ablated')
        present=int(memory['status']==1);sensor=int(observed is not None)
        values={8:present,16:sensor,24:position,176:1,40:float(memory.get('probability',.5)),48:float(observed['probability'] if observed else .5)}
        self.stage('entity',Entity.workspace(values)+'call entity_infer','entity_infer')
        coordinator=self.sessions['entity']
        for offset in (56,64,72,88):values[offset]=integer(coordinator,E+offset)
        policy=self.policy(position,values[72],ablated=control=='qrl-ablated') if values[88] else None
        values[80]=policy['action'] if policy else -1;values[160]=policy['probability_right'] if policy else .5
        self.stage('entity',Entity.workspace(values)+'call entity_decide','entity_decide')
        values[80]=integer(coordinator,E+80);confidence=floating(coordinator,E+112)
        voice=self.say(values,ablated=control=='voice-ablated')
        frame=material(coordinator,E,352)
        task={'kind':'mission','status':1 if voice['faithful'] and voice['terminated'] else 4,'observation':name,'association':rule,'position':position,'class':values[56] if sensor else None,'rule_value':values[64] if present else None,'goal':values[72],'action':values[80],'confidence':confidence,'class_probability':values[48],'memory_probability':values[40],'voice':voice,'frame_hex':frame.hex(),'input':spec,'trace':self.trace[start:],'supported':bool(values[88]),'policy':policy}
        return task

    def standalone_plan(self,position,goal):
        plan=self.policy(position,goal)
        values={8:1,16:1,24:plan['position'],40:1.,48:1.,56:1,64:1,72:plan['goal'],80:plan['action'],88:1,160:plan['probability_right'],176:0}
        voice=self.say(values);plan['voice']=voice
        plan['status']=1 if voice['faithful'] and voice['terminated'] else 4
        return plan

    def identities(self):return Entity.Entity.identities(self)

    def feedback(self,task,success=None,teacher=None):
        before=self.identities();frame=bytes.fromhex(task['frame_hex']);v=self.sessions['v3'];e=self.sessions['entity'];c=self.sessions['voice'];m=self.sessions['memory']
        # Restore only the original task fields, never the older learned state.
        restored=stage_bytes(E+8,frame[8:104])+stage_bytes(E+144,frame[144:184])
        if teacher is not None:
            goldclass=natural(teacher['class'],1);goldrule=natural(teacher['rule'],1)
            self.stage('entity',restored+Entity.workspace({264:goldclass,272:goldrule})+'call entity_score','entity_score')
            verified=floating(e,E+96)
            if success is not None and int(verified)!=natural(success,1):raise ValueError('Reported result conflicts with independently verified task')
            success=verified
        elif success is None:raise ValueError('Verified feedback or explicit result is required')
        else:success=float(natural(success,1))
        self.stage('entity',restored+f'fstore {E+96} {success}\ncall entity_learn','entity_learn')
        updates={'entity':1,'vqc':0,'qrl':0,'memory':0,'voice':0}
        if teacher is not None and task['supported']:
            spec=task['input'];goldclass=natural(teacher['class'],1);goldrule=natural(teacher['rule'],1)
            body=restored+Entity.workspace({264:goldclass,272:goldrule})+'call entity_score\n'+f'store64 {A+344} {task["position"]}\nstore64 {A+352} {task["goal"]}\nstore64 {A+360} 0\nstore64 {A+312} 12\nstore64 {A+320} 2\ncall entity_qrl_feedback'
            self.stage('v3',body,'entity_qrl_feedback')
            self.stage('v3',self.input_body(spec)+f'fstore {A+128} {float(goldclass)}\nstore64 {A} 0\nstore64 {A+280} 0\nfstore {A+4024} .01\ncall supervised_update','supervised_update')
            updates['vqc']=1;updates['qrl']=int(task['class']==goldclass and task['rule_value']==goldrule and task['action'] in (0,1))
            # Rehearsal uses a disposable memory bank. Only learned angles and
            # its counter return; live user associations are never reset.
            rehearsal=self.directory/'memory-rehearsal.rvp';m.save(rehearsal)
            with XiSession(C1.RT/'build/xi_session',rehearsal) as temporary:
                run(temporary,f'store64 {M+16} 0\nstore64 {M+200} 620511\nstore64 {M+208} 2\ncall qm_data\nstore8 {M+10000} {goldrule}\nstore8 {M+11000} 0\nstore8 {M+50000} {goldrule}\ncall qm_train')
                angles=material(temporary,M+64,24);counter=material(temporary,M+24,8)
            self.stage('memory',stage_bytes(M+64,angles)+stage_bytes(M+24,counter),'qm_train/publish_angles',preserves_associations=True)
            updates['memory']=1
        run(c,restored+'call entity_voice_teacher');size=integer(c,E+512);targets=list(material(c,E+520,size));prefix=[]
        for target in [*targets,0]:
            raw=Entity.QC.bits('',prefix)
            body=Entity.QC.stage(raw)+f'call entity_voice_bits\nstore64 {Q+80} 0\ncall qchat_encode\nstore64 {Q+48} {target}\nfstore {Q+32} .03\ncall qchat_train'
            # Each teacher is the native description of the action actually
            # recorded, not the environment's desired alternative action.
            for _ in range(3):run(c,body)
            updates['voice']+=3
            if target:prefix.append(Entity.VOCAB[target])
        self.trace.append({'bank':'voice','operation':'qchat_train','native':True,'updates':updates['voice']})
        after=self.identities()
        return {'kind':'feedback','status':1,'success':bool(success),'updates':updates,'parameter_sha256_before':before,'parameter_sha256_after':after,'changed':{name:before[name]!=after[name] for name in before},'supervision':'independent-labels' if teacher else 'explicit-user-result'}
