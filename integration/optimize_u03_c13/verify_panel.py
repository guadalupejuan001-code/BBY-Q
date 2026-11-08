"""C13 append-only 18-cycle panel and immutable model/checkpoint contract."""
import json
from integration.audit_u03_c00.profile import ROOT


def main():
    doc=ROOT/"docs"
    state=json.loads((doc/"BBY_Q_U03_ESTADO.json").read_text())
    panel=(doc/"BBY_Q_U03_PANEL.md").read_text()
    follow=(doc/"BBY_Q_U03_SIGUIENTE.md").read_text()
    assert state["schema"]=="BBYQ-U03-CYCLE-PANEL-v1"
    assert [c["id"] for c in state["cycles"]]==[f"C{i:02d}" for i in range(18)]
    assert state["current_cycle"]=="C13" and state["next_cycle"]=="C14"
    assert state["latest_verified_cycle"] in ("C12","C13")
    assert state["cycles"][12]["pr"]==98
    assert "validado" in state["cycles"][12]["state"]
    assert state["cycles"][13]["pr_url"] and state["cycles"][13]["pr"]
    assert all(c["pr_url"] for c in state["cycles"][:14])
    assert all(c["pr"] is None and c["pr_url"] is None
               for c in state["cycles"][14:])
    assert all(f"C{i:02d}" in panel for i in range(18))
    assert "C13" in follow and "C14" in follow
    policy=state["history_constraints"]
    assert policy["frozen_sources_expected"]==159
    assert policy["preserve_original_checkpoints"]
    assert policy["protected_main_branch"]
    assert policy["apk_requested"] is False
    assert policy["new_primary_memory_authorities"]==0
    assert policy["agency"]=="BBY Q -> w4U -> QdU"
    assert "BBY Q" in panel and "w4U" in panel and "QdU" in panel
    print(json.dumps({"passed":True,"cycles":18,"current":"C13",
                      "next":"C14","protected":159,"no_apk":True}))


if __name__=="__main__":
    main()
