# Vericoding tasks in t (D8)

These tasks restate verified solutions from the [vericoding benchmark](https://github.com/Beneficial-AI-Foundation/vericoding)
(arXiv 2509.22908): 511 from its Dafny track (`dafny/`), 66 from its Verus track (`verus/`) and 16 from its Lean
track (`lean/`). It is licensed under the
MIT License; a copy is in `LICENSE-vericoding`. Mechanical lifters translated each solution whose constructs
t states, in September 2026 (the Dafny track is the union of six lift passes, 2026-09-26 to 09-28, no task in two). The commit read was
not recorded; the branch head on 2026-10-07 is b265a3b2bce31e09d264306f419e810d02f98f44. File names keep vericoding's
task ids: `va`/`vd`/`vt` prefixes name the source collection the benchmark translated from.

The selection is biased toward programs over integers, booleans and sequences; numbers measured here describe these
tasks, not the benchmark.

`t/audit.py --kernel dafny` (and `verus`, `lean`) measures each specification. A vericoding task is solved by any
program the kernel verifies against its specification, so a survivor the kernel proves is a wrong program that would
count as a solution.
