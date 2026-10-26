"""Isolated environment/oracle. The agent never sees these transition rules.

Hidden coefficients are generated from a seed; the same observation and action
produce the same consequence for a given world's configuration. An alternative
parity regime probes a known limitation of the linear relation learner.
"""
from __future__ import annotations

import random


class RelationalWorld:
    def __init__(self, seed: int, mode: str = "linear", inverted: bool = False):
        if mode not in ("linear", "parity"):
            raise ValueError("Unknown experiment world")
        self.mode = mode
        self.inverted = inverted
        rng = random.Random(seed)
        self._coefficients = [rng.choice((-1, 1)) * rng.uniform(0.65, 1.55)
                              for _ in range(4)]
        self._bias = rng.uniform(-0.24, 0.24)

    def observation(self, rng: random.Random) -> dict:
        return {"signal": rng.uniform(-1.0, 1.0),
                "pressure": rng.uniform(-1.0, 1.0)}

    def step(self, observation: dict, action: int) -> int:
        # The outcome is produced by the environment, not supplied as a lookup
        # table or exposed as a label to the agent before its prediction.
        s, p = observation["signal"], observation["pressure"]
        if self.mode == "parity":
            result = int((s > 0) ^ (p > 0) ^ (action > 0))
        else:
            a, b, c, d = self._coefficients
            result = int(a*s + b*p + c*action + d*s*action + self._bias >= 0)
        return 1 - result if self.inverted else result
