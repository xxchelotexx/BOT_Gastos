import os
import logging
import subprocess

logger = logging.getLogger(__name__)


def transcribe_voice(ogg_path: str) -> str | None:
    """
    Transcribe audio con faster-whisper corriendo localmente.
    Modelo 'tiny' o 'base': rápido, liviano, suficiente para frases cortas.
    """
    wav_path = ogg_path.replace(".ogg", ".wav")

    try:   
    # Para correr en windows/Local
    #     subprocess.run(
    # [
    #     r"C:\ffmpeg\bin\ffmpeg.exe",
    #     "-y",
    #     "-i",
    #     ogg_path,
    #     "-ar",
    #     "16000",
    #     "-ac",
    #     "1",
    #     wav_path,
    # ],
    # check=True,
    # capture_output=True,
    #     )
        subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            ogg_path,
            "-ar",
            "16000",
            "-ac",
            "1",
            wav_path,
        ],
        check=True,
        capture_output=True,
    )
    except Exception as e:
        logger.error(f"Error convirtiendo audio: {e}")
        return None

    try:
        from faster_whisper import WhisperModel

        model_size = os.environ.get("WHISPER_MODEL", "tiny")
        model = WhisperModel(model_size, device="cpu", compute_type="int8")

        segments, _ = model.transcribe(wav_path, language="es")
        text = " ".join(segment.text.strip() for segment in segments)
        return text.strip() or None

    except Exception as e:
        logger.error(f"Error en transcripción local: {e}")
        return None

    finally:
        for path in [ogg_path, wav_path]:
            try:
                os.remove(path)
            except Exception:
                pass
