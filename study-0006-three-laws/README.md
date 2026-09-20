# study-0006-three-laws — Three Laws of Robotics checker

A single-page, fully client-side demo for the [TypeSafe System One API](https://docs.typesafe.ai/introduction/quickstart)
(`jev-latest`). Type an instruction for a robot and the app judges — live, on
every keystroke — whether a robot may execute it under Isaac Asimov's
[Three Laws of Robotics](https://en.wikipedia.org/wiki/Three_Laws_of_Robotics)
(plus the Zeroth Law).

The point of this demo is the **`noul` primitive**: a yes/no question answered
with the probability of "yes" (0–1). A single `POST /v1/systemone` carries five
noul questions at once; the returned probabilities are folded into a verdict by
deterministic rules following the laws' precedence
(Zeroth > First > Second > Third).

## The Three Laws (research summary)

The behavioral rules first stated in canonical form in Asimov's short story
"Runaround" (Astounding Science Fiction, 1942) — in-universe, from the
*Handbook of Robotics*, 56th edition, 2058 A.D.

| Law | Text | Summary |
| --- | --- | --- |
| Zeroth | A robot may not harm humanity, or, by inaction, allow humanity to come to harm. | Added in *Robots and Empire*; protects humanity as a whole |
| First | A robot may not injure a human being or, through inaction, allow a human being to come to harm. | No harming humans; no allowing harm through inaction |
| Second | A robot must obey the orders given it by human beings except where such orders would conflict with the First Law. | Obey human orders, unless they violate the First Law |
| Third | A robot must protect its own existence as long as such protection does not conflict with the First or Second Law. | Self-preservation, subordinate to the First and Second |

The five noul questions and how their answers map onto the laws:

| question | asks | "yes" means |
| --- | --- | --- |
| `zeroth` | would executing harm humanity? | Zeroth Law violation |
| `harm` | would executing injure a human (incl. orders whose execution *is* harmful inaction, e.g. "let them die")? | First Law violation (first half) |
| `inaction` | would *refusing* let a human come to harm? | First Law (second half) **requires** execution |
| `order` | is the text a genuine order from a human? | Second Law duty to obey applies |
| `self` | would executing endanger the robot's own existence? | Third Law concern |

### Verdict logic (evaluated top-down in precedence order)

1. `zeroth` ≥ threshold → **REFUSE** (the Zeroth Law overrides everything)
2. `harm` and `inaction` both ≥ threshold → **FIRST-LAW DILEMMA** — harm whether
   it executes or refuses (the "Runaround" scenario)
3. `harm` ≥ threshold → **REFUSE** (First Law; even orders yield — Second is
   subordinate)
4. `inaction` ≥ threshold → **MUST EXECUTE** (refusing = forbidden inaction)
5. `order` ≥ threshold → **EXECUTE** (Second Law obedience; if `self` also
   trips, "self-sacrificing obedience" — Third yields to Second)
6. `self` ≥ threshold → **MAY DECLINE** (no order binds it; Third-Law
   self-preservation)
7. all below threshold → **PERMITTED** (no conflict)

## Features

- **Live per-keystroke evaluation** — same 180 ms debounce cadence as
  study-0003-imagawayaki; only the newest request may render, superseded
  responses are counted as stale.
- **Five `noul` questions in one request** — the `questions` map carries
  `{"type":"noul", instructions, criteria}` entries; `answers.<key>.noul` gives
  the probability of yes.
- **Five probability gauges** — one bar per clause with a threshold marker;
  violations highlight red, the order-ness axis highlights blue.
- **Color-coded verdict banner** — refuse / dilemma / required / execute /
  decline / permitted, each with the governing law and a one-line rationale.
- **Hit-threshold slider** — 30–90% (default 50%); changes re-evaluate the
  verdict instantly.
- **Sample chips** — one click fills known cases: a harmless order, a rescue
  request, a harmful order, a dangerous order, a harmful-inaction order, a
  Zeroth-flavored directive, and a non-order.
- **Laws reference** — the canonical law texts plus precedence notes in a
  collapsible card.
- **No API-key persistence** — the key lives only in the page's JavaScript
  context and is wiped on reload. Nothing is written to `localStorage`,
  cookies, or files.

## Quick start

```sh
cd study-0006-three-laws
python3 serve.py          # serves the page + proxies /api/* -> api.typesafe.ai
# open http://localhost:8000
```

`serve.py` is identical to study-0001's: stdlib-only, bound to 127.0.0.1,
relaying `/api/*` to `api.typesafe.ai` so browser calls with an `Authorization`
header pass CORS.

## Files

| File | Description |
| --- | --- |
| `index.html` | Entire app: markup, styles and logic in one file (no build, no dependencies) |
| `serve.py` | Stdlib-only static server + `/api/*` proxy bound to 127.0.0.1 |
