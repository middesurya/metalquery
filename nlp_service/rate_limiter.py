"""
Groq API Rate Limiter
Token bucket algorithm to stay within Groq's rate limits.

Groq Free Tier Limits:
- 30 requests/minute (RPM)
- 6,000 tokens/minute (TPM) 
- 14,400 requests/day
"""

import time
import logging
from dataclasses import dataclass
from typing import Tuple
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""
    requests_per_minute: int = 25  # Buffer below 30
    tokens_per_minute: int = 5000  # Buffer below 6000
    max_output_tokens: int = 256   # Reduced from 512


class GroqRateLimiter:
    """
    Token bucket rate limiter for Groq API.
    
    Features:
    - Sliding window for requests per minute
    - Token usage tracking per minute
    - Graceful backoff when limits approached
    """
    
    def __init__(self, config: RateLimitConfig = None):
        self.config = config or RateLimitConfig()
        
        # Sliding window: stores (timestamp, token_count) tuples
        self.request_window: deque = deque()
        self.token_window: deque = deque()
        
        # Stats
        self.total_requests = 0
        self.total_tokens = 0
        self.blocked_requests = 0
    
    def _clean_old_entries(self):
        """Remove entries older than 60 seconds."""
        current_time = time.time()
        cutoff = current_time - 60
        
        # Clean request window
        while self.request_window and self.request_window[0][0] < cutoff:
            self.request_window.popleft()
        
        # Clean token window
        while self.token_window and self.token_window[0][0] < cutoff:
            self.token_window.popleft()
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count from text.
        Rough estimate: ~4 characters per token for English.
        """
        if not text:
            return 0
        return max(1, len(text) // 4)
    
    def get_current_usage(self) -> Tuple[int, int]:
        """Get current requests and tokens used in the last minute."""
        self._clean_old_entries()
        
        requests_used = len(self.request_window)
        tokens_used = sum(t[1] for t in self.token_window)
        
        return requests_used, tokens_used
    
    def can_make_request(self, estimated_tokens: int = 0) -> Tuple[bool, str]:
        """
        Check if a request can be made within rate limits.
        
        Args:
            estimated_tokens: Estimated token usage for the request
            
        Returns:
            Tuple of (allowed, reason)
        """
        self._clean_old_entries()
        
        requests_used, tokens_used = self.get_current_usage()
        
        # Check request limit
        if requests_used >= self.config.requests_per_minute:
            self.blocked_requests += 1
            wait_time = 60 - (time.time() - self.request_window[0][0])
            logger.warning(f"⚠️ Rate limit: {requests_used}/{self.config.requests_per_minute} requests. Wait {wait_time:.1f}s")
            return False, f"Rate limit exceeded. Please wait {wait_time:.0f} seconds."
        
        # Check token limit
        if tokens_used + estimated_tokens > self.config.tokens_per_minute:
            self.blocked_requests += 1
            wait_time = 60 - (time.time() - self.token_window[0][0])
            logger.warning(f"⚠️ Token limit: {tokens_used}/{self.config.tokens_per_minute} tokens. Wait {wait_time:.1f}s")
            return False, f"Token limit exceeded. Please wait {wait_time:.0f} seconds."
        
        return True, "OK"
    
    def record_request(self, input_tokens: int, output_tokens: int = 0):
        """Record a completed request with its token usage."""
        current_time = time.time()
        total_tokens = input_tokens + output_tokens
        
        self.request_window.append((current_time, 1))
        self.token_window.append((current_time, total_tokens))
        
        self.total_requests += 1
        self.total_tokens += total_tokens
        
        requests_used, tokens_used = self.get_current_usage()
        logger.info(f"📊 Rate: {requests_used}/{self.config.requests_per_minute} req/min, "
                   f"{tokens_used}/{self.config.tokens_per_minute} tokens/min")
    
    def get_stats(self) -> dict:
        """Get rate limiter statistics."""
        requests_used, tokens_used = self.get_current_usage()
        
        return {
            "requests_last_minute": requests_used,
            "tokens_last_minute": tokens_used,
            "requests_limit": self.config.requests_per_minute,
            "tokens_limit": self.config.tokens_per_minute,
            "total_requests": self.total_requests,
            "total_tokens": self.total_tokens,
            "blocked_requests": self.blocked_requests,
            "requests_available": self.config.requests_per_minute - requests_used,
            "tokens_available": self.config.tokens_per_minute - tokens_used,
        }


# Global instance
_rate_limiter: GroqRateLimiter = None


def get_rate_limiter() -> GroqRateLimiter:
    """Get singleton rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = GroqRateLimiter()
    return _rate_limiter


def check_rate_limit(estimated_tokens: int = 500) -> Tuple[bool, str]:
    """Quick check if request can proceed."""
    return get_rate_limiter().can_make_request(estimated_tokens)


def record_usage(input_tokens: int, output_tokens: int = 0):
    """Record token usage after request."""
    get_rate_limiter().record_request(input_tokens, output_tokens)
