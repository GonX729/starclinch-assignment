import re
import logging

logger = logging.getLogger(__name__)

# Matches {{ variable_name }} with optional whitespace inside braces
_VAR_PATTERN = re.compile(r"\{\{\s*(\w+)\s*\}\}")


def render_template(body: str, context: dict) -> str:
    """
    Replace {{ variable }} placeholders in a string using the provided context dict.

    - Supported variables: any key present in context (e.g. name, email, phone).
    - Missing variables are left as-is and a warning is logged.
    - Context values are always safely coerced to strings.

    Examples:
        render_template("Hello {{name}}!", {"name": "Alice"})  -> "Hello Alice!"
        render_template("Hi {{name}} ({{missing}})", {"name": "Bob"})
            -> "Hi Bob ({{missing}})"  # missing var kept intact
    """
    def _replace(match):
        key = match.group(1)
        if key in context:
            return str(context[key])
        logger.warning(f"render_template: variable '{{{{{key}}}}}' not found in context — leaving unchanged.")
        return match.group(0)   # return the original {{ key }} unchanged

    return _VAR_PATTERN.sub(_replace, body)
