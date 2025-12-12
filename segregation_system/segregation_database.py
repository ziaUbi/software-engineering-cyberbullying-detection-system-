import sqlite3
import json
import os
from typing import List, Dict
from segregation_system.prepared_session import PreparedSession

class PreparedSessionDatabaseController:
    """
    Gestisce la persistenza delle Prepared Sessions utilizzando SQLite.
    """
    def __init__(self, db_path="segregation_system/segregation_system.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Inizializza il database creando la tabella se non esiste."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prepared_sessions (
                uuid TEXT PRIMARY KEY,
                label TEXT,
                tweet_length INTEGER,
                       
                word_fuck INTEGER,
                word_bulli INTEGER,
                word_muslim INTEGER,
                word_gay INTEGER,
                word_nigger INTEGER,
                word_rape INTEGER,
                       
                event_score INTEGER,
                event_sending_off INTEGER,
                event_caution INTEGER,
                event_substitution INTEGER,
                event_foul INTEGER,
                       
                audio_0 DOUBLE,
                audio_1 DOUBLE,
                audio_2 DOUBLE,
                audio_3 DOUBLE,
                audio_4 DOUBLE,
                audio_5 DOUBLE,
                audio_6 DOUBLE,
                audio_7 DOUBLE,
                audio_8 DOUBLE,
                audio_9 DOUBLE,
                audio_10 DOUBLE,
                audio_11 DOUBLE,
                audio_12 DOUBLE,
                audio_13 DOUBLE,
                audio_14 DOUBLE,
                audio_15 DOUBLE,
                audio_16 DOUBLE,
                audio_17 DOUBLE,
                audio_18 DOUBLE,
                audio_19 DOUBLE
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
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO prepared_sessions (uuid, label, tweet_length, word_fuck, word_bulli, word_muslim, word_gay, word_nigger, word_rape, event_score, event_sending_off, event_caution, event_substitution, event_foul, audio_0, audio_1, audio_2, audio_3, audio_4, audio_5, audio_6, audio_7, audio_8, audio_9, audio_10, audio_11, audio_12, audio_13, audio_14, audio_15, audio_16, audio_17, audio_18, audio_19)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_data.uuid,
                session_data.label,
                session_data.tweet_length,
                session_data.word_fuck,
                session_data.word_bulli,
                session_data.word_muslim,
                session_data.word_gay,
                session_data.word_nigger,
                session_data.word_rape,
                session_data.event_score,
                session_data.event_sending_off,
                session_data.event_caution,
                session_data.event_substitution,
                session_data.event_foul,
                session_data.audio_0,
                session_data.audio_1,
                session_data.audio_2,
                session_data.audio_3,
                session_data.audio_4,
                session_data.audio_5,
                session_data.audio_6,
                session_data.audio_7,
                session_data.audio_8,
                session_data.audio_9,
                session_data.audio_10,
                session_data.audio_11,
                session_data.audio_12,
                session_data.audio_13,
                session_data.audio_14,
                session_data.audio_15,
                session_data.audio_16,
                session_data.audio_17,
                session_data.audio_18,
                session_data.audio_19
            ))
            conn.commit()
            print(f"[Database] Session {session_data.uuid} stored.")
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
                "label": row["label"],
                "tweet_length": row["tweet_length"],
                "word_fuck": row["word_fuck"],
                "word_bulli": row["word_bulli"],
                "word_muslim": row["word_muslim"],
                "word_gay": row["word_gay"],
                "word_nigger": row["word_nigger"],
                "word_rape": row["word_rape"],
                "event_score": row["event_score"],
                "event_sending_off": row["event_sending_off"],
                "event_caution": row["event_caution"],
                "event_substitution": row["event_substitution"],
                "event_foul": row["event_foul"],
                "audio_0": row["audio_0"],
                "audio_1": row["audio_1"],
                "audio_2": row["audio_2"],
                "audio_3": row["audio_3"], 
                "audio_4": row["audio_4"],
                "audio_5": row["audio_5"],
                "audio_6": row["audio_6"],
                "audio_7": row["audio_7"],
                "audio_8": row["audio_8"],
                "audio_9": row["audio_9"],
                "audio_10": row["audio_10"],
                "audio_11": row["audio_11"],
                "audio_12": row["audio_12"],
                "audio_13": row["audio_13"],
                "audio_14": row["audio_14"],
                "audio_15": row["audio_15"],
                "audio_16": row["audio_16"],
                "audio_17": row["audio_17"],
                "audio_18": row["audio_18"],
                "audio_19": row["audio_19"]
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