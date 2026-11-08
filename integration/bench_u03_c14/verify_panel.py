"""C14 append-only panel: verified 18 sequence slots, no APK/merge promotion."""
import json
from integration.audit_u03_c00.profile import ROOT


def main():
    docs=ROOT/"docs"
    state=json.loads((docs/"BBY_Q_U03_ESTADO.json").read_text())
    panel=(docs/"BBY_Q_U03_PANEL.md").read_text()
    next_step=(docs/"BBY_Q_U03_SIGUIENTE.md").read_text()
    assert state["schema"]=="BBYQ-U03-CYCLE-PANEL-v1"
    assert [r["id"] for r in state["cycles"]]==[f"C{i:02d}" for i in range(18)]
    current=int(state["current_cycle"][1:])
    assert 14<=current<=16 and state["next_cycle"]==f"C{current+1:02d}"
    assert 13<=int(state["latest_verified_cycle"][1:])<=current
    assert state["cycles"][13]["pr"]==99
    assert "validado" in state["cycles"][13]["state"]
    assert state["cycles"][14]["pr_url"] and state["cycles"][14]["pr"]
    assert all(r["pr_url"] for r in state["cycles"][:current+1])
    assert all(r["pr"] is None and r["pr_url"] is None for r in state["cycles"][current+1:])
    assert all(f"C{i:02d}" in panel for i in range(18))
    assert "C14" in next_step and "C15" in next_step
    gate=state["history_constraints"]
    assert gate["frozen_sources_expected"]==159
    assert gate["preserve_original_checkpoints"]
    assert gate["protected_main_branch"]
    assert not gate["apk_requested"]
    assert gate["new_primary_memory_authorities"]==0
    assert gate["agency"]=="BBY Q -> w4U -> QdU"
    assert "BBY Q" in panel and "w4U" in panel and "QdU" in panel
    print(json.dumps({"passed":True,"cycles":18,"current":state["current_cycle"],
                      "next":state["next_cycle"],"protected":159,"apk_built":False}))


if __name__=="__main__":
    main()
