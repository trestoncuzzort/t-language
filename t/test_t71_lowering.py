"""t/test_t71_lowering.py: lowering fixes read from the emitted text. No kernel is invoked here.

Run: python3 t/test_t71_lowering.py
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "flight"))

import harness  # noqa: E402
import lower_fstar  # noqa: E402
import lower_rocq  # noqa: E402
import lower_verus  # noqa: E402
import refute_at  # noqa: E402
import tasks_io  # noqa: E402


def _task(rel):
    return tasks_io.load_task(os.path.join(HERE, rel))


class RocqPrefixFrame(unittest.TestCase):
    def test_a_local_reassigned_before_the_loop_is_not_pinned_to_its_initialiser(self):
        t = _task("flight/fixes/px4_serial_control_fixed.t")       # `var m := 0; if ... { m := count; }` then the loop
        src = lower_rocq.lower(t, t["body"])
        lemma = src[src.index("Lemma px4_serial_control_fixed_loop_spec"):]
        lemma = lemma[:lemma.index("Proof.")]
        self.assertNotIn("(m = 0)", lemma)
        self.assertIn("(n = 0)", lemma)                             # never reassigned before the loop: still pinned


class VerusGroundBound(unittest.TestCase):
    def test_projection_of_a_pair_literal_is_its_component(self):
        e = {"op": "fst", "args": [{"op": "pair", "args": [{"int": 1}, {"_seq": [0, 0]}]}]}
        self.assertEqual(lower_verus._gint(e), 1)
        self.assertEqual(lower_verus._gint({"op": "-", "args": [e, {"int": 1}]}), 0)

    def test_a_heap_twin_now_gets_its_certificate(self):
        t = _task("flight/fixes/px4_sumd_receive_fixed.t")
        tb, _op, w = harness.twin_cached(t)
        self.assertIn("t_refutation_certificate", lower_verus.lower(t, tb, witness=w))


class FstarLongLiterals(unittest.TestCase):
    def _cert(self, rel, at):
        t = _task(rel)
        w = refute_at.witness_at(t, {k: refute_at._value(v) for k, v in at.items()})
        src = lower_fstar.lower(t, t["body"], witness=w)
        return src[src.index("let t_refutation_certificate"):]

    def test_a_long_constant_buffer_is_seq_create(self):
        cert = self._cert("flight/findings/px4_serial_control_any.t",
                          {"data": {"fill": 0, "len": 70}, "buf": {"fill": 0, "len": 71}, "count": 71})
        self.assertIn("(Seq.create 70 (0))", cert)
        self.assertNotIn("let t_lit_", cert)

    def test_a_long_varied_literal_is_bound_by_createL_first(self):
        cert = self._cert("flight/findings/px4_sumd_receive_any.t",
                          {"sumd_data": {"fill": 0, "len": 64}, "length": 32})
        self.assertIn("let t_lit_0 = (Seq.createL #int [0; 0; 1; 2;", cert)

    def test_short_witness_literals_are_unchanged(self):
        self.assertEqual(lower_fstar._long_literals({"_seq": [0, 1, 2, 3, 4]}), [])


class LeanDivisionFacts(unittest.TestCase):
    def test_an_entry_state_through_a_division_gets_ediv_nonneg(self):
        import lower_lean
        t = _task("flight/fixes/px4_obstacle_body_fixed.t")             # `bound := 360 / inc` before the loop
        self.assertIn("(0 : Int) ≤ (360 : Int) / inc := Int.ediv_nonneg (by omega) (by omega)",
                      lower_lean.lower(t, t["body"]))

    def test_a_task_without_division_is_unchanged(self):
        import lower_lean
        t = _task("flight/fixes/px4_serial_control_fixed.t")
        self.assertNotIn("ediv_nonneg", lower_lean.lower(t, t["body"]))


if __name__ == "__main__":
    unittest.main()
