"""Natural-language contracts compiled to XI for the shared quantum task."""
from .common import ROOT,C1,C1Tools,Rule,module

RULES=[]
def add(patterns,*actions,intent=10):
    RULES.extend(Rule(pattern,intent,actions) for pattern in patterns)

add(['guarda la regla {name} con valor {a}',
     'recuerda que la regla {name} vale {a}',
     'corrige la regla {name} a {a}'],('remember','name','a'))
add(['lee la regla {name}','recupera la regla {name}',
     'qué valor tiene la regla {name}'],('recall','name'))
add(['observa {name} con muestra {a}','observa {name} con la muestra {a}',
     'crea la muestra {a} para {name}'],('observe','name','a'))
add(['observa {name}','clasifica las observaciones {name}',
     'clasifica {name}'],('observe','name',None))
add(['decide desde {a} hasta {b}','propón un paso desde {a} hacia {b}'],('plan','a','b'))
add(['resuelve {name} usando la regla {kind} desde {a}',
     'usa las observaciones {name} y la regla {kind} para decidir desde {a}',
     'resuelve la tarea con observaciones {name} y la regla {kind} desde {a}'],('mission','name','kind','a'))
add(['observa {name} con muestra {a} y resuelve usando la regla {kind} desde {goal}'],
    ('observe','name','a'),('mission','name','kind','goal'))
add(['guarda la regla {kind} con valor {b} observa {name} con muestra {a} y resuelve desde {goal}'],
    ('remember','kind','b'),('observe','name','a'),('mission','name','kind','goal'))
add(['explica la última decisión','por qué elegiste ese movimiento',
     'explica la última tarea'],('explain',))
add(['evalúa la última tarea con resultado {a}'],('feedback','a'))
add(['aprende de la última tarea'],('feedback',None))
add(['cómo están tus motores','muestra el estado de la entidad'],('status',))
add(['no uses las observaciones {name}','no resuelvas {name}',
     'no decidas desde {a} hasta {b}'],('cancel',),intent=9)
RULES.sort(key=lambda rule:(len(rule.actions),sum(not word.startswith('{') for word in rule.pattern.split())),reverse=True)

def compile_source(vocabulary):
    # An isolated compiler instance binds these contracts without modifying
    # the frozen C1 module or its global contract table.
    compiler=module('bbyq_unified_contract_compiler',ROOT/'integration/sequence2/tools.py')
    compiler.RULES=RULES
    return compiler.source(vocabulary).replace('c2_','uq_')

class Tools:
    def __init__(self,model,metadata):
        self.model=model;self.base=C1Tools.Tools(model,metadata)
        for rule in RULES:
            for token in rule.pattern.split():
                if not token.startswith('{'):model.codec.id(token)
        model.library+='\n'+compile_source(model.codec.words)

    def parse(self,prompt):
        p=self.model.prepare(prompt);self.model.run('call uq_parse')
        code=self.base.integer(64)
        if not code:
            value=self.base.parse(prompt)
            if value is not None:value['domain']='language'
            return value
        n=self.base.integer(80);original=self.base.numbers(C1Tools.A['PI'],n);captures={}
        for i,name in enumerate(C1Tools.SLOTS):
            start,length=self.base.numbers(C1Tools.A['CAP']+16*i,2)
            if length and start+length<=n:
                first=p['tokens'][original[start]];last=p['tokens'][original[start+length-1]]
                captures[name]=p['raw'][first['start']:last['start']+last['length']].decode('utf-8')
        return {'domain':'quantum','rule':code,'intent':self.base.integer(72),'captures':captures}
