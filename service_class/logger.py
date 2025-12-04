import os

class Logger:
    """
    Handles CSV logging for different phases of the Service Class.
    Ensures that existing files are not overwritten.
    """

    def __init__(self, basedir: str, phase: str):
        """
        Initialize the CSVLogger.

        :param basedir: The base directory for the CSVLogger.
        :param phase: The phase for which to log.
        """

        self.basedir = basedir
        self.phase = phase

        self.log_dir = os.path.join(self.basedir, "log")

        os.makedirs(self.log_dir, exist_ok=True)

        self.file_path = self._generate_file_path()

    def _generate_file_path(self) -> str:
        """Generate a new file path ensuring no overwriting."""
        base_name = f"{self.phase}_log"
        file_index = 0
        while os.path.exists(os.path.join(self.log_dir, f"{base_name}_{file_index}.csv")):
            file_index += 1
        return os.path.join(self.log_dir, f"{base_name}_{file_index}.csv")

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