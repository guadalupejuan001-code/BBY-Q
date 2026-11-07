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
    # A persistent panel is append-only across subsequent verified cycles.
    # C09 remains certified even after C10/C11 etc. become current.
    index=int(value["current_cycle"][1:])
    assert 9<=index<=17
    assert int(value["next_cycle"][1:])>index
    assert len({v["id"] for v in cycles})==18
    assert value["history_constraints"]["apk_requested"] is False
    assert value["history_constraints"]["new_primary_memory_authorities"]==0
    assert value["history_constraints"]["preserve_original_checkpoints"]
    assert value["history_constraints"]["frozen_sources_expected"]==159
    assert value["history_constraints"]["agency"]=="BBY Q -> w4U -> QdU"
    assert "C08" in panel and "C09" in panel and "C17" in panel
    assert value["next_cycle"] in next_step and "APK" in next_step
    assert all(v["pr_url"] for v in cycles[:index+1])
    assert "validado" in cycles[9]["state"]
    assert all(v["pr_url"] is None for v in cycles[index+1:])
    print(json.dumps({"passed":True,"cycles":18,"current":value["current_cycle"],
                      "next":value["next_cycle"],"C09_still_validated":True,"no_APK":True}))

if __name__=="__main__":
    main()
