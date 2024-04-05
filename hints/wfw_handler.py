"""Event handler for clients of the server."""
import argparse
import asyncio
import logging
import os
import tempfile
import wave
import string
from typing import Optional

import faster_whisper
from wyoming.asr import Transcribe, Transcript
from wyoming.audio import AudioChunk, AudioStop
from wyoming.event import Event
from wyoming.info import Describe, Info
from wyoming.server import AsyncEventHandler
from .jams import jamspell_fix

_LOGGER = logging.getLogger(__name__)


class FasterWhisperEventHandler(AsyncEventHandler):
    """Event handler for clients."""

    def __init__(
        self,
        wyoming_info: Info,
        cli_args: argparse.Namespace,
        model: faster_whisper.WhisperModel,
        model_lock: asyncio.Lock,
        *args,
        initial_prompt: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.cli_args = cli_args
        self.wyoming_info_event = wyoming_info.event()
        self.model = model
        self.model_lock = model_lock
        self._wav_dir = tempfile.TemporaryDirectory()
        self._wav_path = os.path.join(self._wav_dir.name, "speech.wav")
        self._wav_file: Optional[wave.Wave_write] = None
        self.spellcheck = args.spellcheck
        self.jamspell_model_file = args.jamspell_model_file

    async def handle_event(self, event: Event) -> bool:
        if AudioChunk.is_type(event.type):
            chunk = AudioChunk.from_event(event)

            if self._wav_file is None:
                self._wav_file = wave.open(self._wav_path, "wb")
                self._wav_file.setframerate(chunk.rate)
                self._wav_file.setsampwidth(chunk.width)
                self._wav_file.setnchannels(chunk.channels)

            self._wav_file.writeframes(chunk.audio)
            return True

        if AudioStop.is_type(event.type):
            _LOGGER.debug(
                "Audio stopped. Transcribing with initial prompt=%s",
                self.initial_prompt,
            )
            assert self._wav_file is not None

            self._wav_file.close()
            self._wav_file = None

            async with self.model_lock:
                segments, _info = self.model.transcribe(
                    self._wav_path,
                    language = self.cli_args.language,
                    task = self.cli_args.task,
                    beam_size = self.cli_args.beam_size,
                    best_of = self.cli_args.best_of,
                    patience = self.cli_args.patience,
                    length_penalty = self.cli_args.length_penalty,
                    repetition_penalty = self.cli_args.repetition_penalty,
                    no_repeat_ngram_size = self.cli_args.no_repeat_ngram_size,
                    temperature = self.cli_args.temperature,
                    compression_ratio_threshold = self.cli_args.compression_ratio_threshold,
                    log_prob_threshold = self.cli_args.log_prob_threshold,
                    no_speech_threshold = self.cli_args.no_speech_threshold,
                    condition_on_previous_text = self.cli_args.condition_on_previous_text,
                    prompt_reset_on_temperature = self.cli_args.prompt_reset_on_temperature,
                    initial_prompt = self.cli_args.initial_prompt,
                    prefix = self.cli_args.prefix,
                    suppress_blank = self.cli_args.suppress_blank,
                    suppress_tokens = self.cli_args.suppress_tokens,
                    without_timestamps = self.cli_args.without_timestamps,
                    max_initial_timestamp = self.cli_args.max_initial_timestamp,
                    word_timestamps = self.cli_args.word_timestamps,
                    prepend_punctuations = self.cli_args.prepend_punctuations,
                    append_punctuations = self.cli_args.append_punctuations,
                    vad_filter = self.cli_args.vad_filter,
                    vad_parameters = self.cli_args.vad_parameters,
                    max_new_tokens = self.cli_args.max_new_tokens,
                    chunk_length = self.cli_args.chunk_length,
                    clip_timestamps = self.cli_args.clip_timestamps,
                    hallucination_silence_threshold = self.cli_args.hallucination_silence_threshold,
                    language_detection_threshold = self.cli_args.language_detection_threshold,
                    language_detection_segments = self.cli_args.language_detection_segments,
                )

            text = " ".join(segment.text for segment in segments)

            if self.spellcheck:
                text = jamspell_fix(self.jamspell_model_file, text.strip()).lower()
                text = text.translate(str.maketrans('', '', string.punctuation))

            _LOGGER.info(text)

            await self.write_event(Transcript(text=text).event())
            _LOGGER.debug("Completed request")

            # Reset
            self._language = self.cli_args.language

            return False

        if Transcribe.is_type(event.type):
            transcribe = Transcribe.from_event(event)
            if transcribe.language:
                self._language = transcribe.language
                _LOGGER.debug("Language set to %s", transcribe.language)
            return True

        if Describe.is_type(event.type):
            await self.write_event(self.wyoming_info_event)
            _LOGGER.debug("Sent info")
            return True

        return True
