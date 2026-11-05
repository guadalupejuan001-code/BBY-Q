#!/usr/bin/env python3
"""Transport for one native XI policy step, including already-complete goals."""
import argparse
import json
from pathlib import Path
from types import SimpleNamespace
from campaign import A, XI, Experiment, metrics, sha


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--runtime', required=True)
    parser.add_argument('--state', required=True)
    sub = parser.add_subparsers(dest='command', required=True)
    act = sub.add_parser('act')
    act.add_argument('--position', type=int, choices=range(7), required=True)
    act.add_argument('--goal', type=int, choices=range(7), required=True)
    act.add_argument('--greedy', action='store_true')
    args = parser.parse_args()
    state = Path(args.state).resolve()
    digest = sha(state)
    options = SimpleNamespace(runtime=args.runtime, session_binary=None,
        step_budget=100000000, agent='qrl', task='line_slip', seed=173,
        episodes=1, eval_size=1, classical=False, analytic=False,
        joint_mode='independent', output=str(state.parent/'step-transport'))
    exp = Experiment(options)
    exp.lib += '\n' + (XI/'step.xi').read_text()
    body = f'''load8 r0 {A+1000}
cmp r0 173
je valid_step_model
div r0 0
label valid_step_model
qtrace reset
store64 {A+280} 0
store64 {A+344} {args.position}
store64 {A+352} {args.goal}
store64 {A+360} 0
store64 {A+312} 12
store64 {A+320} {2 if args.greedy else 1}
call qrl_step
qtrace report
qstats
stats'''
    with exp.Session(exp.binary, state) as session:
        before = exp.model_state(session)
        events, elapsed = session.execute(exp.source(body))
        result = metrics(events)
        trace = next(e for e in events if e['type'] == 'quantum_trace')
        backend = next(e for e in events if e['type'] == 'quantum_stats')
        stats = next(e for e in events if e['type'] == 'stats')
        terminal = bool(result['terminal'])
        assert trace['distinct_observed_qubits'] == (0 if terminal else 1000)
        assert stats['components'] == sum(backend[k] for k in
            ['clifford_components', 'adaptive_components', 'reduced_components'])
        assert before == exp.model_state(session), 'Inference changed learned parameters'
    assert sha(state) == digest, 'Inference changed its input checkpoint'
    return {**result, 'terminal': terminal,
        'action': None if terminal else int(result['action']),
        'probability_right': None if terminal else result['probability_right'],
        'qubits_used_by_agent': trace['distinct_observed_qubits'],
        'elapsed_ms': elapsed, 'trace': trace,
        'training_scope': {'trained_goals': [0, 6],
            'goal_seen_in_training': args.goal in [0, 6],
            'arbitrary_goals_validated_correct_directions': 33,
            'arbitrary_goals_validation_cases': 42}}


if __name__ == '__main__':
    print(json.dumps(main(), ensure_ascii=False, indent=2))
