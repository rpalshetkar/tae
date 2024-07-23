import unittest
from pprint import pformat

import pandas as pd
from icecream import ic

from ds import DS
from tests.df import fake_ait_df, fake_bow_df
from view import View


class TestDS(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ic.configureOutput(argToStringFunction=pformat)
        pd.set_option("display.max_rows", 1500)
        pd.set_option("display.max_rows", None)
        pd.set_option("display.max_columns", 200)
        pd.set_option("expand_frame_repr", True)
        pd.set_option("display.width", 20000)
        pd.set_option("display.float_format", "{:10,.0f}".format)
        children = {
            "Subtasks": {"keys": "Group,Headline,Assignee"},
            "Approvals": {"keys": "State,Step"},
            "Reviews": {"keys": "Date,Metric,Measure"},
        }
        # children = None
        bow = fake_bow_df()
        cls.bow = DS(bow, keys=["Group", "Headline"], children=children)
        cls.errors = cls.bow.children["reviews"]
        caps = fake_ait_df()
        cls.caps = DS(caps)

    def test_init_ds_create(self):
        ds = self.dsbow
        assert not ds.df.empty
        ic(ds)

    def test_update_set(self):
        ds = self.dsbow
        key = "RRP|Sample Milestone to set"
        ds[key] = {"effort": 10, "dummy_col": 5}
        ic(key, ds.df.loc[key])

    def test_approvals(self):
        ds = self.dsbow
        wf = ds.children.get("approvals")
        assert wf

    def test_bow_rep(self):
        view = View("templates/specbow.yaml", self.bow)
        html = view.render("templates/template.html")
        with open("report-bow.html", "w") as f:
            f.write(html)

    def test_aits_rep(self):
        view = View("templates/specaits.yaml", self.caps)
        html = view.render("templates/template.html")
        with open("report-aits.html", "w") as f:
            f.write(html)


if __name__ == "__main__":
    unittest.main()
