from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import yaml
from icecream import ic

NO_XLATIONS_SPECIALS = ["LOB", "PL", "PI"]


def df_pytypes(df: pd.DataFrame) -> Dict[str, str]:
    overrides = {
        "datetime.date": "date",
        "pandas.core.frame.DataFrame": "pd",
    }
    types = {
        col: str(df[col].apply(type).unique()[0]).split("'")[1]  # type: ignore  # noqa: PGH003
        for col in df.columns
    }
    for col, ptype in types.items():
        if ptype in overrides:
            types[col] = overrides[ptype]
    return types


def xlate(val: str) -> Tuple[str, str]:
    var = re.sub(r"\W+", "_", val).lower()
    arr: List[str] = [
        i.upper() if i.upper() in NO_XLATIONS_SPECIALS else i.title()
        for i in var.split("_")
    ]
    eng = " ".join(arr)
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


def icf(var: Any, header: str = "") -> str:
    ic.configureOutput(prefix="", outputFunction=lambda s: s)
    icstr: str = ic(var)  # type: ignore[no-untyped-call]
    if header:
        icstr = f"{header}: {icstr}"
    return icstr


def io_stream(file_path: str) -> Optional[str]:
    try:
        with open(file_path, "r", encoding="utf-8") as fp:
            return fp.read()
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except IOError as e:
        print(f"Error: An I/O error occurred while reading the file {file_path}: {e}")

    return None


def read_yaml(yaml_file: str) -> Optional[Any]:
    try:
        yaml_content = io_stream(yaml_file)
        if yaml_content is None:
            return None
        return yaml.safe_load(yaml_content)
    except yaml.YAMLError as e:
        print(f"Error: Failed to parse YAML file {yaml_file}: {e}")
    except Exception as e:
        print(f"Error: An unexpected error occurred while reading {yaml_file}: {e}")

    return None


def is_pivot(df: pd.DataFrame) -> bool:
    if isinstance(df.index, pd.MultiIndex) or isinstance(df.columns, pd.MultiIndex):  # type: ignore  # noqa: PGH003
        return True
    if df.index.name is not None and df.index.name != "key":  # type: ignore  # noqa: PGH003
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
