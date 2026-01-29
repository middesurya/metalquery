# 🎙️ Speech-to-Text Service (Faster-Whisper)

The IGNIS application uses **Faster-Whisper** for efficient local speech-to-text transcription.

## Overview
- **Library**: `faster-whisper` (CTranslate2 backend)
- **Model**: `small` (int8 quantization)
- **Device**: CPU (optimized for speed/accuracy balance)

## requirements
- `faster-whisper`
- `ffmpeg` (must be installed on the system path)

## Usage
The service is exposed via the `NeMoSTT` class (kept named as `stt_service` singleton) in `nlp_service/stt_service.py`.

### Endpoint
`POST /api/v1/transcribe`
- Input: Audio file (multipart/form-data)
- Output: JSON `{"success": true, "text": "..."}`
