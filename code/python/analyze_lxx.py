#!/usr/bin/env python3
"""Analyze Swete's Septuagint with Morpheus.

Source: the First1KGreek TEI transcription of Henry Barclay Swete's *The Old
Testament in Greek* (CC BY-SA 4.0), vendored under ``data/swete-tei``. Each book
is either the corrected ``opp-grc2`` edition or the raw ``1st1K-grc1``
transcription; the corrected one wins when both exist.

Output (mirroring the apostolic-fathers repo's ``data/morph-morpheus``):

  data/morph-morpheus/{NNN}-{abbr}.txt   one token per line, space-separated:
      ref pos parsing text word normalized lemma lang source
  data/books.tsv                         code, abbreviation, name, tlg id
  data/onomasticon-lxx.tsv               lemma, form, count, source

Run with the Morpheus toolkit's venv (it has the ``beta_code`` dependency)::

    MORPHEUS_PY=~/Code/morpheus/python \
      ~/Code/morpheus/.venv/bin/python code/python/analyze_lxx.py
"""
from __future__ import annotations

import os
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from collections import Counter, OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
XML_DIR = os.environ.get("LXX_XML", os.path.join(ROOT, "data", "swete-tei"))
MORPH_DIR = os.environ.get("LXX_MORPH", os.path.join(ROOT, "data", "morph-morpheus"))
MORPHEUS_PY = os.environ.get("MORPHEUS_PY", os.path.expanduser("~/Code/morpheus/python"))
if MORPHEUS_PY not in sys.path:
    sys.path.insert(0, MORPHEUS_PY)

from morpheus_toolkit import Morpheus  # noqa: E402
from morpheus_toolkit.analysis import Analysis  # noqa: E402
from morpheus_toolkit.morphgnt import parsing_code, pos_code  # noqa: E402

NS = "{http://www.tei-c.org/ns/1.0}"

# code -> (tlg id, abbreviation, name). tlg007 and tlg030 are absent upstream.
BOOKS = [
    (1, "tlg001", "Gen", "Genesis"),
    (2, "tlg002", "Exod", "Exodus"),
    (3, "tlg003", "Lev", "Leviticus"),
    (4, "tlg004", "Num", "Numbers"),
    (5, "tlg005", "Deut", "Deuteronomy"),
    (6, "tlg006", "Josh", "Joshua"),
    (7, "tlg008", "Judg", "Judges"),
    (8, "tlg010", "Ruth", "Ruth"),
    (9, "tlg011", "1Kgdms", "1 Kingdoms (1 Samuel)"),
    (10, "tlg012", "2Kgdms", "2 Kingdoms (2 Samuel)"),
    (11, "tlg013", "3Kgdms", "3 Kingdoms (1 Kings)"),
    (12, "tlg014", "4Kgdms", "4 Kingdoms (2 Kings)"),
    (13, "tlg015", "1Chr", "1 Chronicles"),
    (14, "tlg016", "2Chr", "2 Chronicles"),
    (15, "tlg017", "1Esd", "1 Esdras"),
    (16, "tlg018", "2Esd", "2 Esdras (Ezra-Nehemiah)"),
    (17, "tlg019", "Esth", "Esther"),
    (18, "tlg020", "Jdt", "Judith"),
    (19, "tlg021", "Tob", "Tobit"),
    (20, "tlg023", "1Macc", "1 Maccabees"),
    (21, "tlg024", "2Macc", "2 Maccabees"),
    (22, "tlg025", "3Macc", "3 Maccabees"),
    (23, "tlg026", "4Macc", "4 Maccabees"),
    (24, "tlg027", "Ps", "Psalms"),
    (25, "tlg028", "Odes", "Odes"),
    (26, "tlg029", "Prov", "Proverbs"),
    (27, "tlg031", "Song", "Song of Songs"),
    (28, "tlg032", "Job", "Job"),
    (29, "tlg033", "Wis", "Wisdom of Solomon"),
    (30, "tlg034", "Sir", "Sirach"),
    (31, "tlg035", "PssSol", "Psalms of Solomon"),
    (32, "tlg036", "Hos", "Hosea"),
    (33, "tlg037", "Amos", "Amos"),
    (34, "tlg038", "Mic", "Micah"),
    (35, "tlg039", "Joel", "Joel"),
    (36, "tlg040", "Obad", "Obadiah"),
    (37, "tlg041", "Jonah", "Jonah"),
    (38, "tlg042", "Nah", "Nahum"),
    (39, "tlg043", "Hab", "Habakkuk"),
    (40, "tlg044", "Zeph", "Zephaniah"),
    (41, "tlg045", "Hag", "Haggai"),
    (42, "tlg046", "Zech", "Zechariah"),
    (43, "tlg047", "Mal", "Malachi"),
    (44, "tlg048", "Isa", "Isaiah"),
    (45, "tlg049", "Jer", "Jeremiah"),
    (46, "tlg050", "Bar", "Baruch"),
    (47, "tlg051", "Lam", "Lamentations"),
    (48, "tlg052", "EpJer", "Epistle of Jeremiah"),
    (49, "tlg053", "Ezek", "Ezekiel"),
    (50, "tlg054", "Sus", "Susanna (LXX)"),
    (51, "tlg055", "SusTh", "Susanna (Theodotion)"),
    (52, "tlg056", "Dan", "Daniel (LXX)"),
    (53, "tlg057", "DanTh", "Daniel (Theodotion)"),
    (54, "tlg058", "Bel", "Bel and the Dragon (LXX)"),
    (55, "tlg059", "BelTh", "Bel and the Dragon (Theodotion)"),
]

# The First1KGreek transcription renders many capital letters with Latin
# lookalikes (A P X H for Α Ρ Χ Η, C for Σ, …). Map them back to Greek.
LATIN_TO_GREEK = {
    "A": "Α", "B": "Β", "E": "Ε", "Z": "Ζ", "H": "Η", "I": "Ι", "K": "Κ", "M": "Μ",
    "N": "Ν", "O": "Ο", "P": "Ρ", "T": "Τ", "Y": "Υ", "X": "Χ", "C": "Σ", "S": "Σ",
    "G": "Γ", "D": "Δ", "L": "Λ", "R": "Ρ", "F": "Φ", "Q": "Θ", "W": "Ω", "U": "Υ",
    "J": "Ι", "V": "Υ",
    "a": "α", "b": "β", "e": "ε", "z": "ζ", "h": "η", "i": "ι", "k": "κ", "m": "μ",
    "n": "ν", "o": "ο", "p": "ρ", "t": "τ", "y": "υ", "x": "χ", "c": "σ", "s": "σ",
    "g": "γ", "d": "δ", "l": "ι", "r": "ρ", "f": "φ", "q": "θ", "w": "ω", "u": "υ",
    "j": "ι", "v": "υ",
}
PUNCT = ".,;:··!?()[]{}<>«»‘’“”\"'—–-…†‡*|/\\"
GREEK_RE = re.compile(r"[\u0370-\u03FF\u1F00-\u1FFF]")
LATIN_RE = re.compile(r"[A-Za-z]")
ROMAN_RE = re.compile(r"^[IVXLCDMivxlcdm]+$")


def pick_file(tlg: str) -> str | None:
    """The corrected ``opp-grc2`` file for a book, else the raw ``1st1K-grc1``."""
    for edition in ("opp-grc2", "1st1K-grc1"):
        for name in os.listdir(XML_DIR):
            if name.startswith(f"{tlg}__") and edition in name:
                return os.path.join(XML_DIR, name)
    return None


def verse_text(div: ET.Element) -> str:
    """Text of a verse, excluding apparatus notes and headings."""
    parts: list[str] = []

    def walk(el: ET.Element) -> None:
        if el.tag in (NS + "note", NS + "head"):
            return
        if el.text:
            parts.append(el.text)
        for child in el:
            walk(child)
        if el.tail:
            parts.append(el.tail)

    walk(div)
    return re.sub(r"\s+", " ", "".join(parts)).strip()


def clean_token(raw: str) -> str:
    """The analysis form of a raw token ('' to skip a non-word)."""
    token = raw.strip(PUNCT).strip()
    if not token:
        return ""
    has_greek = bool(GREEK_RE.search(token))
    has_latin = bool(LATIN_RE.search(token))
    if has_latin:
        if not has_greek and (ROMAN_RE.match(token) or len(token) < 2):
            return ""  # a Roman numeral or a lone siglum, not a Greek word
        token = "".join(LATIN_TO_GREEK.get(ch, ch) for ch in token)
    return token


def normalize(word: str) -> str:
    """NFC, lower-case; the crude analogue of Tauber's greek_normalisation."""
    return unicodedata.normalize("NFC", word).lower()


def read_book(path: str) -> list[tuple[int, int, str]]:
    """Return ``(chapter, verse, text)`` rows for a book, notes removed."""
    root = ET.parse(path).getroot()
    body = root.find(".//" + NS + "body")
    if body is None:
        return []

    def add(verse: ET.Element, chapter_num: int, rows: list) -> None:
        match = re.match(r"\d+", verse.get("n") or "")
        rows.append((chapter_num, int(match.group()) if match else 0, verse_text(verse)))

    rows: list[tuple[int, int, str]] = []
    chapters = [d for d in body.iter(NS + "div") if d.get("subtype") == "chapter"]
    if chapters:
        for chapter in chapters:
            match = re.match(r"\d+", chapter.get("n") or "0")
            chapter_num = int(match.group()) if match else 0
            for verse in chapter:
                if verse.tag == NS + "div" and verse.get("subtype") == "verse":
                    add(verse, chapter_num, rows)
    else:
        for verse in body.iter(NS + "div"):
            if verse.get("subtype") == "verse":
                add(verse, 1, rows)
    return rows


def main() -> int:
    analyzer = Morpheus(unknown_as_proper=True)

    # Pass 1: parse every book, collecting tokens and distinct forms.
    parsed: list[tuple[int, str, str, list]] = []
    forms: set[str] = set()
    freq: "Counter[str]" = Counter()
    for code, tlg, abbr, name in BOOKS:
        path = pick_file(tlg)
        if not path:
            print(f"  {abbr:<8} MISSING SOURCE")
            continue
        rows = read_book(path)
        tokens_by_row = []
        for chapter_num, verse_num, text in rows:
            tokens = []
            for raw in text.split():
                word = clean_token(raw)
                if word:
                    tokens.append((raw, word))
                    forms.add(word)
                    freq[word] += 1
            tokens_by_row.append((chapter_num, verse_num, tokens))
        parsed.append((code, abbr, name, tokens_by_row))
        print(f"  {abbr:<8} {len(rows):>5} verses")

    print(f"\nDistinct token forms: {len(forms)}")

    # Pass 2: analyze each distinct form once (Morpheus is form-deterministic).
    analyses: dict[str, tuple[str, str, str, bool]] = {}
    ordered = sorted(forms)
    chunk = 20_000
    proposed = 0
    for start in range(0, len(ordered), chunk):
        batch = ordered[start : start + chunk]
        for token, result in zip(batch, analyzer.analyze_tokens(batch)):
            best = result.best
            if best is None:
                continue
            if best.proposed:
                proposed += 1
            analyses[token] = (best.lemma, pos_code(best), parsing_code(best), best.proposed)
        print(f"  analyzed {min(start + chunk, len(ordered))}/{len(ordered)}")

    real = len(ordered) - proposed
    print(
        f"Real analyses: {real}/{len(ordered)} forms ({100 * real / max(len(ordered), 1):.1f}%); "
        f"{proposed} proper-name fallbacks"
    )

    # Pass 3: write the columnar morphology files and the onomasticon.
    os.makedirs(MORPH_DIR, exist_ok=True)
    onomasticon: "OrderedDict[tuple[str, str], int]" = OrderedDict()
    total = 0
    for code, abbr, name, tokens_by_row in parsed:
        lines: list[str] = []
        for chapter_num, verse_num, tokens in tokens_by_row:
            ref = f"{code:03d}{chapter_num:03d}{verse_num:03d}"
            for raw, word in tokens:
                lemma, pos, parsing, is_proposed = analyses.get(word, (word, "N-", "--------", True))
                source = "morpheus-proper" if is_proposed else "morpheus"
                lines.append(
                    " ".join([ref, pos, parsing, raw, word, normalize(word), lemma, "grc", source])
                )
                if is_proposed:
                    key = (lemma, word)
                    onomasticon[key] = onomasticon.get(key, 0) + 1
                total += 1
        out = os.path.join(MORPH_DIR, f"{code:03d}-{abbr}.txt")
        with open(out, "w", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
        print(f"  wrote {out} ({len(lines)} tokens)")

    with open(os.path.join(ROOT, "data", "books.tsv"), "w", encoding="utf-8") as handle:
        handle.write("code\tabbr\tname\ttlg\n")
        for code, tlg, abbr, name in BOOKS:
            handle.write(f"{code}\t{abbr}\t{name}\t{tlg}\n")

    with open(os.path.join(ROOT, "data", "onomasticon-lxx.tsv"), "w", encoding="utf-8") as handle:
        handle.write("lemma\tform\tcount\tsource\n")
        for (lemma, form), count in sorted(onomasticon.items(), key=lambda item: -item[1]):
            handle.write(f"{lemma}\t{form}\t{count}\tmorpheus\n")

    print(f"\n{len(parsed)} books, {total} tokens; onomasticon {len(onomasticon)} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
