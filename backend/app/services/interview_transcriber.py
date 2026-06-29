from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)
class InterviewTranscriber:

    # Recording filename template — matches what the frontend saves.
    RECORDING_TEMPLATE = "question_{n}.webm"

    def __init__(
        self,
        model_size: str = "tiny",
        device: str | None = None,
    ) -> None:
        self.model_size = model_size
        self.device = device
        self._model: Any = None  # lazy-loaded on first use

    # ── Private helpers ───────────────────────────────────────────────────────

    def _load_model(self) -> Any:
        """Load the Whisper model on first call; return cached model thereafter."""
        if self._model is None:
            try:
                import whisper  # type: ignore[import]
            except ImportError as exc:
                raise ImportError(
                    "The 'openai-whisper' package is required.  "
                    "Install it with:  pip install openai-whisper"
                ) from exc

            logger.info(
                "Loading Whisper model '%s' (device=%s) …",
                self.model_size,
                self.device or "auto",
            )
            load_kwargs: dict[str, Any] = {}
            if self.device is not None:
                load_kwargs["device"] = self.device

            self._model = whisper.load_model(self.model_size, **load_kwargs)
            logger.info("Whisper model loaded.")

        return self._model

    def _transcribe_file(self, audio_path: str) -> str:
        model = self._load_model()
        logger.info("Transcribing: %s", audio_path)
        result = model.transcribe(
            audio_path,
            fp16=False,
            language="en",
        )
        transcript: str = result.get("text", "").strip()
        logger.info(
            "Transcription complete for %s (%d chars)",
            os.path.basename(audio_path),
            len(transcript),
        )
        return transcript

    # ── Public API ────────────────────────────────────────────────────────────

    def transcribe_session(
        self,
        session_path: str,
        question_count: int = 5,
    ) -> list[dict[str, Any]]:

        if not os.path.isdir(session_path):
            raise ValueError(
                f"Session directory does not exist: {session_path!r}"
            )

        results: list[dict[str, Any]] = []

        for n in range(1, question_count + 1):
            filename = self.RECORDING_TEMPLATE.format(n=n)
            audio_path = os.path.join(session_path, filename)

            # ── Skip missing files gracefully ─────────────────────────────
            if not os.path.exists(audio_path):
                logger.debug("Recording not found, skipping: %s", audio_path)
                continue

            if os.path.getsize(audio_path) == 0:
                logger.warning("Recording is empty (0 bytes), skipping: %s", audio_path)
                continue

            # ── Transcribe ────────────────────────────────────────────────
            try:
                transcript = self._transcribe_file(audio_path)
            except Exception as exc:
                # Log and skip so a single bad file doesn't abort the session.
                logger.error(
                    "Failed to transcribe %s: %s",
                    audio_path,
                    exc,
                    exc_info=True,
                )
                continue

            results.append({
                "question": n,
                "filename": filename,
                "transcript": transcript,
            })

        # ── Persist to disk ───────────────────────────────────────────────
        output_path = os.path.join(session_path, "transcripts.json")
        with open(output_path, "w", encoding="utf-8") as fh:
            json.dump(results, fh, indent=2, ensure_ascii=False)

        logger.info(
            "Transcription complete — %d/%d questions transcribed.  "
            "Saved to: %s",
            len(results),
            question_count,
            output_path,
        )

        return results