# Speech-to-Text Integration (Faster-Whisper)

The MetalQuery application uses **Faster-Whisper** for efficient local speech-to-text transcription.

---

## Overview

| Component | Value |
|-----------|-------|
| Library | `faster-whisper` (CTranslate2 backend) |
| Model | `small` (int8 quantization) |
| Device | CPU (optimized for speed/accuracy balance) |
| Max Audio | 10MB |

---

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    FRONTEND     │────▶│  DJANGO PROXY   │────▶│   NLP SERVICE   │
│  (Microphone)   │     │ /transcribe/    │     │ /api/v1/transcribe│
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                        │
                               │                        ▼
                        Security Boundary        ┌─────────────┐
                                                 │Faster-Whisper│
                                                 │  STT Model   │
                                                 └─────────────┘
```

**Security**: All audio transcription goes through Django to maintain the security boundary (React → Django → NLP Service).

---

## Requirements

### Python Dependencies

```bash
# In nlp_service/requirements.txt
faster-whisper>=1.0.0
ctranslate2==4.4.0  # Pinned: v4.5+ causes segfaults on Windows
numpy<2.0.0
python-multipart>=0.0.6
```

### System Requirements

- **FFmpeg** must be installed and available in system PATH
- Windows: Download from https://ffmpeg.org/download.html
- Linux: `apt install ffmpeg`
- macOS: `brew install ffmpeg`

---

## Windows Compatibility

The following dependency versions are pinned for Windows compatibility:

| Package | Version | Issue Fixed |
|---------|---------|-------------|
| `chromadb` | 0.5.3 | Rust bindings segfault in v1.x |
| `ctranslate2` | 4.4.0 | Segfaults with faster-whisper in v4.5+ |
| `onnxruntime` | 1.18.0 | DLL loading issues in v1.23+ |
| `numpy` | <2.0.0 | Breaks sentence-transformers |

Install with:
```bash
pip install chromadb==0.5.3 ctranslate2==4.4.0 onnxruntime==1.18.0 "numpy<2.0"
```

---

## API Endpoints

### Django Proxy (Port 8000)

```http
POST /api/chatbot/transcribe/
Content-Type: multipart/form-data

file: <audio_file>
```

### NLP Service (Port 8003)

```http
POST /api/v1/transcribe
Content-Type: multipart/form-data

file: <audio_file>
```

### Response

```json
{
  "success": true,
  "text": "Show OEE by furnace"
}
```

### Error Response

```json
{
  "success": false,
  "error": "Transcription failed: <error_message>"
}
```

---

## Frontend Usage

The voice recording feature is available in both `App.jsx` and `Chatbot.jsx`:

1. Click the microphone button to start recording
2. Speak your query
3. Click again to stop and transcribe
4. The transcribed text appears in the input field

```jsx
// Voice recording flow
const startRecording = async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const mediaRecorder = new MediaRecorder(stream);
  // ... recording logic
};

const sendAudio = async (audioBlob) => {
  const formData = new FormData();
  formData.append('file', audioBlob, 'recording.webm');

  const response = await fetch(`${API_URL}/api/chatbot/transcribe/`, {
    method: 'POST',
    body: formData,
  });
  // ... handle response
};
```

---

## Files

| File | Description |
|------|-------------|
| `nlp_service/stt_service.py` | Faster-Whisper service class |
| `nlp_service/main.py` | `/api/v1/transcribe` endpoint |
| `backend/chatbot/views.py` | Django proxy endpoint |
| `frontend/src/App.jsx` | Voice recording UI |
| `frontend/src/components/Chatbot.jsx` | Voice recording UI (chatbot) |

---

## Troubleshooting

### "STT service not available"
- Ensure `faster-whisper` and `ctranslate2` are installed
- Check that FFmpeg is in system PATH
- Verify model download completed (`~/.cache/huggingface/`)

### Segfault on Windows
- Downgrade ctranslate2: `pip install ctranslate2==4.4.0`
- Ensure numpy < 2.0: `pip install "numpy<2.0"`

### "No audio data"
- Check browser microphone permissions
- Ensure HTTPS or localhost (required for getUserMedia)

---

**Last Updated:** 2026-01-29
