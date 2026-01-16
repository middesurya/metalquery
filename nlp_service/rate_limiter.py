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
from config import settings

@dataclass
class RateLimitConfig:
    """Rate limit configuration - reads from .env via settings."""
    requests_per_minute: int = settings.max_requests_per_minute
    tokens_per_minute: int = settings.max_tokens_per_minute
    max_output_tokens: int = settings.max_output_tokens


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
        
        # Check request limit - smarter wait time calculation
        if requests_used >= self.config.requests_per_minute:
            self.blocked_requests += 1
            if self.request_window:
                # Calculate minimum wait time: when will the NEXT slot be available?
                # Instead of waiting for the oldest request to expire, wait for enough requests to clear
                needed_slots = requests_used - self.config.requests_per_minute + 1
                wait_time = max(1, 60 - (time.time() - self.request_window[needed_slots - 1][0]))
            else:
                wait_time = 1  # Minimum wait
            logger.warning(f"⚠️ Rate limit: {requests_used}/{self.config.requests_per_minute} requests. Wait {wait_time:.1f}s")
            return False, f"Rate limit exceeded. Please wait {wait_time:.0f} seconds."

        # Check token limit - smarter wait time calculation
        if tokens_used + estimated_tokens > self.config.tokens_per_minute:
            if self.token_window:
                # Calculate minimum wait time: when will enough tokens free up?
                # Find the earliest point where tokens_used < limit
                needed_tokens = tokens_used + estimated_tokens - self.config.tokens_per_minute
                cumulative = 0
                wait_time = 1  # Minimum wait

                for i, (timestamp, token_count) in enumerate(self.token_window):
                    cumulative += token_count
                    if cumulative >= needed_tokens:
                        wait_time = max(1, 60 - (time.time() - timestamp))
                        break

                self.blocked_requests += 1
                logger.warning(f"⚠️ Token limit: {tokens_used}/{self.config.tokens_per_minute} tokens. Wait {wait_time:.1f}s")
                return False, f"Token limit exceeded. Please wait {wait_time:.0f} seconds."
            else:
                # Window is empty - allow first request even if large, with warning
                if estimated_tokens > self.config.tokens_per_minute:
                    logger.warning(f"⚠️ Large request: {estimated_tokens} tokens exceeds {self.config.tokens_per_minute}/min limit, but allowing (window empty)")

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


def check_rate_limit(estimated_tokens: int = 300) -> Tuple[bool, str]:
    """Quick check if request can proceed. Default 300 tokens for typical query."""
    return get_rate_limiter().can_make_request(estimated_tokens)


def record_usage(input_tokens: int, output_tokens: int = 0):
    """Record token usage after request."""
    get_rate_limiter().record_request(input_tokens, output_tokens)
