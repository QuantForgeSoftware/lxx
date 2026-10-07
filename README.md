# lxx

An effort at a freely-available, openly-licensed edition of the **Septuagint**
with morphology and lemmas, generated with the [Morpheus](https://github.com/QuantForgeSoftware/morpheus)
morphological analyzer.

## License

The data (text and morphology) is licensed under a
[Creative Commons Attribution-ShareAlike 4.0 International License](http://creativecommons.org/licenses/by-sa/4.0/).

The code (Python scripts) is licensed under the MIT License.

## Why / how

There is no openly-licensed, morphologically-tagged Septuagint that is free to
redistribute. The well-known CATSS/CCAT morphology is non-commercial, requires
downstream recipients to register with CCAT, and its provenance is entangled with
the (permissionless) reuse of the *Analytical Greek New Testament*. So this project
takes a different route:

* **Text:** the [First1KGreek](https://github.com/sleeptillseven/LXX-Swete) TEI
  transcription of Henry Barclay Swete's *The Old Testament in Greek* — **CC BY-SA 4.0**.
  It is vendored under `data/swete-tei/` (corrected `opp-grc2` books are preferred
  over the raw `1st1K-grc1` transcriptions).
* **Morphology:** [Morpheus](https://github.com/QuantForgeSoftware/morpheus), run
  over the text by `code/python/analyze_lxx.py`. Words Morpheus cannot analyze are
  given a synthetic proper-noun analysis (lemma = the surface form) and flagged
  `morpheus-proper`; their forms are collected in `data/onomasticon-lxx.tsv`.

Nothing here is derived from CATSS/CCAT or from the AGNT.

## Current status

* 55 books, 1,135 chapters, **564,842 tokens**.
* Morpheus gives a real analysis for **95.2%** of tokens; the remaining 4.8% are
  proper-name fallbacks (mostly names and the transcription's unaccented
  verse-initial capitals).
* The Swete transcription carries some OCR noise (e.g. Gen 1:3 reads `ὁ θήτω` for
  `ὁ θεὸς γενηθήτω`). That is a limitation of the source text, not the pipeline.

## Data layout

```
data/
  swete-tei/           the source TEI transcriptions (CC BY-SA 4.0, First1KGreek)
  morph-morpheus/      the analyzed text, one file per book: {code}-{abbr}.txt
  books.tsv            code, abbreviation, name, tlg id
  onomasticon-lxx.tsv  proper names: lemma, form, count, source
```

## Codes and fields

### Columns (`data/morph-morpheus/*.txt`, space-separated)

1. **book/chapter/verse** — three-digit fields (`001001001` = book 1, chapter 1,
   verse 1). See `data/books.tsv` for the book codes.
2. **part of speech** — the MorphGNT POS code (see below).
3. **parsing code** — the 8-character MorphGNT parsing code.
4. **text** — the token as it appears, punctuation included.
5. **word** — the token with punctuation stripped (Latin lookalikes repaired).
6. **normalized** — NFC, lower-cased.
7. **lemma** — the Morpheus lemma.
8. **language** — `grc`.
9. **source** — `morpheus`, or `morpheus-proper` for the synthetic proper-noun
   fallback.

### Part of speech code

* `A-` adjective
* `C-` conjunction
* `D-` adverb
* `I-` interjection
* `N-` noun
* `NP` noun, proper (synthetic fallback)
* `P-` preposition
* `RA` definite article
* `RD` demonstrative pronoun
* `RI` interrogative/indefinite pronoun
* `RP` personal pronoun
* `RR` relative pronoun
* `V-` verb
* `X-` particle

### Parsing code

Person, tense, voice, mood, case, number, gender, degree; `-` marks a category
that does not apply. E.g. `3AAI-S--` (aorist indicative 3rd singular) or
`----NSM-` (nominative singular masculine noun).

* person: `1` `2` `3`
* tense: `P` present, `I` imperfect, `F` future, `A` aorist, `X` perfect, `Y` pluperfect
* voice: `A` active, `M` middle, `P` passive
* mood: `I` indicative, `D` imperative, `S` subjunctive, `O` optative, `N` infinitive, `P` participle
* case: `N` nominative, `G` genitive, `D` dative, `A` accusative, `V` vocative
* number: `S` singular, `P` plural, `D` dual
* gender: `M` masculine, `F` feminine, `N` neuter
* degree: `C` comparative, `S` superlative

## Rebuilding

```bash
# requires the Morpheus toolkit on the path (and its venv, which has beta_code)
MORPHEUS_PY=~/Code/morpheus/python \
  ~/Code/morpheus/.venv/bin/python code/python/analyze_lxx.py
```

## Attribution

* Swete's *The Old Testament in Greek*, transcribed by the
  [First1KGreek Project](https://github.com/sleeptillseven/LXX-Swete) (CC BY-SA 4.0).
* Morphological analysis by [Morpheus](https://github.com/QuantForgeSoftware/morpheus).

## Disclaimer

This is a spare-time project. No promises about status or completeness; use at
your own risk.
