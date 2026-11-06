# readability-stats

Readability scores, grade level and reading time for any text, from the
command line. Handy for checking blog posts, documentation, emails or
anything written for the general public.

```console
$ python3 readability.py sample.txt
Words: 26   Sentences: 3   Syllables: 54
Avg words/sentence: 8.67   Avg syllables/word: 2.08

Flesch Reading Ease        22.3  very difficult (college graduate)
Flesch-Kincaid Grade       12.3
Gunning Fog                14.2
SMOG Index                 13.0
Coleman-Liau               13.8
Automated Readability       9.4
Average grade level        12.5

Reading time: 6 sec   Speaking time: 12 sec
```

## Scores

| Score | Reads as |
|---|---|
| Flesch Reading Ease | 0–100, higher is easier. 60–70 is plain English |
| Flesch-Kincaid Grade | US school grade needed to understand the text |
| Gunning Fog | years of education needed, weighted by complex words |
| SMOG Index | grade level, often used for health information |
| Coleman-Liau | grade level based on letters per word, not syllables |
| Automated Readability (ARI) | grade level based on characters per word |

Reading time assumes 238 words per minute (average adult silent reading) and
speaking time 150 words per minute.

## Usage

```bash
python3 readability.py post.md                 # one file
python3 readability.py chapter1.txt chapter2.txt
pbpaste | python3 readability.py               # read from stdin
python3 readability.py --json post.md          # machine-readable output
```

As a library:

```python
from readability import analyze

stats = analyze(open("post.md").read())
print(stats.flesch_reading_ease, stats.flesch_kincaid_grade)
```

## Accuracy

Syllables are counted with English pronunciation rules rather than a
dictionary, so they are occasionally off by one for unusual words. Scores can
therefore differ slightly from other tools, but they work well for comparing
drafts and spotting hard-to-read passages. Markdown symbols and numbers are
ignored; only words are counted.

## Tests

```bash
python3 -m unittest -v
```

## License

MIT
