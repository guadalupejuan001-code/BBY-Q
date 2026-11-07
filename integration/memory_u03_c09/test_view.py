"""C09 fail-closed memory audit, provenance, WAL and conflict contracts."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing

from integration.unified.common import encoded,digest,key
from .view import UnifiedMemoryView,external_claim


class FakeSession:
    def __init__(self,db):
        self.db=db
        self.identity={"native":"U02 original"}
        self.legacy=type("Legacy",(),{"identity":{"native":"C1 original"}})()


def fixture(db):
    db.executescript("""
    CREATE TABLE unified_state(id INTEGER PRIMARY KEY,metadata BLOB,sha TEXT,identity BLOB,revision INTEGER);
    CREATE TABLE state(id INTEGER PRIMARY KEY,snapshot BLOB,sha TEXT,metadata BLOB,metadata_sha TEXT,identity BLOB,revision INTEGER);
    CREATE TABLE unified_banks(name TEXT PRIMARY KEY,snapshot BLOB,sha TEXT);
    CREATE TABLE unified_supervision(name TEXT PRIMARY KEY,value INTEGER);
    CREATE TABLE unified_tasks(id TEXT PRIMARY KEY,frame BLOB,sha TEXT,feedback_id TEXT);
    CREATE TABLE unified_requests(id TEXT PRIMARY KEY,fingerprint TEXT,result BLOB);
    CREATE TABLE requests(id TEXT PRIMARY KEY,fingerprint TEXT,result BLOB);
    CREATE TABLE unified_archives(id TEXT PRIMARY KEY,snapshot BLOB,sha TEXT,metadata BLOB,metadata_sha TEXT);
    """)
    language_meta=encoded({"entities":{"orion":{"id":2000000,"display":"Orión"}},"previous":""})
    lang=b"language-native-snapshot"
    db.execute("INSERT INTO state VALUES(1,?,?,?,?,?,3)",(
        lang,digest(lang),language_meta,digest(language_meta),
        encoded({"native":"C1 original"})))
    input_spec={"kind":"synthetic","seed":88113,"noise":.1}
    proj={"class":1,"probability":.7,"input_sha256":digest(encoded(input_spec)),
          "perception_revision":2,"readout_magic":1234}
    meta={
        "associations":{"faro azul":{"slot":0,"display":"Faro Azul"}},
        "observations":{"nara":input_spec},"observation_names":{"nara":"Nara"},
        "projections":{key("observación Nara"):proj},
        "perception_revision":2,
        "language_sync":[digest(lang),digest(language_meta)],
    }
    raw=encoded(meta)
    db.execute("INSERT INTO unified_state VALUES(1,?,?,?,5)",(
        raw,digest(raw),encoded({"native":"U02 original"})))
    for bank in ("language","memory","v3","router","entity","voice","text"):
        blob=("state-"+bank).encode()
        db.execute("INSERT INTO unified_banks VALUES(?,?,?)",(bank,blob,digest(blob)))
    db.execute("INSERT INTO unified_supervision VALUES('faro azul',1)")
    task=encoded({"kind":"mission","status":1,"id":"mission:2"})
    db.execute("INSERT INTO unified_tasks VALUES('mission:2',?,?,NULL)",(
        task,digest(task)))
    receipt=encoded({"request_id":"mission","results":[{"kind":"mission"}]})
    db.execute("INSERT INTO unified_requests VALUES('mission','f',?)",(receipt,))
    db.execute("INSERT INTO requests VALUES('mission','old-f',?)",(receipt,))
    archive=b"historical-binary"
    metadata=encoded({"revision":4})
    db.execute("INSERT INTO unified_archives VALUES(?,?,?,?,?)",(
        "checkpoint-1",archive,digest(archive),metadata,digest(metadata)))
    return FakeSession(db)


class UnifiedIndexTests(unittest.TestCase):
    def connection(self):
        db=sqlite3.connect(":memory:",isolation_level=None)
        return db,fixture(db)

    def test_verified_unified_view_preserves_typed_sources(self):
        db,session=self.connection()
        with closing(db):
            before=list(db.execute("SELECT name FROM sqlite_master WHERE type='table'"))
            view=UnifiedMemoryView(session)
            report=view.snapshot()
            self.assertEqual(report["revision"],5)
            self.assertEqual(report["C1_revision"],3)
            self.assertTrue(report["C1_synchronized_with_U02"])
            self.assertTrue(report["read_only"])
            self.assertEqual(report["new_memory_authorities"],0)
            self.assertEqual(len(report["bank_sha256"]),7)
            self.assertEqual(report["receipts_verified"],1)
            self.assertEqual(report["archives_verified"],1)
            kinds={e["kind"] for e in report["facts"]}
            self.assertEqual(kinds,{
                "c1_entity_dictionary","qmemory_association",
                "vqc_observation","vqc_projection",
            })
            bit=next(e for e in report["facts"] if e["kind"]=="qmemory_association")
            self.assertEqual(bit["value"],1)
            self.assertEqual(bit["provenance"],"explicit-user-supervision")
            self.assertNotEqual(bit["authority"],"world-truth")
            symbol=next(e for e in report["facts"] if e["kind"]=="c1_entity_dictionary")
            self.assertEqual(symbol["value"],2000000)
            self.assertIn("not-factual",symbol["authority"])
            proj=next(e for e in report["facts"] if e["kind"]=="vqc_projection")
            self.assertEqual(proj["status"],"current")
            self.assertEqual(report["stale_projections"],[])
            self.assertEqual(report["view_sha256"],view.snapshot()["view_sha256"])
            self.assertEqual(before,list(db.execute("SELECT name FROM sqlite_master WHERE type='table'")))
            self.assertFalse(db.in_transaction)

    def test_contradiction_reported_without_autocorrecting_memory(self):
        db,session=self.connection()
        with closing(db):
            view=UnifiedMemoryView(session)
            current=view.snapshot("Faro Azul")
            conflicting=external_claim("Faro Azul","valor",0,"external:observer")
            compare=view.reconcile("Faro Azul",overlay=[conflicting])
            self.assertEqual(compare["status"],"conflict_unresolved")
            self.assertTrue(compare["disagreements"])
            self.assertEqual(compare["new_writes"],0)
            self.assertEqual(view.snapshot("Faro Azul"),current)
            agreed=external_claim("Faro Azul","valor",1,"external:observer")
            ok=view.reconcile("Faro Azul",overlay=[agreed])
            self.assertEqual(ok["status"],"recorded_native_memory_not_world_truth")
            self.assertEqual(view.reconcile("unknown")["status"],"insufficient_evidence")
            forged=dict(conflicting,content_sha256="00"*32)
            with self.assertRaisesRegex(ValueError,"hash"):
                view.reconcile("Faro Azul",overlay=[forged])
            self.assertEqual(view.snapshot("Faro Azul"),current)

    def test_detect_bank_checksum_corruption_without_mutating_banks(self):
        db,session=self.connection()
        with closing(db):
            before=UnifiedMemoryView(session).snapshot()
            db.execute("UPDATE unified_banks SET snapshot=? WHERE name='memory'",(b"tampered",))
            with self.assertRaisesRegex(ValueError,"corrupt native bank: memory"):
                UnifiedMemoryView(session).snapshot()
            self.assertFalse(db.in_transaction)
            db.execute("UPDATE unified_banks SET snapshot=?,sha=? WHERE name='memory'",(
                b"recovered",digest(b"recovered")))
            changed=UnifiedMemoryView(session).snapshot()
            self.assertNotEqual(before["bank_sha256"]["memory"],changed["bank_sha256"]["memory"])

    def test_old_projection_marked_stale_after_perception_revision(self):
        db,session=self.connection()
        with closing(db):
            raw,sha=db.execute("SELECT metadata,sha FROM unified_state").fetchone()
            meta=json.loads(raw)
            meta["perception_revision"]=3
            new=encoded(meta)
            db.execute("UPDATE unified_state SET metadata=?,sha=?",(new,digest(new)))
            report=UnifiedMemoryView(session).snapshot("observación Nara")
            result=next(e for e in report["facts"] if e["kind"]=="vqc_projection")
            self.assertEqual(result["status"],"stale")
            self.assertIn(key("observación Nara"),report["stale_projections"])

    def test_orphan_supervision_and_injected_failure(self):
        db,session=self.connection()
        with closing(db):
            view=UnifiedMemoryView(session)
            with self.assertRaisesRegex(RuntimeError,"Injected"):
                view.snapshot(fail_after="banks")
            self.assertFalse(db.in_transaction)
            db.execute("INSERT INTO unified_supervision VALUES('unlinked',0)")
            with self.assertRaisesRegex(ValueError,"orphaned"):
                view.snapshot()
            self.assertFalse(db.in_transaction)

    def test_fail_closed_on_mirrored_receipt_and_corrupt_task(self):
        db,session=self.connection()
        with closing(db):
            db.execute("UPDATE requests SET result=?",(b'{"fake":true}',))
            with self.assertRaisesRegex(ValueError,"modified legacy receipt"):
                UnifiedMemoryView(session).snapshot()
            db.execute("UPDATE requests SET result=(SELECT result FROM unified_requests WHERE id='mission')")
            db.execute("UPDATE unified_tasks SET frame=?",(b'{"fake":true}',))
            with self.assertRaisesRegex(ValueError,"task frame"):
                UnifiedMemoryView(session).snapshot()

    def test_legacy_external_writer_is_reported_not_silently_merged(self):
        db,session=self.connection()
        with closing(db):
            newmeta=encoded({"entities":{},"previous":"outside C1"})
            db.execute("UPDATE state SET metadata=?,metadata_sha=?,revision=4",(
                newmeta,digest(newmeta)))
            report=UnifiedMemoryView(session).snapshot()
            self.assertFalse(report["C1_synchronized_with_U02"])
            self.assertEqual(report["C1_revision"],4)

    def test_coherent_wal_snapshot_during_concurrent_legacy_writer(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"memory.sqlite"
            with closing(sqlite3.connect(path,isolation_level=None)) as db:
                db.execute("PRAGMA journal_mode=WAL")
                session=fixture(db)
                view=UnifiedMemoryView(session)
                def concurrent_commit():
                    with closing(sqlite3.connect(path,isolation_level=None)) as writer:
                        writer.execute("PRAGMA journal_mode=WAL")
                        writer.execute("BEGIN IMMEDIATE")
                        writer.execute("UPDATE unified_supervision SET value=0 WHERE name='faro azul'")
                        raw=writer.execute("SELECT metadata FROM unified_state").fetchone()[0]
                        writer.execute("UPDATE unified_state SET revision=revision+1 WHERE id=1")
                        writer.execute("COMMIT")
                earlier=view.snapshot("Faro Azul",after_first_read=concurrent_commit)
                self.assertEqual(earlier["revision"],5)
                self.assertEqual(earlier["facts"][0]["value"],1)
                later=view.snapshot("Faro Azul")
                self.assertEqual(later["revision"],6)
                self.assertEqual(later["facts"][0]["value"],0)
                self.assertFalse(db.in_transaction)


if __name__=="__main__":
    unittest.main()
