"""Declared bounded language adapter, compiled to XI; no runtime host matching.

The native learned head must agree with the native structural parser. Grammar
rules supply tool contracts, not training labels or benchmark answers.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Rule:
    pattern: str
    intent: int
    actions: tuple

RULES=[]
def add(patterns,intent,*actions):
    for pattern in patterns: RULES.append(Rule(pattern,intent,actions))

add(['calcula {expr}','calcula cuánto es {expr}','resuelve {expr}',
     'dime cuánto es {expr}','cuánto es {expr}'],2,('math','expr'))
add(['tengo {a} cajas con {b} piezas cada una cuántas piezas tengo en total',
     'hay {a} cajas de {b} piezas cada una calcula el total',
     'tengo {a} paquetes y cada paquete tiene {b} unidades cuál es el total',
     'son {a} grupos de {b} unidades cuántas unidades hay'],2,('binary','a','*','b'))
add(['si pago {a} por algo que cuesta {b} cuánto cambio recibo',
     'pago {a} y cuesta {b} dime el cambio',
     'si cuesta {b} y pago {a} cuánto cambio recibo',
     'había {a} libros y presté {b} cuántos quedan',
     'tenía {a} libros y regalé {b} cuántos quedan',
     'había {a} objetos y regalé {b} dime cuántos quedan'],2,('binary','a','-','b'))
add(['tengo {a} y recibí {b} cuánto tengo',
     'tenía {a} y recibo {b} dime el total'],2,('binary','a','+','b'))
add(['reparto {a} piezas entre {b} cajas cuántas por caja',
     'distribuye {a} unidades entre {b} personas cuántas recibe cada persona'],2,('binary','a','/','b'))
for kind in ['nave','robot','proyecto','estrella']:
    add([f'recuerda que mi {kind} se llama {{name}}',
         f'quiero que recuerdes que mi {kind} se llama {{name}}',
         f'guarda el nombre de mi {kind} {{name}}',
         f'el nombre de mi {kind} es {{name}}'],3,('put',f'mi {kind}','nombre','$name',1,'relation'))
    add([f'cómo se llama mi {kind}',f'dime el nombre de mi {kind}',
         f'dime cómo se llama mi {kind}',f'cuál es el nombre de mi {kind}'],4,('lookup',f'mi {kind}','nombre'))
    add([f'corrige el nombre de mi {kind} a {{name}}',
         f'me equivoqué mi {kind} se llama {{name}}'],8,('put',f'mi {kind}','nombre','$name',1,'relation'))
add(['con lo que sabes dime si {name} es mortal',
     'dime si {name} pertenece a los mortales',
     'con lo que aprendiste dime si {name} es mortal',
     'según lo que sabes {name} es mortal',
     'pertenece {name} a los mortales',
     'con lo que acabas de aprender dime si {name} pertenece a los mortales'],5,('query','$name','es','mortal',1))
add(['recuerda que {name} es {kind}','aprende que {name} es {kind}'],3,('put','$name','es','$kind',1,'exact'))
add(['recuerda que {name} no es {kind}'],3,('put','$name','es','$kind',-1,'exact'))
add(['si alguien es {kind} entonces es {goal}',
     'aprende que todos los {kind} son {goal}',
     'recuerda la regla si alguien es {kind} entonces es {goal}'],3,('rule','$kind','$goal'))
add(['es {name} {kind}','dime si {name} es {kind}'],5,('query','$name','es','$kind',1))
add(['la {name} está conectada al parque y el parque a la tienda dime cómo llegar de {name} a tienda',
     'hay un camino desde {name} hasta el parque y del parque a la tienda dime la ruta de {name} a tienda'],6,
    ('put','$name','conecta','parque',1,'exact'),('put','parque','conecta','tienda',1,'exact'),('route','$name','tienda'))
add(['la {name} está conectada al puente y el puente al taller explica cómo llegar de {name} a taller'],6,
    ('put','$name','conecta','puente',1,'exact'),('put','puente','conecta','taller',1,'exact'),('route','$name','taller'))
add(['la {name} está conectada al jardín y el jardín al museo explícame cómo llegar de {name} a museo',
     'desde {name} puedo ir al jardín y desde el jardín al museo cómo llego de {name} a museo'],6,
    ('put','$name','conecta','jardín',1,'exact'),('put','jardín','conecta','museo',1,'exact'),('route','$name','museo'))
add(['recuerda que {name} conecta {goal}'],3,('put','$name','conecta','$goal',1,'exact'))
add(['dime la ruta de {name} a {goal}','cómo llego de {name} a {goal}',
     'busca un camino desde {name} hasta {goal}'],6,('route','$name','$goal'))
for verb in ['salúdame y después calcula','salúdame y luego calcula','salúdame y después calcula cuánto es','hola y calcula']:
    add([verb+' {expr}'],7,('greet',),('math','expr'))
add(['me equivoqué antes {name} ya no está activa corrige ese dato',
     'corrige ese dato {name} no es activa',
     'me equivoqué {name} no está activa corrige ese dato',
     'corrige lo anterior {name} ya no es activa',
     'actualiza el dato {name} está inactiva'],8,('put','$name','es','activa',-1,'polarity'))
for prefix in ['no calcules','por favor no calcules','ahora no calcules',
               'no definas','no expliques','por favor no definas',
               'prefiero que no expliques','no quiero la definición de',
               'no me expliques','no quiero aprender','no necesito que definas',
               'ahora no me definas']:
    add([prefix+' {expr}'],9,('cancel',))
# Multi-step corrections are one transaction even when the later tool fails.
add(['recuerda que mi nave se llama {name} y luego calcula {expr}'],7,
    ('put','mi nave','nombre','$name',1,'relation'),('math','expr'))

SLOTS=['a','b','name','kind','goal','expr']

# Longer compositions must be tried before a trailing name span can absorb
# their second clause. This priority is part of the compiled grammar.
RULES.sort(key=lambda rule:(len(rule.actions),sum(not w.startswith('{') for w in rule.pattern.split())),reverse=True)

def lexical_words():
    import re
    return {w for rule in RULES for w in re.findall(r'[^\W\d_]+',rule.pattern)
            if w not in SLOTS}
