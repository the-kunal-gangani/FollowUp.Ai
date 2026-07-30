import os
from faster_whisper import WhisperModel

_model_cache = {}


def _resolve_model_name(model_size, language):
    if language == "en" and not model_size.endswith(".en"):
        return f"{model_size}.en"
    return model_size


def get_model(model_size="base", language="en"):
    resolved = _resolve_model_name(model_size, language)
    if resolved not in _model_cache:
        _model_cache[resolved] = WhisperModel(
            resolved,
            device="cpu",
            compute_type="int8",
            cpu_threads=max(os.cpu_count() or 4, 1),
        )
    return _model_cache[resolved]


def transcribe_audio(audio_path, model_size="base", language="en", progress_callback=None):
    model = get_model(model_size, language)

    transcribe_kwargs = {
        "beam_size": 1,
        "vad_filter": True,
        "vad_parameters": {"min_silence_duration_ms": 500},
    }
    if language:
        transcribe_kwargs["language"] = language

    segments, info = model.transcribe(audio_path, **transcribe_kwargs)

    text_parts = []
    for segment in segments:
        text_parts.append(segment.text.strip())
        if progress_callback:
            progress_callback(segment.end, info.duration)

    return " ".join(text_parts).strip(), info.language