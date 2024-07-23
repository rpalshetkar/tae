import io
import re

import pandas as pd


class Reader:
    def __init__(self):
        self.readers = {
            "pd": lambda x: x.copy(),
            "dict": lambda x: pd.DataFrame.from_dict(x, orient="columns"),
            "str": lambda x: pd.read_csv(io.StringIO(x)),
            "bytes": lambda x: pd.read_csv(io.BytesIO(x)),
            "csv": lambda x: pd.read_csv(x),
            "json": lambda x: pd.read_json(x),
            "xls": lambda x: pd.read_excel(x),
            "qzt": lambda x: self._qz_to_df(x),
            "txf": lambda x: self._txf_to_df(x),
            "http": lambda x: self._txf_to_df(x),
        }
        self.dtypes = {
            pd.DataFrame: "pd",
            dict: "dict",
            str: "str",
            bytes: "bytes",
        }

    def _infer_parser(self, data):
        for dtype, parser in self.dtypes.items():
            if isinstance(data, dtype):
                return parser, self.readers[parser]

        if isinstance(data, str):
            uri, _ = data.split("://", 1) if "://" in data else ("", data)
            if uri in self.readers:
                return uri, self.readers[uri]

            pattern = r"\.([^.]+)$"
            match = re.search(pattern, data)
            if match and match.group(1) in self.readers:
                return match.group(1), self.readers[match.group(1)]

        raise ValueError(f"Unsupported data type: {type(data)}")

    def to_df(self, data):
        parser, reader = self._infer_parser(data)
        return parser, reader(data)
