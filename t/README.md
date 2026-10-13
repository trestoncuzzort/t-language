# t

**t is a specification interlingua, not a programming language.** A task is
written once in t, with a typed signature, preconditions, postconditions and a
small body, then lowered mechanically to established verifiers, whose kernels
supply every verdict. t itself proves nothing and is trusted for nothing; that
is the design, not a temporary weakness. The trust always bottoms out in a
kernel with decades of adversarial history.

**Seven kernels are live**, and a task counts only when all seven agree:

| kernel | backend as measured |
|---|---|
| Dafny | 4.11.0 / Z3 |
| Verus | 0.2026.08.30 |
| SPARK | gnatprove FSF 16.1.0 / Why3 1.8.2 |
| Frama-C | 33.0 (Arsenic) / alt-ergo 2.4.3 |
| Lean 4 | 4.33.1 |
| Rocq | 9.2 |
| F\* | 2026.08.30 |

Prior art this stands on rather than beside: Why3 (one spec language, many
provers) and Viper (one intermediate verification language, many frontends).
If t ever grows its own checker, that checker gets verified inside Rocq or Lean
(the CakeML path) before anything trusts it: a homemade language certifying a
homemade system is two unaudited instruments signing each other's receipts, and
that is refused here in advance.

## What t covers

Integers, booleans, sequences, pairs, and strings as character sequences.
Loops with invariants, `decreases` clauses, quantifiers (`forall`, `exists`),
and recursive specification functions. Since 2026-10-07 also arrays written in
place ("Heap (v1)"), parallel loops ("Concurrency (v1)") and IEEE binary64 floats
("Floats (v1)"), each lowered where a kernel can carry it and refused by name
where it cannot.

A task is written as a `.t` file in the surface notation
([`SYNTAX.md`](SYNTAX.md)), parsed and printed by `surface.py`. The JSON that
older documents call "the format" is the AST that notation parses to; it is
derived from the `.t` text and never edited by hand.

## The twin rule

Every lowering also emits a **broken twin**, and a task counts only when the
real lowering VERIFIES **and** the twin is REFUTED: one witness that the
specification is provable, one that it has teeth. A twin that still verifies is
a vacuous specification and the task is refused.

REFUTED means the kernel accepted a certificate lemma restating a measured
witness, not a bare failing exit code. That distinction was learned: until
2026-09-02, Dafny's exit 4 (could-not-prove) was read as refuted. It is not a
countermodel and is no longer read as one.

[`twins/`](twins/) ships 426 pairs as a standalone artifact: 213 verified
programs answering 90 problems, each paired with a near-miss one deliberate
edit away, the concrete input at which the near-miss breaks the specification
the program keeps, and seven independent refutations at that input. A pair is
written only when both halves are on the record.

## Where the verdicts come from

- **One matrix.** 130 tasks in [`AGREEMENT.md`](AGREEMENT.md), 66 verified with the
  twin refuted in all seven kernels (Dafny 111, Verus 104, Lean 89, Rocq 84,
  F\* 84, SPARK 79, Frama-C 71), regenerated from a clean clone with no cell moved.
- **Nested loops, closed 2026-09-18.** A `while` inside a `while` was an
  abstain in Lean, Rocq and F\* and a timeout in Frama-C; all seven now verify
  it with its twin refuted. Two of those fixes were honesty defects rather than
  gaps: Lean could leave a goal unsolved that `sorryAx` then discharged, so a
  lowering that proved nothing could read as verified, and Frama-C was not slow
  at all, the lowering was emitting an invariant of its own that is false.
- **A grammar that is the notation.** [`t.gbnf`](t.gbnf) is t's syntax as a
  grammar a generator can decode against, with identifier rules generated from
  the lexer's keyword set. [`grammar_check.py`](grammar_check.py) proves it
  accepts all 4,208 programs the parser accepts and refuses 590 of 590 replies
  the parser refuses.

## Using it

`python3 t/cli.py <subcommand>` is the entry point for working on a single
task: `parse`, `check`, `format`, `lower`, `verify`, `twin`, `explain`. Text
output by default, `--json` for JSON Lines, one record per diagnostic.
Documented with a real example per subcommand in [`COMMAND.md`](COMMAND.md).
`cli.py verify t/tasks` writes a byte-identical `AGREEMENT.md` modulo the
timestamp.

Verifying a whole directory of tasks in parallel is [`run_par.py`](run_par.py);
kernel setup is [`RUN-ON-LINUX.md`](RUN-ON-LINUX.md) and [`RUN-ON-MACOS.md`](RUN-ON-MACOS.md).

An editor integration lives in `editors/vscode/`: a plain JavaScript extension
with a TextMate grammar covering every `surface.KEYWORDS` and
`surface.STR_METHODS` entry (checked by `test_vscode.py`), a client that starts
`lsp.py` over stdio, and a "t verdicts" TreeView fed by the `t/verdicts`
notification. This machine has no display, so the window itself is unverified
here; `editors/WALKTHROUGH.md` measures everything reachable without one.

## Files

| Path | What it is |
|---|---|
| `SPEC.md`, `SYNTAX.md` | the task format and the surface grammar |
| `surface.py`, `check_wf.py` | parser, printer, well-formedness |
| `lower_*.py` | one lowering per kernel, plus twin generation |
| `verifiers/` | one driver per kernel, each collecting its own verdict and version |
| `tasks/` | the 114 committed tasks, as `.t` |
| `twins/` | 426 verified/near-miss pairs over 90 problems, with separating inputs |
| `run_par.py`, `cli.py` | the directory driver and the single-task entry point |
| `to_python.py` | a proved task handed back as checked Python |
| `out/` | lowered sources and verdicts, regenerated; witnesses are committed |

