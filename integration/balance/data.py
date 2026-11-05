"""Predeclared Spanish curriculum. Validation and test phrasings stay separate."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
ABSTAIN='necesito más ejemplos para aprender .'

def build():
    original=json.loads((ROOT/'integration/qchat100/release/training-corpus.json').read_text())
    train=[dict(r,kind='known') for r in original['train']]
    val=[];test=[]
    topics=[('memoria','la memoria conserva información .'),('dato','un dato representa información .'),
      ('algoritmo','un algoritmo es una serie de instrucciones .'),('circuito','un circuito aplica puertas a los cúbits .'),
      ('cúbit','un cúbit es una unidad de información cuántica .'),('entrelazamiento','el entrelazamiento crea correlaciones cuánticas .'),
      ('medición','medir produce un resultado según el estado .'),('interferencia','la interferencia combina amplitudes .'),
      ('xi','xi es nuestro lenguaje de instrucciones .'),('ether','ether ejecuta nuestro núcleo cuántico .')]
    forms={
      'train':['quiero aprender sobre {}','enséñame la definición de {}','háblame del concepto {}','¿qué significa {}?',
               'dime qué representa {}','puedes explicar {}','explícame {}','define el término {}'],
      'validation':['¿puedes decir qué es {}?','me interesa entender {}','define para mí {}','quiero conocer el significado de {}'],
      'test':['¿me explicas el significado de {}?','ayúdame a comprender {}','quisiera saber qué representa {}','necesito una definición de {}']}
    for target,key in [(train,'train'),(val,'validation'),(test,'test')]:
      for topic,answer in topics:
        target.extend({'input':f.format(topic),'response':answer,'previous':'','kind':'known'} for f in forms[key])
        if key=='train':
          for p in ['explicalo otra vez','dime mas','repítelo','cuéntalo otra vez']:
            target.append({'input':p,'response':answer,'previous':'qué es '+topic,'kind':'context'})
        else:
          for p in (['repítelo','cuéntalo otra vez'] if key=='validation' else ['explícalo otra vez','dime más']):
            target.append({'input':p,'response':answer,'previous':('define para mí ' if key=='validation' else 'quisiera conocer ')+topic,'kind':'context'})
    families=[
      ('hola x .',['hey bby q','qué tal bby q','hola x','buenas bby q','hola hola','hola de nuevo','buenas tardes','saludos x'],['buenas bby','hey hola x','hola qué tal x'],['hola bby q qué tal','buenas noches bby q','saludos bby q']),
      ('soy bby q .',['presenta tu nombre','quiero conocer tu nombre','dime cómo te llamas','bby q quién eres','cuál es tu nombre','tú cómo te llamas'],['¿puedes decir tu nombre?','cómo debo llamarte','cuál nombre tienes'],['me dices cómo te llamas','quisiera conocer tu nombre','¿quién eres tú?']),
      ('tengo cien cúbits .',['dime cuántos cubits usas','cuántos cúbits tiene qchat','qué cantidad de cúbits tienes','cuántos qubits utiliza qchat','tu número de qubits','cuántos cubits usa tu generador'],['¿puedes decir cuántos cúbits usas?','quiero conocer tu número de qubits','cuántos cúbits utilizas'],['¿qué número de cúbits tienes?','cuál es tu cantidad de cúbits','dime la cantidad de qubits que usas']),
      ('aprendo con ejemplos y correcciones .',['quiero entender cómo aprendes','aprendes con ejemplos','aprendes con correcciones','explica tu aprendizaje','cómo es tu modo de aprender','dime cómo aprendes'],['puedes explicar tu aprendizaje','de qué forma aprendes','háblame de tu aprendizaje'],['¿cómo puedes aprender tú?','explícame cómo aprendes','quiero saber de qué manera aprendes']),
      ('de nada x .',['muchísimas gracias','gracias de nuevo','gracias bby q','te doy las gracias','bby gracias por responder','muchas gracias x'],['gracias por la ayuda','muchas gracias bby q','te agradezco la respuesta'],['gracias por responder bby q','muy agradecido bby q','gracias por ayudarme']),
      ('hasta luego x .',['chau','me voy adiós','hasta la próxima','adiós bby q','nos vemos luego','hasta otra vez'],['bueno nos vemos','adiós hasta pronto','bby q hasta luego'],['me despido hasta luego','hasta pronto bby q','nos vemos bby q']),
      ('puedes corregirme para que aprenda .',['cómo te puedo enseñar','quiero corregirte','cómo puedo enseñarte','quiero enseñarte algo','necesito darte una corrección','puedo corregirte con ejemplos'],['¿cómo puedo corregirte?','quisiera enseñarte','quiero darte una corrección'],['dime cómo puedo enseñarte','explícame cómo te corrijo','me dices cómo puedo corregirte']),
      ('mis estados clifford usan álgebra exacta .',['qué exactitud tienen tus estados','háblame de tus estados clifford','cómo representas tus estados exactos','explícame tu exactitud','tus estados son clifford','cómo es la exactitud de tus estados'],['quiero saber si tus estados son exactos','puedes explicar tus estados clifford','tus estados usan álgebra exacta'],['explícame si tus estados son exactos','qué significa la exactitud de tus estados','cuál es la representación de tus estados clifford']),
      (ABSTAIN,['te falta aprender','tienes límites','necesitas más ejemplos','puedes equivocarte','ya sabes todo','sabes de todo'],['conoces ya todo','entonces puedes saberlo todo','quiero saber si sabes todo'],['dime si ya conoces todo','tú sabes ya de todo','¿lo sabes absolutamente todo?'])]
    for answer,tr,va,te in families:
      for target,items in [(train,tr),(val,va),(test,te)]:target.extend({'input':s,'response':answer,'previous':'','kind':'known'} for s in items)
    unknown={
      'train':['volcán','galaxia','guitarra','fotosíntesis','átomo','océano','batería','imán','turbina','telescopio','espejo','plasma','neutrino','terremoto','dinosaurio','bacteria'],
      'validation':['motor eléctrico','satélite','electrón','glaciar','órbita','antena','meteoro','cristal'],
      'test':['motor diésel','supernova','proteína','gravedad','eclipse','tornado','cromosoma','semiconductor']}
    for target,key in [(train,'train'),(val,'validation'),(test,'test')]:
      for topic in unknown[key]:
        for form in ['qué es {}','explícame {}']:
          target.append({'input':form.format(topic),'response':ABSTAIN,'previous':'','kind':'unknown'})
    def unique(items):
      out={}
      for r in items:
        k=(r['input'],r.get('previous',''))
        if k in out:assert out[k]['response']==r['response'],k
        out[k]=r
      return list(out.values())
    train,val,test=map(unique,[train,val,test])
    keys=lambda rows:{(r['input'],r.get('previous','')) for r in rows}
    assert not keys(train)&keys(val) and not keys(train)&keys(test) and not keys(val)&keys(test)
    return {'schema':1,'train':train,'validation':val,'test':test,'original_retention':original['train'],
            'scope':'Learned Spanish topic families, paraphrases, context and explicit refusal for unlearned topics; no general conversation claim'}

if __name__=='__main__':
    d=build();print(json.dumps({k:len(v) for k,v in d.items() if isinstance(v,list)}))
