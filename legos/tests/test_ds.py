from pprint import pformat
from typing import Any, Dict

import pandas as pd
import pytest
from icecream import ic

from dns.ds import DS
from dns.view import View

from .fixtures.tdf import fake_ait_df, fake_bow_df, fake_comp_df, fake_funding_df

TDIR = "tests/templates"
ODIR = "tests/outputs"


@pytest.fixture(scope="module")  # type: ignore  # noqa: PGH003
def setup_data() -> Dict[str, Any]:
    ic.configureOutput(argToStringFunction=pformat)
    pd.set_option("display.max_rows", 1500)
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", 200)
    pd.set_option("expand_frame_repr", True)
    pd.set_option("display.width", 20000)
    pd.set_option("display.float_format", "{:10,.0f}".format)
    children: dict[str, dict[str, Any]] = {
        "Subtasks": {"keys": "Group,Headline,Assignee"},
        "Approvals": {"keys": "State,Step"},
        "Reviews": {"keys": "Date,Metric,Measure"},
    }
    # children = None
    bow_ds = DS(fake_bow_df(), keys=["Group", "Headline"], children=children)
    errors_ds = bow_ds.children["reviews"]
    dss = {
        "bow": bow_ds,
        "caps": DS(fake_ait_df()),
        "errors": errors_ds,
        "funding": DS(fake_funding_df()),
        "comp": DS(fake_comp_df()),
    }
    return dss


def test_init_ds_create(setup_data: Dict[str, DS]) -> None:
    ds = setup_data["bow"]
    assert not ds.df.empty
    ic(ds)


def test_update_set(setup_data: Dict[str, DS]) -> None:
    ds = setup_data["bow"]
    key = "RRP|Sample Milestone to set"
    ds[key] = {"effort": 10, "dummy_col": 5}
    ic(key, ds.df.loc[key])


def test_approvals(setup_data: Dict[str, DS]) -> None:
    ds = setup_data["bow"]
    wf = ds.children.get("approvals")
    assert wf


def test_bow_rep(setup_data: Dict[str, DS]) -> None:
    view = View(f"{TDIR}/specbow.yaml", setup_data["bow"])
    html = view.render(f"{TDIR}/template.html")
    with open(f"{ODIR}/report-bow.html", "w") as f:
        f.write(html)


def test_aits_rep(setup_data: Dict[str, DS]) -> None:
    view = View(f"{TDIR}/specaits.yaml", setup_data["caps"])
    html = view.render(f"{TDIR}/template.html")
    with open(f"{ODIR}/report-aits.html", "w") as f:
        f.write(html)


def test_funding_sankey(setup_data: Dict[str, DS]) -> None:
    _sankey_chart("funding", setup_data)


def test_comp_sankey(setup_data: Dict[str, DS]) -> None:
    _sankey_chart("comp", setup_data)


def _sankey_chart(which, setup_data: Dict[str, DS]) -> None:
    view = View(f"{TDIR}/specbow.yaml", setup_data[which])
    df = view.df
    if which == "funding":
        levels: list[str] = ["LOB", "Base Init", "Program", "Receiver", "PI Car"]
        value_col = "Funding"
        title = "Funding Distribution"
    elif which == "comp":
        levels: list[str] = ["Fnc Mgr", "Rating", "Band"]
        value_col = "Ic Incr"
        title = "Comp Distribution"
    else:
        raise ValueError("Invalid input")
    view._sankey(df, levels, value_col, title)
