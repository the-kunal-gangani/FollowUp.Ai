from faster_whisper import WhisperModel

_model_cache = {}


def get_model(model_size="base"):
    if model_size not in _model_cache:
        _model_cache[model_size] = WhisperModel(model_size, device="cpu", compute_type="int8")
    return _model_cache[model_size]


def transcribe_audio(audio_path, model_size="base", progress_callback=None):
    model = get_model(model_size)
    segments, info = model.transcribe(audio_path, beam_size=5)

    text_parts = []
    for segment in segments:
        text_parts.append(segment.text.strip())
        if progress_callback:
            progress_callback(segment.end, info.duration)

    return " ".join(text_parts).strip(), info.language