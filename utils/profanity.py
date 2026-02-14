import re
from typing import Iterable, List, Tuple

BADWORDS = {
    "idiot", "arsch", "scheisse", "scheiße", "fuck", "fick", "bastard", "hurensohn",
}


def _normalize(text: str) -> str:
    t = text.lower()
    t = (
        t.replace("ä", "ae")
         .replace("ö", "oe")
         .replace("ü", "ue")
         .replace("ß", "ss")
    )
    return t


def contains_profanity(text: str) -> bool:
    if not text:
        return False
    t = _normalize(text)
    for w in BADWORDS:
        ww = re.escape(_normalize(w))
        if re.search(rf"\b{ww}\b", t):
            return True
    return False


def validate_text_fields(
    data: dict,
    fields: Iterable[str],
) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    for field in fields:
        value = data.get(field)
        if isinstance(value, str) and contains_profanity(value):
            errors.append(
                f"Bitte keine Schimpfwörter im Feld „{field}“ verwenden."
            )
    return (len(errors) == 0), errors
