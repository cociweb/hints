import logging
import os
from pathlib import Path
from urllib.request import urlopen
import shutil
from progress.bar import Bar

_LOGGER = logging.getLogger(__name__)
def download_custom_model(model_url_prefix: str, dest_dir: Path, purge: bool = False, timeout: int = None) -> bool:
    """
    Downloads custom model files: model.bin, vocabulary.txt, config.json and hash.json directly to destination directory.

    Returns directory of downloaded custom model.
    """

    result: bool = False
    dest_dir = Path(dest_dir)
    model_dir = Path(dest_dir / "custom")



    if model_dir.is_dir() and purge:
        # Remove model directory if it already exists
        shutil.rmtree(model_dir)


    dest_dir.mkdir(parents=True, exist_ok=True)
    model_dir.mkdir(parents=True, exist_ok=True)

    _LOGGER.debug("Dest_dir is %s and the model_dir is %s", dest_dir, model_dir )

    filelist = ["model.bin", "vocabulary.txt", "config.json"]

    for fname in filelist:
        model_url = model_url_prefix + fname
        _LOGGER.info("%s", model_url)
        try:
            with urlopen(model_url, timeout=timeout) as d, open(model_dir / fname, "wb") as savefile:
                data = d.read()
                bar = Bar('Downloading ' + fname, max=len(data), fill='#', suffix='%(percent).1f%% - %(elapsed_td)s')
                for i in range(len(data)):
                    savefile.write(data[i:i+1])
                    bar.next()
                bar.finish()
                savefile.close()
                _LOGGER.info("%s is downloaded into %s from url: %s", fname, model_dir, model_url )
        except Exception as e:
            _LOGGER.warning("Download failed on  %s from %s! Info: %s", fname, model_url, e)

        try:
            chmod_files(model_dir, fname)
        except Exception as e:
            _LOGGER.warning("Failed to chmod file: %s. Info: %s", fname, e)

    if check_files(model_dir, filelist):
        result = True

    return result

def check_files(model_dir, filelist):
    for filename in filelist:
        if not os.path.isfile(os.path.join(model_dir, filename)):
            return False
    return True

def chmod_files(model_dir, filelist):
    for fname in filelist:
        os.chmod(os.path.join(model_dir, fname), 0o755)
