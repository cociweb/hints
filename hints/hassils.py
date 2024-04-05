import logging
import sys
import subprocess
import json
#from hassil.sample import main as sample_sentences
from progress.bar import Bar
from pathlib import Path

_LOGGER = logging.getLogger(__name__)

def sample_hassil_sentences(entity_info: list, area_info: list, intent_dir: Path, output_file: Path, iterations:int=1000, lang:str="en"):
    _LOGGER.debug("Folder: " + str(output_file) + "!")
    try:

        # Calculate total iterations
        total_iterations = (len(area_info) if area_info else 1) * (len(entity_info) if entity_info else 1)

        # Create a progress bar
        _LOGGER.info("Generating dataset from the intents, areas and entities...")
        bar = Bar('Processing', max=total_iterations, fill='#', suffix='%(percent).1f%% - %(elapsed_td)s')

        # Backup the original arguments
        original_args = sys.argv

        with open(f"{output_file}", "w") as f:
            pass

        for area in area_info:
            for entity in entity_info:

                # Ensure area and entity are strings or bytes-like objects
                if isinstance(area, str) and isinstance(entity, str):
                    # Replace the command-line arguments with the ones you want to pass
                    cmd_args = [sys.executable, "-m", "hassil.sample",  str(intent_dir), '-n', str(iterations), '--areas', area, '--names', entity, '--language', lang]
                    # Run the command and capture stdout
                    process = subprocess.Popen(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = process.communicate()

                    # Decode the stdout (assuming it's in UTF-8)
                    sentences = stdout.decode("utf-8").splitlines()

                    if sentences:
                        with open(f"{output_file}", "a") as f:
                            text_values = []
                            for sentence in sentences:
                                try:
                                    data = json.loads(sentence)
                                    text_value = data.get("text").lower()
                                    if text_value:
                                        text_values.append(text_value)
                                        _LOGGER.debug(f"Sampled sentence: {text_value}")
                                    else:
                                        _LOGGER.warning(f"No 'text' value found in line: {sentence.strip()}")
                                except json.JSONDecodeError:
                                    _LOGGER.warning(f"Invalid JSON format in line: {sentence.strip()}")

                            # Write all text values at once
                            f.write("\n".join(text_values) + "\n")
                    else:
                        _LOGGER.warning(f"Sample sentences returned empty for area {area} and entity {entity}")

                # Update the progress bar
                bar.next()

        # Finish the progress bar
        bar.finish()


        # Restore the original arguments
        sys.argv = original_args
    except Exception as e:
        _LOGGER.error(f"Error: {e}")
