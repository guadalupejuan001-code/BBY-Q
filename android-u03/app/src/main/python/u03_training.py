"""Durable, user-directed training over the unchanged original XI engines.

Each edit runs on a new SQLite copy. Only a committed journal entry selects
that version, so interruption never leaves a half-trained candidate selected.
Activation is explicit, validated, compare-and-swap guarded, and backed up.
The ordinary chat continues to use its original single SQLite authority.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from contextlib import contextmanager, closing
import json
import os
import re
import sqlite3
import tempfile
import time
import unicodedata
import uuid
import zipfile

SCHEMA = "BBYQ-C17-user-training-v1"
_ACTIONS = {"status", "create", "fact", "rule", "query", "joint_prepare",
            "joint_feedback", "joint_discard", "validate", "activate", "restore", "export"}


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha(value):
    return sha256(value).hexdigest()


def _fingerprint(value):
    return _sha(_json(value).encode())


def _now():
    return time.time_ns()


def _text(value, field, maximum=160):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ValueError(field + " requiere texto no vacío de hasta " + str(maximum) + " caracteres")
    if any(ord(c) < 32 for c in value):
        raise ValueError(field + " no admite saltos de línea ni controles")
    return " ".join(value.strip().split())


def _symbol(value, field):
    value = _text(value, field, 64)
    if not re.fullmatch(r"[^\W\d_]+(?: [^\W\d_]+){0,5}", value, re.UNICODE):
        raise ValueError(field + " debe contener entre una y seis palabras, sólo letras")
    return value


def _question_key(text):
    """Conservative lexical exposure key; not a semantic novelty detector."""
    text = unicodedata.normalize("NFKC", text).casefold()
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    text = " ".join(text.split())
    if text.startswith("dime si "):
        text = text[8:]
    return " ".join(token for token in text.split() if token != "es")


def _exposures(session):
    exposed = session.setdefault("question_exposures", {})
    for event in session["events"]:
        if event["action"] == "query":
            text = event["input"].get("text", "")
            exposed.setdefault(_question_key(text), {"request_id": event["request_id"],
                                                     "split": event["input"].get("split", "practice")})
    return exposed


def _id(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{32}", value):
        raise ValueError("Identificador de sesión desconocido")
    return value


def _copy(source, target):
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(str(source), timeout=60)) as src:
        with closing(sqlite3.connect(str(target), timeout=60)) as dst:
            src.backup(dst)
            if dst.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise RuntimeError("La copia SQLite no superó su verificación")


def _seal(path):
    with closing(sqlite3.connect(str(path), timeout=60)) as db:
        db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        db.execute("PRAGMA journal_mode=DELETE")
    with Path(path).open("rb") as stream:
        os.fsync(stream.fileno())


def _snapshot(path):
    from integration.unified.session import Session
    from integration.memory_u03_c09.view import UnifiedMemoryView
    with Session(path) as model:
        model._banks()  # Authenticates actual bytes, not only stored SHA fields.
        view = UnifiedMemoryView(model).snapshot()
        if len(view["bank_sha256"]) != 7 or not view["C1_synchronized_with_U02"]:
            raise RuntimeError("La autoridad original C1/U02 perdió su identidad")
        if view["new_memory_authorities"] != 0:
            raise RuntimeError("No se permite una autoridad de memoria adicional")
        return model.snapshot()


def _identity(path):
    result = {"snapshot": _snapshot(path)}
    # Failed/read-only receipts also count as new personal activity. A revision
    # alone would miss them and silently discard history during activation.
    h = sha256()
    with closing(sqlite3.connect(str(path))) as db:
        for table in ("requests", "unified_requests"):
            h.update(table.encode())
            for row in db.execute("SELECT id,fingerprint,result FROM " + table + " ORDER BY id"):
                for value in row:
                    raw = value.encode() if isinstance(value, str) else bytes(value)
                    h.update(len(raw).to_bytes(8, "big")); h.update(raw)
    result["receipts_sha256"] = h.hexdigest()
    return result


def _native(path, request_id, prompt, payload=None):
    from integration.unified.session import Session
    with Session(path) as model:
        return model.turn(request_id, prompt, payload)


def _require_native(receipt, kind):
    item = next((x for x in reversed(receipt.get("results", [])) if x.get("kind") == kind), None)
    if not receipt.get("ok") or item is None or item.get("status") != 1:
        raise ValueError("XI no aceptó esta lección: " + _json(receipt))
    return item


@contextmanager
def _evaluation_copy(source):
    with tempfile.TemporaryDirectory(prefix="bbyq-c17-evaluate-") as tmp:
        path = Path(tmp) / "evaluation.sqlite"
        _copy(source, path)
        yield path


def _evaluate(source, prompt, identifier):
    # No teacher, expected result, gradient or feedback can enter this call.
    with _evaluation_copy(source) as path:
        return _native(path, identifier, prompt)


def _query_status(receipt):
    item = next((x for x in reversed(receipt.get("results", [])) if x.get("kind") == "query"), None)
    if item is None:
        return None
    status = item.get("status")
    if status == 1 and not item.get("proof"):
        return None
    return status


def _weights(path):
    from integration.joint_u03_c11.campaign import _read_weights
    return _read_weights(path)[0]


def _connect(folder):
    folder.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(folder / "journal.sqlite"), timeout=60, isolation_level=None)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=FULL")
    db.executescript("""
      CREATE TABLE IF NOT EXISTS sessions(id TEXT PRIMARY KEY,document TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS requests(id TEXT PRIMARY KEY,fingerprint TEXT NOT NULL,result TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
    """)
    return db


def _load(db, identifier):
    row = db.execute("SELECT document FROM sessions WHERE id=?", (_id(identifier),)).fetchone()
    if row is None:
        raise ValueError("No existe esa sesión de entrenamiento")
    return json.loads(row[0])


def _save(db, session):
    db.execute("INSERT INTO sessions VALUES(?,?) ON CONFLICT(id) DO UPDATE SET document=excluded.document",
               (session["session_id"], _json(session)))


def _active(db):
    row = db.execute("SELECT value FROM settings WHERE key='active'").fetchone()
    return json.loads(row[0]) if row else None


def _summary(session, active):
    return {"session_id": session["session_id"], "title": session["title"],
            "state": session["state"], "created_ns": session["created_ns"],
            "training_count": session["training_count"],
            "holdout_count": (session.get("validation") or {}).get("holdout_count", len(session["holdouts"])),
            "active": bool(active and active["session_id"] == session["session_id"]),
            "pending_exercise_id": session.get("pending_exercise_id"),
            "backup_id": session.get("backup_id")}


def _event(session, request_id, action, payload, result):
    session["events"].append({"request_id": request_id, "action": action, "time_ns": _now(),
                              "input": payload, "result": result,
                              "candidate_snapshot": session["candidate_snapshot"]})


def _edited(session, target, snapshot):
    session["candidate_path"] = str(target)
    session["candidate_snapshot"] = snapshot
    session["holdouts"] = []
    session["validation"] = None
    session["state"] = "training"


def _check_editable(session):
    if session["state"] in ("activated", "restored"):
        raise ValueError("Esta versión ya se publicó. Crea una sesión nueva desde tu modelo personal actual")


def _stage(folder, session, request_id):
    destination = folder / session["session_id"] / "versions" / (_sha(request_id.encode()) + ".sqlite")
    # A killed request may have left its unpublished stage. Never reuse it as
    # the next input; rebuild from the last journal-selected candidate.
    for suffix in ("", "-wal", "-shm", "-journal"):
        item = Path(str(destination) + suffix)
        if item.exists():
            item.unlink()
    _copy(Path(session["candidate_path"]), destination)
    return destination


def _validate(session):
    baseline = Path(session["baseline_path"]); candidate = Path(session["candidate_path"])
    before = {"baseline": _identity(baseline), "candidate": _identity(candidate)}
    results = {"baseline": {"regressions": [], "holdouts": []},
               "candidate": {"regressions": [], "holdouts": []}}
    regressions = (("calcula 7 + 3", 10.0), ("calcula 9 - 4", 5.0), ("calcula 6 * 7", 42.0))
    for name, source in (("baseline", baseline), ("candidate", candidate)):
        for index, (prompt, value) in enumerate(regressions):
            receipt = _evaluate(source, prompt, "c17-validation-math-" + str(index))
            item = next((x for x in receipt.get("results", []) if x.get("kind") == "math"), {})
            passed = bool(receipt.get("ok") and item.get("status") == 1 and item.get("value") == value)
            results[name]["regressions"].append({"text": prompt, "expected": value,
                                                 "passed": passed, "receipt": receipt})
        for index, case in enumerate(session["holdouts"]):
            receipt = _evaluate(source, case["text"], "c17-validation-holdout-" + str(index))
            actual = _query_status(receipt)
            results[name]["holdouts"].append({"text": case["text"], "expected_status": case["expected_status"],
                                              "actual_status": actual, "passed": actual == case["expected_status"],
                                              "receipt": receipt})
    joint = [e for e in session["events"] if e["action"] == "joint_feedback"]
    if joint:
        from integration.joint_u03_c11.campaign import _episode, score_runs
        from integration.joint_u03_c11.native import native_sample_teacher
        from integration.joint_u03_c11.protocol import Heldout
        from integration.unified.session import Session
        used = {e["seed"] for e in session["exercises"].values()}
        seeds = []
        for lower, upper in ((23060113, 2147483648), (0, 23060113)):
            for seed in range(lower, upper):
                if seed not in used:
                    seeds.append(seed)
                if len(seeds) == 2:
                    break
            if len(seeds) == 2:
                break
        if len(seeds) != 2:
            raise ValueError("Se necesitan dos muestras reservadas que nunca se hayan usado para entrenar")
        cases = tuple(Heldout("personal-validation", ("Vela", "Delta")[i],
                             ("Sol Claro", "Luna Serena")[i], seed) for i, seed in enumerate(seeds))
        predictions = {name: [_episode(source, case) for case in cases]
                       for name, source in (("baseline", baseline), ("candidate", candidate))}
        # Open the oracle only after every arm's native inference completed.
        with Session(baseline) as model:
            origin = model.initial["v3"]
        teachers = {case.seed: native_sample_teacher(origin, case.seed) for case in cases}
        for name in predictions:
            results[name]["joint_regression"] = score_runs(predictions[name], teachers, cases)
    reasons = []
    if session["training_count"] < 1:
        reasons.append("Añade al menos una lección o un feedback nativo")
    joint_count = results["candidate"].get("joint_regression", {}).get("total", 0)
    if not session["holdouts"] and not joint_count:
        reasons.append("Añade al menos una pregunta reservada con resultado esperado")
    if session.get("pending_exercise_id"):
        reasons.append("Termina el feedback del ejercicio pendiente")
    if not all(x["passed"] for x in results["candidate"]["regressions"]):
        reasons.append("El candidato falla una regresión aritmética original")
    if not all(x["passed"] for x in results["candidate"]["holdouts"]):
        reasons.append("El candidato no supera todas tus preguntas reservadas")
    for field in ("regressions", "holdouts"):
        if sum(x["passed"] for x in results["candidate"][field]) < sum(x["passed"] for x in results["baseline"][field]):
            reasons.append("El candidato retrocede frente al control en " + field)
    if joint:
        if joint_count < 2:
            reasons.append("Faltan dos muestras conjuntas reservadas válidas")
        for metric in ("class_correct", "rule_correct", "supported_faithful", "native_receipt_ok"):
            if results["candidate"]["joint_regression"][metric] != joint_count:
                reasons.append("El candidato falla una comprobación conjunta reservada: " + metric)
            if results["candidate"]["joint_regression"][metric] < results["baseline"]["joint_regression"][metric]:
                reasons.append("Regresión conjunta: " + metric)
    for name in results:
        score = results[name]
        correct_joint = sum(row["class_correct"] and row["rule_correct"] and row["supported_and_faithful"] and row["receipt_ok"]
                            for row in score.get("joint_regression", {}).get("raw", []))
        score["correct"] = sum(row["passed"] for row in score["holdouts"]) + correct_joint
        score["total"] = len(session["holdouts"]) + joint_count
    if before != {"baseline": _identity(baseline), "candidate": _identity(candidate)}:
        raise RuntimeError("La evaluación modificó una versión de entrenamiento")
    return {"passed": not reasons, "activation_allowed": not reasons, "reasons": reasons,
            **results, "training_count": session["training_count"],
            "holdout_count": len(session["holdouts"]) + joint_count,
            "user_holdout_count": len(session["holdouts"]), "native_joint_holdout_count": joint_count,
            "candidate_identity": before["candidate"],
            "labels_not_sent_to_inference": True, "evaluated_in_copies": True,
            "scope": "regresiones acotadas y preguntas personales; no demuestra inteligencia general ni mejora universal",
            "validated_ns": _now()}


def _switch_marker(path, request_id, fingerprint, result, active):
    with closing(sqlite3.connect(str(path))) as db:
        db.execute("CREATE TABLE IF NOT EXISTS bbyq_training_switches(id TEXT PRIMARY KEY,fingerprint TEXT NOT NULL,result TEXT NOT NULL,active TEXT NOT NULL)")
        db.execute("INSERT OR REPLACE INTO bbyq_training_switches VALUES(?,?,?,?)",
                   (request_id, fingerprint, _json(result), _json(active)))
        db.commit()


def _recover_switch(db, personal_db, args, fingerprint):
    # The personal SQLite copy and this marker commit in one SQLite backup
    # transaction. If the app died before the outer journal commit, replay
    # reconstructs the journal from the authoritative durable marker.
    if args["action"] not in ("activate", "restore"):
        return None
    with closing(sqlite3.connect(str(personal_db))) as live:
        exists = live.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='bbyq_training_switches'").fetchone()
        row = live.execute("SELECT fingerprint,result,active FROM bbyq_training_switches WHERE id=?", (args["request_id"],)).fetchone() if exists else None
    if not row:
        return None
    if row[0] != fingerprint:
        raise ValueError("El identificador ya se usó con otro contenido")
    result = json.loads(row[1]); active = json.loads(row[2])
    session = _load(db, args["session_id"])
    session["state"] = "activated" if args["action"] == "activate" else "restored"
    if args["action"] == "activate":
        session["backup_id"] = result["backup_id"]
        session["backup_path"] = result["backup_path"]
        session["activated_identity"] = result["activated_identity"]
    _event(session, args["request_id"], args["action"], args, result)
    _save(db, session)
    db.execute("INSERT OR REPLACE INTO settings VALUES('active',?)", (_json(active),))
    return result


def _reconcile_switches(db, personal_db):
    """Recover a completed switch even if the next action is not its retry."""
    with closing(sqlite3.connect(str(personal_db))) as live:
        exists = live.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='bbyq_training_switches'").fetchone()
        rows = list(live.execute("SELECT id,fingerprint,result FROM bbyq_training_switches ORDER BY rowid")) if exists else []
    missing = [(identifier, fingerprint, json.loads(raw)) for identifier, fingerprint, raw in rows
               if not db.execute("SELECT 1 FROM requests WHERE id=?", (identifier,)).fetchone()]
    if not missing:
        return
    db.execute("BEGIN IMMEDIATE")
    try:
        for identifier, fingerprint, result in missing:
            args = {"action": result["action"], "session_id": result["session_id"], "request_id": identifier,
                    "recovered_from_personal_sqlite": True}
            recovered = _recover_switch(db, personal_db, args, fingerprint)
            if recovered is None:
                raise RuntimeError("Falta el comprobante duradero de activación")
            db.execute("INSERT INTO requests VALUES(?,?,?)", (identifier, fingerprint, _json(recovered)))
        db.execute("COMMIT")
    except BaseException:
        db.execute("ROLLBACK")
        raise


def _export(folder, session, root):
    import u03_mobile as base
    export = folder / session["session_id"] / "exports" / (uuid.uuid4().hex + ".zip")
    export.parent.mkdir(parents=True, exist_ok=True)
    report = {"schema": SCHEMA, "session": session,
              "runtime": "Original BBY Q U02 / XI / C17 Android personal training",
              "orchestration": "BBY Q -> w4U -> QdU",
              "training_parameters_are_original_XI": True,
              "scope": "Facts and rules teach native memory; joint synthetic feedback trains native parameters. No external language model.",
              "source_commit": base._manifest.get("apk_source_commit"),
              "android_version": base._manifest.get("android_version"),
              "source_sha256": base._manifest.get("mobile_sources_sha256", {}),
              "runtime_archive_sha256": base._manifest.get("archive_sha256"),
              "training_guide_sha256": base._manifest.get("training_guide_sha256"),
              "exported_ns": _now()}
    # SQLite backups include any WAL bytes and are independent of app paths.
    with tempfile.TemporaryDirectory(prefix="bbyq-c17-export-") as temp:
        temp = Path(temp)
        entries = {}
        for name, source in (("candidate.sqlite", session["candidate_path"]), ("baseline.sqlite", session["baseline_path"])):
            target = temp / name; _copy(Path(source), target); _seal(target)
            entries[name] = target.read_bytes()
        entries["report.json"] = (_json(report) + "\n").encode()
        manifest = {"schema": SCHEMA, "session_id": session["session_id"],
                    "files": {name: {"sha256": _sha(raw), "bytes": len(raw)} for name, raw in entries.items()}}
        with zipfile.ZipFile(export, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for name, raw in entries.items():
                archive.writestr(name, raw)
            archive.writestr("manifest.json", _json(manifest) + "\n")
    return {"path": str(export), "filename": "BBY-Q-entrenamiento-" + session["session_id"][:8] + ".zip",
            "mime": "application/zip", "sha256": _sha(export.read_bytes()), "bytes": export.stat().st_size}


def run(args, root, personal_db):
    import u03_mobile as base
    with base._lock:
        return _run(args, Path(root), Path(personal_db))


def _run(args, root, personal_db):
    import u03_mobile as base
    if not isinstance(args, dict) or args.get("action") not in _ACTIONS:
        raise ValueError("Acción de entrenamiento desconocida")
    args = dict(args); action = args["action"]
    folder = personal_db.parent.parent / "training-v1"
    db = _connect(folder)
    try:
        _reconcile_switches(db, personal_db)
        if action == "status":
            active = _active(db)
            rows = [json.loads(row[0]) for row in db.execute("SELECT document FROM sessions ORDER BY rowid DESC")]
            result = {"ok": True, "action": action, "sessions": [_summary(s, active) for s in rows],
                      "personal_snapshot": _snapshot(personal_db), "active": active}
            if args.get("session_id"):
                session = _load(db, args["session_id"])
                result.update(session_id=session["session_id"], session=_summary(session, active),
                              candidate_snapshot=_snapshot(Path(session["candidate_path"])),
                              baseline_snapshot=session["baseline_identity"]["snapshot"],
                              events=session["events"], validation=session["validation"])
                pending = session.get("pending_exercise_id")
                result["pending_exercise"] = ({k: session["exercises"][pending][k]
                                                for k in ("exercise_id", "prediction", "teacher")}
                                               if pending else None)
            return result
        request_id = _text(args.get("request_id"), "request_id", 200)
        args["request_id"] = request_id
        fingerprint = _fingerprint(args)
        db.execute("BEGIN IMMEDIATE")
        prior = db.execute("SELECT fingerprint,result FROM requests WHERE id=?", (request_id,)).fetchone()
        if prior:
            if prior[0] != fingerprint:
                raise ValueError("El identificador ya se usó con otro contenido")
            db.execute("COMMIT")
            return json.loads(prior[1])
        recovered = _recover_switch(db, personal_db, args, fingerprint)
        if recovered is not None:
            db.execute("INSERT INTO requests VALUES(?,?,?)", (request_id, fingerprint, _json(recovered)))
            db.execute("COMMIT")
            return recovered
        if action == "create":
            identifier = uuid.uuid4().hex
            directory = folder / identifier; directory.mkdir()
            baseline = directory / "baseline.sqlite"; candidate = directory / "versions" / "initial.sqlite"
            origin = _identity(personal_db)
            _copy(personal_db, baseline); _copy(baseline, candidate)
            session = {"session_id": identifier, "title": _text(args.get("title", "Mi entrenamiento"), "Título", 80),
                       "state": "training", "created_ns": _now(), "baseline_path": str(baseline),
                       "baseline_identity": origin, "candidate_path": str(candidate),
                       "candidate_snapshot": _snapshot(candidate), "training_count": 0,
                       "holdouts": [], "exercises": {}, "events": [], "validation": None,
                       "pending_exercise_id": None, "parent_active": _active(db)}
            result = {"ok": True, "action": action, "session_id": identifier,
                      "session": _summary(session, _active(db))}
        else:
            session = _load(db, args.get("session_id"))
            identifier = session["session_id"]
            result = {"ok": True, "action": action, "session_id": identifier}
            source = Path(session["candidate_path"])
            if action in ("fact", "rule", "joint_prepare", "joint_feedback"):
                _check_editable(session)
                if action != "joint_feedback" and session.get("pending_exercise_id"):
                    raise ValueError("Completa el feedback del ejercicio pendiente antes de otra lección")
                target = _stage(folder, session, request_id)
                if action in ("fact", "rule"):
                    if action == "fact":
                        subject = _symbol(args.get("subject"), "Sujeto"); prop = _symbol(args.get("property"), "Propiedad")
                        prompt = "recuerda que " + subject + " es " + prop; kind = "put"
                    else:
                        antecedent = _symbol(args.get("antecedent"), "Premisa"); consequence = _symbol(args.get("consequence"), "Consecuencia")
                        prompt = "si alguien es " + antecedent + " entonces es " + consequence; kind = "rule"
                    receipt = _native(target, "c17-" + request_id, prompt)
                    _require_native(receipt, kind)
                    session["training_count"] += 1
                    result.update(receipt=receipt, reply=base._reply(receipt), text=prompt,
                                  learning_kind="native_memory", model_weights_claimed_changed=False)
                elif action == "joint_prepare":
                    seed = args.get("seed", 2023144612); bit = args.get("rule", 1); position = args.get("position", 3)
                    if type(seed) is not int or not 0 <= seed <= 2147483647 or type(bit) is not int or bit not in (0, 1) or type(position) is not int or not 0 <= position <= 6:
                        raise ValueError("Muestra 0..2147483647, regla 0/1 y posición 0..6 requeridas")
                    exercise_id = uuid.uuid4().hex
                    prompt = f"guarda la regla Faro Claro con valor {bit} observa Umbral con muestra {seed} y resuelve desde {position}"
                    receipt = _native(target, "c17-" + request_id, prompt)
                    prediction = _require_native(receipt, "mission")
                    # The mission is committed before this separate teacher is
                    # computed. Neither label is present in the inference call.
                    from integration.joint_u03_c11.native import native_sample_teacher
                    from integration.unified.session import Session
                    with Session(Path(session["baseline_path"])) as model:
                        original = model.initial["v3"]
                    teacher = {"class": native_sample_teacher(original, seed), "rule": bit, "action": None}
                    session["exercises"][exercise_id] = {"exercise_id": exercise_id, "seed": seed,
                        "rule": bit, "position": position, "task_id": prediction["task_id"],
                        "prediction": prediction, "teacher": teacher, "feedback_request_id": None,
                        "before_path": str(source), "before_snapshot": session["candidate_snapshot"],
                        "before_holdouts": session["holdouts"], "before_validation": session["validation"],
                        "before_state": session["state"]}
                    session["pending_exercise_id"] = exercise_id
                    result.update(exercise_id=exercise_id, prediction=prediction, teacher=teacher,
                                  receipt=receipt, labels_revealed_after_inference=True,
                                  scope="ejercicio sintético con maestro XI independiente, no conocimiento del mundo")
                else:
                    exercise_id = args.get("exercise_id")
                    if exercise_id != session.get("pending_exercise_id") or exercise_id not in session["exercises"]:
                        raise ValueError("El ejercicio no está pendiente o ya recibió feedback")
                    exercise = session["exercises"][exercise_id]
                    from integration.unified.session import Session
                    with Session(target) as model:
                        metadata = json.loads(model.db.execute("SELECT metadata FROM unified_state WHERE id=1").fetchone()[0])
                        if metadata.get("last_task") != exercise["task_id"]:
                            raise RuntimeError("La tarea pendiente ya no coincide con su checkpoint")
                    before_weights = _weights(target)
                    receipt = _native(target, "c17-" + request_id, "aprende de la última tarea",
                                      {"labels": {"class": exercise["teacher"]["class"], "rule": exercise["rule"]}})
                    feedback = _require_native(receipt, "feedback")
                    if feedback.get("supervision") != "independent-labels":
                        raise RuntimeError("El feedback no utilizó supervisión nativa verificada")
                    after_weights = _weights(target)
                    changes = {key: before_weights[key] != after_weights[key] for key in before_weights}
                    if not any(changes.values()):
                        raise RuntimeError("No cambió ninguna región de parámetros nativos")
                    exercise["feedback_request_id"] = request_id
                    session["pending_exercise_id"] = None
                    session["training_count"] += 1
                    result.update(receipt=receipt, parameter_changes=changes, changed_regions=sum(changes.values()),
                                  before_weight_sha256=before_weights, candidate_weight_sha256=after_weights,
                                  native_XI_training=True, preserved_original_sources=True)
                _edited(session, target, _snapshot(target)); _seal(target)
                result["candidate_snapshot"] = session["candidate_snapshot"]
            elif action == "joint_discard":
                _check_editable(session)
                pending = session.get("pending_exercise_id")
                if not pending:
                    raise ValueError("No hay un ejercicio pendiente que descartar")
                if args.get("exercise_id") not in (None, pending):
                    raise ValueError("El ejercicio pendiente cambió; vuelve a cargar esta sesión")
                exercise = session["exercises"][pending]
                if _snapshot(Path(exercise["before_path"])) != exercise["before_snapshot"]:
                    raise RuntimeError("El checkpoint previo al ejercicio cambió")
                session.update(candidate_path=exercise["before_path"], candidate_snapshot=exercise["before_snapshot"],
                               holdouts=exercise["before_holdouts"], validation=exercise["before_validation"],
                               state=exercise["before_state"], pending_exercise_id=None)
                exercise["discarded_request_id"] = request_id
                result.update(discarded=True, exercise_id=pending, candidate_snapshot=session["candidate_snapshot"])
            elif action == "query":
                text = _text(args.get("text"), "Pregunta", 256)
                split = args.get("split", "practice")
                if split not in ("practice", "holdout"):
                    raise ValueError("La pregunta debe ser práctica o reservada")
                if split == "holdout":
                    expected = args.get("expected_status")
                    if type(expected) is not int or expected not in (0, 1):
                        raise ValueError("Indica 1 si debe demostrarlo o 0 si carece de evidencia")
                    if not re.match(r"^(?:es\s+.+|dime si\s+.+\s+es\s+.+)", text.lower()):
                        raise ValueError("Usa una pregunta reservada como: dime si Nara es útil")
                    if _question_key(text) in _exposures(session):
                        raise ValueError("Ya viste el resultado de esa pregunta en esta sesión. Reserva otra pregunta nueva; no se puede cambiar su etiqueta después de verla")
                receipt = _evaluate(source, text, "c17-query-" + request_id)
                result.update(receipt=receipt, reply=base._reply(receipt), split=split,
                              candidate_modified=False, labels_not_sent_to_inference=True)
                _exposures(session).setdefault(_question_key(text), {"request_id": request_id, "split": split})
                if split == "holdout":
                    actual = _query_status(receipt)
                    if actual not in (0, 1):
                        raise ValueError("La pregunta no produjo una consulta nativa admitida: " + _json(receipt))
                    session["holdouts"].append({"text": text, "expected_status": expected,
                                                 "first_receipt": receipt, "request_id": request_id})
                    session["validation"] = None
                    result.update(expected_status=expected, actual_status=actual, correct=actual == expected)
            elif action == "validate":
                session["validation"] = _validate(session)
                if session["state"] not in ("activated", "restored"):
                    session["state"] = "validated" if session["validation"]["passed"] else "needs_training"
                result["validation"] = session["validation"]
            elif action == "activate":
                _check_editable(session)
                validation = session.get("validation")
                if not validation or not validation["activation_allowed"]:
                    raise ValueError("Primero supera la validación de este candidato")
                if _identity(source) != validation["candidate_identity"]:
                    raise RuntimeError("El candidato cambió después de validarse")
                if _identity(personal_db) != session["baseline_identity"]:
                    raise ValueError("La conversación cambió desde que creaste esta sesión. Crea una sesión nueva desde el estado actual y vuelve a añadir tus lecciones; esta sesión sigue guardada")
                backup_id = uuid.uuid4().hex
                backup = folder / identifier / "backups" / (backup_id + ".sqlite")
                _copy(personal_db, backup); _seal(backup)
                activated_identity = _identity(source)
                result.update(active=True, backup_id=backup_id, backup_path=str(backup), activated_identity=activated_identity)
                active = {"session_id": identifier, "backup_id": backup_id, "activated_identity": activated_identity}
                staged = folder / identifier / "activation" / (_sha(request_id.encode()) + ".sqlite")
                _copy(source, staged)
                _switch_marker(staged, request_id, fingerprint, result, active)
                _copy(staged, personal_db)
                session.update(state="activated", backup_id=backup_id, backup_path=str(backup), activated_identity=activated_identity)
                db.execute("INSERT OR REPLACE INTO settings VALUES('active',?)", (_json(active),))
            elif action == "restore":
                if args.get("backup_id") != session.get("backup_id") or session.get("state") != "activated":
                    raise ValueError("No hay una copia activada que coincida con ese identificador")
                active = _active(db)
                if not active or active["session_id"] != identifier:
                    raise ValueError("Otra sesión es ahora la activa; restaura primero esa versión")
                changed = _identity(personal_db) != session["activated_identity"]
                if changed and args.get("confirm_discard_new_activity") is not True:
                    raise ValueError("Tu chat tuvo actividad posterior. Confirma explícitamente volver a la copia anterior")
                rescue = folder / identifier / "backups" / ("before-restore-" + _sha(request_id.encode()) + ".sqlite")
                _copy(personal_db, rescue); _seal(rescue)
                staged = folder / identifier / "activation" / ("restore-" + _sha(request_id.encode()) + ".sqlite")
                _copy(Path(session["backup_path"]), staged)
                parent_active = session.get("parent_active")
                result.update(restored=True, backup_id=session["backup_id"], post_activation_activity_preserved=str(rescue))
                _switch_marker(staged, request_id, fingerprint, result, parent_active)
                _copy(staged, personal_db)
                session["state"] = "restored"
                db.execute("INSERT OR REPLACE INTO settings VALUES('active',?)", (_json(parent_active),))
            elif action == "export":
                result.update(_export(folder, session, root))
        _event(session, request_id, action, args, result)
        _save(db, session)
        db.execute("INSERT INTO requests VALUES(?,?,?)", (request_id, fingerprint, _json(result)))
        db.execute("COMMIT")
        return result
    except BaseException:
        if db.in_transaction:
            db.execute("ROLLBACK")
        raise
    finally:
        db.close()
