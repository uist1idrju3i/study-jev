# study-0005-turing — is it Turing-complete? Score vs Noul

A single-page, fully client-side demo for the [TypeSafe System One API](https://docs.typesafe.ai/introduction/quickstart)
(`jev-latest`). Describe a computational system — a language, machine, automaton,
game mechanic, whatever — and two question types race on the **same state** to
answer *"is it Turing-complete?"*:

- **`score`** — a five-level ordered scale from *clearly not* to *clearly*;
  the answer carries a continuous `score` (0–4), per-level `probabilities`, and
  `confidence`. Normalized to 0–1 as `score / 4`.
- **`noul`** — a yes/no question returning the probability that the answer is
  yes, already on 0–1.

Both requests are fired in parallel per judgment, each timed independently with
`performance.now()`, so the two answers — and their RTTs — are directly
comparable on a shared axis and in the paired history table.

## Features

- **Live per-keystroke judging** — same 180 ms debounce cadence as
  study-0003-imagawayaki. Every pause sends one request *pair* on identical
  state; stale responses are discarded (latest-wins) but still counted as RTT
  samples.
- **Shared 0–1 axis** — both verdicts plotted as markers on one
  *not Turing-complete → Turing-complete* continuum; an AGREE / DISAGREE badge
  compares the two.
- **Side-by-side panels** — score shows the level distribution and confidence;
  noul shows a probability gauge. Each tracks its own last/mean/min/max RTT and
  token usage.
- **Paired history** — last 12 complete pairs: both verdicts, both RTTs, Δ and
  which side was faster, and whether the verdicts agreed.
- **Example chips** — one click fills the prompt with a known-complete system
  (brainfuck, Game of Life, two-stack PDA, TypeScript types…), a known
  not-complete one (regex, single-stack PDA, Dhall…), or a gray zone
  (HTML+CSS+clicks, a single terminating program).
- **No API-key persistence** — the key lives only in the page's JavaScript
  context and is wiped on reload. Nothing is written to `localStorage`,
  cookies, or files.

## What "Turing-complete" means (research notes)

- **Definition.** A system of data-manipulation rules is *Turing-complete* iff
  it can simulate an arbitrary Turing machine — equivalently, compute every
  Turing-computable function (Church–Turing thesis). It suffices to simulate
  any one known-complete system: a universal Turing machine, a two-counter
  (Minsky) machine, a cyclic-tag system, Rule 110, or the lambda calculus.
- **Practical ingredients.** Sequencing + conditional branching; *unbounded*
  repetition (loops, recursion, self-reapplication); *unbounded* read/write
  storage. A system that guarantees termination (a "total" language such as
  Dhall or the total fragments of Coq/Agda) cannot be complete. One pushdown
  stack alone gives only context-free power — two stacks suffice.
- **Unbounded ≠ infinite.** No physical machine is strictly complete (finite
  memory — technically a linear bounded automaton). The convention is to judge
  the abstract model as if memory were unbounded, so real computers count.
- **Gray zones.** Bounded variants (fixed-width integers, Befunge-93's 80×25
  grid) are formally not complete but conventionally called so; systems like
  HTML+CSS3 or the C preprocessor are complete only when externally iterated;
  and Turing completeness is a property of a *model*, not of a single program
  run.
- **Undecidability.** Whether an arbitrary system is Turing-complete is itself
  undecidable — every verdict on this page is calibrated inference, not a
  proof.
- **Reference points.** Complete: general-purpose languages, brainfuck,
  Game of Life, Rule 110, Excel, Minecraft redstone, Factorio, Magic: The
  Gathering, PowerPoint, C++ templates, TypeScript/Scala/Java type systems,
  `printf` format strings, x86 MMU fault handling, recursive SQL, mod_rewrite,
  Wang tiles, Vim normal mode. Not complete: finite automata, classic regex,
  single-stack PDAs, straight-line arithmetic, propositional logic, static
  markup (HTML alone, JSON, Markdown), SQL-92, XPath 1.0, total languages.

## Quick start

```sh
cd study-0005-turing
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
