"""jamspell spell-checker"""

import asyncio
from pathlib import Path
import logging
import jamspell

_LOGGER = logging.getLogger(__name__)

async def generate_jamspell_model(alphabet, intent_file, jamspell_model_file):

    # Read sentences from the external file
#    with open(intent_file, 'r') as file:
#        sentences = file.readlines()


    # Initialize the JamSpell trainer
    corrector = jamspell.TSpellCorrector()

    # Train the model using the sentences
#    for sentence in sentences:
#        _LOGGER.debug(f"Training sentence: {sentence}")
#        _LOGGER.debug(f"Training alphabet: {alphabet}")
        #corrector.TrainLangModel(sentence.strip(), str(alphabet), str(jamspell_dir / jamspell_model_file))
    if corrector.TrainLangModel(str(intent_file), str(alphabet), str(jamspell_model_file)):
        _LOGGER.info(f"Language model generated as {jamspell_model_file}!")
    else:
        _LOGGER.error(f"Language model generation failed!")


async def jamspell_fix(jamspell_model_file, sentence):
    # Initialize the JamSpell spellchecker
    corrector = jamspell.TSpellCorrector()
    return str(corrector.FixFragment(sentence))

    # Check if the sentence is spelled correctly