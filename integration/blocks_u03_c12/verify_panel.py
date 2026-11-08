"""C12 complete U03 dashboard and strict no-merge/no-APK integrity gate."""
import json

from integration.audit_u03_c00.profile import ROOT


def main():
    folder = ROOT / "docs"
    state = json.loads((folder / "BBY_Q_U03_ESTADO.json").read_text())
    panel = (folder / "BBY_Q_U03_PANEL.md").read_text()
    next_step = (folder / "BBY_Q_U03_SIGUIENTE.md").read_text()
    assert [r["id"] for r in state["cycles"]] == [f"C{i:02d}" for i in range(18)]
    assert state["schema"] == "BBYQ-U03-CYCLE-PANEL-v1"
    current=int(state["current_cycle"][1:])
    assert 12<=current<=16
    assert state["next_cycle"]==f"C{current+1:02d}"
    assert 11<=int(state["latest_verified_cycle"][1:])<=current
    assert state["cycles"][11]["pr"] == 97
    assert "validado" in state["cycles"][11]["state"]
    assert state["cycles"][12]["pr_url"]
    assert all(r["pr_url"] for r in state["cycles"][:current+1])
    assert all(r["pr"] is None and r["pr_url"] is None
               for r in state["cycles"][current+1:])
    assert all(f"C{i:02d}" in panel for i in range(18))
    assert "C12" in next_step and "C13" in next_step
    constraints = state["history_constraints"]
    assert constraints["frozen_sources_expected"] == 159
    assert constraints["preserve_original_checkpoints"]
    assert constraints["protected_main_branch"]
    assert constraints["new_primary_memory_authorities"] == 0
    assert constraints["agency"] == "BBY Q -> w4U -> QdU"
    assert constraints["apk_requested"] is False
    assert "BBY Q" in panel and "w4U" in panel and "QdU" in panel
    print(json.dumps({"passed": True, "cycles": 18, "current": state["current_cycle"],
                      "next": state["next_cycle"], "apk_built": False, "protected": 159}))


if __name__ == "__main__":
    main()
