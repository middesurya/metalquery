"""
Visualization Config Validator - Security and correctness validation.
"""

from typing import Dict, Tuple, Any, List
import logging

logger = logging.getLogger(__name__)


class VizConfigValidator:
    """
    Validates chart configurations for security and correctness.
    Prevents XSS, code injection, and ensures valid structure.
    """

    ALLOWED_CHART_TYPES = {
        "line", "bar", "pie", "progress_bar", "area",
        "scatter", "kpi_card", "metric_grid", "table"
    }

    MAX_DATA_POINTS = 1000
    MAX_SERIES = 10
    MAX_STRING_LENGTH = 500
    MAX_RECURSION_DEPTH = 10

    # Dangerous patterns that could indicate XSS or code injection
    DANGEROUS_PATTERNS = [
        # JavaScript injection
        "javascript:", "vbscript:", "data:",
        # Event handlers
        "onclick", "onerror", "onload", "onmouseover", "onfocus", "onblur",
        "onkeydown", "onkeyup", "onchange", "onsubmit", "onmouseenter",
        # Script tags
        "<script", "</script>", "<iframe", "</iframe>",
        # JS execution
        "eval(", "Function(", "setTimeout(", "setInterval(",
        "new Function", "constructor(",
        # Prototype pollution
        "__proto__", "prototype", "constructor",
        # DOM manipulation
        "document.", "window.", "alert(", "confirm(", "prompt(",
        "innerHTML", "outerHTML", "insertAdjacentHTML",
        # URL manipulation
        "location.", "href=", "src=",
        # Template literals that could execute
        "${", "{{", "}}"
    ]

    # Allowed keys in config objects
    ALLOWED_CONFIG_KEYS = {
        'type', 'data', 'options', 'generated'
    }

    ALLOWED_OPTION_KEYS = {
        'title', 'xAxis', 'yAxis', 'lines', 'bars', 'tooltip', 'legend',
        'animation', 'grid', 'dataKey', 'nameKey', 'colors', 'innerRadius',
        'outerRadius', 'label', 'fill', 'fillOpacity', 'unit', 'thresholds',
        'trend', 'color', 'columns', 'strokeWidth', 'name', 'stroke', 'radius'
    }

    def validate(self, config: Dict) -> Tuple[bool, str]:
        """
        Validate chart configuration.

        Args:
            config: Chart configuration dict

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not config:
            return False, "Empty configuration"

        if not isinstance(config, dict):
            return False, "Configuration must be a dictionary"

        # Check chart type
        chart_type = config.get("type")
        if chart_type not in self.ALLOWED_CHART_TYPES:
            return False, f"Invalid chart type: {chart_type}"

        # Check data size
        data = config.get("data")
        if data:
            if isinstance(data, list):
                if len(data) > self.MAX_DATA_POINTS:
                    return False, f"Too many data points: {len(data)} (max: {self.MAX_DATA_POINTS})"
            elif isinstance(data, dict):
                # For gauge/kpi_card single value data
                pass

        # Check for dangerous patterns
        dangerous = self._find_dangerous_patterns(config)
        if dangerous:
            logger.warning(f"Dangerous patterns found in chart config: {dangerous}")
            return False, "Invalid content detected in configuration"

        # Check string lengths
        long_strings = self._find_long_strings(config)
        if long_strings:
            return False, f"String value too long in: {long_strings[0]}"

        # Validate structure
        structure_valid, structure_error = self._validate_structure(config)
        if not structure_valid:
            return False, structure_error

        return True, "Valid"

    def _find_dangerous_patterns(self, obj: Any, depth: int = 0) -> List[str]:
        """Recursively check for dangerous patterns."""
        if depth > self.MAX_RECURSION_DEPTH:
            return []

        found = []

        if isinstance(obj, str):
            obj_lower = obj.lower()
            for pattern in self.DANGEROUS_PATTERNS:
                if pattern.lower() in obj_lower:
                    found.append(pattern)

        elif isinstance(obj, dict):
            for key, value in obj.items():
                # Check key
                if isinstance(key, str):
                    key_lower = key.lower()
                    for pattern in self.DANGEROUS_PATTERNS:
                        if pattern.lower() in key_lower:
                            found.append(f"key:{pattern}")
                # Check value
                found.extend(self._find_dangerous_patterns(value, depth + 1))

        elif isinstance(obj, list):
            for item in obj:
                found.extend(self._find_dangerous_patterns(item, depth + 1))

        return found

    def _find_long_strings(self, obj: Any, path: str = "", depth: int = 0) -> List[str]:
        """Find strings that exceed maximum length."""
        if depth > self.MAX_RECURSION_DEPTH:
            return []

        found = []

        if isinstance(obj, str):
            if len(obj) > self.MAX_STRING_LENGTH:
                found.append(path or "root")

        elif isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                found.extend(self._find_long_strings(value, new_path, depth + 1))

        elif isinstance(obj, list):
            for i, item in enumerate(obj[:100]):  # Limit iteration
                new_path = f"{path}[{i}]"
                found.extend(self._find_long_strings(item, new_path, depth + 1))

        return found

    def _validate_structure(self, config: Dict) -> Tuple[bool, str]:
        """Validate config structure."""
        # Must have type
        if 'type' not in config:
            return False, "Missing 'type' field"

        # Options must be dict if present
        options = config.get('options')
        if options is not None and not isinstance(options, dict):
            return False, "'options' must be a dictionary"

        # Data validation based on type
        chart_type = config.get('type')
        data = config.get('data')

        if chart_type in ('line', 'bar', 'area', 'pie', 'table'):
            if data is not None and not isinstance(data, list):
                return False, f"'{chart_type}' chart requires array data"

        if chart_type in ('progress_bar', 'kpi_card'):
            if data is not None and not isinstance(data, (dict, list)):
                return False, f"'{chart_type}' chart requires object or array data"

        return True, "Valid"

    def sanitize(self, config: Dict) -> Dict:
        """
        Sanitize config by removing dangerous content.

        Args:
            config: Chart configuration

        Returns:
            Sanitized configuration
        """
        if not config:
            return config

        return self._sanitize_recursive(config)

    def _sanitize_recursive(self, obj: Any, depth: int = 0) -> Any:
        """Recursively sanitize object."""
        if depth > self.MAX_RECURSION_DEPTH:
            return obj

        if isinstance(obj, str):
            sanitized = obj
            # Remove dangerous patterns
            for pattern in self.DANGEROUS_PATTERNS:
                sanitized = sanitized.replace(pattern, '')
                sanitized = sanitized.replace(pattern.lower(), '')
            # Truncate if too long
            if len(sanitized) > self.MAX_STRING_LENGTH:
                sanitized = sanitized[:self.MAX_STRING_LENGTH]
            return sanitized

        elif isinstance(obj, dict):
            return {
                self._sanitize_recursive(k, depth + 1): self._sanitize_recursive(v, depth + 1)
                for k, v in obj.items()
            }

        elif isinstance(obj, list):
            # Limit array size
            truncated = obj[:self.MAX_DATA_POINTS]
            return [self._sanitize_recursive(item, depth + 1) for item in truncated]

        return obj

    def validate_and_sanitize(self, config: Dict) -> Tuple[bool, Dict, str]:
        """
        Validate and sanitize config in one pass.

        Returns:
            Tuple of (is_valid, sanitized_config, message)
        """
        # First sanitize
        sanitized = self.sanitize(config)

        # Then validate
        is_valid, message = self.validate(sanitized)

        return is_valid, sanitized, message
