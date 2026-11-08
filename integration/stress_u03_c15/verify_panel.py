"""Append-only C00-C17 dashboard gate for C15, without APK or promotion."""
import json
from integration.audit_u03_c00.profile import ROOT


def main():
    docs=ROOT/"docs"
    state=json.loads((docs/"BBY_Q_U03_ESTADO.json").read_text())
    panel=(docs/"BBY_Q_U03_PANEL.md").read_text()
    follow=(docs/"BBY_Q_U03_SIGUIENTE.md").read_text()
    assert state["schema"]=="BBYQ-U03-CYCLE-PANEL-v1"
    assert [c["id"] for c in state["cycles"]]==[f"C{i:02d}" for i in range(18)]
    assert state["current_cycle"]=="C15" and state["next_cycle"]=="C16"
    assert state["latest_verified_cycle"] in ("C14","C15")
    assert state["cycles"][14]["pr"]==100
    assert "validado" in state["cycles"][14]["state"]
    assert state["cycles"][15]["pr"] is not None and state["cycles"][15]["pr_url"]
    assert all(c["pr_url"] for c in state["cycles"][:16])
    assert all(c["pr"] is None and c["pr_url"] is None for c in state["cycles"][16:])
    assert all(f"C{i:02d}" in panel for i in range(18))
    assert "C15" in follow and "C16" in follow
    protection=state["history_constraints"]
    assert protection["frozen_sources_expected"]==159
    assert protection["preserve_original_checkpoints"]
    assert protection["protected_main_branch"]
    assert protection["new_primary_memory_authorities"]==0
    assert protection["apk_requested"] is False
    assert protection["agency"]=="BBY Q -> w4U -> QdU"
    assert "BBY Q" in panel and "w4U" in panel and "QdU" in panel
    print(json.dumps({"passed":True,"cycles":18,"current":"C15",
                      "next":"C16","protected":159,"apk_built":False}))


if __name__=="__main__":
    main()
