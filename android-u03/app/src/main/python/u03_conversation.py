"""Personal conversation adapter over original, authenticated BBY Q XI.

U02 remains the sole writable knowledge authority. Personal questions run on
copies; explicit lessons use the existing transactional turn API. The user's
original E025 conversation program supplies frozen reference knowledge and
social language through the same native XI runtime, never an external model.
Presentation, routing and abstentions are labelled separately from inference.
"""
from __future__ import annotations

from contextlib import closing
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
import base64
import gzip
import json
import math
import os
import re
import sqlite3
import struct
import tempfile
import time
import unicodedata
import uuid

UNKNOWN = "No tengo suficiente información para responder."
SCHEMA = "BBYQ-0-personal-conversations-v2"
K = 8040000000000000000
Z = 9185000000000000000
REFERENCE_K = 7400000000000000000
REFERENCE_SOURCE_SHA256 = "c4e418a2d86126a2f2c2cf1dcd8b4e9776aafe93e5859d94cf4c4f1e2083fb45"
REFERENCE_SEED_SHA256 = "ce058a65092dd9892b6fd55276a17287b764a16bc526ccbfa0085154baef9631"
_reference_cache = None


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha(raw):
    return sha256(raw).hexdigest()


def _fold(text):
    plain = "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))
    return " ".join(re.sub(r"[¿?¡!.,;:]", " ", plain.casefold()).split())


def _input(value, name="texto", limit=4096):
    if not isinstance(value, str) or not value.strip() or len(value) > limit or "\x00" in value:
        raise ValueError("Se requiere " + name + " no vacío, de hasta " + str(limit) + " caracteres")
    return value.strip()


def _connect(folder):
    folder.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(folder / "conversation.sqlite"), timeout=60, isolation_level=None)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=FULL")
    db.executescript("""
      CREATE TABLE IF NOT EXISTS preferences(key TEXT PRIMARY KEY,value TEXT NOT NULL);
      INSERT OR IGNORE INTO preferences VALUES('view','0');
      CREATE TABLE IF NOT EXISTS requests(id TEXT PRIMARY KEY,fingerprint TEXT NOT NULL,state TEXT NOT NULL,
         action TEXT NOT NULL,input TEXT NOT NULL,route TEXT,view INTEGER NOT NULL,created_ms INTEGER NOT NULL,result TEXT);
      CREATE TABLE IF NOT EXISTS messages(id TEXT PRIMARY KEY,view INTEGER NOT NULL,role TEXT NOT NULL,
         text TEXT NOT NULL,request_id TEXT NOT NULL,created_ms INTEGER NOT NULL,provenance TEXT);
    """)
    _migrate_conversations(db)
    return db


def _migrate_conversations(db):
    """Keep C18 message/receipt bytes and view IDs; only add a reversible index."""
    db.execute("BEGIN IMMEDIATE")
    try:
        db.execute("""CREATE TABLE IF NOT EXISTS conversations(
          id TEXT PRIMARY KEY,view INTEGER NOT NULL UNIQUE,title TEXT NOT NULL,
          title_custom INTEGER NOT NULL,archived INTEGER NOT NULL,
          created_ms INTEGER NOT NULL,updated_ms INTEGER NOT NULL)""")
        version = db.execute("SELECT value FROM preferences WHERE key='conversation_schema'").fetchone()
        if not version or int(version[0]) < 2:
            active = _view(db)
            views = {active}
            views.update(row[0] for row in db.execute("SELECT DISTINCT view FROM messages"))
            views.update(row[0] for row in db.execute("SELECT DISTINCT view FROM requests"))
            now = time.time_ns() // 1000000
            for view in sorted(views):
                bounds = db.execute("SELECT MIN(created_ms),MAX(created_ms) FROM messages WHERE view=?", (view,)).fetchone()
                first = db.execute("SELECT text FROM messages WHERE view=? AND role='user' ORDER BY rowid LIMIT 1", (view,)).fetchone()
                title = _title(first[0]) if first else "Nueva conversación"
                db.execute("INSERT OR IGNORE INTO conversations VALUES(?,?,?,?,?,?,?)",
                           ("legacy-view-" + str(view), view, title, 0, 0, bounds[0] or now, bounds[1] or now))
            db.execute("INSERT OR REPLACE INTO preferences VALUES('conversation_schema','2')")
        db.execute("CREATE INDEX IF NOT EXISTS conversation_messages_view ON messages(view)")
        db.execute("CREATE INDEX IF NOT EXISTS conversation_requests_view ON requests(view,state)")
        db.execute("COMMIT")
    except BaseException:
        db.execute("ROLLBACK")
        raise


def _view(db):
    return int(db.execute("SELECT value FROM preferences WHERE key='view'").fetchone()[0])


def _title(text):
    value = " ".join(str(text).split())
    return value[:60] + ("…" if len(value) > 60 else "")


def _conversation(db, identifier=None, view=None):
    if identifier is not None:
        identifier = _input(identifier, "conversation_id", 200)
        row = db.execute("SELECT id,view,title,title_custom,archived,created_ms,updated_ms FROM conversations WHERE id=?", (identifier,)).fetchone()
    else:
        row = db.execute("SELECT id,view,title,title_custom,archived,created_ms,updated_ms FROM conversations WHERE view=?", (_view(db) if view is None else view,)).fetchone()
    if not row:
        raise ValueError("No se encuentra esta conversación")
    identifier, view, title, custom, archived, created, updated = row
    count = db.execute("SELECT COUNT(*) FROM messages WHERE view=?", (view,)).fetchone()[0]
    last = db.execute("SELECT text FROM messages WHERE view=? ORDER BY rowid DESC LIMIT 1", (view,)).fetchone()
    return {"id": identifier, "conversation_id": identifier, "view_id": view, "title": title,
            "archived": bool(archived), "created_at_ms": created, "updated_at_ms": updated,
            "message_count": count, "preview": _title(last[0]) if last else ""}


def _active_id(db):
    return _conversation(db)["id"]


def _conversations(db, include_archived=False, query=""):
    rows = db.execute("SELECT id FROM conversations" + ("" if include_archived else " WHERE archived=0") +
                      " ORDER BY updated_ms DESC,view DESC").fetchall()
    values = [_conversation(db, row[0]) for row in rows]
    if query:
        term = _fold(_input(query, "búsqueda", 200))
        values = [value for value in values if term in _fold(value["title"] + " " + value["preview"])]
    return values


def _new_conversation(db, title=None):
    view = db.execute("SELECT COALESCE(MAX(view),-1)+1 FROM conversations").fetchone()[0]
    identifier = "chat-" + uuid.uuid4().hex
    now = time.time_ns() // 1000000
    explicit = title is not None
    title = _input(title, "título", 120) if explicit else "Nueva conversación"
    db.execute("INSERT INTO conversations VALUES(?,?,?,?,?,?,?)", (identifier, view, title, int(explicit), 0, now, now))
    db.execute("UPDATE preferences SET value=? WHERE key='view'", (str(view),))
    return _conversation(db, identifier)


def _pending(db, view):
    identifier = _conversation(db, view=view)["id"]
    return [{"request_id": row[0], "text": json.loads(row[1]).get("text", ""), "conversation_id": identifier,
             "request": json.loads(row[1])}
            for row in db.execute("SELECT id,input FROM requests WHERE state='pending' AND view=? ORDER BY rowid", (view,))]


def _message(row):
    identifier, role, text, request_id, created, provenance = row
    result = {"id": identifier, "role": role, "text": text, "request_id": request_id, "created_at_ms": created}
    if provenance:
        result["provenance"] = json.loads(provenance)
        result["response_origin"] = result["provenance"]["response_origin"]
    return result


def _history(db, view=None, archived=False):
    sql = "SELECT id,role,text,request_id,created_ms,provenance FROM messages"
    params = () if archived else (_view(db) if view is None else view,)
    if not archived:
        sql += " WHERE view=?"
    return [_message(row) for row in db.execute(sql + " ORDER BY rowid", params)]


def _last_answer(db, view):
    # Courtesy alone does not introduce a new subject or numeric result.
    # Stop at the first other turn: do not search past a topic change,
    # ambiguity or clarification to manufacture a convenient antecedent.
    courtesy = {"gracias", "muchas gracias", "gracias bby q", "de nada"}
    row = None
    answer = None
    for candidate in db.execute("SELECT request_id,provenance FROM messages WHERE view=? AND role='assistant' ORDER BY rowid DESC LIMIT 64", (view,)):
        if not candidate[1]:
            break
        value = json.loads(candidate[1])
        if _fold(value.get("request_text", "")) in courtesy:
            continue
        row, answer = candidate, value
        break
    if row is None:
        return None
    route = answer.get("route", {})
    if route.get("kind") in ("why", "repeat") and route.get("previous") and answer.get("response_origin") != "abstention":
        context = dict(route["previous"])
        context["conversation_id"] = _conversation(db, view=view)["id"]
        return context
    return {"route": {key: value for key, value in route.items() if key != "previous"},
            "normalized_prompt": answer.get("normalized_prompt"),
            "response_origin": answer.get("response_origin"), "request_id": row[0],
            "conversation_id": _conversation(db, view=view)["id"],
            "context": _referents(answer)}


def _referents(answer):
    """Explicit local referents from a real prior turn, not semantic memory."""
    route = answer.get("route", {})
    receipt = answer.get("receipt") or {}
    rows = receipt.get("results", [])
    text = answer.get("request_text", "")
    # A conjunction of subjects/clauses is not one unambiguous antecedent.
    if len(re.findall(r"\bes\b", _fold(text))) > 1 or re.search(r"\b(?:y|o)\b", _fold(route.get("subject", ""))):
        return {"ambiguous": True}
    numbers = [row["value"] for row in rows if row.get("kind") == "math" and row.get("status") == 1]
    if len(numbers) == 1:
        return {"numeric_result": numbers[0]}
    subjects = {row["subject"] for row in rows if row.get("kind") == "put" and row.get("status") == 1 and row.get("subject")}
    if len(subjects) > 1:
        return {"ambiguous": True}
    subject = next(iter(subjects)) if subjects else route.get("subject")
    if subject and route.get("kind") in ("personal", "definition"):
        return {"subject": subject}
    return {}


def _material(native, address, size):
    pieces = []
    for offset in range(0, size, 60000):
        length = min(60000, size - offset)
        events, _ = native.execute("#!reverse-pc-machine-v1\nbudget 1000000\nmem_materialize " + str(address + offset) + " " + str(length) + "\nhalt\n")
        pieces.append(bytes.fromhex(next(e["hex"] for e in events if e.get("type") == "memory_materialization")))
    return b"".join(pieces)


def _numbers(native, address, count):
    return list(struct.unpack("<" + "q" * count, _material(native, address, 8 * count))) if count else []


def _labels(metadata, root):
    schema = json.loads((Path(root) / "build/zero/schema.json").read_text())
    labels = {int(value): name for name, value in schema["words"].items()}
    labels.update({entry["id"]: entry.get("display", canonical)
                   for canonical, entry in metadata.get("entities", {}).items()})
    return labels, schema


def _fact(row, labels):
    subject, relation, value, polarity = row[:4]
    s, r, v = (labels.get(number, "símbolo " + str(number)) for number in (subject, relation, value))
    if r == "nombre":
        text = s + " se llama " + v + "."
    else:
        text = s + (" no " if polarity < 0 else " ") + r + " " + v + "."
    return {"id": row[4], "subject": s, "predicate": r, "value": v, "polarity": polarity, "text": text,
            "source": "native_VQC_projection" if _fold(s).startswith("observacion ") else "native_C1_stored_fact"}


def personal_memory(root, personal_db, query=""):
    from integration.unified.session import Session
    from integration.unified.common import C1
    with Session(personal_db) as model:
        raw = model._banks()["language"]
        metadata = json.loads(model.db.execute("SELECT metadata FROM state WHERE id=1").fetchone()[0])
        state = model.snapshot()
    labels, _ = _labels(metadata, root)
    with tempfile.TemporaryDirectory(prefix="bbyq0-memory-") as temp:
        path = Path(temp) / "language.rvp"; path.write_bytes(raw)
        with C1.XiSession(C1.RT / "build/xi_session", path) as native:
            fact_count, rule_count = _numbers(native, K, 2)
            if not 0 <= fact_count <= 1024 or not 0 <= rule_count <= 256:
                raise RuntimeError("La memoria nativa declara un tamaño inválido")
            facts_raw = _numbers(native, K + 100000, fact_count * 8)
            rules_raw = _numbers(native, K + 200000, rule_count * 16)
    facts = [_fact(facts_raw[i:i+8], labels) for i in range(0, len(facts_raw), 8)]
    rules = []
    for i in range(0, len(rules_raw), 16):
        row = rules_raw[i:i+16]
        first, last = labels.get(row[2], str(row[2])), labels.get(row[10], str(row[10]))
        rules.append({"id": row[13], "antecedent": first, "consequence": last,
                      "text": "Si alguien es " + first + ", entonces es " + last + ".",
                      "source": "native_C1_stored_rule"})
    if query:
        term = _fold(query)
        facts = [row for row in facts if term in _fold(row["text"])]
        rules = [row for row in rules if term in _fold(row["text"])]
    return {"ok": True, "action": "personal_memory", "facts": facts, "rules": rules,
            "fact_count": fact_count, "rule_count": rule_count, "revision": state["revision"],
            "bank_sha256": state["banks"]["language"], "knowledge_modified": False,
            "scope": "Afirmaciones y reglas almacenadas; las proyecciones VQC son predicciones, no verdad externa"}


def _read_proof(database, receipt, root):
    from integration.unified.session import Session
    from integration.unified.common import C1
    query = next((row for row in reversed(receipt.get("results", [])) if row.get("kind") == "query"), None)
    if not query or not query.get("proof") or query.get("status") != 1:
        return []
    with Session(database) as model:
        raw = model._banks()["language"]
        metadata = json.loads(model.db.execute("SELECT metadata FROM state WHERE id=1").fetchone()[0])
    labels, _ = _labels(metadata, root)
    proof = []
    with tempfile.TemporaryDirectory(prefix="bbyq0-proof-") as temp:
        path = Path(temp) / "language.rvp"; path.write_bytes(raw)
        with C1.XiSession(C1.RT / "build/xi_session", path) as native:
            count = _numbers(native, Z + 80, 1)[0]
            for identifier in query["proof"]:
                if type(identifier) is not int or not 1 <= identifier <= count <= 1024:
                    raise RuntimeError("La prueba XI contiene una referencia inválida")
                row = _numbers(native, Z + 100000 + 64 * (identifier - 1), 8)
                fact = _fact(row, labels)
                fact.update(proof_id=identifier, native_rule_id=row[5], parents=[x for x in row[6:8] if x])
                if row[5]:
                    rule = _numbers(native, Z + 200000 + 128 * (row[5] - 1), 16)
                    fact["rule_text"] = "Si alguien es " + labels.get(rule[2], str(rule[2])) + ", entonces es " + labels.get(rule[10], str(rule[10])) + "."
                proof.append(fact)
    return proof


def _personal_definition(subject, root, personal_db):
    """Original Zero wildcard query: native closure, never a Python graph walk."""
    from integration.unified.session import Session
    from integration.unified.common import C1, C1Tools
    with Session(personal_db) as model:
        raw = model._banks()["language"]
        metadata = json.loads(model.db.execute("SELECT metadata FROM state WHERE id=1").fetchone()[0])
        output = model.output
    labels, schema = _labels(metadata, root)
    entry = next((entry for canonical, entry in metadata.get("entities", {}).items()
                  if _fold(canonical) == _fold(subject) or _fold(entry.get("display", "")) == _fold(subject)), None)
    if entry is None:
        return None
    with tempfile.TemporaryDirectory(prefix="bbyq0-definition-") as temp:
        path = Path(temp) / "language.rvp"; path.write_bytes(raw)
        with C1.Model(path, metadata["vocabulary"], output) as native:
            tools = C1Tools.Tools(native, metadata)
            tools.grounded()
            facts, statuses = [], []
            for polarity in (1, -1):
                native.run(C1.stage64(Z + 16384, [entry["id"], schema["words"]["es"], -1, polarity]))
                tools.raw_zero(1)
                statuses.append(struct.unpack("<q", native.memory(Z + 16, 8))[0])
                count = struct.unpack("<q", native.memory(Z + 112, 8))[0]
                if not 0 <= count <= 64:
                    raise RuntimeError("Cantidad de resultados nativos inválida")
                identifiers = list(struct.unpack("<" + "q" * count, native.memory(Z + 300000, count * 8))) if count else []
                for identifier in identifiers:
                    if not 1 <= identifier <= 1024:
                        raise RuntimeError("Índice de conclusión nativa inválido")
                    row = list(struct.unpack("<8q", native.memory(Z + 100000 + 64 * (identifier - 1), 64)))
                    fact = _fact(row, labels)
                    fact.update(proof_id=identifier, native_rule_id=row[5], parents=[x for x in row[6:8] if x])
                    if row[5]:
                        rule = list(struct.unpack("<16q", native.memory(Z + 200000 + 128 * (row[5] - 1), 128)))
                        fact["rule_text"] = "Si alguien es " + labels.get(rule[2], str(rule[2])) + ", entonces es " + labels.get(rule[10], str(rule[10])) + "."
                    facts.append(fact)
    if not facts:
        return None
    status = 2 if 2 in statuses else 1
    receipt = {"ok": status == 1, "entity": "U02", "committed": False,
               "results": [{"kind": "definition", "status": status, "subject": subject, "facts": facts}],
               "trace": [{"native": True, "bank": "language", "operation": "c2_knowledge/zero_solve"}]}
    return receipt


def _personal_inference(prompt, identifier, root, personal_db):
    from integration.reasoning_u03_c10.session import ReasoningSession
    import u03_integrated as core
    from u03_training import _copy
    with tempfile.TemporaryDirectory(prefix="bbyq0-readonly-") as temp:
        copy = Path(temp) / "personal.sqlite"; _copy(personal_db, copy)
        with ReasoningSession(copy, memo=core._memo, parallel_hash_workers=2) as model:
            receipt = model.turn(identifier, prompt)
        return receipt, _read_proof(copy, receipt, root)


def _reference(root, text, previous=None):
    global _reference_cache
    from integration.unified.common import C1
    folder = Path(root) / "ai/releases/e025"
    if _reference_cache is None or _reference_cache[0] != str(root):
        release = json.loads((folder / "release.json").read_text())
        raw = gzip.decompress(base64.b64decode((folder / "controller.rvp.gz.b64").read_bytes()))
        source = (folder / "conversation-linked.xi").read_bytes()
        if _sha(raw) != REFERENCE_SEED_SHA256 or release["sha256"]["seed"] != REFERENCE_SEED_SHA256 or _sha(source) != REFERENCE_SOURCE_SHA256:
            raise RuntimeError("El modelo de referencia E025 no coincide con su identidad original")
        _reference_cache = (str(root), raw, source.decode().split("\n", 1)[1], _sha(source))
    _, raw, source, source_hash = _reference_cache
    inputs = [previous, text] if previous else [text]
    if any(len(value.encode()) > 255 for value in inputs):
        return None
    with tempfile.TemporaryDirectory(prefix="bbyq0-reference-") as temp:
        path = Path(temp) / "reference.rvp"; path.write_bytes(raw)
        with C1.XiSession(C1.RT / "build/xi_session", path) as native:
            for prompt in inputs:
                data = prompt.encode()
                fields = [(REFERENCE_K + 16, 1), (REFERENCE_K + 17, len(data)), (REFERENCE_K + 3, 1)]
                fields += [(REFERENCE_K + 128 + i, byte) for i, byte in enumerate(data)]
                program = "#!reverse-pc-machine-v1\nbudget 100000000\n" + "".join(f"store8 {address} {value}\n" for address, value in fields) + source
                events, _ = native.execute(program)
            spoken = bytes(int(e["value"]) for e in events if e.get("register") in ("r14", "r9")).decode("utf-8")
    if not spoken.strip():
        return None
    return {"ok": True, "entity": "BBY Q E025 frozen reference", "committed": False,
            "results": [{"kind": "text", "text": spoken, "native_source": "E025"}],
            "trace": [{"native": True, "bank": "reference_E025", "operation": "original_conversation_XI"}],
            "reference_checkpoint_sha256": _sha(raw), "reference_source_sha256": source_hash,
            "native_output_sha256": _sha(spoken.encode()), "native_events_sha256": _sha(_json(events).encode()),
            "personal_memory_written": False, "reference_writes_discarded": True, "input": text,
            "context_input": previous}


def _strip(text):
    return text.strip().strip("¿?¡! .\n\t")


def _resolution(last, kind, prompt, **values):
    return {"kind": kind, "source_request_id": last.get("request_id"),
            "source_conversation_id": last.get("conversation_id"), "expanded_prompt": prompt,
            "deterministic_reference_resolution": True, **values}


def _route(text, db, view):
    clean = _strip(text); folded = _fold(clean)
    last = _last_answer(db, view)
    if folded in {"por que", "porque", "explicame por que", "explica por que", "como lo sabes",
                  "y por que", "y porque", "y como lo sabes", "y explicame por que"}:
        return {"kind": "why", "previous": last,
                "context_resolution": _resolution(last, "previous_turn", last.get("normalized_prompt")) if last else None}
    context = last.get("context", {}) if last else {}
    match = re.fullmatch(r"(?:y\s+)?(?:(?:cu[aá]nto (?:da|es)|calcula|multiplica)\s+)?(?:eso|el resultado)\s*(por|entre|m[aá]s|menos|[×÷*/+\-])\s*(-?(?:\d+(?:[.,]\d*)?|[.,]\d+))", clean, re.I)
    if match:
        number = context.get("numeric_result")
        if type(number) not in (int, float) or (type(number) is float and not math.isfinite(number)) or context.get("ambiguous"):
            return {"kind": "clarify", "reply": "¿Qué resultado quieres usar? Escribe el número o la cuenta completa."}
        operator = {"por": "*", "entre": "/", "mas": "+", "menos": "-", "×": "*", "÷": "/"}.get(_fold(match.group(1)), match.group(1))
        # Preserve exact integers, and serialize the shortest round-tripping
        # float as a plain decimal accepted by the original native reader.
        literal = str(number) if type(number) is int else format(Decimal(repr(number)), "f")
        prompt = "calcula " + literal + " " + operator + " " + match.group(2)
        return {"kind": "personal", "prompt": prompt, "write": False,
                "context_resolution": _resolution(last, "numeric_result", prompt, resolved_value=number)}
    match = re.fullmatch(r"(?:y\s+es|(?:y\s+)?(?:[ée]l|ella|eso|ese|esa)\s+es)\s+(.+)", clean, re.I)
    if not match:
        match = re.fullmatch(r"es\s+(\S+)", clean, re.I)
    if match:
        subject = context.get("subject")
        if not subject or context.get("ambiguous"):
            return {"kind": "clarify", "reply": "¿De quién hablamos? Escribe el nombre para que pueda comprobarlo."}
        property_text = re.sub(r"^(?:un|una|el|la)\s+", "", match.group(1), flags=re.I)
        prompt = "dime si " + subject + " es " + property_text
        return {"kind": "personal", "prompt": prompt, "write": False, "subject": subject,
                "reference_prompt": prompt,
                "context_resolution": _resolution(last, "subject", prompt, resolved_subject=subject)}
    if folded in {"que recuerdas", "que recuerdas de mi", "que sabes de mi", "muestra tu memoria"}:
        return {"kind": "memory"}
    if folded in {"ayuda", "que puedes hacer", "como te enseno", "como puedo entrenarte"}:
        return {"kind": "help"}
    expression = clean.replace("×", "*").replace("÷", "/")
    if re.fullmatch(r"[\d\s+\-*/().,]+", expression) and re.search(r"\d", expression):
        return {"kind": "personal", "prompt": "calcula " + expression, "write": False}
    match = re.fullmatch(r"(?:cu[aá]nto es|cu[aá]nto da|calcula|resuelve|dime cu[aá]nto es)\s+(.+)", clean, re.I)
    if match:
        expression = match.group(1).replace("×", "*").replace("÷", "/")
        if re.fullmatch(r"[\d\s+\-*/().,]+", expression) and re.search(r"\d", expression):
            return {"kind": "personal", "prompt": "calcula " + expression, "write": False}
    for pattern, operator in ((r"suma (-?[\d.,]+) y (-?[\d.,]+)", "+"),
                              (r"multiplica (-?[\d.,]+) por (-?[\d.,]+)", "*"),
                              (r"divide (-?[\d.,]+) entre (-?[\d.,]+)", "/")):
        match = re.fullmatch(pattern, clean, re.I)
        if match:
            return {"kind": "personal", "prompt": f"calcula {match.group(1)} {operator} {match.group(2)}", "write": False}
    if re.match(r"^(recuerda|aprende|guarda|corrige|actualiza|quiero que recuerdes|necesito que recuerdes)\b", folded):
        prompt = clean
        prompt = re.sub(r"^(?:necesito|quiero) que recuerdes\s+(?:que\s+)?", "recuerda que ", prompt, flags=re.I)
        prompt = re.sub(r"^(?:recuerda|aprende) que (si alguien\s+)", r"\1", prompt, flags=re.I)
        return {"kind": "personal", "prompt": prompt, "write": True}
    if re.match(r"^(observa|crea la muestra|resuelve la tarea|resuelve .+ usando la regla|decide desde)\b", folded):
        return {"kind": "personal", "prompt": clean, "write": True}
    if re.match(r"^(como se llama mi|dime el nombre de mi|cual es el nombre de mi|dime como se llama mi|lee la regla|recupera la regla|dime la ruta|como llego|busca un camino|no calcules|no definas|no expliques)\b", folded):
        return {"kind": "personal", "prompt": clean, "write": False}
    match = re.fullmatch(r"(?:qu[eé] es|qu[eé] significa|qui[eé]n es|h[aá]blame de|qu[eé] sabes de)\s+(?:el |la |un |una )?(.+)", clean, re.I)
    if match:
        return {"kind": "definition", "subject": match.group(1), "prompt": clean}
    match = re.fullmatch(r"(?:dime si |comprueba si |sabes si |por qu[eé] )?(.+?)\s+es\s+(.+)", clean, re.I)
    if match and not folded.startswith(("que ", "quien ", "si ")):
        return {"kind": "personal", "prompt": "dime si " + match.group(1) + " es " + match.group(2),
                "write": False, "subject": match.group(1), "reference_prompt": clean,
                "explain": folded.startswith("por que ")}
    if folded.startswith("es "):
        return {"kind": "personal", "prompt": clean, "write": False, "reference_prompt": clean}
    social = {"hola", "hola bby q", "hey", "buenas", "buenos dias", "buenas tardes", "buenas noches",
              "como estas", "que tal", "gracias", "muchas gracias", "de nada", "adios", "hasta luego",
              "quien eres", "como te llamas", "cual es tu nombre"}
    if folded in social or re.match(r"^(que|quien|cuando|donde|como|hablame|explica|define|dime si)\b", folded):
        return {"kind": "reference", "prompt": clean}
    if folded in {"repitelo", "explicalo otra vez", "dime mas"} and last:
        return {"kind": "repeat", "previous": last,
                "context_resolution": _resolution(last, "previous_turn", last.get("normalized_prompt"))}
    return {"kind": "unknown"}


def _render(receipt, root, personal_db, explain=False, proof=None):
    rows = receipt.get("results", [])
    query = next((r for r in rows if r.get("kind") == "query"), None)
    if query:
        if query.get("status") == 1 and query.get("proof"):
            if explain and proof:
                parts = []
                for step in reversed(proof):
                    if step.get("rule_text") and step["rule_text"] not in parts:
                        parts.append(step["rule_text"])
                    if step["text"] not in parts:
                        parts.append(step["text"])
                return "La prueba usa lo que tengo guardado: " + " ".join(parts), True, "native_result_rendering"
            return "Sí, puedo demostrarlo con la información que tengo.", True, "native_result_rendering"
        if query.get("status") == -1:
            return "No. La información guardada indica lo contrario.", True, "native_result_rendering"
        if query.get("status") == 2:
            return "Tengo información contradictoria sobre eso. Revisa los datos que me enseñaste.", False, "native_result_rendering"
        return UNKNOWN, False, "abstention"
    if any(r.get("kind") == "definition" and r.get("status") == 2 for r in rows):
        return "Tengo información contradictoria sobre eso. Revisa los datos que me enseñaste.", False, "native_result_rendering"
    if not receipt.get("ok"):
        return UNKNOWN, False, "abstention"
    parts = []
    origin = "native_result_rendering"
    for row in rows:
        kind = row.get("kind")
        if kind == "text":
            value = row.get("text", "").strip()
            if not value or _fold(value).startswith(("no tengo informacion suficiente", "no tengo suficiente informacion", "necesito mas ejemplos", "no entendi", "aprendi", "he aprendido")):
                return UNKNOWN, False, "abstention"
            parts.append(value); origin = "native_reference" if row.get("native_source") == "E025" else "native_text"
        elif kind == "math" and row.get("status") == 1:
            parts.append(str(row["value"]) if type(row["value"]) is int else format(row["value"], ".15g"))
        elif kind == "put":
            memory = personal_memory(root, personal_db)
            fact = next((f for f in memory["facts"] if _fold(f["subject"]) == _fold(row["subject"]) and _fold(f["value"]) == _fold(str(row["value"])) and f["polarity"] == row.get("polarity", 1)), None)
            parts.append("He guardado: " + fact["text"] if fact else "He guardado lo que me pediste.")
        elif kind == "rule":
            parts.append("He guardado la regla.")
        elif kind == "lookup":
            parts.append("Se llama " + str(row["value"]) + ".")
        elif kind == "definition":
            if explain:
                evidence = []
                for fact in row["facts"]:
                    for statement in (fact.get("rule_text"), fact["text"]):
                        if statement and statement not in evidence:
                            evidence.append(statement)
                parts.append("La prueba usa lo que tengo guardado: " + " ".join(evidence))
            else:
                parts.append("Según mi memoria: " + " ".join(f["text"] for f in row["facts"]))
        elif kind == "route":
            parts.append("La ruta es: " + " → ".join(row.get("path", [])) + ".")
        elif kind in ("greet", "cancel"):
            parts.append(row.get("text", ""))
        elif kind == "feedback":
            parts.append("He aplicado el aprendizaje a mis modelos y guardado el resultado.")
        elif kind == "recall":
            parts.append("El valor guardado es " + str(row.get("value")) + ".")
        elif kind in ("mission", "explain"):
            voice = row.get("voice", {})
            if isinstance(voice.get("text"), str):
                parts.append(voice["text"])
            else:
                parts.append("La tarea produjo la acción " + str(row.get("action")) + "." if row.get("supported") else UNKNOWN)
    return ("\n".join(p for p in parts if p), True, origin) if parts else (UNKNOWN, False, "abstention")


def _answer(route, request_id, text, root, personal_db):
    import u03_integrated as core
    kind = route["kind"]
    provenance = {"route": route, "request_text": text, "response_origin": "abstention",
                  "native_XI": False, "receipt": None, "personal_memory_written": False,
                  "deterministic_presentation_is_model_generation": False}
    if route.get("context_resolution"):
        provenance["context_resolution"] = route["context_resolution"]
    if kind == "clarify":
        provenance["response_origin"] = "interface"
        return route["reply"], False, provenance
    if kind in ("why", "repeat"):
        previous = route.get("previous")
        if not previous:
            return UNKNOWN, False, provenance
        earlier = previous.get("route", {})
        if earlier.get("kind") == "reference" or previous.get("response_origin") == "native_reference":
            prompt = earlier.get("prompt") or previous.get("normalized_prompt")
            if prompt:
                receipt = _reference(root, "por qué" if kind == "why" else prompt, prompt if kind == "why" else None)
                if receipt:
                    reply, understood, origin = _render(receipt, root, personal_db)
                    provenance.update(response_origin=origin, native_XI=True, receipt=receipt,
                                      normalized_prompt="por qué" if kind == "why" else prompt)
                    return reply, understood, provenance
        prompt = previous.get("normalized_prompt")
        if earlier.get("kind") == "definition" and earlier.get("subject"):
            receipt = _personal_definition(earlier["subject"], root, personal_db)
            if receipt:
                reply, understood, origin = _render(receipt, root, personal_db, explain=kind == "why")
                provenance.update(response_origin=origin, native_XI=True, receipt=receipt, normalized_prompt=prompt)
                return reply, understood, provenance
        if prompt and earlier.get("kind") == "personal" and not earlier.get("write"):
            receipt, proof = _personal_inference(prompt, "conversation-why-" + request_id, root, personal_db)
            reply, understood, origin = _render(receipt, root, personal_db, explain=kind == "why", proof=proof)
            provenance.update(response_origin=origin, native_XI=True, receipt=receipt, proof=proof, normalized_prompt=prompt)
            return reply, understood, provenance
        return UNKNOWN, False, provenance
    if kind == "help":
        provenance["response_origin"] = "interface"
        return "Puedes preguntarme sobre lo que sé, hacer cálculos o decirme «recuerda que…». En Modelo puedes revisar mi memoria y entrenarme con ejemplos.", True, provenance
    if kind == "memory":
        memory = personal_memory(root, personal_db)
        provenance.update(response_origin="native_result_rendering", native_XI=True, memory=memory)
        lines = [row["text"] for row in memory["facts"]]
        return ("Tengo guardado: " + " ".join(lines) if lines else "Todavía no tengo hechos personales guardados."), True, provenance
    if kind == "definition":
        receipt = _personal_definition(route["subject"], root, personal_db)
        if receipt:
            reply, understood, origin = _render(receipt, root, personal_db)
            provenance.update(response_origin=origin, native_XI=True, receipt=receipt, normalized_prompt=route["prompt"])
            return reply, understood, provenance
        kind = "reference"
    if kind == "personal":
        prompt = route["prompt"]
        if route.get("write"):
            result = json.loads(core.turn("conversation-" + request_id, prompt, ""))
            receipt = result["receipt"]; proof = []
            changed = any(row.get("kind") in ("put", "rule", "remember", "observe", "mission", "feedback")
                          and row.get("status") == 1 for row in receipt.get("results", []))
            provenance["personal_memory_written"] = bool(changed and receipt.get("committed"))
            if not changed:
                provenance.update(native_XI=True, receipt=receipt, normalized_prompt=prompt)
                return UNKNOWN, False, provenance
        else:
            receipt, proof = _personal_inference(prompt, "conversation-" + request_id, root, personal_db)
        reply, understood, origin = _render(receipt, root, personal_db, explain=route.get("explain", False), proof=proof)
        provenance.update(response_origin=origin, native_XI=True, receipt=receipt, proof=proof, normalized_prompt=prompt)
        if understood or not route.get("reference_prompt"):
            return reply, understood, provenance
        memory = personal_memory(root, personal_db)
        question = " " + _fold(route.get("reference_prompt", prompt)) + " "
        if any(" " + _fold(row["subject"]) + " " in question for row in memory["facts"]):
            return reply, understood, provenance
        provenance["personal_attempt"] = receipt
        kind = "reference"
    if kind == "reference":
        prompt = route.get("reference_prompt", route.get("prompt", text))
        receipt = _reference(root, prompt)
        if receipt:
            reply, understood, origin = _render(receipt, root, personal_db)
            provenance.update(response_origin=origin, native_XI=True, receipt=receipt, normalized_prompt=prompt)
            return reply, understood, provenance
    return UNKNOWN, False, provenance


def run(args, root, personal_db):
    import u03_mobile as base
    with base._lock:
        return _run(args, Path(root), Path(personal_db))


def _run(args, root, personal_db):
    import u03_mobile as base
    if not isinstance(args, dict):
        raise ValueError("Argumentos de conversación inválidos")
    action = args.get("action")
    if action == "personal_memory":
        return personal_memory(root, personal_db, args.get("query", ""))
    if action not in ("send", "history", "clear_view", "export", "list", "create", "select", "open", "rename", "archive", "restore"):
        raise ValueError("Acción de conversación desconocida")
    folder = personal_db.parent.parent / "conversation-v1"
    with closing(_connect(folder)) as db:
        if action == "list":
            return {"ok": True, "action": action, "active_conversation_id": _active_id(db),
                    "conversations": _conversations(db, args.get("include_archived") is True, args.get("query", ""))}
        if action == "history":
            conversation = _conversation(db, args.get("conversation_id"))
            view = conversation["view_id"]
            return {"ok": True, "action": action, "view_id": view, "conversation_id": conversation["id"],
                    "conversation": conversation, "active_conversation_id": _active_id(db),
                    "messages": _history(db, view, args.get("include_archived") is True and not args.get("conversation_id")),
                    "pending_requests": _pending(db, view)}
        request_id = _input(args.get("request_id"), "request_id", 200)
        clean_args = dict(args); clean_args["request_id"] = request_id
        if action == "send":
            clean_args["text"] = _input(args.get("text"))
        fingerprint = _sha(_json(clean_args).encode())
        prior = db.execute("SELECT fingerprint,state,result,route,view,created_ms FROM requests WHERE id=?", (request_id,)).fetchone()
        if prior and prior[0] != fingerprint:
            raise ValueError("Este identificador ya corresponde a otro mensaje")
        if prior and prior[1] == "complete":
            # A historical receipt is immutable. In particular, replay must
            # neither select its old conversation nor recompute its context.
            return json.loads(prior[2])
        if action == "send":
            if prior:
                route, view, created = json.loads(prior[3]), prior[4], prior[5]
                conversation = _conversation(db, view=view)
            else:
                conversation = _conversation(db, args.get("conversation_id"))
                if conversation["archived"]:
                    raise ValueError("Restaura esta conversación para volver a escribir en ella")
                view = conversation["view_id"]
                route, created = _route(clean_args["text"], db, view), time.time_ns() // 1000000
                db.execute("BEGIN IMMEDIATE")
                try:
                    db.execute("INSERT INTO requests VALUES(?,?,'pending',?,?,?,?,?,NULL)",
                               (request_id, fingerprint, action, _json(clean_args), _json(route), view, created))
                    db.execute("INSERT INTO messages VALUES(?,?,?,?,?,?,NULL)",
                               (request_id + ":user", view, "user", clean_args["text"], request_id, created))
                    if conversation["message_count"] == 0:
                        db.execute("UPDATE conversations SET title=CASE WHEN title_custom=0 THEN ? ELSE title END,updated_ms=? WHERE view=?",
                                   (_title(clean_args["text"]), created, view))
                    else:
                        db.execute("UPDATE conversations SET updated_ms=? WHERE view=?", (created, view))
                    db.execute("COMMIT")
                except BaseException:
                    db.execute("ROLLBACK"); raise
            reply, understood, provenance = _answer(route, request_id, clean_args["text"], root, personal_db)
            provenance.update(source_commit=base._manifest.get("apk_source_commit"),
                              module_sha256=base._manifest.get("mobile_sources_sha256", {}).get("u03_conversation.py"),
                              conversation_id=conversation["id"])
            finished = time.time_ns() // 1000000
            user = {"id": request_id + ":user", "role": "user", "text": clean_args["text"], "request_id": request_id, "created_at_ms": created}
            assistant = {"id": request_id + ":assistant", "role": "assistant", "text": reply,
                         "request_id": request_id, "created_at_ms": finished,
                         "response_origin": provenance["response_origin"], "provenance": provenance}
            result = {"ok": True, "action": action, "request_id": request_id, "reply": reply,
                      "understood": understood, "response_origin": provenance["response_origin"],
                      "native_XI": provenance["native_XI"], "receipt": provenance["receipt"],
                      "messages": [user, assistant], "message_scope": "new_turn", "view_id": view,
                      "conversation_id": conversation["id"]}
            db.execute("BEGIN IMMEDIATE")
            try:
                db.execute("INSERT INTO messages VALUES(?,?,?,?,?,?,?)",
                           (assistant["id"], view, "assistant", reply, request_id, finished, _json(provenance)))
                db.execute("UPDATE conversations SET updated_ms=? WHERE view=?", (finished, view))
                db.execute("UPDATE requests SET state='complete',result=? WHERE id=?", (_json(result), request_id))
                db.execute("COMMIT")
            except BaseException:
                db.execute("ROLLBACK"); raise
            return result
        if action == "export":
            conversation = _conversation(db, args.get("conversation_id")); view = conversation["view_id"]
            all_views = args.get("include_archived") is True
            exported = _conversations(db, True) if all_views else [conversation]
            document = {"schema": SCHEMA, "view_id": view, "conversation_id": conversation["id"],
                        "messages": _history(db, view, all_views),
                        "scope": "all_conversations" if all_views else "conversation",
                        "conversations": [dict(item, messages=_history(db, item["view_id"])) for item in exported],
                        "source_commit": base._manifest.get("apk_source_commit"),
                        "source_sha256": base._manifest.get("mobile_sources_sha256", {}),
                        "exported_ms": time.time_ns() // 1000000, "model_checkpoint_included": False}
            destination = folder / "exports" / (uuid.uuid4().hex + ".json")
            destination.parent.mkdir(exist_ok=True)
            with destination.open("w") as stream:
                stream.write(_json(document) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
            result = {"ok": True, "action": action, "path": str(destination), "conversation_id": conversation["id"],
                      "filename": "BBY-Q-0-conversacion.json", "mime": "application/json", "sha256": _sha(destination.read_bytes())}
        elif action not in ("create", "clear_view"):
            conversation = _conversation(db, _input(args.get("conversation_id"), "conversation_id", 200))
            view = conversation["view_id"]
        db.execute("BEGIN IMMEDIATE")
        try:
            if action in ("create", "clear_view"):
                conversation = _new_conversation(db, args.get("title")); view = conversation["view_id"]
            elif action in ("select", "open"):
                if conversation["archived"]:
                    raise ValueError("Restaura esta conversación para volver a usarla")
                db.execute("UPDATE preferences SET value=? WHERE key='view'", (str(view),))
            elif action == "rename":
                title = " ".join(_input(args.get("title"), "título", 120).split())
                db.execute("UPDATE conversations SET title=?,title_custom=1,updated_ms=? WHERE view=?",
                           (title, time.time_ns() // 1000000, view))
            elif action == "archive":
                db.execute("UPDATE conversations SET archived=1,updated_ms=? WHERE view=?", (time.time_ns() // 1000000, view))
                if _view(db) == view:
                    other = db.execute("SELECT view FROM conversations WHERE archived=0 ORDER BY updated_ms DESC,view DESC LIMIT 1").fetchone()
                    if other:
                        db.execute("UPDATE preferences SET value=? WHERE key='view'", (str(other[0]),))
                    else:
                        _new_conversation(db)
            elif action == "restore":
                db.execute("UPDATE conversations SET archived=0,updated_ms=? WHERE view=?", (time.time_ns() // 1000000, view))
            if action != "export":
                conversation = _conversation(db, view=view)
                result = {"ok": True, "action": action, "view_id": view, "conversation_id": conversation["id"],
                          "conversation": conversation, "active_conversation_id": _active_id(db), "personal_memory_erased": False}
                if action in ("create", "clear_view"):
                    result["messages"] = []
            db.execute("INSERT INTO requests VALUES(?,?,'complete',?,?,NULL,?,?,?)",
                       (request_id, fingerprint, action, _json(clean_args), view, time.time_ns() // 1000000, _json(result)))
            db.execute("COMMIT")
        except BaseException:
            db.execute("ROLLBACK"); raise
        return result
