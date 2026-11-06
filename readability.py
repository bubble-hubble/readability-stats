#!/usr/bin/env python3
"""readability-stats: readability scores, grade level and reading time for text.

Scores computed:
  * Flesch Reading Ease          (higher = easier, 0-100)
  * Flesch-Kincaid Grade Level
  * Gunning Fog Index
  * SMOG Index
  * Coleman-Liau Index
  * Automated Readability Index (ARI)

Syllables are estimated with a heuristic, so scores can differ slightly from
other tools. Pure Python 3 standard library.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import asdict, dataclass

WORD_RE = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)*")
SENTENCE_END_RE = re.compile(r"[.!?]+(?=\s|$)|\n\s*\n")
ABBREVIATIONS = {"mr", "mrs", "ms", "dr", "prof", "sr", "jr", "st", "vs", "etc",
                 "e.g", "i.e", "inc", "ltd", "co", "no", "fig"}

WPM_READ = 238   # average adult silent reading speed
WPM_SPEAK = 150  # typical speaking pace


def count_syllables(word: str) -> int:
    """Estimate the syllables in an English word."""
    w = word.lower().replace("’", "'")
    w = re.sub(r"'s?$", "", w)
    w = re.sub(r"[^a-z]", "", w)
    if not w:
        return 0
    if len(w) <= 3:
        return 1
    # Silent endings: "-es" (but not after s/x/z/ch/sh/ce/ge), "-ed" (but not
    # "-ted"/"-ded"), lone "-e" (but not "-le").
    w = re.sub(r"(?:[^laeiouyszxcgh]es|[^laeiouytd]ed|[^laeiouy]e)$", lambda m: m.group(0)[0], w)
    w = re.sub(r"^y", "", w)
    groups = re.findall(r"[aeiouy]+", w)
    count = len(groups)
    # Vowel pairs that are usually two syllables: "ia", "io" as in "radio", "piano"
    # (but not "-tion", "-sion", "-cial", "-cian").
    count += len(re.findall(r"[^aeioutsc]i[ao]", w))
    return max(1, count)


def split_sentences(text: str) -> list[str]:
    pieces, start = [], 0
    for m in SENTENCE_END_RE.finditer(text):
        before = text[start:m.start()].split()
        last = before[-1].lower().rstrip(".") if before else ""
        if m.group(0) == "." and last in ABBREVIATIONS:
            continue
        piece = text[start:m.end()].strip()
        if WORD_RE.search(piece):
            pieces.append(piece)
        start = m.end()
    tail = text[start:].strip()
    if WORD_RE.search(tail):
        pieces.append(tail)
    return pieces


@dataclass
class Stats:
    sentences: int
    words: int
    characters: int
    syllables: int
    complex_words: int
    avg_words_per_sentence: float
    avg_syllables_per_word: float
    flesch_reading_ease: float
    flesch_kincaid_grade: float
    gunning_fog: float
    smog_index: float
    coleman_liau: float
    automated_readability: float
    reading_time_min: float
    speaking_time_min: float


def analyze(text: str) -> Stats:
    words = WORD_RE.findall(text)
    if not words:
        raise ValueError("no words found in the text")
    sentences = max(1, len(split_sentences(text)))
    n = len(words)
    letters = sum(len(re.sub(r"[^A-Za-z]", "", w)) for w in words)
    syl = [count_syllables(w) for w in words]
    syllables = sum(syl)
    polysyllables = sum(1 for s in syl if s >= 3)
    # Gunning Fog "complex": 3+ syllables, not a proper noun, not just a suffix.
    complex_words = sum(
        1 for w, s in zip(words, syl)
        if s >= 3 and not w[0].isupper() and not re.search(r"(?:es|ed|ing)$", w.lower())
    )

    wps = n / sentences
    spw = syllables / n
    L = letters / n * 100
    S = sentences / n * 100

    return Stats(
        sentences=sentences,
        words=n,
        characters=letters,
        syllables=syllables,
        complex_words=complex_words,
        avg_words_per_sentence=round(wps, 2),
        avg_syllables_per_word=round(spw, 2),
        flesch_reading_ease=round(206.835 - 1.015 * wps - 84.6 * spw, 1),
        flesch_kincaid_grade=round(0.39 * wps + 11.8 * spw - 15.59, 1),
        gunning_fog=round(0.4 * (wps + 100 * complex_words / n), 1),
        smog_index=round(1.043 * math.sqrt(polysyllables * 30 / sentences) + 3.1291, 1),
        coleman_liau=round(0.0588 * L - 0.296 * S - 15.8, 1),
        automated_readability=round(4.71 * letters / n + 0.5 * wps - 21.43, 1),
        reading_time_min=round(n / WPM_READ, 1),
        speaking_time_min=round(n / WPM_SPEAK, 1),
    )


def ease_label(score: float) -> str:
    bands = [(90, "very easy (5th grade)"), (80, "easy (6th grade)"),
             (70, "fairly easy (7th grade)"), (60, "plain English (8th-9th grade)"),
             (50, "fairly difficult (10th-12th grade)"), (30, "difficult (college)")]
    for floor, label in bands:
        if score >= floor:
            return label
    return "very difficult (college graduate)"


def render_text(s: Stats) -> str:
    grade = (s.flesch_kincaid_grade + s.gunning_fog + s.smog_index
             + s.coleman_liau + s.automated_readability) / 5
    lines = [
        f"Words: {s.words:,}   Sentences: {s.sentences:,}   Syllables: {s.syllables:,}",
        f"Avg words/sentence: {s.avg_words_per_sentence}   Avg syllables/word: {s.avg_syllables_per_word}",
        "",
        f"Flesch Reading Ease      {s.flesch_reading_ease:>6}  {ease_label(s.flesch_reading_ease)}",
        f"Flesch-Kincaid Grade     {s.flesch_kincaid_grade:>6}",
        f"Gunning Fog              {s.gunning_fog:>6}",
        f"SMOG Index               {s.smog_index:>6}",
        f"Coleman-Liau             {s.coleman_liau:>6}",
        f"Automated Readability    {s.automated_readability:>6}",
        f"Average grade level      {grade:>6.1f}",
        "",
        f"Reading time: {fmt_minutes(s.reading_time_min)}   "
        f"Speaking time: {fmt_minutes(s.speaking_time_min)}",
    ]
    return "\n".join(lines)


def fmt_minutes(m: float) -> str:
    if m < 1:
        return f"{max(1, round(m * 60))} sec"
    return f"{m:.1f} min"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Readability scores for text files or stdin.")
    p.add_argument("files", nargs="*", help="text files (default: read stdin)")
    p.add_argument("--json", action="store_true", help="output JSON")
    a = p.parse_args(argv)

    sources = a.files or ["-"]
    results = {}
    for src in sources:
        try:
            text = sys.stdin.read() if src == "-" else open(src, encoding="utf-8").read()
            results[src] = analyze(text)
        except (OSError, UnicodeDecodeError, ValueError) as e:
            print(f"{src}: {e}", file=sys.stderr)
            return 1

    if a.json:
        out = {k: asdict(v) for k, v in results.items()}
        print(json.dumps(out if len(out) > 1 else next(iter(out.values())), indent=2))
    else:
        for i, (src, s) in enumerate(results.items()):
            if len(results) > 1:
                print(("\n" if i else "") + f"== {src} ==")
            print(render_text(s))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
