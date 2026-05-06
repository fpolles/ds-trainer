"""CSV dataset generators for TAKE_HOME exercises."""
from __future__ import annotations

import os
import random
from pathlib import Path

_REGISTRY: dict[str, "callable"] = {}


def register(key: str):
    def decorator(fn):
        _REGISTRY[key] = fn
        return fn
    return decorator


def generate(key: str, output_dir: Path) -> Path:
    """Generate a dataset and write it to output_dir. Returns the CSV path."""
    if key not in _REGISTRY:
        raise ValueError(f"Unknown dataset generator: '{key}'. Available: {list(_REGISTRY)}")
    output_dir.mkdir(parents=True, exist_ok=True)
    return _REGISTRY[key](output_dir)


def list_generators() -> list[str]:
    return list(_REGISTRY.keys())


@register("email_campaign")
def _email_campaign(output_dir: Path) -> Path:
    import pandas as pd
    rng = random.Random(42)
    rows = []
    for user_id in range(1, 201):
        group = "treatment" if user_id <= 100 else "control"
        for week in range(1, 9):
            baseline = rng.randint(2, 6)
            if group == "treatment" and week >= 5:
                purchases = baseline + rng.randint(1, 4)
            else:
                purchases = baseline + rng.randint(-1, 1)
            purchases = max(0, purchases)
            rows.append({"user_id": user_id, "week": week, "group": group, "purchases": purchases})
    df = pd.DataFrame(rows)
    path = output_dir / "email_campaign.csv"
    df.to_csv(path, index=False)
    return path


@register("rfm_transactions")
def _rfm_transactions(output_dir: Path) -> Path:
    import pandas as pd
    import datetime
    rng = random.Random(42)

    reference_date = datetime.date(2024, 4, 1)
    rows = []
    for customer_id in range(1, 501):
        segment = rng.choice(["champion", "regular", "at_risk", "lost"])
        match segment:
            case "champion":
                n_orders = rng.randint(8, 20)
                days_back_max = 30
                avg_value = rng.uniform(80, 200)
            case "regular":
                n_orders = rng.randint(3, 7)
                days_back_max = 90
                avg_value = rng.uniform(30, 80)
            case "at_risk":
                n_orders = rng.randint(2, 5)
                days_back_max = 180
                avg_value = rng.uniform(20, 60)
            case "lost":
                n_orders = rng.randint(1, 2)
                days_back_max = 365
                avg_value = rng.uniform(10, 40)
            case _:
                n_orders = 1
                days_back_max = 200
                avg_value = 30.0

        last_purchase_days = rng.randint(1, days_back_max)
        for i in range(n_orders):
            days_ago = last_purchase_days + rng.randint(0, 30) * i
            order_date = reference_date - datetime.timedelta(days=days_ago)
            order_value = round(avg_value * rng.uniform(0.7, 1.3), 2)
            rows.append({
                "customer_id": customer_id,
                "order_date": order_date.isoformat(),
                "order_value": order_value,
            })

    df = pd.DataFrame(rows)
    path = output_dir / "rfm_transactions.csv"
    df.to_csv(path, index=False)
    return path


@register("house_prices")
def _house_prices(output_dir: Path) -> Path:
    import pandas as pd
    rng = random.Random(42)
    rows = []
    neighborhoods = ["Downtown", "Suburbs", "Uptown", "Riverside"]
    for i in range(300):
        sqft = rng.randint(800, 3500)
        bedrooms = rng.randint(1, 6)
        bathrooms = rng.randint(1, 4)
        age = rng.randint(0, 60)
        neighborhood = rng.choice(neighborhoods)
        n_score = {"Downtown": 1.3, "Uptown": 1.2, "Suburbs": 1.0, "Riverside": 1.1}[neighborhood]
        price = (sqft * 200 + bedrooms * 10000 - age * 500) * n_score * rng.uniform(0.85, 1.15)
        rows.append({
            "id": i + 1,
            "sqft": sqft,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "age_years": age,
            "neighborhood": neighborhood,
            "price": round(price, 0),
        })
    df = pd.DataFrame(rows)
    path = output_dir / "house_prices.csv"
    df.to_csv(path, index=False)
    return path


@register("churn_data")
def _churn_data(output_dir: Path) -> Path:
    import pandas as pd
    rng = random.Random(42)
    rows = []
    for user_id in range(1, 1001):
        tenure_months = rng.randint(1, 48)
        monthly_spend = round(rng.uniform(10, 200), 2)
        num_support_contacts = rng.randint(0, 10)
        plan = rng.choice(["basic", "standard", "premium"])
        churn_prob = max(0, min(1,
            0.3
            - 0.005 * tenure_months
            + 0.05 * num_support_contacts
            + (0.2 if plan == "basic" else 0)
            - (0.1 if plan == "premium" else 0)
        ))
        churned = int(rng.random() < churn_prob)
        rows.append({
            "user_id": user_id,
            "tenure_months": tenure_months,
            "monthly_spend": monthly_spend,
            "num_support_contacts": num_support_contacts,
            "plan": plan,
            "churned": churned,
        })
    df = pd.DataFrame(rows)
    path = output_dir / "churn_data.csv"
    df.to_csv(path, index=False)
    return path
