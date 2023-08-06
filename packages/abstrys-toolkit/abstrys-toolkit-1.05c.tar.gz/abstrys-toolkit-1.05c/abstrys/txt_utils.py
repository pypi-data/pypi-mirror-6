# abstrys text utility functions and classes.
import re

def camel2snake(text, sep=r'_'):
    """Convert *text* from CamelCase (or camelCase) into snake_case."""
    rebounds = [r'([a-z])([A-Z])', r'([A-Z])([A-Z])']
    ophic_text = str(text)
    for b in rebounds:
        ophic_text = re.sub(b, (r'\g<1>'+ sep + r'\g<2>'), ophic_text)
    return ophic_text.lower()

