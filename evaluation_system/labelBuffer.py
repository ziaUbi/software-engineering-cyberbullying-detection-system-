"""
Author: Rossana Antonella Sacco
"""

import os
import sqlite3
from typing import List, Tuple
from evaluation_system.label import Label

class LabelBuffer:
    """
    A specialized SQLite database manager class for storing Label instances
    for the Cyberbullying evaluation system.
    """

    def __init__(self, db_name: str = "labels.db"):
        """
        Initialize the LabelBuffer with a given database name.

        :param db_name: The name of the SQLite database file.
        """
        self.db_name = db_name
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.db_path = os.path.join(current_dir, db_name)
    
        self.create_table()
        

    def _connect(self):
        """Establish a connection to the database."""
        return sqlite3.connect(self.db_path)

    def create_table(self) -> None:
        """
        Create the labels table in the database.
        The table has the following columns:
        - uuid (TEXT): Unique identifier for the label.
        - cyberbullying (TEXT): String indicating the status.
        - expert (INTEGER): Integer indicating if the label was assigned by an expert (0 or 1).
        The primary key is a composite key of (uuid, expert) to allow both classifier and expert labels
        for the same UUID.
        """
        query = """
        CREATE TABLE IF NOT EXISTS labels (
            uuid TEXT NOT NULL,
            cyberbullying TEXT NOT NULL,
            expert INTEGER NOT NULL,
            PRIMARY KEY (uuid, expert)
        )
        """
        self.execute_query(query)

    def execute_query(self, query: str, params: Tuple = ()) -> None:
        """
        Execute a single query that does not return results (INSERT, UPDATE, DELETE).
        
        :param query: The SQL query to execute.
        :param params: Tuple of parameters to use with the query.
        """
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")

    def fetch_query(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """
        Execute a query and return the results (SELECT).
        
        :return: List of tuples representing the query results.
        """
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []

    def save_label(self, label: 'Label') -> None:
        """
        Save a Label instance to the database.
        
        :param label: The Label instance to save.
        """
        query = """
        INSERT OR REPLACE INTO labels (uuid, cyberbullying, expert)
        VALUES (?, ?, ?)
        """
        self.execute_query(query, (label.uuid, label.cyberbullying, label.expert))

    def get_classifier_labels(self, limit: int = 100) -> List[Label]:
        """
        Get the first 'limit' classifier labels from the database (expert=0).
        Ordered by UUID to ensure alignment with expert labels.
        """
        query = "SELECT uuid, cyberbullying, expert FROM labels WHERE expert = 0 ORDER BY uuid LIMIT ?"
        rows = self.fetch_query(query, (limit,))
        # we use bool(row[2]) to convert integer back to boolean, as expert is stored as INTEGER in the DB
        return [Label(uuid=row[0], cyberbullying=row[1], expert=bool(row[2])) for row in rows]

    def get_expert_labels(self, limit: int = 100) -> List[Label]:
        """
        Get the first 'limit' expert labels from the database (expert=1).
        """
        query = "SELECT uuid, cyberbullying, expert FROM labels WHERE expert = 1 ORDER BY uuid LIMIT ?"
        rows = self.fetch_query(query, (limit,))
        return [Label(uuid=row[0], cyberbullying=row[1], expert=bool(row[2])) for row in rows]

    def delete_labels(self, limit: int) -> None:
        """
        Delete the first 'limit' labels from the database for BOTH classifier and expert.
        This is used to clear processed labels from the buffer (sliding window).
        """
        # Delete the first limit classifier labels
        query_classifier = """
        DELETE FROM labels WHERE rowid IN (
            SELECT rowid FROM labels WHERE expert = 0 ORDER BY uuid LIMIT ?
        )
        """
        self.execute_query(query_classifier, (limit,))

        # Delete the first limit expert labels
        query_expert = """
        DELETE FROM labels WHERE rowid IN (
            SELECT rowid FROM labels WHERE expert = 1 ORDER BY uuid LIMIT ?
        )
        """
        self.execute_query(query_expert, (limit,))

    def get_num_classifier_labels(self) -> int:
        """
        Get the total number of classifier labels in the database.
        """
        query = "SELECT COUNT(*) FROM labels WHERE expert = 0"
        result = self.fetch_query(query)
        return result[0][0] if result else 0

    def get_num_expert_labels(self) -> int:
        """
        Get the total number of expert labels in the database.
        """
        query = "SELECT COUNT(*) FROM labels WHERE expert = 1"
        result = self.fetch_query(query)
        return result[0][0] if result else 0