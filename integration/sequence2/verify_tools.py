#!/usr/bin/env python3
"""Native tool semantics, independent of learned-reader selection."""
import json,tempfile
from pathlib import Path
import build as B
import engine as E
from tools import Tools,build_zero,A
from schema import ROOT
import train

def main():
    B.main();build_zero();v,out=train.vocabularies();checks=[]
    with tempfile.TemporaryDirectory(prefix='c1-native-tools-') as folder:
        state=Path(folder)/'tools.rvp';E.birth(state,len(out))
        with E.Model(state,v,out) as model:
            tools=Tools(model,{})
            def run(text):
                parsed=tools.parse(text)
                assert parsed is not None,text
                return tools.execute(parsed)
            assert run('calcula -(17 + 9) * 4 / 2')['results'][-1]['value']==-52
            assert run('Tengo 137 cajas con 24 piezas cada una. ¿Cuántas piezas tengo en total?')['results'][-1]['value']==3288
            assert run('calcula 9 / (7 - 7)')['status']==4
            assert run('calcula 9007199254740993 + 1')['status']==4
            checks.append('native arithmetic, narrative arguments, invalid division and numeric precision boundary')
            assert run('Recuerda que mi nave se llama Niña Ámbar.')['ok']
            assert run('¿Cómo se llama mi nave?')['results'][-1]['value']=='Niña Ámbar'
            assert run('Corrige el nombre de mi nave a Niño Ébano.')['ok']
            assert run('Dime el nombre de mi nave.')['results'][-1]['value']=='Niño Ébano'
            assert run('Recuerda que mi robot se llama Nino Ebano.')['ok']
            assert run('¿Cómo se llama mi robot?')['results'][-1]['value']=='Nino Ebano'
            checks.append('exact multiword names, accents, enie and replacement of prior names')
            run('recuerda que Cielo es activa');negative=tools.parse('recuerda que Cielo no es activa')
            assert negative['captures']['name']=='Cielo',negative
            assert tools.execute(negative)['ok']
            assert run('dime si Cielo es activa')['status']==2
            run('Me equivoqué: Cielo no está activa. Corrige ese dato.')
            result=run('dime si Cielo es activa')
            assert result['results'][-1]['status']==-1,result
            checks.append('negative evidence, explicit contradiction and correction remove superseded evidence')
            run('si alguien es humano entonces es mortal');run('recuerda que Ícaro Lunar es humano')
            result=run('Dime si Ícaro Lunar es mortal.')
            assert result['results'][-1]['status']==1 and len(result['results'][-1]['proof'])==2,result
            assert run('Dime si Desconocido es mortal.')['status']==0
            checks.append('existing XI inference supplies a proof and distinguishes missing knowledge')
            result=run('La Ámbar está conectada al puente y el puente al taller. Explica cómo llegar de Ámbar a taller.')
            assert result['results'][-1]['path']==['Ámbar','puente','taller'],result
            assert run('dime la ruta de Ámbar a inexistente')['status']==0
            checks.append('existing XI route planner and unreachable target')
            count=tools.integer(0)
            cancelled=run('Ahora no calcules 137 por 24.')
            assert cancelled['results'][0]['kind']=='cancel' and tools.integer(0)==count
            assert tools.parse('inventa una habilidad completamente desconocida') is None
            composed=tools.parse('recuerda que mi nave se llama Neral Blanco y luego calcula 17 + 4')
            assert composed['intent']==7 and composed['captures']['name']=='Neral Blanco',composed
            checks.append('negative request has no action; unsupported text rejected; composition does not become part of a name')
            # Reopening a native checkpoint preserves facts independently of
            # the host metadata used solely to render exact symbol strings.
            saved=Path(folder)/'reopened.rvp';model.s.save(saved);vocabulary=list(model.codec.words);metadata=tools.meta
        with E.Model(saved,vocabulary,out) as reopened:
            tools=Tools(reopened,metadata);parsed=tools.parse('Dime si Ícaro Lunar es mortal.')
            assert tools.execute(parsed)['results'][-1]['status']==1
            checks.append('native facts and rules persist through close and reopen')
    report={'passed':True,'checks':checks,'count':len(checks),'scope':'Native tools only; not learned-reader or end-to-end accuracy'}
    p=ROOT/'build/sequence2/tool-checks.json';p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
