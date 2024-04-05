import logging
import json
from hassil.sample import main as sample_sentences
from progress.bar import Bar

_LOGGER = logging.getLogger(__name__)

async def sample_hassil_sentences(entity_info, area_info, intent_dir, output_file, iterations=1000, lang="en"):
    _LOGGER.debug("Folder: " + str(intent_dir) + "/" + str(output_file) + "!")

    # Calculate total iterations
    total_iterations = (len(area_info) if area_info else 1) * (len(entity_info) if entity_info else 1)

    # Create a progress bar
    _LOGGER.info("Generating dataset from the intents, areas and entities...")
    bar = Bar('Processing', max=total_iterations, fill='#', suffix='%(percent).1f%% - %(elapsed_td)s')

    with open(f"{intent_dir}/{output_file}", "w") as f:
        pass

    for area in area_info:
        for entity in entity_info:

            # Ensure area and entity are strings or bytes-like objects
            if isinstance(area, str) and isinstance(entity, str):
                # Call the sample_sentences function directly instead of using subprocess
                sentences = sample_sentences(intent_dir, n=iterations, areas=area, names=entity, language=lang)

                if sentences:
                    with open(f"{intent_dir}/{output_file}", "a") as f:
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
