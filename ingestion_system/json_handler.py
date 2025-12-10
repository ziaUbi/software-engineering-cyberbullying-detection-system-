import json
import logging
import jsonschema
import base64
import os
import uuid

class JsonHandler:
    """
    A class to read and save json files.
    """

    def read_json_file(self, filepath):
        """
        Read a json file.

        Returns:
            filecontent: content of json file or None if error.
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                filecontent = json.load(f)
            return filecontent

        except Exception as e:
            print(f"Error reading file at path {filepath}: {e}")
            return None

    def validate_json(self, json_data: dict, schema_path: str) -> bool:
        """
        Validate a json object against a json schema in a file.
        :param json_data: json object
        :param schema_path: path to the json schema
        :return: True if json object is valid, False otherwise
        """
        try:
            with open(schema_path, "r", encoding="UTF-8") as file:
                json_schema = json.load(file)
            
            jsonschema.validate(instance=json_data, schema=json_schema)
            return True

        except FileNotFoundError:
            logging.error(f"Schema file not found at: {schema_path}")
            return False
            
        except json.JSONDecodeError:
            logging.error(f"Schema file at {schema_path} is not valid JSON.")
            return False

        except jsonschema.exceptions.ValidationError as ex:
            logging.error(f"JSON Validation Error: {ex.message}")
            return False
            
        except Exception as e:
            logging.error(f"Unexpected error during validation: {e}")
            return False
        


    def save_base64_audio_to_file(base64_string: str, output_folder: str = "./temp_audio") -> str:
        """
        Decodifica una stringa Base64 e la salva come file audio su disco.
        Restituisce il percorso assoluto del file salvato.
        """
        # 1. Crea la cartella se non esiste
        os.makedirs(output_folder, exist_ok=True)
        
        # 2. Pulizia dell'header (se presente)
        # A volte il base64 arriva come "data:audio/wav;base64,UklGR..."
        if "," in base64_string:
            base64_string = base64_string.split(",")[1]
        
        # 3. Decodifica da Testo a Bytes
        try:
            audio_bytes = base64.b64decode(base64_string)
        except Exception as e:
            print(f"Errore nella decodifica Base64: {e}")
            return ""

        # 4. Genera un nome file univoco
        filename = f"{uuid.uuid4()}.wav" # Assumiamo wav, o mp3 se sai il formato
        file_path = os.path.join(output_folder, filename)
        
        # 5. Scrivi i bytes su file (modalità 'wb' = write binary)
        with open(file_path, "wb") as f:
            f.write(audio_bytes)
            
        return os.path.abspath(file_path)