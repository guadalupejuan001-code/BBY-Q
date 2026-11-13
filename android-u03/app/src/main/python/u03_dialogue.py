"""Train and use personal conversational responses with the native C1 readout."""
from contextlib import closing
import json
from pathlib import Path
import re
import sqlite3
import tempfile
import unicodedata


TOKENS = re.compile(r"\w+|[^\w\s]")
CORRECTION = re.compile(r"(?:no\s*,\s*)?(?:mejor\s+)?(?:dilo|responde|contesta)\s+as[ií]"
                        r"(?:\s*[:,]\s*|\s+|$)(.*)", re.I | re.S)
EXAMPLE = re.compile(r'cuando\s+te\s+(?:diga|pregunte)\s+(?:«([^»]+)»|"([^"]+)")\s*,?\s*'
                     r'(?:responde|contesta|di)(?:\s*:\s*|\s+|$)(.*)', re.I | re.S)
EXAMPLE_PREFIX = re.compile(r"cuando\s+te\s+(?:diga|pregunte)\b", re.I)
FORMS = {
    "hola": {"hola", "hey", "ey", "buenas", "hola de nuevo", "hola otra vez", "qué onda"},
    "cómo estás": {"cómo estás", "como estas", "qué tal", "que tal", "cómo te va", "como te va"},
    "hasta luego": {"adiós", "adios", "hasta luego", "nos vemos", "hasta pronto", "chau"},
}


def instruction(text):
    match = EXAMPLE.fullmatch(text)
    if match:
        return (match[1] or match[2]).strip(), _unquote(match[3])
    match = CORRECTION.fullmatch(text)
    if match:
        return None, _unquote(match[1])
    if EXAMPLE_PREFIX.match(text):
        return "", ""
    return None


def _unquote(text):
    text = text.strip()
    if len(text) >= 2 and (text[0], text[-1]) in {('«', '»'), ('"', '"'), ('“', '”')}:
        return text[1:-1].strip()
    return text


def _phrase(text):
    phrase = unicodedata.normalize("NFC", text).casefold().strip("¿?¡! .\n\t")
    return " ".join(phrase.split())


def cue(route, text):
    kind = route["kind"]
    if kind == "profile" and "value" in route:
        value = unicodedata.normalize("NFC", route["value"]).casefold()
        return "presentación " + route["predicate"] + " " + value
    if kind == "definition":
        return "definición " + _phrase(route["subject"])
    if kind not in ("unknown", "reference"):
        return None
    phrase = _phrase(text)
    phrase = re.sub(r"^(?:(?:oye|por favor|bby q)[, ]+)+", "", phrase)
    phrase = re.sub(r"(?:[, ]+(?:por favor|bby q))+$", "", phrase).strip(" ,¿?¡!.")
    if not phrase or not any(char.isalnum() for char in phrase):
        return None
    return "conversación " + next((name for name, forms in FORMS.items() if phrase in forms), phrase)


def _model(path, words, output):
    from integration.unified.common import C1

    model = C1.Model(path, words, output)
    # Give each output position enough weight to distinguish repeated words and
    # punctuation. This coefficient belongs only to the new personal readout.
    position_scale = "cmp r6 8\njne c1_scale_done\nfset f23 .5\n"
    if model.library.count(position_scale) != 1:
        model.s.close()
        raise RuntimeError("Cambió el programa XI del lector de texto")
    model.library = model.library.replace(position_scale, position_scale.replace(".5", "4"))
    return model


def _train(root, phrase, answer):
    from integration.unified.common import C1, digest
    from schema import C, S, LIMITS

    spans = list(TOKENS.finditer(answer))
    tokens = [match[0] for match in spans]
    if not tokens or len(tokens) >= LIMITS["output_tokens"]:
        return None, "Enséñame una frase de hasta 63 palabras y signos de puntuación."
    if len(C1.words(phrase)) > LIMITS["tokens"] or len(phrase.encode()) > LIMITS["raw_bytes"]:
        return None, "Usa una frase más corta para decirme cuándo debo responder así."
    ends = [0, *(match.end() for match in spans[:-1])]
    gaps = [answer[start:match.start()] for start, match in zip(ends, spans)]
    output = ["<eos>", *dict.fromkeys(tokens)]
    seed = Path(root) / "build/dialogue/seed.rvp"
    with tempfile.TemporaryDirectory(prefix="bbyq-dialogue-") as temp, _model(seed, ["<pad>"], output) as model:
        model.run(f"store64 {C+208} {len(output)}\nfstore {C+112} 0.7")
        model.prepare(phrase, cache=S["CACHE"], retain_bytes=False)
        program = "".join(model.active(tokens[:i], cache=S["CACHE"]) +
                          f"store64 {C+64} {model.output_ids[token]}\ncall c1_train\n"
                          for i, token in enumerate([*tokens, "<eos>"]))
        for _ in range(8):
            model.run(program)
            candidate = model.generate(phrase)
            if candidate["terminated"] and candidate["tokens"] == tokens:
                path = Path(temp) / "trained.rvp"
                model.s.save(path)
                return (path.read_bytes(), {"input_vocabulary": model.codec.words, "output_vocabulary": output,
                                            "gaps": gaps, "answer_sha256": digest(answer.encode()),
                                            "native_updates": model.number(224)}), None
    return None, "Todavía no consigo decir esa frase completa. Puedes probar con una frase más corta."


def teach(database, root, identifier, phrase, prompt, answer):
    from integration.unified.common import digest, encoded

    fingerprint = digest(encoded({"cue": phrase, "prompt": prompt, "answer": answer}))
    with closing(sqlite3.connect(database, timeout=60, isolation_level=None)) as db, db:
        db.execute("PRAGMA synchronous=FULL")
        db.execute("BEGIN IMMEDIATE")
        prior = db.execute("SELECT fingerprint,result FROM unified_requests WHERE id=?", (identifier,)).fetchone()
        if prior:
            if prior[0] != fingerprint:
                raise ValueError("Este identificador ya corresponde a otro ejemplo")
            return json.loads(prior[1])
        trained, error = _train(root, phrase, answer)
        row = {"kind": "dialogue_lesson", "status": int(trained is not None), "prompt": prompt}
        trace = []
        if trained is not None:
            checkpoint, info = trained
            checkpoint_sha = digest(checkpoint)
            metadata = encoded(info)
            db.execute("""CREATE TABLE IF NOT EXISTS dialogue_lessons(
                cue TEXT PRIMARY KEY, checkpoint BLOB NOT NULL, checkpoint_sha TEXT NOT NULL,
                metadata BLOB NOT NULL, metadata_sha TEXT NOT NULL)""")
            db.execute("INSERT OR REPLACE INTO dialogue_lessons VALUES(?,?,?,?,?)",
                       (phrase, checkpoint, checkpoint_sha, metadata, digest(metadata)))
            row.update(checkpoint_sha256=checkpoint_sha, native_updates=info["native_updates"],
                       answer_sha256=info["answer_sha256"])
            trace.append({"bank": "personal_dialogue", "operation": "c1_train/c1_next", "native": True})
        else:
            row["reason"] = error
        receipt = {"ok": bool(trained), "committed": bool(trained), "entity": "U02", "request_id": identifier,
                   "results": [row], "trace": trace}
        record = (identifier, fingerprint, encoded(receipt))
        db.execute("INSERT INTO unified_requests VALUES(?,?,?)", record)
        db.execute("INSERT INTO requests VALUES(?,?,?)", record)
        return receipt


def generate(database, phrase):
    from integration.unified.common import digest

    if phrase is None:
        return None
    with closing(sqlite3.connect(database, timeout=60)) as db:
        if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='dialogue_lessons'").fetchone():
            return None
        row = db.execute("SELECT checkpoint,checkpoint_sha,metadata,metadata_sha FROM dialogue_lessons WHERE cue=?",
                         (phrase,)).fetchone()
    if not row:
        return None
    checkpoint, checkpoint_sha, metadata, metadata_sha = row
    if digest(checkpoint) != checkpoint_sha or digest(metadata) != metadata_sha:
        raise RuntimeError("El ejemplo de conversación guardado está dañado")
    info = json.loads(metadata)
    with tempfile.TemporaryDirectory(prefix="bbyq-dialogue-read-") as temp:
        path = Path(temp) / "trained.rvp"
        path.write_bytes(checkpoint)
        with _model(path, info["input_vocabulary"], info["output_vocabulary"]) as model:
            prediction = model.generate(phrase)
    tokens = prediction["tokens"]
    if not prediction["terminated"] or len(tokens) != len(info["gaps"]):
        return None
    text = "".join(gap + token for gap, token in zip(info["gaps"], tokens))
    if digest(text.encode()) != info["answer_sha256"]:
        return None
    return {"ok": True, "committed": False, "entity": "U02", "checkpoint_sha256": checkpoint_sha,
            "native_output_sha256": info["answer_sha256"], "results": [{"kind": "text", "text": text, "tokens": tokens}],
            "trace": [{"bank": "personal_dialogue", "operation": "c1_encode_input/c1_next", "native": True}]}
