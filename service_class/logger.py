import os

class Logger:
    """
    Handles logging in a CSV file for different phases of the Service Class.
    Ensures that existing files are not overwritten.
    """

    def __init__(self, basedir: str, phase: str):
        """
        Initialize the Logger.

        :param basedir: The base directory for the Logger.
        :param phase: The phase for which to log.
        """

        self.basedir = basedir
        self.log_dir = os.path.join(self.basedir, "logs")
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.phase = phase

        """Generate a new file path ensuring no overwriting."""
        base_name = f"{self.phase}_log"
        file_index = 0
        while os.path.exists(os.path.join(self.log_dir, f"{base_name}_{file_index}.csv")):
            file_index += 1
        self.file_path = os.path.join(self.log_dir, f"{base_name}_{file_index}.csv")

    def write_header(self, header: str):
        """
        Write the header to the CSV file.

        :param header: The header to write.
        """
        with open(self.file_path, "w") as file:
            file.write(header + "\n")

    def log(self, row: str):
        """
        Append a row to the CSV file.

        :param row: The row to append.
        """
        with open(self.file_path, "a") as file:
            file.write(row + "\n")