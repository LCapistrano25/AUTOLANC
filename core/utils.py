import os

def verify_directory_exists(directory_path: str) -> bool:
    """
    Verify if a directory exists.

    Args:
        directory_path (str): The path to the directory to verify.

    Returns:
        bool: True if the directory exists, False otherwise.
    """
    return os.path.isdir(directory_path)