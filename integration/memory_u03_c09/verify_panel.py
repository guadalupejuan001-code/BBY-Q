#!/usr/bin/env python3
"""Verify persisted U03 status dashboard is exact and never claims deployment."""
import json
from pathlib import Path
from integration.audit_u03_c00.profile import ROOT

def main():
    path=ROOT/"docs/BBY_Q_U03_ESTADO.json"
    value=json.loads(path.read_text())
    panel=(ROOT/"docs/BBY_Q_U03_PANEL.md").read_text()
    next_step=(ROOT/"docs/BBY_Q_U03_SIGUIENTE.md").read_text()
    assert value["schema"]=="BBYQ-U03-CYCLE-PANEL-v1"
    cycles=value["cycles"]
    assert [v["id"] for v in cycles]==[f"C{i:02d}" for i in range(18)]
    assert value["current_cycle"]=="C09" and value["next_cycle"]=="C10"
    assert len({v["id"] for v in cycles})==18
    assert value["history_constraints"]["apk_requested"] is False
    assert value["history_constraints"]["new_primary_memory_authorities"]==0
    assert value["history_constraints"]["preserve_original_checkpoints"]
    assert value["history_constraints"]["frozen_sources_expected"]==159
    assert value["history_constraints"]["agency"]=="BBY Q -> w4U -> QdU"
    assert "C08" in panel and "C09" in panel and "C17" in panel
    assert "C10" in next_step and "APK" in next_step
    assert all(v["pr_url"] for v in cycles[:9])
    assert all(v["pr_url"] is None for v in cycles[10:])
    print(json.dumps({"passed":True,"cycles":18,"current":"C09",
                      "next":"C10","no_APK":True}))

if __name__=="__main__":
    main()
