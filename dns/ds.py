from __future__ import annotations

from itertools import islice
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

import pandas as pd

from reader import Reader
from utils import df_pytypes, icf, xlate, xlation_map

if TYPE_CHECKING:
    from ntypes import SourceTypeVar, StrLStrTypeVar


class DS:
    def __init__(
        self,
        source: SourceTypeVar,
        keys: Optional[StrLStrTypeVar] = None,
        children: Optional[Dict[str, Union[str, Any]]] = None,
    ):
        if children is None:
            children = {}
        self._to_df(source)

        if keys:
            if isinstance(keys, str):
                keys = keys.split(",")
        refs = self._xdf(keys, children)

        self.schema = refs["schema"]
        self.df = refs["df"]
        self.children = refs["children"]

        self.xlations = xlation_map(self.df.columns)
        if self.xlations.get("var"):
            del self.xlations["var"]

        self.kv = refs["kv"]
        self.length = self.df.count()

    def _to_df(self, data: SourceTypeVar) -> None:
        xp, xdf = Reader().to_df(data)
        xlations = xlation_map(xdf.columns)
        xdf.columns = [xlations["var"].get(col) for col in xdf.columns]
        self.protocol: str = xp
        self._odf: pd.DataFrame = xdf

    def _xdf(
        self, keys: Optional[List[str]] = None, children: Optional[Dict] = None
    ) -> Dict[str, Any]:
        if children is None:
            children = {}
        if keys is None:
            keys = []
        df: pd.DataFrame = self._odf.copy()
        self.keys = [xlate(var)[0] for var in keys]
        schema = df_pytypes(df)
        nested = [col for col, ptype in schema.items() if ptype == "pd"]
        for col, ptype in schema.items():
            if ptype == "datex":
                df[col] = df[col].dt.strftime("%Y-%m-%d")

        if self.keys:
            unknown = set(self.keys) - set(df.columns)
            if unknown:
                raise ValueError(f"Unknown keys: {unknown}")
            df["key"] = df[self.keys].astype(str).agg("|".join, axis=1)
            df.set_index("key", inplace=True)

        nodes: Dict[str, "DS"] = {}

        for k, val in (children or {}).items():
            child = xlate(k)[0]
            if child not in nested:
                continue
            ccols = val["keys"]
            if ccols:
                if isinstance(ccols, str):
                    ccols = ccols.split(",")
                ndf = pd.concat(df[child].tolist(), keys=df.index)
                ndf["pkey"] = ndf.index.get_level_values(0)
                ndf.reset_index(inplace=True, drop=True)
                ckeys = ["pkey", *ccols]
                nodes[child] = DS(ndf, keys=ckeys)

        for child in nested:
            df.drop(child, axis=1, inplace=True)

        return {
            "schema": df_pytypes(df),
            "df": df,
            "xlations": xlation_map(df.columns),
            "children": nodes,
            "kv": df.to_dict(orient="index"),
        }

    @property
    def df_humanized(self):
        hdf = self.df.copy()
        hdf.columns = [self.xlations["human"].get(col, col) for col in hdf.columns]
        return hdf

    def _type(self, col) -> Any:
        try:
            return self.df[col].dtype
        except KeyError as err:
            raise ValueError(f"Key {col} not found in dataset") from err

    def __getitem__(self, key: str) -> Dict[str, Any]:
        return self.kv.get(key) or {}

    def __setitem__(self, key: str, value: Any) -> None:
        v = self.kv.get(key) or {}
        v |= value
        try:
            self.df.loc[key] = v
        except KeyError as err:
            raise ValueError(f"Key missing {key}") from err
        self.kv[key] = v

    def unique(self, cols: StrLStrTypeVar) -> List:
        try:
            return self.df[cols].astype(str).agg("|".join, axis=1).unique().tolist()
        except KeyError as err:
            raise ValueError(f"One of the fields {cols} not found in dataset") from err

    def join(  # noqa: PLR0913
        self,
        other: "DS",
        on: StrLStrTypeVar = None,
        how: str = "inner",
        left: str = "(A)",
        right: str = "(B)",
        lkeys: StrLStrTypeVar = None,
        rkeys: StrLStrTypeVar = None,
    ) -> "DS":
        lkeys = lkeys or self.keys or ["key"]
        rkeys = rkeys or other.keys or ["key"]

        def _prepare_df(df, keys):
            df_keys = df[keys]
            df_keys["key"] = df[keys].astype(str).agg("|".join, axis=1)
            return df_keys

        ldf = _prepare_df(self.df, lkeys)
        rdf = _prepare_df(other.df, rkeys)

        joined = ldf.join(rdf, on=on, how=how, lsuffix=left, rsuffix=right)
        return DS(joined, keys=self.meta["keys"])

    def __str__(self):
        kvs = dict(islice(self.kv.items(), 5))
        data = [
            ["Protocol", self.protocol],
            ["Schema", icf(self.schema)],
            ["Keys", self.keys],
            ["Xlations", icf(self.xlations)],
            ["Columns", icf(self.df.columns)],
            ["Dataframe", self.df.head(10)],
            ["KVs", icf(kvs)],
            ["Children", icf(self.children)],
        ]
        sep = "-" * 60 + "\n"
        return sep.join(f"{header} ->{content}\n" for header, content in data)

    def __repr__(self):
        return self.__str__()
