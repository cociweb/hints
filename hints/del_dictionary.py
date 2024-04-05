import sys
from pathlib import Path
from typing import Union
from hassil.sample import main



def generate_dictionary_from_intents(src_dir: Union[str, Path], dest_file: Union[str, Path], m: int = 1000) -> Path:
    src_dir = Path(src_dir)
    dest_file = Path(dest_file)

    if dest_file.exists():
        dest_file.unlink()

    main(src_dir=src_dir, max_sentences_per_intent=m)

def execute_hassil_with_args(args: list, dest_dir: Union[str, Path], output_file: str):
    dest_dir = Path(dest_dir)
    output = dest_dir / output_file
    try:
        with open(output, 'w') as file:
            sys.stdout = file
            main(*args)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        sys.stdout = sys.__stdout__