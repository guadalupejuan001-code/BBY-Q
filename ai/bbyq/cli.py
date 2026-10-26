"""Command line interface: transparent interactions, introspection and evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .experiment import campaign
from .model import choose_action, experience, new_entity, predict
from .store import NativeStore


def _dump(value):
    print(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True))


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="bbyq", description="BBY Q experimental entity")
    parser.add_argument("--state", default="entity.rvp", help="One canonical RVPC2 state file")
    parser.add_argument("--reverse-pc", help="Executable built from pinned REVERSE-PC")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("birth", help="Create a new persistent entity, refusing to overwrite")
    sub.add_parser("inspect", help="Show identity, hypotheses, history and native stats")
    step = sub.add_parser("step", help="Perform an experience and transactionally learn")
    probe = sub.add_parser("predict", help="Non-mutating inference and explanation")
    for command in (step, probe):
        command.add_argument("--signal", type=float, required=True)
        command.add_argument("--pressure", type=float, required=True)
        command.add_argument("--action", type=int, choices=(-1, 1), required=True)
    step.add_argument("--outcome", type=int, choices=(0, 1), required=True)
    step.add_argument("--no-learning", action="store_true")
    sub.add_parser("native-stats", help="Show InverseMemory and InfiniteCore resources")
    exp = sub.add_parser("experiment", help="Independent Stage 2 learning campaign")
    exp.add_argument("--seed", type=int, default=42)
    exp.add_argument("--runs", type=int, default=5)
    exp.add_argument("--train", type=int, default=400)
    exp.add_argument("--test", type=int, default=240)
    exp.add_argument("--output", type=Path, help="Save evaluation JSON (not state)")
    exp.add_argument("--persist", action="store_true", help="Commit the final learned entity to a NEW RVPC2 state")
    arguments = parser.parse_args(argv)

    if arguments.command == "experiment":
        report, evolved = campaign(arguments.seed, arguments.runs,
                                   arguments.train, arguments.test)
        if arguments.persist:
            native_store = NativeStore(arguments.state, arguments.reverse_pc)
            native_store.initialize(evolved)
            if native_store.read() != evolved:
                raise RuntimeError("Learned entity mismatch after native restore")
            report["native_persistence_verified"] = True
            report["native_storage"] = native_store.stats()
            report["native_state_path"] = str(native_store.state_path)
        if arguments.output:
            arguments.output.parent.mkdir(parents=True, exist_ok=True)
            arguments.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        _dump(report)
        return

    store = NativeStore(arguments.state, arguments.reverse_pc)
    if arguments.command == "birth":
        entity = new_entity()
        store.initialize(entity)
        _dump({"born": True, "id": entity["id"], "state_file": str(store.state_path),
               "identity_continuity": True})
    elif arguments.command == "inspect":
        entity = store.read()
        _dump({"entity": entity, "physical_storage": store.stats()})
    elif arguments.command == "native-stats":
        _dump(store.stats())
    elif arguments.command == "predict":
        entity = store.read()
        obs = {"signal": arguments.signal, "pressure": arguments.pressure}
        _dump({"id": entity["id"], "step": entity["steps"],
               "inference": predict(entity, obs, arguments.action),
               "suggested_action": choose_action(entity, obs)})
    elif arguments.command == "step":
        obs = {"signal": arguments.signal, "pressure": arguments.pressure}
        entity, result = store.transact(
            lambda obj: experience(obj, obs, arguments.action,
                                   arguments.outcome, learn=not arguments.no_learning))
        _dump({"id": entity["id"], "experience": result,
               "hypotheses": entity["model"]["weights"]})


if __name__ == "__main__":
    main()
