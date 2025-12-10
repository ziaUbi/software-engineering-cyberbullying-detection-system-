import sqlite3
import json
from typing import List, Any

from ingestion_system import DATABASE_FILE_PATH

class RecordBufferController:
    """
    Controller for managing the record buffer using sqlite3 directly.
    Manages storage for: tweet, audio, events, label.
    """

    def __init__(self):
        """
        Initialize the connection and the table.
        """
        # Connessione diretta al database SQLite
        # check_same_thread=False è utile se il controller viene chiamato da thread diversi
        self.conn = sqlite3.connect(DATABASE_FILE_PATH, check_same_thread=False)
        self.cursor = self.conn.cursor()

        # Opzionale: Pulisce il DB all'avvio 
        # Se vuoi persistenza tra riavvii, commenta la riga sotto.
        self._drop_table()

        # Creazione Tabella
        self._create_table()

    def _drop_table(self):
        """Internal method to drop the table."""
        self.cursor.execute("DROP TABLE IF EXISTS records")
        self.conn.commit()

    def _create_table(self):
        """Internal method to create the table schema."""
        query = ("CREATE TABLE IF NOT EXISTS records ("
                 "uuid TEXT PRIMARY KEY, "
                 "tweet TEXT, "
                 "audio TEXT, "
                 "events TEXT, "
                 "label TEXT);")
        self.cursor.execute(query)
        self.conn.commit()

    def store_record(self, record: dict) -> None:
        """
        Stores a record. Handles INSERT (if new UUID) and UPDATE (specific field).
        """
        uuid = record["value"]["uuid"]
        source_type = record["source"] # es. "tweet", "audio"

        # 1. INSERT OR IGNORE: create a new row if UUID doesn't exist
        insert_query = ("INSERT OR IGNORE INTO records (uuid, tweet, audio, events, label) "
                        "VALUES (?, NULL, NULL, NULL, NULL);")
        self.cursor.execute(insert_query, (uuid,))

        # 2. PREPARE: Convert the record content to JSON string
        record_content = {k: v for k, v in record["value"].items() if k != "UUID"}
        json_content = json.dumps(record_content)

        # 3. UPDATE: set the specific source field
        if source_type in ["tweet", "audio", "events", "label"]:
            update_query = f"UPDATE records SET {source_type} = ? WHERE uuid = ?;"
            self.cursor.execute(update_query, (json_content, uuid))
            
            # Commit the changes
            self.conn.commit()
        else:
            print(f"Warning: Unknown source type '{source_type}' for uuid {uuid}")

    def get_records(self, uuid: str) -> List[Any]:
        """
        Retrieves data for a UUID and returns a list formatted for RawSession.
        Returns: [uuid, tweet_dict, audio_dict, events_dict, label_dict]
        """
        query = "SELECT uuid, tweet, audio, events, label FROM records WHERE uuid = ?;"
        self.cursor.execute(query, (uuid,))
        row = self.cursor.fetchone()

        if not row:
            return []

        # row è una tupla: (uuid, tweet_json, audio_json, ...)
        result = [row[0]] # Inseriamo l'UUID come primo elemento

        # Iteriamo sugli altri campi (tweet, audio, events, label)
        for col_value in row[1:]:
            if col_value:
                # Se c'è del testo (JSON), lo convertiamo in Dizionario
                result.append(json.loads(col_value))
            else:
                # Se è NULL nel DB, mettiamo None
                result.append(None)

        return result

    def remove_records(self, uuid: str) -> None:
        """
        Deletes a record from the db.
        """
        query = "DELETE FROM records WHERE uuid = ?;"
        self.cursor.execute(query, (uuid,))
        self.conn.commit()

    def close(self):
        """Closes the database connection."""
        self.conn.close()