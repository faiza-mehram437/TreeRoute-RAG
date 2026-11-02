"""Format paper metadata as APA 7, MLA 9 and BibTeX citations (sample from TreeRoute)."""

import re

from samples.models import Citations, PaperInfo

STOPWORDS = {"a", "an", "the", "on", "of", "in", "for", "and", "to", "with"}


def split_name(name: str) -> tuple[str, str]:
    """Return (given names, family name). Handles "Ashish Vaswani" and "Vaswani, Ashish"."""
    name = " ".join(name.split())
    if "," in name:
        family, given = (part.strip() for part in name.split(",", 1))
        return given, family
    parts = name.split(" ")
    return " ".join(parts[:-1]), parts[-1]


def initials(given: str) -> str:
    """'Ashish' -> 'A.', 'Aidan N.' -> 'A. N.', 'Jean-Paul' -> 'J.-P.'"""
    out = []
    for word in given.replace(".", " ").split():
        out.append("-".join(f"{piece[0]}." for piece in word.split("-") if piece))
    return " ".join(out)


def apa_author(name: str) -> str:
    given, family = split_name(name)
    return f"{family}, {initials(given)}" if given else family


def _apa_authors(authors: list[str]) -> str:
    names = [apa_author(a) for a in authors]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    if len(names) > 20:
        return ", ".join(names[:19]) + ", ... " + names[-1]
    return ", ".join(names[:-1]) + ", & " + names[-1]


def _sentence(text: str) -> str:
    text = text.strip()
    return text if text.endswith((".", "?", "!")) else text + "."


def _doi_url(info: PaperInfo) -> str | None:
    if info.doi:
        return f"https://doi.org/{info.doi}"
    if info.arxiv_id:
        return f"https://arxiv.org/abs/{info.arxiv_id}"
    return info.url


def format_apa(info: PaperInfo) -> str:
    year = info.year or "n.d."
    parts = [f"{_apa_authors(info.authors)} ({year}).".strip(), _sentence(info.title)]
    if info.venue:
        parts.append(f"*{info.venue}*.")
    if link := _doi_url(info):
        parts.append(link)
    return " ".join(parts)


def _mla_authors(authors: list[str]) -> str:
    if not authors:
        return ""
    given, family = split_name(authors[0])
    first = f"{family}, {given}" if given else family
    if len(authors) == 1:
        return _sentence(first)
    if len(authors) == 2:
        return _sentence(f"{first}, and {authors[1]}")
    return f"{first}, et al."


def format_mla(info: PaperInfo) -> str:
    title = info.title.strip().rstrip(".")
    parts = [_mla_authors(info.authors), f'"{title}."']
    tail = ", ".join(str(p) for p in (f"*{info.venue}*" if info.venue else None, info.year) if p)
    if tail:
        parts.append(tail + ".")
    if link := _doi_url(info):
        parts.append(link + ".")
    return " ".join(p for p in parts if p)


def bibtex_key(info: PaperInfo) -> str:
    family = split_name(info.authors[0])[1] if info.authors else "unknown"
    words = [w for w in re.findall(r"[a-z0-9]+", info.title.lower()) if w not in STOPWORDS]
    key = re.sub(r"[^a-z0-9]", "", family.lower()) + str(info.year or "")
    return key + (words[0] if words else "")


def format_bibtex(info: PaperInfo) -> str:
    fields = {
        "title": "{" + info.title.strip().rstrip(".") + "}",
        "author": " and ".join(f"{f}, {g}" if g else f for g, f in map(split_name, info.authors)),
        "year": str(info.year) if info.year else None,
        "journal": info.venue,
        "doi": info.doi,
        "eprint": info.arxiv_id,
        "archivePrefix": "arXiv" if info.arxiv_id else None,
        "url": _doi_url(info),
    }
    body = ",\n".join(f"  {k} = {{{v}}}" for k, v in fields.items() if v)
    entry = "article" if info.venue else "misc"
    return f"@{entry}{{{bibtex_key(info)},\n{body}\n}}"


def format_all(info: PaperInfo) -> Citations:
    return Citations(apa=format_apa(info), mla=format_mla(info), bibtex=format_bibtex(info))
