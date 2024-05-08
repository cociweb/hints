import argparse
import logging
import json
from . import __all__

#_LOGGER = logging.getLogger(__name__)
def core_args():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--model",
        required=True,
        help="Name of faster-whisper model to use",
    )
    parser.add_argument(
        "--model-dir",
        required=True,
        default="./model",
        help="Data directory to check for downloaded models.",
    )
    parser.add_argument(
        "--proto",
        required=True,
        default="tcp://0.0.0.0:10300",
        help="unix:// or tcp://"
    )
    parser.add_argument(
        "--local-files-only",
        action="store_true",
        help="faster-whisper: If True, avoid downloading the file and return the path to the local cached file if it exists."
    )
    parser.add_argument(
        "--custom-model-url",
        help="Full URL (with https:// prefix) of a remote directory or Huggingface repository(author/repo) or a single folder in the model-dir. In the remote directory model.bin, vocabulary.txt, config.json, are required!",
    )
    parser.add_argument(
        "--timeout",
        help="Set timeout for the download activity. Default is 30 seconds",
    )


# -----------------------------------------------------------------------------

    parser.add_argument(
        "--data-dir",
        required=True,
        default="./data",
        help="Data directory for the downloadables",
    )
    parser.add_argument(
        "--language",
        default="en",
        help="Default language to set for spell-check",
    )
    parser.add_argument(
        "--spellcheck",
        action="store_true",
        help="Default alphabet for spell-checking",
    )
    parser.add_argument(
        "--alphabet",
        help="Default alphabet for spell-checking",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Log DEBUG messages"
    )
    parser.add_argument(
        "--tag",
        default="latest",
        help="Tag name for the versions of the intents. Default is the latest released tag. 'main' can be also used for the master branch."
    )
    parser.add_argument(
        "--ha-api-url",
        help="Home Assistant API URL"
    )
    parser.add_argument(
        "--token",
        help="Long-lived access token"
    )
    parser.add_argument(
        "--hassil-iterations",
        default=1000,
        help="Limit number of sentences per intent"
    )
    parser.add_argument(
        "--force-generate-intent",
        action="store_true",
        help="Force to initialize the data structure"
    )
    parser.add_argument(
        "--force-generate-spellcheck",
        action="store_true",
        help="Force to initialize the data structure"
    )
    parser.add_argument(
        "--force-download-model",
        action="store_true",
        help="Force to initialize the model structure"
    )
    parser.add_argument(
        "--log-format",
        default=logging.BASIC_FORMAT,
        help="Format for log messages"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=__all__[0],
        help="Print version and exit",
    )

    # Add more core arguments as needed
    args, _ = parser.parse_known_args()
    return args

def whisper_args():

    '''
    --audio "audio.wav" --language "en" --task "transcribe"
    --beam_size 5 --best_of 5 --patience 1 --length_penalty 1 
    --repetition_penalty 1 --no_repeat_ngram_size 0 --temperature 0.0 0.2 0.4 0.6 0.8 1.0 
    --compression_ratio_threshold 2.4 --log_prob_threshold -1.0 --no_speech_threshold 0.6 
    --condition_on_previous_text True --prompt_reset_on_temperature 0.5 --initial_prompt "Hello" 
    --prefix "Hi" --suppress_blank True --suppress_tokens -1 --without_timestamps False 
    --max_initial_timestamp 1.0 --word_timestamps False 
    --prepend_punctuations "\"'“¿([{-" --append_punctuations "\"'.。,，!！?？:：”)]}、" 
    --vad_filter False --vad_parameters '{"threshold": 0.6, "min_speech_duration_ms": 300, "max_speech_duration_s": 1000.0, "min_silence_duration_ms": 2500, "window_size_samples": 2048, "speech_pad_ms": 500}' 
    --max_new_tokens 100 --chunk_length 10 --clip_timestamps "0" --hallucination_silence_threshold 0.5 
    --language_detection_threshold 0.5 --language_detection_segments 1
    '''

    # Create argument parser
    parser = argparse.ArgumentParser()

    # transcribe params
    parser.add_argument("--audio", type=str, help="Path to the input file (or a file-like object), or the audio waveform.")
    parser.add_argument("-o", "--output", help="Output .srt file")
    parser.add_argument('--language', type=str, default=None,
                        help='the language spoken in the audio')
    parser.add_argument('--task', type=str, default='transcribe',
                        help='task to execute (transcribe or translate)')
    parser.add_argument('--beam_size', type=int, default=5,
                        help='beam size to use for decoding')
    parser.add_argument('--best_of', type=int, default=5,
                        help='number of candidates when sampling with non-zero temperature')
    parser.add_argument('--patience', type=float, default=1,
                        help='beam search patience factor')
    parser.add_argument('--length_penalty', type=float,
                        default=1, help='exponential length penalty constant')
    parser.add_argument('--repetition_penalty', type=float,
                        default=1, help='exponential repetition penalty constant')
    parser.add_argument('-- no_repeat_ngram_size', type=int,
                        default=0, help='n-gram size for no-repeat-ngram constant')
    parser.add_argument('--temperature', type=float, nargs='+', default=[
                        0.0, 0.2, 0.4, 0.6, 0.8, 1.0], help='temperature for sampling. It can be a tuple of temperatures')
    parser.add_argument('--compression_ratio_threshold', type=float, default=2.4,
                        help='if the gzip compression ratio is above this value, treat as failed')
    parser.add_argument('--log_prob_threshold', type=float, default=-1.0,
                        help='if the average log probability over sampled tokens is below this value, treat as failed')
    parser.add_argument('--no_speech_threshold', type=float, default=0.6,
                        help='if the no_speech probability is higher than this value AND the average log probability over sampled tokens is below `log_prob_threshold`, consider the segment as silent')
    parser.add_argument('--condition_on_previous_text', type=bool, default=True,
                        help='if True, the previous output of the model is provided as a prompt for the next window; disabling may make the text inconsistent across windows, but the model becomes less prone to getting stuck in a failure loop')
    parser.add_argument('--prompt_reset_on_temperature', type=float,
                        default=0.5, help='exponential repetition penalty constant')
    parser.add_argument('--initial_prompt', type=str, default=None,
                        help='optional text to provide as a prompt for the first window')
    parser.add_argument('--prefix', type=str, default=None,
                        help='optional text to provide as a prefix for the first window')
    parser.add_argument('--suppress_blank', type=bool, default=True,
                        help='suppress blank outputs at the beginning of the sampling')
    parser.add_argument('--suppress_tokens', type=int, nargs='+',
                        default=[-1], help='list of token IDs to suppress. -1 will suppress a default set of symbols as defined in the model config.json file')
    parser.add_argument('--without_timestamps', type=bool,
                        default=False, help='only sample text tokens')
    parser.add_argument('--max_initial_timestamp', type=float, default=1.0,
                        help='the initial timestamp cannot be later than this')
    parser.add_argument('--word_timestamps', type=bool, default=False,
                        help='extract word-level timestamps using the cross-attention pattern and dynamic time warping, and include the timestamps for each word in each segment')
    parser.add_argument('--prepend_punctuations', type=str,
                        default='\"\'“¿([{-', help='if word_timestamps is True, merge these punctuation symbols with the next word')
    parser.add_argument('--append_punctuations', type=str, default='\"\'.。,，!！?？:：”)]}、',
                        help='if word_timestamps is True, merge these punctuation symbols with the previous word')
    parser.add_argument('--vad_filter', type=bool, default=False,
                        help='Enable the voice activity detection (VAD) to filter out parts of the audio without speech. This step is using the Silero VAD model https://github.com/snakers4/silero-vad.')
    parser.add_argument('--max_new_tokens', type=int,
                        default=None, help='Maximum number of new tokens to generate')
    parser.add_argument('--chunk_length', type=int,
                        default=None, help='Maximum length of audio chunks')
    parser.add_argument('--clip_timestamps', type=str, default=0,
                        help='the initial timestamp cannot be later than this')
    parser.add_argument('--hallucination_silence_threshold', type=float, default=None,
                        help='threshold for hallucination detection')
    parser.add_argument('--hotwords', type=str, default=None,
                        help='Hotwords for the model')
    parser.add_argument('--language_detection_threshold', type=float, default=None,
                        help='threshold for language detection')
    parser.add_argument('--language_detection_segments', type=int,
                        default=1, help='Maximum number of segments for language detection')
    parser.add_argument('--vad_parameters', type=json.loads, default=json.dumps({
                        "threshold": 0.5,
                        "min_speech_duration_ms": 250,
                        "max_speech_duration_s": float("inf"),
                        "min_silence_duration_ms": 2000,
                        "window_size_samples": 1024,
                        "speech_pad_ms": 400
                        }),
                        help='The VAD parameters as a JSON string')
    # WhisperModel params
    parser.add_argument('--model_size_or_path', type=str, default='base',
                        help='Size of the model to use (tiny, tiny.en, base, base.en, small, small.en, medium, medium.en, large-v1, or large-v2) or a path to a converted model directory. When a size is configured, the converted model is downloaded from the Hugging Face Hub.')
    parser.add_argument('--device', type=str, default='auto',
                        help='Device to use for computation ("cpu", "cuda", "auto").')
    parser.add_argument('--device_index', type=int, nargs='+', default=[
                        0], help='Device ID to use. The model can also be loaded on multiple GPUs by passing a list of IDs (e.g. [0, 1, 2, 3]). In that case, multiple transcriptions can run in parallel when transcribe() is called from multiple Python threads (see also num_workers).')
    parser.add_argument('--compute_type', type=str, default='default',
                        help='Type to use for computation. See https://opennmt.net/CTranslate2/quantization.html.')
    parser.add_argument('--cpu_threads', type=int, default=4,
                        help='Number of threads to use when running on CPU (4 by default). A non zero value overrides the OMP_NUM_THREADS environment variable.')
    parser.add_argument('--num_workers', type=int, default=1, help='When transcribe() is called from multiple Python threads, having multiple workers enables true parallelism when running the model (concurrent calls to self.model.generate() will run in parallel). This can improve the global throughput at the cost of increased memory usage.')
    parser.add_argument('--download_root', type=str, default=None,
                        help='Directory where the models should be saved. If not set, the models are saved in the standard Hugging Face cache directory.')
    parser.add_argument('--local_files_only', type=bool, default=False,
                        help='If True, avoid downloading the file and return the path to the local cached file if it exists.')


    # Add more core arguments as needed
    args, _ = parser.parse_known_args()
    return args