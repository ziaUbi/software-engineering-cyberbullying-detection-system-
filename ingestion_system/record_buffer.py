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

        # Pulisce il DB all'avvio 
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
        Saves CLEAN values (unwrapped) into the database columns.
        """
        value_data = record["value"]
        uuid = value_data["uuid"]
        source_type = record["source"] 

        # 1. INSERT OR IGNORE: crea la riga vuota se non esiste
        insert_query = ("INSERT OR IGNORE INTO records (uuid, tweet, audio, events, label) "
                        "VALUES (?, NULL, NULL, NULL, NULL);")
        self.cursor.execute(insert_query, (uuid,))

        # 2. EXTRACT & PREPARE: Estraiamo SOLO il dato che ci serve
        content_to_save = None

        if source_type == "tweet":
            content_to_save = value_data.get("tweet")
        
        elif source_type == "audio":
            # Gestiamo entrambi i casi (file_path o audio) per sicurezza
            content_to_save = value_data.get("file_path") or value_data.get("audio")
        
        elif source_type == "events":
            content_to_save = value_data.get("events")
        
        elif source_type == "label":
            content_to_save = value_data.get("label")

        # Se non abbiamo trovato il dato, usciamo o logghiamo errore
        if content_to_save is None:
            print(f"Warning: No valid data found for source '{source_type}' in record {uuid}")
            return

        # Convertiamo il SINGOLO VALORE in stringa JSON
        # Esempio: "testo" diventa "\"testo\"", [1,2] diventa "[1, 2]"
        json_content = json.dumps(content_to_save)

        # 3. UPDATE: aggiorniamo la colonna specifica
        if source_type in ["tweet", "audio", "events", "label"]:
            update_query = f"UPDATE records SET {source_type} = ? WHERE uuid = ?;"
            self.cursor.execute(update_query, (json_content, uuid))
            
            self.conn.commit()
            # print(f"Stored {source_type} for {uuid}") # Debug opzionale
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