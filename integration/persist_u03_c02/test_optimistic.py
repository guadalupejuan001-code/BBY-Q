"""C02 deterministic SQL delta tests that do not require a native runtime."""
from __future__ import annotations

from contextlib import closing
import sqlite3
import unittest

from .optimistic import Action, StaleSnapshot, differences, publish, table_views


class PersistenceContractTests(unittest.TestCase):
    def connection(self):
        db = sqlite3.connect(":memory:", isolation_level=None)
        db.execute("CREATE TABLE state (id INTEGER PRIMARY KEY, data BLOB NOT NULL, revision INT NOT NULL)")
        db.execute("CREATE TABLE requests (id TEXT PRIMARY KEY, content TEXT NOT NULL)")
        db.execute("INSERT INTO state VALUES(1,?,0)", (b"original",))
        db.execute("INSERT INTO requests VALUES('first','value')")
        return db

    def test_apply_only_modified_rows_and_preserve_history_order(self):
        with closing(self.connection()) as db, closing(self.connection()) as staged:
            baseline = table_views(db)
            staged.execute("UPDATE state SET data=?,revision=1 WHERE id=1", (b"changed",))
            staged.execute("INSERT INTO requests VALUES('z-last','two')")
            staged.execute("INSERT INTO requests VALUES('a-last','three')")
            target = table_views(staged)
            actions = differences(baseline, target)
            self.assertEqual(len(actions), 3)
            db.execute("BEGIN IMMEDIATE")
            publish(db, baseline, actions)
            db.execute("COMMIT")
            self.assertEqual(table_views(db), target)
            self.assertEqual([row[0] for row in db.execute("SELECT * FROM requests ORDER BY rowid")],
                             ["first", "z-last", "a-last"])
            self.assertEqual(db.execute("SELECT data FROM state").fetchone()[0], b"changed")

    def test_deletion_has_primary_key_guard(self):
        with closing(self.connection()) as live, closing(self.connection()) as staged:
            baseline = table_views(live)
            staged.execute("DELETE FROM requests WHERE id='first'")
            actions = differences(baseline, table_views(staged))
            live.execute("BEGIN IMMEDIATE")
            publish(live, baseline, actions)
            live.execute("COMMIT")
            self.assertEqual(live.execute("SELECT COUNT(*) FROM requests").fetchone()[0], 0)

    def test_rollback_after_partial_delta(self):
        with closing(self.connection()) as live:
            before = table_views(live)
            live.execute("BEGIN IMMEDIATE")
            try:
                publish(live, before, [
                    Action("state", "update", (1,), (1, b"unpublished", 2)),
                    Action("requests", "insert", ("first",), ("first", "collision")),
                ])
            except sqlite3.IntegrityError:
                live.execute("ROLLBACK")
            else:
                self.fail("Expected duplicate-key failure")
            self.assertEqual(table_views(live), before)

    def test_reject_schema_mutation(self):
        with closing(self.connection()) as live, closing(self.connection()) as staged:
            before = table_views(live)
            staged.execute("ALTER TABLE requests ADD COLUMN extra INTEGER")
            with self.assertRaisesRegex(ValueError, "schema changed"):
                differences(before, table_views(staged))

    def test_reject_null_primary_key(self):
        with closing(sqlite3.connect(":memory:")) as db:
            db.execute("CREATE TABLE bad(id TEXT PRIMARY KEY, value TEXT)")
            db.execute("INSERT INTO bad VALUES(NULL,'ambiguous')")
            with self.assertRaisesRegex(ValueError, "Ambiguous"):
                table_views(db)

    def test_reject_no_primary_key(self):
        with closing(sqlite3.connect(":memory:")) as db:
            db.execute("CREATE TABLE unsupported(message TEXT)")
            with self.assertRaisesRegex(ValueError, "PRIMARY KEY"):
                table_views(db)

    def test_guarded_update_rejects_missing_row(self):
        with closing(self.connection()) as db:
            before = table_views(db)
            db.execute("DELETE FROM state")
            with self.assertRaises(StaleSnapshot):
                publish(db, before, [Action("state", "update", (1,), (1, b"x", 1))])

    def test_data_version_detects_commits_from_other_connection(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "db.sqlite"
            with closing(sqlite3.connect(path, isolation_level=None)) as a, \
                 closing(sqlite3.connect(path, isolation_level=None)) as b:
                a.execute("PRAGMA journal_mode=WAL")
                a.execute("CREATE TABLE state(id INTEGER PRIMARY KEY, revision INT NOT NULL)")
                a.execute("INSERT INTO state VALUES(1,0)")
                before = a.execute("PRAGMA data_version").fetchone()[0]
                b.execute("UPDATE state SET revision=1")
                after = a.execute("PRAGMA data_version").fetchone()[0]
                self.assertNotEqual(before, after)


if __name__ == "__main__":
    unittest.main()
