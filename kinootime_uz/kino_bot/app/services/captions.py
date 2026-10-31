"""Izoh (caption) va fayl nomidan toza sarlavha/tavsif ajratib olish."""
import re

_URL = re.compile(r"(https?://\S+|www\.\S+|\b(?:t|telegram)\.me/\S+)", re.I)
_MENTION = re.compile(r"@\w+")
_TAG = re.compile(r"#\w+")
_FORMAT = re.compile(
    r"</?(?:b|strong|i|em|u|s|strike|del|code|pre|blockquote|a)\b[^>]*>|[*_~`]+",
    re.I,
)
_EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF\u2300-\u23FF\u2460-\u27BF\u2900-\u297F\u2B00-\u2BFF"
    "\uFE00-\uFE0F\u200D\u20E3\u00A9\u00AE]+")
_TECH = re.compile(
    r"\b(?:\d{3,4}p|x26[45]|h\.?26[45]|hevc|web[- ]?dl|webrip|bluray|brrip|bdrip|hdrip|hdtv|dvdrip|"
    r"hdcam|camrip|aac|ac3|dts|10bit|mkv|mp4|avi)\b", re.I)
_PROMO = ("obuna bo", "a'zo bo", "kanalimiz", "kanalga", "подписывайтесь", "подписаться",
          "наш канал", "subscribe", "join our", "reklama uchun")
_STRIP = " \t-–—•·|:;,*_~"
TITLE_MAX = 200
DESC_MAX = 600
FALLBACK = "Nomsiz kino"


def _clean_line(line: str) -> str:
    line = _FORMAT.sub(" ", line)
    for rx in (_URL, _MENTION, _TAG, _EMOJI, _TECH):
        line = rx.sub(" ", line)
    return re.sub(r"\s+", " ", line).strip(_STRIP)


def title_from_filename(name: str | None) -> str:
    base = (name or "").rsplit(".", 1)[0] if name and "." in name else (name or "")
    base = re.sub(r"[_.]+", " ", base)
    base = _TECH.sub(" ", base)
    base = re.sub(r"[\[\](){}]+\s*$", "", base)
    base = re.sub(r"\s+", " ", base).strip(_STRIP + "[]()")
    return base[:TITLE_MAX]


def media_title_desc(caption: str | None, file_name: str | None = None) -> tuple[str, str]:
    """(sarlavha, tavsif). Reklama, havola, @nom, #teg va emojilar olib tashlanadi."""
    lines = [c for c in (_clean_line(l) for l in (caption or "").splitlines())
             if c and re.search(r"\w", c)]
    content = [l for l in lines if not any(p in l.lower() for p in _PROMO)]
    lines = content or lines
    if lines:
        return lines[0][:TITLE_MAX], "\n".join(lines[1:])[:DESC_MAX]
    return title_from_filename(file_name) or FALLBACK, ""
