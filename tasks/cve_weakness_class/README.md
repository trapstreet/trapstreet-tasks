# cve_weakness_class

Given the published description of one software vulnerability, name the weakness
class it belongs to — one of 30 CWE identifiers.

```
In link_load_gnss_image of link_device.c, there is a possible out-of-bounds
write due to a missing bounds check. This could lead to local escalation of
privilege with System execution privileges needed.
```

→ `ANSWER: CWE-787`

## The set

1,500 cases, 50 for each of the 30 classes, no two carrying the same
description text. Each case is one CVE published
between 2026-07-01 and 2026-09-15, with the weakness class recorded for it in
the National Vulnerability Database by the organisation that assigned the CVE.

Balanced rather than natural: in the wild `CWE-284` alone is 9.4% of CVEs, and
a model that leant on the base rate would collect points for nothing. Every
class carries equal weight here, which makes the task harder than production
and makes per-class results readable.

Descriptions that cite a CWE identifier are excluded from the pool — otherwise
a regular expression would answer those without reading anything. So are
descriptions citing any CVE identifier: NVD is a public lookup, and a CVE id in
the text is an answer key one request away.

That filter does not close the channel completely, and the benchmark does not
claim it does. These descriptions are NVD's own text, published verbatim, so a
solution with a search engine can look up the string itself. Nothing in the
case set prevents that — it is the cost of using real records rather than
paraphrases. Read a score with that in mind, or run offline.

## Scoring

Exact match against the recorded CWE. Chance is 0.033.

CWE is a hierarchy: `CWE-862` (Missing Authorization) sits under `CWE-284`
(Improper Access Control), and an analyst can reasonably record either. Naming
a parent or a child of the recorded class scores zero, the same as any other
miss — partial credit would bake one abstraction level into the metric. Instead
the run report publishes what share of each arm's errors were parent-or-child
rather than unrelated, so an abstraction-level slip and a misread flaw show up
as different failures.

The run report also carries cost per correct answer, per-class accuracy, and the
most frequent confusions.

## Baselines

Trivial predictors, run through this task's own judge over all 1,500 cases
(2026-09-20):

| | accuracy |
|---|---|
| **lexical match of description to class name** | **0.541** |
| uniform random over the 30 options | 0.033 |
| always the most frequent class in the wild | 0.033 |
| output with no identifier from the option list | 0.000 |

The lexical row is the number that matters. 392 of the 1,500 descriptions
contain the recorded class's own name somewhere in the prose — "out-of-bounds
write", "SQL injection" — and a string matcher collects those for free. That
is deliberate: it is how these descriptions are written, and cropping around it
would make the task an artefact. It does mean **0.541 is the floor a
submission has to clear** to have demonstrated anything.

Accuracy is not expected to separate the strongest arms. Probing across model
tiers while designing this, the spread from a 1B open model to the best arm was
about 52 points, but the top three landed within two points of each other —
closer than 1,500 cases can resolve. What separates arms at that level is cost
per correct answer, where the measured spread was two orders of magnitude, and
error structure. The run report publishes both.

## Running it

Each case directory holds `description.txt`. `inputs/task.md` carries the
instructions and the full option list. Print one line:

```
ANSWER: CWE-787
```

The identifier must be one of the 30 options. Parsing is forgiving about the
marker — the last valid identifier in your output is taken — but the answer
itself must match exactly.

## Acknowledgements

Vulnerability records come from the **National Vulnerability Database**,
maintained by NIST, which places its data in the public domain.

Weakness classes come from **CWE™**, maintained by MITRE and released for free
public use. CWE is a trademark of The MITRE Corporation. Catalogue version
v4.20.

Neither NIST nor MITRE endorses this benchmark.
