# Groq API Rate Limiting - Implementation Summary

## Overview

Added rate limiting to prevent hitting Groq API limits on the free tier.

---

## Files Changed

| File | Change |
|------|--------|
| `nlp_service/rate_limiter.py` | **NEW** - Token bucket rate limiter |
| `nlp_service/config.py` | Added rate limit settings |
| `nlp_service/main.py` | Integrated rate limiter, added status endpoint |
| `.env.example` | Added rate limit variables |

---

## Configuration

Add to `.env`:
```ini
MAX_REQUESTS_PER_MINUTE=25
MAX_TOKENS_PER_MINUTE=5000
MAX_OUTPUT_TOKENS=256
```

| Setting | Default | Groq Limit | Purpose |
|---------|---------|------------|---------|
| `MAX_REQUESTS_PER_MINUTE` | 25 | 30 | API calls per minute |
| `MAX_TOKENS_PER_MINUTE` | 5000 | 6000 | Tokens per minute |
| `MAX_OUTPUT_TOKENS` | 256 | 512 (old) | Max response tokens |

---

## New API Endpoint

**GET** `/api/v1/rate-limit-status`

Returns current usage:
```json
{
  "requests_last_minute": 5,
  "tokens_last_minute": 2500,
  "requests_limit": 25,
  "tokens_limit": 5000,
  "requests_available": 20,
  "tokens_available": 2500
}
```

---

## Behavior

- **Rate limit exceeded** → Returns HTTP 429 with wait time
- **Logging** → Shows `Rate: X/25 req/min, Y/5000 tokens/min`
- **Token estimation** → ~4 characters per token
