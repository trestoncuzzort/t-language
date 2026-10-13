# t

**t** is a small specification language for programs that have to be proved
correct. A task is written once: a typed signature, preconditions,
postconditions and a short body. `verify` lowers it mechanically into seven
proof systems, Dafny, Verus, SPARK, Frama-C, Lean 4, Rocq and F\*, and reports
each kernel's verdict. t proves nothing itself and is trusted for nothing:
every verdict is a kernel's, and the trust bottoms out in checkers with
decades of adversarial history.

## A task

```
t 1
gate recursion
task gcd(a: int, b: int) returns (r: int)
  requires a >= 0
  requires b >= 0
  ensures r == gcds(a, b)
  decreases a + b
spec fun gcds(a: int, b: int): int
  decreases a + b
= if a <= 0 then b else if b <= 0 then a else if a > b then gcds(a - b, b) else if b > a then gcds(a, b - a) else a
{
  if a == 0 {
    r := b;
  } else {
    if b == 0 {
      r := a;
    } else {
      if a > b {
        r := gcd(a - b, b);
      } else {
        if b > a {
          r := gcd(a, b - a);
        } else {
          r := a;
        }
      }
    }
  }
}
```

`t 1` names the language version. `gate recursion` names the tier of the
language the task uses: v1 has three gates, quantifiers with sequences, loops
with invariants, and recursion with termination. `requires` and `ensures` are
the contract; `decreases` is the termination measure the kernels must accept;
`spec fun` is a specification function, pure and recursive, that the contract
may name. The body is the program. A loop carries its `invariant` and
`decreases` clauses inline ([`t/tasks/reverse.t`](t/tasks/reverse.t)).

```
$ python3 t/cli.py verify t/tasks/clamp.t
dafny: COUNTS, real is a real proof; wrong-var twin is refuted, the kernel found this wrong
verus: COUNTS, real is a real proof; wrong-var twin is refuted, the kernel found this wrong
spark: COUNTS, real is a real proof; wrong-var twin is refuted, the kernel found this wrong
framac: COUNTS, real is a real proof; wrong-var twin is refuted, the kernel found this wrong
lean: COUNTS, real is a real proof; wrong-var twin is refuted, the kernel found this wrong
rocq: COUNTS, real is a real proof; wrong-var twin is refuted, the kernel found this wrong
fstar: COUNTS, real is a real proof; wrong-var twin is refuted, the kernel found this wrong
```

## What the language has

- **Values.** Mathematical integers (no overflow, Euclidean `/` and `%`),
  booleans, sequences (`seq`, immutable, updated as `s[i := v]`), pairs and
  tuples, strings as character sequences, finite sets, maps, and user
  `datatype`s: records, sums and recursive types. Every expression must be
  defined: an index out of range or a division by zero is a proof obligation,
  never undefined behaviour.
- **Contracts.** `requires`, `ensures`, `decreases`; `spec fun` with its own
  `decreases`; `lemma`s with their own contracts; `forall` and `exists` over
  ranges and collections; `old(e)` where a task writes an array in place.
- **Statements.** Assignment, `if`, `while` with `invariant` and `decreases`,
  calls to other tasks, early exits (`break`, `continue`, `return`, rewritten
  away before lowering), comprehensions and the higher-order calls `fold`,
  `sort_by`, `max_by`, `min_by`.
- **v1 extensions, each opened by measurement.** Arrays written in place
  ("Heap (v1)"), parallel loops whose race freedom is checked by rule
  ("Concurrency (v1)"), and IEEE-754 binary64 floats beside exact `real`
  ("Floats (v1)"). A kernel that cannot carry a construct refuses the task by
  name; nothing is weakened to fit.
- **What does not exist, on purpose.** Unbounded quantifiers, aliasing,
  allocation, mutual recursion, function values beyond the four higher-order
  calls, and implicit conversions. [`t/SYNTAX.md`](t/SYNTAX.md) lists every
  construct with one example each; [`t/SPEC.md`](t/SPEC.md) is normative.

## What `verify` does

1. **Parses and checks** the `.t` file (`surface.py`, `check_wf.py`): scopes,
   types, acyclic specification functions, well-formed contracts. A task that
   fails here is refused with the rule it broke.
2. **Lowers** it once per kernel (`lower_*.py`), pinning the kernel version in
   the verdict. Seven kernels, four proof engines: Z3 behind Dafny (through
   Boogie), Verus, F\* and SPARK as run here; Alt-Ergo behind Frama-C's WP; the
   Lean kernel; the Rocq kernel, whose compiled proofs `coqchk` re-checks.
3. **Applies the twin rule.** Every lowering also emits a *twin*: the same
   program one deliberate edit away, with a concrete input at which the twin
   breaks the contract. A cell counts only when the kernel proves the real
   program **and** refutes the twin by accepting a certificate at that input.
   A specification that cannot tell the two apart is vacuous and is refused.
   "Refuted" means an accepted certificate, never a bare failing exit code.
4. **Reports** one line per kernel: counts, refused by name, or abstained with
   the construct named. `--json` gives one record per diagnostic.

Measured from a clean clone on 2026-10-07, over the 130 tasks in
[`t/AGREEMENT.md`](t/AGREEMENT.md):

| kernel | version | proved with the twin refuted |
|---|---|---|
| Dafny | 4.11.0 / Z3 | 111 |
| Verus | 0.2026.08.30 | 104 |
| Lean 4 | 4.33.1 | 89 |
| Rocq | 9.2 | 84 |
| F\* | 2026.08.30 | 84 |
| SPARK | gnatprove FSF 16.1.0 / Why3 1.8.2 | 79 |
| Frama-C | 33.0 / alt-ergo 2.4.3 | 71 |

66 tasks are proved, with the twin refuted, in all seven.

## Running it

The container pins every kernel at the versions above (about 25 minutes to
build, 10 GB):

```
docker build -t t-proof-engine .
alias t='docker run --rm -v "$PWD:/work" -w /work t-proof-engine'
```

Or install the kernels natively ([`t/RUN-ON-LINUX.md`](t/RUN-ON-LINUX.md),
[`t/RUN-ON-MACOS.md`](t/RUN-ON-MACOS.md), [`t/RUN-ON-WINDOWS.md`](t/RUN-ON-WINDOWS.md))
and use `alias t='python3 t/cli.py'`. Python 3.10 or later, standard library
only.

```
t parse   task.t          # the AST the notation parses to
t check   task.t          # well-formedness, with the rule named on refusal
t format  task.t          # the canonical printing (parse . print is the identity)
t lower   task.t --kernel lean    # the lowered source, to read or to hand to the kernel yourself
t verify  task.t          # every present kernel; --kernels dafny,rocq to choose
t twin    task.t          # the twin and the input where it breaks the contract
t audit   task.t --kernel dafny   # how much room the contract leaves for wrong programs
t repair  task.t --kernel dafny   # add the clauses that kill the audit's survivors, then prove them
t build   t/tasks --target c      # compile the proven lowerings and run them against the interpreter
t explain refuted         # what a verdict word means
```

`t verify t/tasks` runs a whole directory; [`t/run_par.py`](t/run_par.py)
does it in parallel and regenerates the agreement table. An editor
integration lives in `t/editors/vscode/` (syntax, diagnostics and a verdicts
view over `t/lsp.py`); [`t/LSP.md`](t/LSP.md) describes the protocol.

[`QUICKSTART.md`](QUICKSTART.md) walks through one routine, seven proofs and
an audit of its specification in a few minutes.

## Documents

| document | what it is |
|---|---|
| [`t/TUTORIAL.md`](t/TUTORIAL.md) | the language, taught by example |
| [`t/SYNTAX.md`](t/SYNTAX.md) | the surface grammar, one example per construct |
| [`t/SPEC.md`](t/SPEC.md) | the normative specification: the three gates, each extension, each kernel's duty |
| [`t/CONFORMANCE.md`](t/CONFORMANCE.md) | what a conforming implementation and a conforming lowering must do |
| [`t/COMMAND.md`](t/COMMAND.md) | every `cli.py` subcommand with a real example |
| [`t/LSP.md`](t/LSP.md) | the language server |
| [`t/AGREEMENT.md`](t/AGREEMENT.md) | the cross-kernel agreement table, regenerated from a clean clone |
| [`t/RELATED-WORK.md`](t/RELATED-WORK.md) | Why3, Viper, Dafny, Verus, SPARK, Frama-C, Lean, Rocq, F\*, and the benchmarks |
| [`t/README.md`](t/README.md) | the implementation: files, lowerings, verifiers |

## Examples

| directory | contents |
|---|---|
| [`t/tasks/`](t/tasks) | 114 tasks, one construct or idiom each |
| [`t/twins/`](t/twins) | 426 verified/near-miss pairs over 90 problems, each with its separating input and seven refutations |
| [`t/autonomy/`](t/autonomy) | 25 routines of the kind a navigation, guidance and control stack is made of: clamps, voting, PID, geofence, time to collision |
| [`t/flight/`](t/flight) | 27 functions restated from PX4 flight code, with bodies that break their contracts under `findings/` and the repaired ones under `fixes/` |

## License

[Research Use License](LICENSE) for t; the PX4-derived examples under
`t/flight/` carry their own [BSD-3-Clause notice](t/flight/LICENSE-PX4). See
[`NOTICE`](NOTICE) for provenance.
