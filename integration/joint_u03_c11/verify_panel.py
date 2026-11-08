#!/usr/bin/env python3
"""C11 persistent U03 sequence panel, authority, status and no-APK gate."""
import json
from integration.audit_u03_c00.profile import ROOT


def main():
    folder=ROOT/"docs"
    state=json.loads((folder/"BBY_Q_U03_ESTADO.json").read_text())
    panel=(folder/"BBY_Q_U03_PANEL.md").read_text()
    follow=(folder/"BBY_Q_U03_SIGUIENTE.md").read_text()
    ids=[r["id"] for r in state["cycles"]]
    assert ids==[f"C{i:02d}" for i in range(18)]
    assert state["schema"]=="BBYQ-U03-CYCLE-PANEL-v1"
    current=int(state["current_cycle"][1:])
    assert 11<=current<=16 and state["next_cycle"]==f"C{current+1:02d}"
    assert int(state["latest_verified_cycle"][1:])>=10
    assert state["history_constraints"]["agency"]=="BBY Q -> w4U -> QdU"
    assert state["history_constraints"]["frozen_sources_expected"]==159
    assert state["history_constraints"]["new_primary_memory_authorities"]==0
    assert state["history_constraints"]["preserve_original_checkpoints"]
    assert not state["history_constraints"]["apk_requested"]
    assert state["history_constraints"]["protected_main_branch"]
    assert state["cycles"][10]["pr"]==96 and "validado" in state["cycles"][10]["state"]
    assert state["cycles"][11]["state"]!="pendiente"
    assert all(r["pr"] is None for r in state["cycles"][current+1:])
    assert all(r["pr_url"] for r in state["cycles"][:current+1])
    assert all(f"C{i:02d}" in panel for i in range(18))
    assert "C11" in follow and "C12" in follow and "APK" in follow
    assert "w4U" in panel and "QdU" in panel
    print(json.dumps({
        "passed":True,"cycles":18,"current":state["current_cycle"],"next":state["next_cycle"],
        "agency_preserved":True,"apk_built":False,
        "frozen_count":159,
    }))


if __name__=="__main__":
    main()
