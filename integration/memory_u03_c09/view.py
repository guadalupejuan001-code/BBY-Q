"""C09: one authenticated read-only view of the ORIGINAL U02/C1 memory.

This is NOT a second memory store. It reads the existing original SQLite
transactionally, validates hashes and identity, and indexes user-supervised
QMemory associations, observations, VQC projections and task provenance.
Never promotes native probability to truth, external hashes to digital source
signatures, or old snapshots to current state. All historical C1/U02 and
RVPC2 checkpoint bytes remain untouched.
"""
from __future__ import annotations

from hashlib import sha256
import json
import sqlite3
from typing import Any

from integration.unified.common import encoded, digest, key


def external_claim(subject: str, predicate: str, value: int, source: str) -> dict:
    """Construct a content-integrity-checked assertion, not verified truth."""
    if not all(isinstance(x,str) and 0<len(x)<=256
               for x in (subject,predicate,source)):
        raise ValueError("C09 claim requires bounded subject/predicate/source")
    if type(value) is not int or value not in (0,1):
        raise ValueError("C09 permits only explicit binary overlay values")
    value={"subject":subject,"predicate":predicate,
           "value":value,"source":source}
    return {**value,"content_sha256":digest(encoded(value))}


def verified_overlay(value: dict) -> dict:
    """A hash proves payload consistency, NOT issuer authenticity."""
    if not isinstance(value,dict) or set(value)!={
            "subject","predicate","value","source","content_sha256"}:
        raise ValueError("C09 malformed external assertion")
    basis={k:value[k] for k in ("subject","predicate","value","source")}
    expected=external_claim(**basis)
    if expected!=value:
        raise ValueError("C09 external content hash or typed value corrupted")
    return {
        "kind":"external_candidate","subject":key(value["subject"]),
        "predicate":key(value["predicate"]),"value":value["value"],
        "source":value["source"],"content_sha256":value["content_sha256"],
        "provenance":"unverified-external-content-only",
        "authority":"no","can_override_native_memory":False,
    }


class UnifiedMemoryView:
    """Opt-in wrapper around the existing U02 Session.db and identity.

    SQLite/WAL read transaction ensures a coherent revision and bank SHA
    across all read operations. No tables are created and no SQL writes
    are performed. The caller keeps ownership of the U02 connection.
    """

    def __init__(self, session):
        self.session=session
        self.db=session.db

    def _read(self, subject=None, *, fail_after=None):
        if self.db.in_transaction:
            raise RuntimeError("C09 cannot nest a read in an active writer transaction")
        self.db.execute("BEGIN")
        try:
            result=self._collect(subject,fail_after=fail_after)
            self.db.execute("COMMIT")
            return result
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def snapshot(self, subject=None, *, fail_after=None):
        if subject is not None and (not isinstance(subject,str) or not subject.strip()):
            raise ValueError("C09 subject must be nonempty text")
        return self._read(subject,fail_after=fail_after)

    def _collect(self, subject, *, fail_after=None):
        select=self.db.execute
        state=select(
            "SELECT metadata,sha,identity,revision FROM unified_state WHERE id=1"
        ).fetchone()
        if state is None or digest(state[0])!=state[1]:
            raise ValueError("C09 corrupt unified metadata")
        if json.loads(state[2])!=self.session.identity:
            raise ValueError("C09 original model/identity mismatch")
        metadata=json.loads(state[0])
        rev=int(state[3])
        legacy=select(
            "SELECT snapshot,sha,metadata,metadata_sha,identity,revision "
            "FROM state WHERE id=1"
        ).fetchone()
        if legacy is None or digest(legacy[0])!=legacy[1] or digest(legacy[2])!=legacy[3]:
            raise ValueError("C09 corrupt original C1 state or metadata")
        if json.loads(legacy[4])!=self.session.legacy.identity:
            raise ValueError("C09 legacy C1 model identity mismatch")
        oldmeta=json.loads(legacy[2])
        if fail_after=="legacy":
            raise RuntimeError("Injected C09 read fault")
        banks={}
        for name,raw,checksum in select(
                "SELECT name,snapshot,sha FROM unified_banks ORDER BY name"):
            if digest(raw)!=checksum:
                raise ValueError("C09 corrupt native bank: "+name)
            banks[name]=checksum
        if "memory" not in banks or "language" not in banks or "v3" not in banks:
            raise ValueError("C09 requires original native memory/language/VQC banks")
        # The C1-compatible language bank is an authenticated snapshot.
        # When an older C1 client commits independently, the U02 sync
        # marker is stale; report it, NEVER silently claim convergence.
        sync=(metadata.get("language_sync")==[legacy[1],legacy[3]])
        if fail_after=="banks":
            raise RuntimeError("Injected C09 audit fault")

        facts=[]
        associated=metadata.get("associations",{})
        if not isinstance(associated,dict):
            raise ValueError("C09 malformed associations")
        supervision=dict(select(
            "SELECT name,value FROM unified_supervision ORDER BY name"))
        for name,entry in sorted(associated.items()):
            if not isinstance(entry,dict) or type(entry.get("slot")) is not int:
                raise ValueError("C09 invalid quantum association slot")
            bit=supervision.get(name)
            if bit is not None and (type(bit) is not int or bit not in (0,1)):
                raise ValueError("C09 malformed supervised bit")
            facts.append({
                "kind":"qmemory_association","subject":name,
                "predicate":"valor","value":bit,
                "display":entry.get("display",name),"slot":entry["slot"],
                "provenance":"explicit-user-supervision" if bit is not None else "unmeasured-association",
                "authority":"recorded-user-input-not-world-truth",
                "bank_sha256":banks["memory"],"revision":rev,
                "status":"recorded" if bit is not None else "unverified",
            })
        # Orphan labels must be detected, not discarded or reintroduced.
        if set(supervision)-set(associated):
            raise ValueError("C09 orphaned supervision outside QMemory metadata")

        observations=metadata.get("observations",{})
        projections=metadata.get("projections",{})
        names=metadata.get("observation_names",{})
        if not all(isinstance(x,dict) for x in (observations,projections,names)):
            raise ValueError("C09 malformed VQC observation metadata")
        seen_projection_keys=set()
        stale=[]
        for name,spec in sorted(observations.items()):
            if not isinstance(spec,dict) or spec.get("kind") not in ("synthetic","external"):
                raise ValueError("C09 malformed observed sensor input")
            shown=names.get(name,name)
            projection_key=key("observación "+shown)
            record=projections.get(projection_key)
            specsha=digest(encoded(spec))
            facts.append({
                "kind":"vqc_observation","subject":projection_key,
                "predicate":"input_sha256","value":specsha,
                "provenance":"sensor-input-not-truth",
                "kind_of_input":spec["kind"],"bank_sha256":banks["v3"],
                "revision":rev,"status":"recorded",
            })
            if record is None:
                stale.append(projection_key)
                continue
            if not isinstance(record,dict) or record.get("class") not in (0,1):
                raise ValueError("C09 malformed VQC projection")
            current=(record.get("input_sha256")==specsha
                     and record.get("perception_revision")==metadata.get("perception_revision",0))
            seen_projection_keys.add(projection_key)
            status="current" if current else "stale"
            if not current:
                stale.append(projection_key)
            facts.append({
                "kind":"vqc_projection","subject":projection_key,
                "predicate":"clase","value":record["class"],
                "status":status,"provenance":"learned-derivation-not-world-truth",
                "input_sha256":record.get("input_sha256"),
                "perception_revision":record.get("perception_revision"),
                "bank_sha256":banks["v3"],"revision":rev,
            })
        if set(projections)-seen_projection_keys:
            # A projection without the current observation must not appear
            # to be a live established memory.
            for p in sorted(set(projections)-seen_projection_keys):
                if p not in stale:
                    stale.append(p)

        tasks=[]
        for taskid,frame,checksum,feedback in select(
                "SELECT id,frame,sha,feedback_id FROM unified_tasks ORDER BY id"):
            if digest(frame)!=checksum:
                raise ValueError("C09 corrupt persisted task frame: "+taskid)
            details=json.loads(frame)
            tasks.append({
                "task_id":taskid,"kind":details.get("kind"),
                "feedback_id":feedback,"frame_sha256":checksum,
                "origin":"U02 committed native task frame",
                "status":"feedback-recorded" if feedback is not None else "awaiting-feedback",
            })
        count=0
        for identifier,fingerprint,result in select(
                "SELECT id,fingerprint,result FROM unified_requests ORDER BY rowid"):
            mirrored=select(
                "SELECT result FROM requests WHERE id=?",(identifier,)
            ).fetchone()
            if mirrored is None or mirrored[0]!=result:
                raise ValueError("C09 unmapped/modified legacy receipt: "+identifier)
            if not isinstance(json.loads(result),dict):
                raise ValueError("C09 malformed native receipt")
            count+=1
        for task in tasks:
            if task["feedback_id"] is not None:
                target=select("SELECT id FROM unified_requests WHERE id=?",
                              (task["feedback_id"],)).fetchone()
                if target is None:
                    raise ValueError("C09 feedback references nonexistent committed receipt")
        archives=0
        for archiveid,raw,snapshot_sha,meta,meta_sha in select(
                "SELECT id,snapshot,sha,metadata,metadata_sha FROM unified_archives"):
            if digest(raw)!=snapshot_sha or digest(meta)!=meta_sha:
                raise ValueError("C09 corrupt signed archived bank: "+archiveid)
            archives+=1

        if subject is not None:
            sought=key(subject)
            facts=[record for record in facts
                   if record["subject"]==sought]
        facts.sort(key=lambda row:(row["subject"],row["kind"],row["predicate"]))
        result={
            "schema":"BBYQ-U03-C09-read-only-memory-v1",
            "authority":"existing-U02-SQLite-and-XI-checkpoint",
            "revision":rev,
            "C1_revision":int(legacy[5]),
            "C1_synchronized_with_U02":sync,
            "snapshot_sha256":state[1],"bank_sha256":banks,
            "facts":facts,
            "tasks":tasks if subject is None else [],
            "receipts_verified":count,
            "archives_verified":archives,
            "stale_projections":sorted(set(stale)),
            "read_only":True,"new_memory_authorities":0,
            "semantic_models_C06_C07_C08_trained_state_modified":False,
            "does_not_claim_world_truth":True,
        }
        result["view_sha256"]=digest(encoded(result))
        return result

    def reconcile(self,subject, *, predicate="valor", overlay=()):
        """Non-destructive comparison; conflict is NOT a choice of truth.

        Hash-checked external overlay statements are STILL untrusted. A
        contrary statement must yield a flagged conflict, never silently
        overwrite QMemory or any native model state.
        """
        if not isinstance(predicate,str) or not predicate.strip():
            raise ValueError("C09 predicate must be nonempty")
        original=self.snapshot(subject)
        accepted=[f for f in original["facts"]
                  if f["predicate"]==key(predicate)
                  and f["status"] in ("current","recorded")
                  and type(f["value"]) is int and f["value"] in (0,1)]
        candidates=[verified_overlay(item) for item in overlay]
        matching=[f for f in candidates if f["subject"]==key(subject)
                  and f["predicate"]==key(predicate)]
        values={f["value"] for f in accepted+matching}
        if len(values)>1:
            status="conflict_unresolved"
        elif accepted:
            status="recorded_native_memory_not_world_truth"
        elif matching:
            status="unverified_external_candidate"
        else:
            status="insufficient_evidence"
        return {
            "subject":key(subject),"predicate":key(predicate),
            "status":status,"native_records":accepted,
            "external_unverified":matching,
            "disagreements":len(values)>1,
            "original_view_sha256":original["view_sha256"],
            "new_writes":0,"native_checkpoints_changed":False,
            "required_follow_up":(
                "Verify conflicting sources before accepting a correction"
                if len(values)>1 else
                "Request corroborating evidence" if not accepted else None),
        }
