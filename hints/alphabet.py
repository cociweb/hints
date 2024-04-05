"""language specific alphabet selector"""

from pathlib import Path
import logging
import sys
import shutil

_LOGGER = logging.getLogger(__name__)

def generate_alphabet(language_code: str, base_path: Path ='./alphabet/', alphabet: str = 'abcdefghijklmnopqrstuvwxyz') -> str:
    if not alphabet_exist(language_code, base_path):
        if not copy_alphabet(language_code, base_path):
            file_path = base_path / f"{language_code}_alphabet.py"
            with open(file_path, 'w') as file:
                file.write(f"\"\"\"Generated language file\"\"\"\n\n")
                file.write(f"__alphabet__ = ")
                file.write(f"\"{alphabet}\"")
            _LOGGER.info("No custom alphabet file is found in %s, default alphabet is used: '%s'", base_path, alphabet)
    else:
        return get_alphabet(language_code, base_path)

def alphabet_path(language_code: str, base_path: Path ='./alphabet/') -> Path:
    return base_path / f"{language_code}_alphabet.py"

def alphabet_exist(language_code: str, base_path: Path ='./alphabet/') -> bool:
    file_path = alphabet_path(language_code, base_path)
    return file_path.is_file()

def copy_alphabet(language_code: str, base_path: Path ='./alphabet/', sys_path: Path = 'hints/language/') -> bool:
    result: bool = False
    for path in [Path(p) / Path(sys_path) for p in sys.path if p.endswith('packages')]:
        if alphabet_exist(language_code, path) and not alphabet_exist(language_code, base_path):
            shutil.copyfile(path / f"{language_code}_alphabet.py", base_path / f"{language_code}_alphabet.py")
            _LOGGER.info(f"Alphabet copied from {path} to {base_path}")
            result = True
            break
    else:
        path = Path.cwd() / Path(sys_path)
        if alphabet_exist(language_code, path) and not alphabet_exist(language_code, base_path):
            shutil.copyfile(path / f"{language_code}_alphabet.py", base_path / f"{language_code}_alphabet.py")
            _LOGGER.info(f"Alphabet copied from {path} to {base_path}")
            result = True
    return result


def get_alphabet(language_code: str, base_path: Path ='./alphabet/'):
    file_path = base_path / f"{language_code}_alphabet.py"
    if not file_path.is_file():
        _LOGGER.error(f"No alphabet file found for language code: {language_code} at {file_path}")
        return None

    # Read the entire file content
    alphabet_content = file_path.read_text()

    # Extract the alphabet from the content
    start_marker = '__alphabet__ = "'
    end_marker = '"'
    start_index = alphabet_content.find(start_marker)
    end_index = alphabet_content.find(end_marker, start_index + len(start_marker))
    if start_index == -1 or end_index == -1:
        _LOGGER.error(f"Alphabet content is not valid for language code: {language_code} at {file_path}")
        return None

    alphabet = alphabet_content[start_index + len(start_marker):end_index]
    return alphabet

