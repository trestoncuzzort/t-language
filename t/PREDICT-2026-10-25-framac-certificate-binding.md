# Keep certificate negation through Frama-C normalization

The dawnr fixed-answer control found a Frama-C false refusal: its printer turns a negated inequality into an
equality, and the adapter's negation guard then rejects the certificate despite the kernel accepting its proof.
Three diagnostic repetitions reproduced the explicit guard reason. The original control remains recorded;
this repair does not substitute favorable diagnostic results into it.

The existing negative controls are in `test_framac_adapter_controls.py` and `test_verifiers_framac_review.py`.
Keep the adapter unchanged. Encode a certificate's original predicate using a fresh ACSL local binding inside
the negation. By the documented local-binding semantics, `!(\let p = P; p)` means `!P`; it adds no assumption,
axiom, or changed invariant. A printer-only probe on Frama-C 33.0 retains the outer negation for this form.
The binding name must avoid existing identifiers. Apply the same encoding to value, undefined-expression,
loop-exit and termination-measure certificates.

Sources: [ACSL local bindings, section 2.2](https://frama-c.com/download/acsl-implementation-20.0-Calcium.pdf),
`lower_framac.py`'s four certificate builders, and the
[fixed-source diagnosis](https://github.com/trestoncuzzort/dawnr/blob/main/release/evidence/spec33-framac-diagnostic-2026-10-25.json).

Before the repaired kernel runs, predict:

1. A fresh scalar nonzero example with a broken zero-return branch reads verified/refuted with three agreeing
   repetitions per side. Its printed certificate passes the unchanged negation guard. Any refusal or
   disagreement falsifies this prediction.
2. The existing negative certificate, vacuity and inconsistent-definition controls remain rejected. An accepted
   negative control falsifies the repair and stops promotion.
3. Re-run the entire registered `t/tasks` Frama-C column on the same pinned binaries and unchanged budgets,
   once at the base revision and once with the repair. No previously agreeing cell becomes non-agreeing.
   Any such change falsifies this prediction and must be examined by name before landing.
4. The existing four-task, seven-kernel container control remains 28 agreeing cells. Any loss falsifies it.

The full column and native proof tests run on GitHub. Local checks cover syntax, name hygiene and printer
behavior only. Results, including failures, will be appended here. No dawnr grading pin changes until the
engine repair is validated; changed evaluator code will need a fresh matched dawnr baseline and control.
