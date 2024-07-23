from __future__ import annotations

import base64
import io
from typing import TYPE_CHECKING, Any, Dict, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import seaborn as sns
from jinja2 import Environment, Template

from utils import io_stream, is_pivot, read_yaml

if TYPE_CHECKING:
    from pandas.io.formats.style import Styler

    from ds import DS


class View:
    def __init__(self, report_spec: str, ds: DS):
        self.spec: Dict[str, Any] = read_yaml(report_spec)
        self.df: pd.DataFrame = ds.df_humanized
        self.jenv: Environment = Environment()
        sns.set_theme(style="darkgrid")

    def render(self, jtmpl: str) -> str:
        layout = "layout"
        template: Template = self.jenv.from_string(io_stream(jtmpl))
        names = [i["name"] for i in self.spec[layout]]
        elements = {}
        for k, v in [
            ("pivots", self._df_pivot),
            ("charts", self._df_chart),
            ("tables", self._df_table),
        ]:
            if self.spec.get(k):
                elements[k] = {
                    name: v(spc) for name, spc in self.spec[k].items() if name in names
                }

        to_style = {
            **elements.get("pivots", {}),
            **elements.get("tables", {}),
        }
        styled_data = {
            name: self.df_style(data).to_html() for name, data in to_style.items()
        }

        return template.render(
            header=self.spec["header"],
            footer=self.spec["footer"],
            styled_data=styled_data,
            charts=elements.get("charts", {}),
            layout=self.spec[layout],
        )

    def _df_pivot(self, spec: Dict[str, Any]) -> pd.DataFrame:
        return pd.pivot_table(self.df, **spec)

    def _df_chart(self, spec: Dict[str, Any]) -> Optional[str]:
        chart_type = spec["type"]
        if chart_type not in ["line", "bar", "heatmap", "gantt", "histogram"]:
            return None
        cparams = {
            "data": self.df.sort_values(by=spec["x"]),
            "x": spec["x"],
            "y": spec["y"],
            "hue": spec.get("z"),
        }
        palette = "Reds" if cparams["y"] == "Errors" else "Blues"
        if cparams["hue"]:
            cparams["palette"] = sns.color_palette(palette=palette)
            cparams["hue_order"] = sorted(self.df[cparams["hue"]].unique())

        if chart_type == "heatmap":
            h_pivot = self.df.pivot_table(
                index=spec["z"],
                columns=spec["x"],
                values=spec["y"],
                aggfunc="sum",
            )
            labels = np.array(h_pivot.values).reshape(
                len(h_pivot.index), len(h_pivot.columns)
            )
            labels = np.round(labels).astype(int)
            cparams = {"df": h_pivot, "labels": labels}

        elif chart_type == "gantt":
            cparams = {
                "data": self.df.head(20),
                "y": spec["x"],
                "x_start": spec["y"],
                "x_end": spec["z"],
                "text": spec["show"],
            }
        elif chart_type == "histogram":
            h_pivot = self.df.pivot_table(
                index=spec["x"],
                columns=spec["z"],
                values=spec["y"],
                aggfunc="sum",
            )
            cparams = {"data": h_pivot}

        plt.figure(figsize=(10, 10))  # Increase figure size
        if chart_type in ["line", "histogram"]:
            sns.lineplot(
                **cparams,
                marker=True,
                style=cparams.get("hue"),
                dashes=False,
                estimator=None,
            )
        elif chart_type == "bar":
            sns.barplot(
                **cparams,
                errorbar=None,
            )
        elif chart_type == "heatmap":
            sns.heatmap(cparams["df"], annot=cparams["labels"], fmt="d")
        elif chart_type == "gantt":
            fig = px.timeline(
                cparams["data"],
                **{
                    k: cparams[k]
                    for k in [
                        "x_start",
                        "x_end",
                        "y",
                        "text",
                    ]
                },
            )
            fig.show()

        plt.tight_layout()

        img = io.BytesIO()
        plt.savefig(img, format="png", bbox_inches="tight", dpi=300)
        img.seek(0)
        plt.close()

        return base64.b64encode(img.getvalue()).decode()

    def _df_table(self, spec: Dict[str, Any]) -> pd.DataFrame:
        return (
            self.df[spec["columns"]]
            .sort_values(by=spec["columns"])
            .head(spec.get("rows", 10))
        )

    def df_style(self, df: pd.DataFrame, is_table=False) -> Styler:
        def _color_negative_red(val):
            return f"color: {'red' if val < 0 else 'black'}"

        gradient = sns.light_palette("seagreen", as_cmap=True)
        style_kwargs = {
            "font-family": "arial, sans-serif",
            "background-color": "white",
            "font-size": "medium",
            "text-align": "right",
            "width": "auto",
            "padding": "0px 20px 0px 0px",
        }
        table_styles = [
            {"selector": "td:hover", "props": [("background-color", "#EFEFE0")]},
            {
                "selector": ".index_name",
                "props": [
                    ("font-style", "italic"),
                    ("color", "black"),
                    ("font-size", "110%"),
                    ("font-weight", "bold"),
                    ("padding", "0.5em"),
                    ("text-align", "left"),
                ],
            },
            {
                "selector": "th:not(.index_name)",
                "props": [
                    ("font-style", "italic"),
                    ("color", "black"),
                    ("font-size", "110%"),
                    ("font-weight", "bold"),
                    ("padding", "0.5em"),
                    ("text-align", "right"),
                ],
            },
            {"selector": "td", "props": [("padding", "0.3em")]},
            {"selector": "tr", "props": [("padding", "0.5em")]},
            {
                "selector": "",
                "props": [
                    ("padding", "0.5em"),
                    ("border-collapse", "collapse"),
                ],
            },
        ]

        styled = (
            df.style.set_properties(**style_kwargs)
            .format(precision=0, thousands=",", na_rep="")
            .background_gradient(cmap=gradient, axis=0)
            .highlight_null(color="transparent")
        )
        styled.set_table_attributes('border="1" border-color="grey"')
        styled.set_table_styles(table_styles)

        if not is_pivot(df) or "key" in df.columns:
            styled.hide(axis="index")

        num_columns = df.select_dtypes(include=["number"]).columns
        styled.map(_color_negative_red, subset=num_columns)

        return styled
