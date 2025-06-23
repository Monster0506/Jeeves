import os
import sqlite3
from unittest.mock import patch

import pytest

from src.core.database import DatabaseError, DatabaseManager


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test_jeeves.db")


@pytest.fixture
def db(db_path):
    db = DatabaseManager(db_path)
    yield db
    db.close_connections()
    if os.path.exists(db_path):
        os.remove(db_path)


# --- THREADS ---
def test_create_and_get_thread(db):
    # Insert thread directly
    with db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO threads (name, icon) VALUES (?, ?)", ("TestThread", "icon"))
        thread_id = cursor.lastrowid
        conn.commit()
    thread = db.get_thread(thread_id)
    assert thread["name"] == "TestThread"
    assert thread["icon"] == "icon"
    assert thread["is_active"]
    assert not thread["is_archived"]


def test_get_threads_and_find_by_name(db):
    # Insert threads
    with db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO threads (name, icon) VALUES (?, ?)", ("Alpha", "a"))
        cursor.execute(
            "INSERT INTO threads (name, icon, is_active, is_archived) VALUES (?, ?, ?, ?)",
            ("Beta", "b", 0, 1),
        )
        conn.commit()
    threads = db.get_threads(active_only=False, include_archived=True)
    assert len(threads) >= 2
    found = db.find_threads_by_name("Alpha")
    assert any(t["name"] == "Alpha" for t in found)


def test_update_thread(db):
    with db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO threads (name, icon) VALUES (?, ?)", ("Gamma", "g"))
        thread_id = cursor.lastrowid
        conn.commit()
    updated = db.update_thread(
        thread_id,
        name="Gamma2",
        is_archived=1,
        tags=["tag1", "tag2"],
        metadata={"foo": 1},
    )
    assert updated
    thread = db.get_thread(thread_id)
    assert thread["name"] == "Gamma2"
    assert thread["is_archived"]
    assert thread["tags"] == ["tag1", "tag2"]
    assert thread["metadata"] == {"foo": 1}


def test_update_thread_invalid_key(db):
    with db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO threads (name, icon) VALUES (?, ?)", ("Delta", "d"))
        thread_id = cursor.lastrowid
        conn.commit()
    updated = db.update_thread(thread_id, not_a_column="nope")
    assert not updated


def test_get_thread_message_counts(db):
    with db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO threads (name, icon) VALUES (?, ?)", ("Epsilon", "e"))
        thread_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO messages (thread_id, sender, content) VALUES (?, ?, ?)",
            (thread_id, "user", "msg1"),
        )
        cursor.execute(
            "INSERT INTO messages (thread_id, sender, content) VALUES (?, ?, ?)",
            (thread_id, "ai", "msg2"),
        )
        conn.commit()
    counts = db.get_thread_message_counts()
    assert thread_id in counts
    assert counts[thread_id] == 2


# --- MESSAGES ---
def test_add_and_get_messages(db):
    with db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO threads (name, icon) VALUES (?, ?)", ("Zeta", "z"))
        thread_id = cursor.lastrowid
        conn.commit()
    msg_id = db.add_message(thread_id, "user", "Hello")
    assert isinstance(msg_id, int)
    msgs = db.get_messages(thread_id)
    assert any(m["content"] == "Hello" for m in msgs)


def test_add_message_with_attachments(db):
    with db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO threads (name, icon) VALUES (?, ?)", ("Eta", "e"))
        thread_id = cursor.lastrowid
        conn.commit()
    attachments = [
        {
            "file_name": "f.txt",
            "file_path": "/tmp/f.txt",
            "file_size": 1,
            "mime_type": "text/plain",
            "hash": "abc",
        }
    ]
    msg_id = db.add_message(thread_id, "user", "With attachment", attachments=attachments)
    assert isinstance(msg_id, int)
    with db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM attachments WHERE message_id = ?", (msg_id,))
        rows = cursor.fetchall()
        assert len(rows) == 1
        assert rows[0][2] == "f.txt"


def test_update_message(db):
    with db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO threads (name, icon) VALUES (?, ?)", ("Theta", "t"))
        thread_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO messages (thread_id, sender, content) VALUES (?, ?, ?)",
            (thread_id, "user", "old"),
        )
        msg_id = cursor.lastrowid
        conn.commit()
    updated = db.update_message(msg_id, content="new", metadata={"x": 1})
    assert updated
    msgs = db.get_messages(thread_id)
    assert any(m["content"] == "new" for m in msgs)


def test_update_message_no_fields(db):
    with db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO threads (name, icon) VALUES (?, ?)", ("Iota", "i"))
        thread_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO messages (thread_id, sender, content) VALUES (?, ?, ?)",
            (thread_id, "user", "msg"),
        )
        msg_id = cursor.lastrowid
        conn.commit()
    updated = db.update_message(msg_id)
    assert not updated


# --- USER SETTINGS ---
def test_set_and_get_user_setting(db):
    ok = db.set_user_setting("theme", "dark", value_type="string", description="UI theme")
    assert ok
    val = db.get_user_settings("theme")
    assert val == "dark"
    all_settings = db.get_user_settings()
    assert "theme" in all_settings


def test_set_user_setting_types(db):
    db.set_user_setting("intkey", 42, value_type="int")
    db.set_user_setting("floatkey", 3.14, value_type="float")
    db.set_user_setting("boolkey", True, value_type="bool")
    db.set_user_setting("jsonkey", {"a": 1}, value_type="json")
    assert db.get_user_settings("intkey") == 42
    assert db.get_user_settings("floatkey") == 3.14
    assert db.get_user_settings("boolkey") is True
    assert db.get_user_settings("jsonkey") == {"a": 1}


# --- ANALYTICS, STATS, BACKUP, CLEANUP, VACUUM ---
def test_get_database_stats(db):
    stats = db.get_database_stats()
    assert "total_threads" in stats
    assert "total_messages" in stats
    assert "database_size_bytes" in stats


def test_backup_database(db, tmp_path):
    backup_path = tmp_path / "backup.db"
    assert db.backup_database(str(backup_path))
    assert os.path.exists(backup_path)


def test_cleanup_old_messages(db):
    with db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO threads (name, icon) VALUES (?, ?)", ("Kappa", "k"))
        thread_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO messages (thread_id, sender, content, timestamp) VALUES (?, ?, ?, datetime('now', '-40 days'))",
            (thread_id, "user", "oldmsg"),
        )
        conn.commit()
    deleted = db.cleanup_old_messages(days_old=30)
    assert deleted >= 1


def test_vacuum_database(db):
    assert db.vacuum_database()


def test_close_connections(db):
    db.close_connections()  # Should not raise


# --- ERROR HANDLING ---
def test_execute_with_retry_database_locked(db):
    # Simulate database locked error
    def op():
        raise sqlite3.OperationalError("database is locked")

    with patch.object(db, "max_retries", 2):
        with pytest.raises(DatabaseError):
            db._execute_with_retry(op)


def test_get_connection_database_locked(db_path):
    # Create DatabaseManager first (it will initialize successfully)
    from src.core.database import DatabaseError, DatabaseManager

    db = DatabaseManager(db_path)

    # Close existing connections and clear the connection pool
    for conn in db._connection_pool.values():
        try:
            conn.close()
        except Exception:
            pass
    db._connection_pool.clear()

    # Now patch sqlite3.connect to simulate database locked error
    with patch("sqlite3.connect", side_effect=sqlite3.OperationalError("database is locked")):
        with patch.object(db, "max_retries", 2):
            with pytest.raises(DatabaseError):
                with db._get_connection():
                    pass


def test_get_connection_other_error(db_path):
    # Create DatabaseManager first (it will initialize successfully)
    from src.core.database import DatabaseError, DatabaseManager

    db = DatabaseManager(db_path)

    # Close existing connections and clear the connection pool
    for conn in db._connection_pool.values():
        try:
            conn.close()
        except Exception:
            pass
    db._connection_pool.clear()

    # Now patch sqlite3.connect to simulate other error
    with patch("sqlite3.connect", side_effect=Exception("fail")):
        with patch.object(db, "max_retries", 2):
            with pytest.raises(DatabaseError):
                with db._get_connection():
                    pass


def test_backup_database_failure(db, tmp_path):
    # Simulate backup failure
    with patch("shutil.copy2", side_effect=Exception("fail")):
        assert not db.backup_database(str(tmp_path / "fail.db"))


def test_vacuum_database_failure(db):
    # Simulate vacuum failure
    with patch.object(db, "_get_connection") as mock_conn:
        mock_conn.side_effect = Exception("fail")
        assert not db.vacuum_database()
