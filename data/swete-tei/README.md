# Source text

The TEI XML files here are the [First1KGreek](https://github.com/sleeptillseven/LXX-Swete)
transcriptions of Henry Barclay Swete's *The Old Testament in Greek* (Cambridge,
1909), licensed **CC BY-SA 4.0**.

Each book is present as either:

* `tlgNNN__tlg0527.tlgNNN.opp-grc2.xml` — the corrected edition, or
* `tlgNNN__tlg0527.tlgNNN.1st1K-grc1.xml` — the raw First1KGreek transcription.

When both exist, `code/python/analyze_lxx.py` prefers `opp-grc2`.

The files are vendored for reproducibility. The `tlgNNN` identifier maps to a book
in `../books.tsv`.

Note: the transcription capitalises many verse-initial words and sometimes renders
their capitals with Latin lookalikes (`APXH` for `ΑΡΧΗ`); the analyzer repairs
those before analysis. It also carries some OCR noise (e.g. Gen 1:3 `ὁ θήτω` for
`ὁ θεὸς γενηθήτω`).
