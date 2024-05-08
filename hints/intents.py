import io
import os
import json
import glob
import shutil
import tarfile
import logging

from pathlib import Path
from typing import Union
from urllib.request import urlopen
import urllib.error
from progress.bar import Bar



_LOGGER = logging.getLogger(__name__)

def copy_files(src_dir: Path, dst_dir: Path):

    # Get a list of all file names in the sentences/responses directory
    file_names = os.listdir(src_dir)

    # Use shutil to copy each file from sentences/responses folder
    for file_name in file_names:
        shutil.copy(os.path.join(src_dir, file_name), dst_dir)

    _LOGGER.debug("All the files are copied from %s to %s", src_dir, dst_dir )

    return

def delete_exceptions(dir: str):

    try:
        fileList = glob.glob(os.path.join(dir, f"*ListAddItem.yaml"))
        for files in fileList:
            if os.path.isfile(files):
                os.remove(files)
                _LOGGER.debug("Exceptional file is removed: %s", files )
    except:
        pass

    return

def get_intents_version(tag: str):

    user = "home-assistant"
    repo = "intents"

    url = f"https://api.github.com/repos/{user}/{repo}/releases/latest"
    response = urlopen(url)
    data = json.loads(response.read().decode())
    tag_name = data['tag_name']
    url_latest= f"https://github.com/{user}/{repo}/archive/refs/tags/{tag_name}.tar.gz"


    if tag.lower() == "main":
        tag_name = "main"
        url = f"https://github.com/{user}/{repo}/archive/refs/heads/main.tar.gz"
    elif tag == None:
        tag_name = data['tag_name']
        url = url_latest
    else:
        tag_name = tag.lower()
        url = f"https://github.com/{user}/{repo}/archive/refs/tags/{tag_name}.tar.gz"


    _LOGGER.debug("The latest released intent version is: %s", tag_name )

    return url, url_latest

def download_intents(url: str, url_latest: str, timeout: int = None):

    try:
        # Download the source code tarball
        response = urlopen(url, timeout=timeout)

    except urllib.error.HTTPError as e:
        if e.code == 404:
            # If the primary URL returns a 404 error, try the backup URL
            try:
                response = urlopen(url_latest, timeout=timeout)
            except urllib.error.HTTPError as e:
                _LOGGER.warning("Failed to download from both URLs: %s", e )
        else:
            _LOGGER.warning("An HTTP error occurreds: %s", e )
    except Exception as e:
        _LOGGER.warning("An error occurred: %s", e )
    # Extract the tarball

    return response

def safe_extract(tarinfo, path):
    # Implement your safety checks here.
    # If the member is safe to extract, return it.
    # If it's not safe (e.g., path traversal, symlink etc.), return None.
    return tarinfo

def get_intents(language: str, tag: str, dest_dir: Union[str, Path], timeout: int = None):
    """
    Returns directory of downloaded intent.
    """
    dest_dir = Path(dest_dir)
    intent_dir = dest_dir / f"intent_{language}"
    intent_cache_dir = dest_dir / f"intent_{language}/cache"

    for fname in os.listdir(Path(intent_dir)):
        if fname.endswith('.yaml'):
            _LOGGER.debug("Intents are already downloaded.")
            break
    else:
        # do stuff if a file .yaml doesn't exist.

        if intent_dir.is_dir():
            # Remove model directory if it already exists
            shutil.rmtree(intent_dir)

        dest_dir.mkdir(parents=True, exist_ok=True)
        intent_dir.mkdir(parents=True, exist_ok=True)
        intent_cache_dir.mkdir(parents=True, exist_ok=True)
        _LOGGER.debug("Dest_dir is %s and the intent_dir is: %s", dest_dir, intent_dir )

        url, url_latest = get_intents_version(tag)

        response = download_intents(url, url_latest, timeout=timeout)


        total_size = int(response.headers.get('content-length', 0))
        block_size = 8192
        file_size_dl = 0
        file_name = url.split('/')[-1]
        _LOGGER.info("Using intent version: %s, from url: %s", tag, url)
        with open(file_name, 'wb') as file:
            with Bar('Downloading Intents...', max=total_size, fill='#', suffix='%(percent).1f%% - %(elapsed_td)s') as bar:

                while True:
                    buffer = response.read(block_size)
                    if not buffer:
                        break

                    file.write(buffer)
                    file_size_dl += len(buffer)
                    bar.next(len(buffer))


        # Extract the contents with progress bar
        with tarfile.open(file_name) as tar:
            num_files = len(tar.getmembers())
            with Bar('Extracting...', max=num_files, fill='#', suffix='%(percent).1f%% - %(elapsed_td)s') as bar:
                for file in tar.getmembers():
                    tar.extract(file, path=intent_cache_dir, filter=safe_extract)
                    bar.next()
        tar.close()
        extracted_folder = [f for f in os.listdir(intent_cache_dir) if os.path.isdir(os.path.join(intent_cache_dir, f))]

        src_sentences_dir = intent_cache_dir / extracted_folder[0] / f"sentences/{language}"
        src_responses_dir = intent_cache_dir / extracted_folder[0] / f"responses/{language}"

        copy_files(src_sentences_dir, intent_dir)
        copy_files(src_responses_dir, intent_dir)

        delete_exceptions(intent_dir)

        shutil.rmtree(intent_cache_dir)
        _LOGGER.debug("Temporal cache directory is removed: %s", intent_cache_dir)

    return



