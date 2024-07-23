import random
from datetime import date, datetime, timedelta
from random import choice, randint

import pandas as pd
from faker import Faker


def _subtasks(fake, leads, start_date, end_date, effort):
    task_columns = [
        "Headline",
        "Group",
        "Start Date",
        "End Date",
        "Effort",
        "Assignee",
    ]
    subtasks = []
    num_subtasks = randint(5, 6)
    for _ in range(num_subtasks):
        subtask_headline = " ".join(fake.words(randint(2, 5))).title()
        subtask_group = choice(leads)
        subtask_start_date = fake.date_between(start_date, end_date)
        subtask_effort = randint(1, effort)
        subtask_end_date = subtask_start_date + timedelta(days=subtask_effort)
        task_lead = choice(leads)
        subtask_assignee = f"{task_lead}-DIR{random.randint(1, 5)}"
        subtasks.append(
            [
                subtask_headline,
                subtask_group,
                subtask_start_date,
                subtask_end_date,
                subtask_effort,
                subtask_assignee,
            ]
        )
        sub_df = pd.DataFrame(subtasks, columns=task_columns)
    return sub_df


def _reviews(metrics, measure, lead, assignee):
    start_date = datetime(2024, 3, 31)
    end_date = datetime.now()
    review_dates = []
    current_date = start_date
    while current_date <= end_date:
        review_dates.append(current_date)
        current_date += timedelta(days=7)

    err_msgs = {
        "xBOW": [
            "Status not updated",
            "Headline standards not followed",
            "Project completed but status not updated",
            "Effort remaining is not proportional",
            "Jira not updating latest story count",
            "JIRA reference not found",
        ],
        "SPAM": [
            "Emails not going via DNS",
            "Email Spam not reduced",
        ],
    }

    data = []
    for review_date in review_dates:
        num_errors = random.randint(1, 4)
        errors = random.sample(err_msgs.get(metrics), num_errors)
        error_string = "#".join(errors)
        error_count = sum(random.randint(5, 10) for _ in range(len(errors)))
        data.append(
            {
                "Date": review_date.strftime("%Y-%m-%d"),
                "Metric": metrics,
                "Measure": measure,
                "Lead": lead,
                "Assignee": assignee,
                "Notes": error_string,
                "Value": error_count,
            }
        )

    return pd.DataFrame(data)


def fake_bow_df(num_rows: int = 100, seed: int = 42) -> pd.DataFrame:
    fake = Faker()
    Faker.seed(seed)
    random.seed(seed)

    groups = ["DNS", "EES", "DMO", "RISK", "MDA"]
    cars = ["SOOR", "PRICING", "RISK", "DMO", "EES"]
    leads = ["AN", "BZ", "RC", "KL", "KA"]
    trains = groups
    stakeholders = [fake.name() for _ in range(20)]
    columns = [
        "Train",
        "Car",
        "Headline",
        "Group",
        "Lead",
        "Effort",
        "Errors",
        "Stakeholder",
        "Assignee",
        "Start Date",
        "End Date",
        "Subtasks",
        "Approvals",
        "Reviews",
    ]
    workflow = ["Step", "Who", "State", "Comments", "Is Waiting"]

    data = []
    for _ in range(num_rows):
        headline = " ".join(fake.words(randint(2, 5))).title()
        group = choice(groups)
        lead = choice(leads)
        train = choice(trains)
        car = choice(cars)
        effort = randint(1, 30)
        errors = randint(0, 100)
        stakeholder = choice(stakeholders)
        start_date = fake.date_between(date(2023, 1, 1), date(2023, 12, 31))
        end_date = start_date + timedelta(days=effort)
        assignee = f"{lead}-DIR{random.randint(1, 5)}"
        sub_df = _subtasks(fake, leads, start_date, end_date, effort)
        approvals = [
            [1, "Lead", "Waiting", "Entry Approval", True],
            [2, "Accountable", "Waiting", "Management Approval", False],
            [3, "SLT", "Waiting", "SLT Approval", False],
        ]
        appr_df = pd.DataFrame(approvals, columns=workflow)
        rv_df = _reviews("xBOW", "Errors", lead, assignee)
        data.append(
            [
                train,
                car,
                headline,
                group,
                lead,
                effort,
                errors,
                stakeholder,
                assignee,
                start_date,
                end_date,
                sub_df,
                appr_df,
                rv_df,
            ]
        )
    df = pd.DataFrame(data, columns=columns)
    return df


def fake_ait_df(num_rows=100):
    countries = ["China", "Japan", "Korea", "India", "Singapore"]
    desks = ["RATES", "LCT", "CREDIT", "TSY"]
    currencies = ["USD", "INR", "KRW", "CNY", "HKD", "SGD"]
    capabilities_l1 = ["Trading", "Operations", "Finance"]
    capabilities_l2 = {
        "Trading": [
            "Trade Capture",
            "Trading Venues",
            "Risk Management",
            "Electronic Trading",
        ],
        "Operations": ["Settlement", "Documentation"],
        "Finance": ["Subledger", "General Ledger"],
    }
    asset_classes = ["CASH", "FX", "RATES", "CMDY"]
    products = {
        "CASH": ["CASH", "MM", "DEPOSITS", "LOANS", "CP"],
        "FX": ["SPOT", "FXFWD", "FXSWP", "NDF", "NDS", "FXO", "EXOTICS"],
        "RATES": [
            "BONDS",
            "REPOS",
            "IRS",
            "CCS",
            "CAPFLR",
            "SWOPT",
            "NRXCCY",
            "TRS",
            "BONDFWD",
            "TBS",
            "SN",
            "FUTURES",
        ],
        "CMDY": [
            "FNO",
            "SWAPS",
            "OPTIONS",
            "FWD",
        ],
    }
    data = []
    for _ in range(num_rows):
        capability_l1 = random.choice(capabilities_l1)
        asset_class = random.choice(asset_classes)
        row = {
            "Country": random.choice(countries),
            "Desk": random.choice(desks),
            "Currency": random.choice(currencies),
            "Capability L1": capability_l1,
            "Capability L2": random.choice(capabilities_l2[capability_l1]),
            "Asset Class": asset_class,
            "Product": random.choice(products[asset_class]),
            "Application": f"AIT{random.randint(1, 25)}",
            "Score": random.randint(-100, 500),
        }
        data.append(row)
    return pd.DataFrame(data)
