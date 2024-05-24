"""Home-assistant INtent Text Spell-checker"""

import asyncio
import logging
import os
import shutil
import sys
from pathlib import Path
from typing import Optional

#from . import __version__
from .alphabet import alphabet_exist, get_alphabet, generate_alphabet, alphabet_path
from .intents import get_intents
#from .del_dictionary import generate_dictionary_from_intents
from .hints_parser import fetch_data_from_api
from .ha_assist import generate_entity_info, generate_area_info, load_assist_data
from .hassils import sample_hassil_sentences
from .jams import generate_jamspell_model



import re
from functools import partial
import faster_whisper
from wyoming.info import AsrModel, AsrProgram, Attribution, Info
from wyoming.server import AsyncServer
from . import __all__
from .wfw_handler import FasterWhisperEventHandler
from .wfw_download import download_custom_model

from .args import core_args, whisper_args







_LOGGER = logging.getLogger(__name__)




def prepare_folder(folder: Path, force: bool) -> bool:
    result: bool = False
    if folder is not None and (not folder.exists() or not folder.is_dir()):
        folder.mkdir(parents=True, exist_ok=True)
        result = True
    elif folder is not None and force:
        _LOGGER.debug("Folder %s is forcefully created!", folder)
        shutil.rmtree(folder)
        folder.mkdir(parents=True, exist_ok=True)
        result = True
    elif folder.exists() and folder.is_dir() and not force:
        _LOGGER.debug("Folder %s is already available.", folder)
        return True
    else:
        folder.mkdir(parents=True, exist_ok=True)
        result = True
    _LOGGER.debug("Folder %s is ready to use.", folder)
    return result

async def main() -> None:

    args = core_args()
    w_args = whisper_args()

    w_args.language=args.language
    w_args.local_files_only=args.local_files_only
    w_args.task="transcribe"
    w_args.download_root = None

    #args = parser.parse_args()
#    args, whisper_args = parser.parse_known_args()

    # Convert list of unknown args to a dictionary
#    whisper_dict = {whisper_args[i].lstrip('-').replace('-', '_'): whisper_args[i + 1] for i in range(0, len(whisper_args), 2)}

    # Convert dictionary to a Namespace object
#    w_args = argparse.Namespace(**whisper_dict)



    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO, format=args.log_format
    )
    _LOGGER.debug(args)
    _LOGGER.debug(w_args)


    ##TODO: model checking!


    data_dir: Optional[Path] = None
    model_dir: Optional[Path] = None

    data_dir=Path(args.data_dir)
    model_dir=Path(args.model_dir)


    purge_model_dir: bool = False

    if args.local_files_only and args.force_download_model:
        _LOGGER.error("local-files-only and force-download-model are mutually exclusive!")
        exit(1)
    elif args.force_download_model:
        purge_model_dir = True
    elif args.local_files_only:
        purge_model_dir = False

    if args.spellcheck:
        if args.language is None or args.language.lower() == 'en':
            # Whisper does not understand "auto"
            args.language = 'en'

        if args.tag == None:
            # Whisper does not understand "auto"
            args.tag = 'latest'



        intent_dir: Optional[Path] = None
        jamspell_dir: Optional[Path] = None
        alphabet_dir: Optional[Path] = None
        model_dir: Optional[Path] = None


        intent_suffix = Path(f"intent_{args.language}")
        intent_dir = Path(os.path.join(data_dir, intent_suffix))
        jamspell_dir = Path(f"{data_dir}/jamspell")
        alphabet_dir = Path(f"{data_dir}/alphabet")


        folders = [data_dir, intent_dir, jamspell_dir, alphabet_dir, model_dir]
        permissions = [
            False,
            args.force_generate_intent,
            args.force_generate_intent or args.force_generate_spellcheck,
            False,
            purge_model_dir
            ]
        for folder, permission in zip(folders, permissions):
            prepare_folder(folder, permission)


        alphabet: str = args.alphabet or 'abcdefghijklmnopqrstuvwxyz'
        language: str = args.language or 'en'

        if args.language and alphabet_exist(args.language, alphabet_dir):
            alphabet = get_alphabet(args.language, alphabet_dir) if get_alphabet(args.language, alphabet_dir) else alphabet
            _LOGGER.debug("%s alphabet file is loaded from %s folder", args.language, alphabet_dir)
        elif args.language and args.alphabet:
            generate_alphabet(args.language, alphabet_dir, args.alphabet)
            _LOGGER.debug("%s alphabet file in %s is generated from: %s", args.language, alphabet_dir, args.alphabet)
        else:
            generate_alphabet(language, alphabet_dir, alphabet)

        get_intents(language, args.tag, data_dir, args.timeout)


        intent_file = Path(f"{intent_dir}/merged_intents.txt")
        if intent_file.exists():
            _LOGGER.info("Intent file is already generated and will be reused.")
        else:
            _LOGGER.info("Intent file generation will be started soon.")


            if args.ha_api_url and args.token is not None:
                fetch_data_from_api(args.ha_api_url, args.token, intent_dir)

            # Load data from entities.txt and areas.txt
            entities_data = load_assist_data(os.path.join(intent_dir, "entities.txt"))
            areas_data = load_assist_data(os.path.join(intent_dir, "areas.txt"))

            #Generate entity and area info
            entity_info = generate_entity_info(entities_data)
            area_info = generate_area_info(areas_data)


            sample_hassil_sentences(entity_info, area_info, intent_dir, intent_file, iterations=args.hassil_iterations, lang=language)

        args. jamspell_model_file = jamspell_dir / f"jamspell_{language}.bin" or jamspell_dir / f"{args.jamspell}"
        if not args.jamspell_model_file.exists():
            _LOGGER.info("Jamspell model is not available.")
            if not args.jamspell_model_file.is_file():
                _LOGGER.info("Generating Jamspell model.")
                alphabet_file = alphabet_path(language, alphabet_dir)
                await generate_jamspell_model(alphabet_file, intent_file, args.jamspell_model_file)
        else:
            _LOGGER.info("Jamspell model already available.")

# -----------------------------------------------------------------------------
# WFW service
# -----------------------------------------------------------------------------

    if args.custom_model_url and args.model.lower() == "custom":
        model_path = str(model_dir / "custom")
        model_file = Path(model_path + "/model.bin")
        if args.custom_model_url.startswith("http") and (purge_model_dir or not model_file.exists()):
            _LOGGER.info("Downloading custom model from %s", args.custom_model_url)
            if not args.custom_model_url.endswith("/"):
                args.custom_model_url += "/"
            download_custom_model(args.custom_model_url.strip(), model_dir, purge_model_dir, args.timeout)
            w_args.local_files_only = True
        elif not purge_model_dir:
            args.model = str(model_dir / "custom")
        elif args.custom_model_url.count("/") == 1:
            args.model = args.custom_model_url
        else:
            args.model = args.custom_model_url

    model_name = args.model
    match = re.match(r"^(tiny|base|small|medium)[.-]int8$", args.model)
    if match:
        # Original models re-uploaded to huggingface
        model_size = match.group(1)
        model_name = f"{model_size}-int8"
        args.model = f"rhasspy/faster-whisper-{model_name}"
    else:
        w_args.model_size_or_path=args.model
        model_name=args.model


    if args.language == "auto":
        # Whisper does not understand "auto"
        args.language = None

    wyoming_info = Info(
        asr=[
            AsrProgram(
                name=__all__[1],
                description=__all__[2],
                attribution=Attribution(
                    name=__all__[3],
                    url=__all__[6],
                ),
                installed=True,
                version=__all__[0],
                models=[
                    AsrModel(
                        name=model_name,
                        description=model_name,
                        attribution=Attribution(
                            name="Systran",
                            url="https://huggingface.co/Systran",
                        ),
                        installed=True,
                        languages=faster_whisper.tokenizer._LANGUAGE_CODES,  # pylint: disable=protected-access
                        version=faster_whisper.__all__[1],
                    )
                ],
            )
        ],
    )

    # Load model
    _LOGGER.debug("Loading %s", args.model)
    whisper_model = faster_whisper.WhisperModel(
        args.model,
        download_root=str(model_dir),
        device=w_args.device,
        compute_type=w_args.compute_type,
        local_files_only=w_args.local_files_only,
    )
    server = AsyncServer.from_uri(args.proto)
    _LOGGER.info("Ready")
    model_lock = asyncio.Lock()
    await server.run(
        partial(
            FasterWhisperEventHandler,
            wyoming_info,
            w_args,
            whisper_model,
            model_lock,
        )
    )













# -----------------------------------------------------------------------------

def run() -> None:
    try:

        asyncio.run(main())
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        pass

