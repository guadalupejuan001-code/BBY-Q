"""Declared C1 curriculum. Scoring and transport only, no host inference."""
import hashlib,importlib.util,random
from pathlib import Path
from schema import ROOT
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
BASE=module('c1_original_data',ROOT/'integration/balance/data.py')
ABSTAIN='necesito más ejemplos para aprender .'
TOPICS=[('memoria','la memoria conserva información .'),('dato','un dato representa información .'),('algoritmo','un algoritmo es una serie de instrucciones .'),('circuito','un circuito aplica puertas a los cúbits .'),('cúbit','un cúbit es una unidad de información cuántica .'),('entrelazamiento','el entrelazamiento crea correlaciones cuánticas .'),('medición','medir produce un resultado según el estado .'),('interferencia','la interferencia combina amplitudes .'),('xi','xi es nuestro lenguaje de instrucciones .'),('ether','ether ejecuta nuestro núcleo cuántico .')]
KEYWORDS='no nunca sin sí si año ano tengo tenía habia había hay cajas piezas cada por entre pago pagué cuesta costó cuesta pago cambio recibo libros presté preste regalé regalo compré compre recibí recibi sumé sume añadí anadi salúdame saludame saluda hola después despues luego y calcula cuánto cuanto quedan queda total exactamente recuerda que mi nave proyecto robot se llama cómo como nombre llamado está esta es pertenece los las el la un una a de del al desde hasta conectada conectado conecta llegar ruta camino corrige corrección correccion me equivoqué equivoque antes ya ese dato humana humano humana humanos mortales mortal activa activo activos inactiva inactivo resuelve aprende regla entonces consulta observa recupera porqué porque'.split()
def rng(split):return random.Random(int.from_bytes(hashlib.sha256(('C1:2026110504:'+split).encode()).digest()[:8],'little'))
def corpus():
 old=BASE.build();out={name:[dict(r) for r in old[name]] for name in ['train','validation','test']}
 cancel='de acuerdo . no daré esa definición .'
 forms={'train':['no definas {}','no expliques {}','no quiero la definición de {}','no me expliques {}','no quiero aprender {}'], 'validation':['por favor no definas {}','prefiero que no expliques {}'], 'test':['no necesito que definas {}','ahora no me definas {}']}
 for split,items in forms.items():
  for topic,answer in TOPICS:
   out[split]+=[{'input':form.format(topic),'response':cancel,'kind':'negation'} for form in items]
  # Ordered contrasts deliberately share the same words while changing order.
  # Train/validation/test use disjoint ordered pairs of known topics.
  pairs=[(a,b) for a in range(10) for b in range(10) if a!=b]
  for index,(a,b) in enumerate(pairs):
   if index%5 != {'train':0,'validation':1,'test':2}[split] and not(split=='train' and index%5 in [3,4]):continue
   ta,answer=TOPICS[a];tb=TOPICS[b];out[split].append({'input':f'define {ta} no {tb}','response':answer,'kind':'order'})
 # Training-only context variety: the same topic must survive new history
 # wrappers. Validation and final-test phrasings are never copied here.
 for topic,answer in TOPICS:
  for previous in ['explícame {}','define el término {}','quiero aprender sobre {}']:
   for followup in ['repítelo','dime mas','cuéntalo otra vez','repite por favor']:
    out['train'].append({'input':followup,'previous':previous.format(topic),'response':answer,'kind':'context'})
 return out
def intentions(split):
 r=rng(split);forms={
  2:{'train':['Tengo {a} cajas con {b} piezas cada una. ¿Cuántas piezas tengo en total?','Si pago {a} por algo que cuesta {b}, ¿cuánto cambio recibo?','Había {a} libros y presté {b}. ¿Cuántos quedan?','Tengo {a} y recibí {b}. ¿Cuánto tengo?','Reparto {a} piezas entre {b} cajas. ¿Cuántas por caja?'], 'validation':['Hay {a} cajas de {b} piezas cada una. Calcula el total.','Pago {a} y cuesta {b}. Dime el cambio.','Tenía {a} libros y regalé {b}. ¿Cuántos quedan?'], 'test':['Tengo {a} paquetes y cada paquete tiene {b} unidades. ¿Cuál es el total?','Si cuesta {b} y pago {a}, ¿cuánto cambio recibo?','Había {a} objetos y regalé {b}. Dime cuántos quedan.']},
  3:{'train':['Recuerda que mi nave se llama {name}.','Recuerda que mi proyecto se llama {name}.'], 'validation':['Recuerda que mi robot se llama {name}.'], 'test':['Recuerda que mi estrella se llama {name}.']},
  4:{'train':['¿Cómo se llama mi nave?','Dime el nombre de mi proyecto.'], 'validation':['¿Cómo se llama mi robot?'], 'test':['¿Cómo se llama mi estrella?']},
  5:{'train':['Con lo que sabes, dime si {name} es mortal.','Dime si {name} pertenece a los mortales.'], 'validation':['Con lo que aprendiste, dime si {name} es mortal.'], 'test':['Con lo que acabas de aprender, dime si {name} pertenece a los mortales.']},
  6:{'train':['La {name} está conectada al parque y el parque a la tienda. Dime cómo llegar de {name} a tienda.'], 'validation':['La {name} está conectada al puente y el puente al taller. Explica cómo llegar de {name} a taller.'], 'test':['La {name} está conectada al jardín y el jardín al museo. Explícame cómo llegar de {name} a museo.']},
  7:{'train':['Salúdame y después calcula {a} por {b}.','Hola y calcula {a} + {b}.'], 'validation':['Salúdame y luego calcula {a} por {b}.'], 'test':['Salúdame y después calcula cuánto es {a} por {b}.']},
  8:{'train':['Me equivoqué antes: {name} ya no está activa. Corrige ese dato.','Corrige ese dato: {name} no es activa.'], 'validation':['Me equivoqué: {name} no está activa. Corrige ese dato.'], 'test':['Me equivoqué antes: {name} ya no está activa. Corrige ese dato.']},
  9:{'train':['No calcules {a} por {b}.','No definas memoria.','No expliques circuito.'], 'validation':['Por favor no calcules {a} por {b}.'], 'test':['Ahora no calcules {a} por {b}.']}}
 rows=[]
 for intent,modes in forms.items():
  for form in modes[split]:
   for i in range(8 if split=='train' else 4):
    a=r.randrange(80,500);b=r.randrange(1,70);name={'train':['Nara','Faro Azul','Luz del Sur','Iria'][i%4],'validation':'Orenda Verde','test':'Neral Blanco'}[split];rows.append({'input':form.format(a=a,b=b,name=name),'intent':intent})
 text=corpus()[split]
 rows += [{'input':row['input'],'previous':row.get('previous',''),'intent':0 if row.get('kind')=='unknown' else 9 if row.get('kind')=='negation' else 1} for row in text]
 controls={'train':['xyzzy plugh frobnitz','¿qué ocurrió en otro planeta?','haz algo que no entiendes'],
           'validation':['zorbax quux','¿qué pasa en un universo desconocido?','inventa una habilidad desconocida'],
           'test':['qwerty asdf zxcv','¿qué sucedió en una galaxia desconocida?','ejecuta una tarea que no conoces']}
 rows +=[{'input':s,'intent':0} for s in controls[split]]
 unique={}
 for row in rows:
  key=(row['input'],row.get('previous',''))
  if key in unique and unique[key]['intent']!=row['intent']:raise ValueError('Conflicting intent labels')
  unique[key]=row
 return list(unique.values())
