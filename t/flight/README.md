# Example tasks restated from PX4 flight code

The `.t` files here restate small functions from PX4-Autopilot (BSD-3-Clause, see `LICENSE-PX4`) as t tasks:
each carries the contract the function is meant to keep and verifies like every other t task
(`python3 t/cli.py verify t/flight`). `findings/` holds bodies that break their contract at a concrete input
(`real_inputs.json` lists those inputs; `refute_at.py` refutes a body there), and `fixes/` the same functions
with the contract restored. They exercise the parts of the language embedded code needs: fixed-width bounds
stated as preconditions, index arithmetic that wraps, ring buffers, interpolation and hysteresis state machines.
