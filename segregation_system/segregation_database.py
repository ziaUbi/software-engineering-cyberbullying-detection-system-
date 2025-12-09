import sqlite3
import json
import os
from typing import List, Dict
from prepared_session import PreparedSession

class PreparedSessionDatabaseController:
    """
    Gestisce la persistenza delle Prepared Sessions utilizzando SQLite.
    """
    def __init__(self, db_path="segregation_system.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Inizializza il database creando la tabella se non esiste."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prepared_sessions (
                uuid TEXT PRIMARY KEY,
                text TEXT,
                tweet_length INTEGER,
                audio_db TEXT,
                events TEXT,
                label TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def store_prepared_session(self, session_data: PreparedSession):
        """
        Salva una sessione nel database.
        I campi lista (audio_db, events) vengono serializzati in JSON.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Serializza liste in stringhe JSON per salvarle in SQLite
        audio_str = json.dumps(session_data.get("audio_db", []))
        events_str = json.dumps(session_data.get("events", []))
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO prepared_sessions (uuid, text, tweet_length, audio_db, events, label)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                session_data["uuid"],
                json.dumps(session_data.get("text", [])), # Text potrebbe essere una lista di frasi
                session_data.get("tweet_length", 0),
                audio_str,
                events_str,
                session_data["label"]
            ))
            conn.commit()
            print(f"[Database] Session {session_data['uuid']} stored.")
        except sqlite3.Error as e:
            print(f"[Database] Error storing session: {e}")
        finally:
            conn.close()

    def get_all_prepared_sessions(self) -> List[PreparedSession]:
        """Recupera tutte le sessioni dal database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM prepared_sessions')
        rows = cursor.fetchall()
        conn.close()

        sessions = []
        for row in rows:
            sessions.append({
                "uuid": row["uuid"],
                "text": json.loads(row["text"]),
                "tweet_length": row["tweet_length"],
                "audio_db": json.loads(row["audio_db"]),
                "events": json.loads(row["events"]),
                "label": row["label"]
            })
        return sessions

    def get_number_of_sessions_stored(self) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM prepared_sessions')
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def remove_all_prepared_sessions(self):
        """Cancella tutte le sessioni dopo aver generato i learning sets."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM prepared_sessions')
        conn.commit()
        conn.close()
        print("[Database] All sessions removed.")