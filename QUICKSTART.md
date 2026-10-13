# Quickstart: one routine, seven proofs, and a check on the spec

Two minutes once the kernels are installed. Every output below was produced by the commands above it on
2026-10-07.

## 1. Get the seven kernels

Either build the container, which pins every kernel by sha256 at the versions the published tables were measured on:

    docker build -t t-proof-engine .
    alias t='docker run --rm -v "$PWD:/work" -w /work t-proof-engine'

The build takes about 25 minutes and the image is 10 GB. CI builds it on a fresh runner and checks four tasks
verified, with their twins refuted, in all seven kernels (`.github/workflows/container.yml`).

Or install them natively ([t/RUN-ON-LINUX.md](t/RUN-ON-LINUX.md), [t/RUN-ON-MACOS.md](t/RUN-ON-MACOS.md)) and use:

    alias t='python3 t/cli.py'

## 2. Write a routine once

`t/tasks/clamp.t`:

```
t 1
task clamp(x: int, lo: int, hi: int) returns (r: int)
  requires lo <= hi
  ensures lo <= r and r <= hi
  ensures lo <= x and x <= hi ==> r == x
{
  r := max(lo, min(hi, x));
}
```

## 3. Prove it in all seven kernels

    $ t verify t/tasks/clamp.t
    dafny: COUNTS, real is a real proof; wrong-var twin is refuted, the kernel found this wrong
    verus: COUNTS, real is a real proof; wrong-var twin is refuted, the kernel found this wrong
    spark: COUNTS, real is a real proof; wrong-var twin is refuted, the kernel found this wrong
    framac: COUNTS, real is a real proof; wrong-var twin is refuted, the kernel found this wrong
    lean: COUNTS, real is a real proof; wrong-var twin is refuted, the kernel found this wrong
    rocq: COUNTS, real is a real proof; wrong-var twin is refuted, the kernel found this wrong
    fstar: COUNTS, real is a real proof; wrong-var twin is refuted, the kernel found this wrong

15 s on one desktop. Each kernel proved the routine **and** refuted its twin, a one-edit mutant
(`t twin t/tasks/clamp.t` shows which edit, and the input where the twin breaks the contract). A cell counts only
when both happen.

## 4. Ask whether the spec is strong enough

The twin rule asks for one wrong program the spec rejects. The audit asks about all of them. Delete the second
`ensures` from clamp and audit what is left:

    $ t audit clamp_weak.t --kernel dafny
    clamp: 10 mutants, 6 killed, 0 same, 0 diverge, 4 survivor(s); wrong-var#1 `r := max(lo, min(hi, x));` -> `r := max(hi, min(hi, x));` at x=0, lo=0, hi=1 -> real 0, twin 1
      dafny: real verified, this survivor verified (a different program, proved against the same spec)

With only `lo <= r and r <= hi`, Dafny proves a program that returns 1 where clamp returns 0. Put the `ensures` back:

    $ t audit t/tasks/clamp.t --kernel dafny
    clamp: 10 mutants, 10 killed, 0 same, 0 diverge, 0 survivor(s)
      dafny: real verified


## 5. Read a verdict

    $ t explain refuted
    dafny: refuted is refuted, the kernel found this wrong
    ...

Next: [t/TUTORIAL.md](t/TUTORIAL.md) teaches the language, [t/SYNTAX.md](t/SYNTAX.md) has one example per construct,
and [t/SPEC.md](t/SPEC.md) is the normative specification.
