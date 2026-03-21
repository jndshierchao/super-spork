---
name: tencent-cloud-asr
description: This skill should be used when users want to use Tencent Cloud ASR (Automatic Speech Recognition) for voice-to-text conversion or voice dialogue development.
---

# Tencent Cloud ASR Skill

## Purpose

Provide capabilities for voice-to-text conversion and voice dialogue development using Tencent Cloud ASR API.

## When to Use This Skill

Use this skill when:
- User asks to convert audio to text using Tencent Cloud ASR
- User wants to implement voice dialogue or voice assistant
- User needs to process audio files with speech recognition
- User wants to integrate Tencent Cloud ASR into their application

## How to Use

### Prerequisites

1. **Get Tencent Cloud Credentials**:
   - SecretId and SecretKey from [Tencent Cloud Console](https://console.cloud.tencent.com/cam/capi)
   - Enable ASR service at [Tencent Cloud ASR](https://console.cloud.tencent.com/asr)

2. **Install Dependencies**:
   ```bash
   pip install tencentcloud-sdk-python-core
   # or
   npm install tencentcloud-sdk-nodejs
   ```

### Available Scripts

#### 1. Audio Transcription (scripts/asr_client.py)

Use `scripts/asr_client.py` for batch audio file transcription.

**Python Usage:**
```python
from scripts.asr_client import TencentASR

# Initialize with your credentials
asr = TencentASR(secret_id="your_secret_id", secret_key="your_secret_key")

# Transcribe audio file
result = asr.recognize("path/to/audio.wav", engine_type="16k")
print(result)
```

#### 2. Real-time ASR (scripts/realtime_asr.py)

Use `scripts/realtime_asr.py` for real-time speech recognition.

**Features:**
- Stream audio input
- Real-time text output
- Support for dialogue mode

### Configuration Options

| Parameter | Description | Values |
|-----------|-------------|--------|
| engine_type | Audio engine | `16k` (16kHz), `8k` (8kHz) |
| speaker_diarization | Speaker separation | `0` (disable), `1` (enable) |
| word_info | Word-level timestamps | `0` (disable), `1` (enable) |

### Voice Dialogue Development

For building voice dialogue systems:

1. **ASR Module** - Convert speech to text
2. **NLP Module** - Process text intent (can use Tencent Cloud TI-ONE or other NLP services)
3. **TTS Module** - Convert response to speech (Tencent Cloud TTS)
4. **Dialog Manager** - Handle conversation flow

### Reference Documentation

See `references/tencent_asr_api.md` for detailed API documentation.

## Supported Audio Formats

- PCM/WAV (recommended)
- MP3
- AMR
- AAC
- OGG

## Rate Limits

- Synchronous recognition: 60 requests/minute
- File size limit: 60MB
- Audio duration limit: 60 seconds (for sync)
