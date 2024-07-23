from __future__ import annotations

import re
from typing import Any, Dict, List

import pandas as pd
import yaml
from icecream import ic


def df_pytypes(df):
    overrides = {
        "datetime.date": "date",
        "pandas.core.frame.DataFrame": "pd",
    }
    types = {
        col: str(df[col].apply(type).unique()[0]).split("'")[1] for col in df.columns
    }
    for col, ptype in types.items():
        if ptype in overrides:
            types[col] = overrides[ptype]
    return types


def xlate(val: str):
    var = re.sub(r"\W+", "_", val).lower()
    eng = re.sub(r"_", " ", var).title()
    return var, eng


def xlation_map(vals: List[str]) -> Dict[str, Dict[str, str]]:
    xlations: Dict[str, Dict[str, str]] = {
        "human": {},
        "var": {},
    }
    for val in vals:
        var, eng = xlate(val)
        xlations["human"][var] = eng
        xlations["var"][eng] = var
        xlations["var"][val] = var
    return xlations


def icf(var: Any, header: str = "") -> Any:
    fstr = ic.format(var)
    # print(fstr)
    return fstr


def io_stream(file_path):
    with open(file_path, "r") as fp:
        return fp.read()


def read_yaml(yaml_file):
    return yaml.safe_load(io_stream(yaml_file))


def is_pivot(df):
    if isinstance(df.index, pd.MultiIndex) or isinstance(df.columns, pd.MultiIndex):
        return True
    if df.index.name is not None and df.index.name != "key":
        return True
    if len(df.columns.names) > 1:
        return True
    return False


"""
import spacy
def humanize(text: str) -> str:
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    return " ".join(
        [token.text.lower() if not token.ent_type_ else token.text for token in doc]
    )
"""
