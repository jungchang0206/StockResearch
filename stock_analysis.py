import requests
import os
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def fetch_company_facts(cik):
    headers = {"User-Agent": "StockResearcher (jungchang02062004@gmail.com)"}
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    response = requests.get(url, headers=headers)
    return response.json()


def get_cik_from_ticker(ticker):
    headers = {"User-Agent": "StockResearcher (jungchang02062004@gmail.com)"}
    url = f"https://www.sec.gov/files/company_tickers.json"
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        for entry in data.values():
            if entry["ticker"] == ticker.upper():
                return str(entry["cik_str"]).zfill(10)
        return None
    except Exception as e:
        print(f"Error fetching CIK: {e}")
        return None


def get_latest_eps_and_year(facts):
    try:
        net_income_facts = facts["facts"]["us-gaap"]["NetIncomeLoss"]["units"]["USD"]
        shares_facts = facts["facts"]["us-gaap"]["CommonStockSharesOutstanding"][
            "units"
        ]["shares"]
        latest_net_income_fact = sorted(
            net_income_facts, key=lambda x: x["end"], reverse=True
        )[0]
        latest_shares_fact = sorted(shares_facts, key=lambda x: x["end"], reverse=True)[
            0
        ]
        eps = latest_net_income_fact["val"] / latest_shares_fact["val"]
        year = latest_net_income_fact["end"][:4]
        return eps, year
    except Exception as e:
        print(f"Error calculating EPS: {e}")
        return None, None


def get_latest_revenue_and_year(facts):
    try:
        revenue_facts = facts["facts"]["us-gaap"]["Revenues"]["units"]["USD"]
        latest_revenue_fact = sorted(
            revenue_facts, key=lambda x: x["end"], reverse=True
        )[0]
        revenue = latest_revenue_fact["val"]
        year = latest_revenue_fact["end"][:4]
        return revenue, year
    except Exception as e:
        print(f"Error fetching Revenue: {e}")
        return None, None


def get_latest_gross_profit_and_year(facts):
    try:
        gross_profit_facts = facts["facts"]["us-gaap"]["GrossProfit"]["units"]["USD"]
        latest_gross_profit_fact = sorted(
            gross_profit_facts, key=lambda x: x["end"], reverse=True
        )[0]
        gross_profit = latest_gross_profit_fact["val"]
        year = latest_gross_profit_fact["end"][:4]
        return gross_profit, year
    except Exception as e:
        print(f"Error fetching Gross Profit: {e}")
        return None, None


def get_latest_operating_income_and_year(facts):
    try:
        operating_income_facts = facts["facts"]["us-gaap"]["OperatingIncomeLoss"][
            "units"
        ]["USD"]
        latest_operating_income_fact = sorted(
            operating_income_facts, key=lambda x: x["end"], reverse=True
        )[0]
        operating_income = latest_operating_income_fact["val"]
        year = latest_operating_income_fact["end"][:4]
        return operating_income, year
    except Exception as e:
        print(f"Error fetching Operating Income: {e}")
        return None, None


def save_all_us_gaap_metadata_to_txt(facts, filename="us_gaap_metadata.txt"):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(current_dir, filename)
        us_gaap_facts = facts["facts"]["us-gaap"]
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("=== All US GAAP Financial Metadata (latest available) ===\n")
            for tag, tag_data in us_gaap_facts.items():
                units = tag_data.get("units", {})
                if "USD" in units:
                    latest_fact = sorted(
                        units["USD"], key=lambda x: x["end"], reverse=True
                    )[0]
                    value = latest_fact["val"]
                    end_date = latest_fact["end"]
                    f.write(f"{tag} \n")
            f.write("========================================================\n")
        print(f"US GAAP metadata saved to {filepath}")
    except Exception as e:
        print(f"Error saving US GAAP metadata: {e}")


def extract_metric(facts, tag, unit="USD"):
    try:
        tag_facts = facts["facts"]["us-gaap"][tag]["units"][unit]
        latest_fact = sorted(tag_facts, key=lambda x: x["end"], reverse=True)[0]
        return latest_fact["val"], latest_fact["end"]
    except Exception:
        return None, None


def extract_eps(facts):
    net_income, _ = extract_metric(facts, "NetIncomeLoss")
    shares, _ = extract_metric(facts, "CommonStockSharesOutstanding", unit="shares")
    if net_income is not None and shares is not None and shares != 0:
        return net_income / shares
    return None


def extract_ebitda(facts):
    # EBITDA ≈ OperatingIncomeLoss + Depreciation
    op_income, _ = extract_metric(facts, "OperatingIncomeLoss")
    dep_amort, _ = extract_metric(facts, "Depreciation")
    if op_income is not None and dep_amort is not None:
        return op_income + dep_amort
    return None


def print_key_metrics(facts):
    metrics = {
        "Gross Profit": extract_metric(facts, "GrossProfit"),
        "Operating Income": extract_metric(facts, "OperatingIncomeLoss"),
        "Net Income": extract_metric(facts, "NetIncomeLoss"),
        "EPS": (extract_eps(facts), None),
        "Shares Outstanding": extract_metric(
            facts, "CommonStockSharesOutstanding", unit="shares"
        ),
        "EBITDA": (extract_ebitda(facts), None),
    }
    print("=== Key Financial Metrics (latest available) ===")
    for name, (val, date) in metrics.items():
        if val is not None:
            if date:
                print(f"{name}: {val} (Period ending: {date})")
            else:
                print(f"{name}: {val}")
        else:
            print(f"{name}: Not available or cannot be calculated")
    print("===============================================")


def plot_metric_over_time(facts, tag, label=None, unit="USD"):
    """Plot a single US GAAP metric over time if available."""
    try:
        tag_facts = facts["facts"]["us-gaap"][tag]["units"][unit]
        data = [
            (fact["end"], fact["val"])
            for fact in tag_facts
            if "end" in fact and "val" in fact
        ]
        if not data:
            print(f"No data for {label or tag}")
            return
        data.sort()
        dates = [pd.to_datetime(d[0]) for d in data]
        values = [d[1] for d in data]
        plt.figure(figsize=(10, 6))
        plt.plot(dates, values, marker="o", linewidth=2)
        plt.title(f"{label or tag} Over Time")
        plt.xlabel("Period End Date")
        plt.ylabel(f"{label or tag} ({unit})")
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.tight_layout()
        # plt.show()
    except Exception as e:
        print(f"Error plotting {label or tag}: {e}")


def plot_eps_over_time(facts):
    """Plot EPS over time if possible."""
    try:
        net_income_facts = facts["facts"]["us-gaap"]["NetIncomeLoss"]["units"]["USD"]
        shares_facts = facts["facts"]["us-gaap"]["CommonStockSharesOutstanding"][
            "units"
        ]["shares"]
        net_income_dict = {
            fact["end"]: fact["val"]
            for fact in net_income_facts
            if "end" in fact and "val" in fact
        }
        shares_dict = {
            fact["end"]: fact["val"]
            for fact in shares_facts
            if "end" in fact and "val" in fact
        }
        periods = sorted(set(net_income_dict.keys()) & set(shares_dict.keys()))
        if not periods:
            print("No overlapping periods for EPS calculation.")
            return
        eps_values = [
            net_income_dict[p] / shares_dict[p] if shares_dict[p] != 0 else None
            for p in periods
        ]
        dates = [pd.to_datetime(p) for p in periods]
        plt.figure(figsize=(10, 6))
        plt.plot(dates, eps_values, marker="o", linewidth=2)
        plt.title("EPS Over Time")
        plt.xlabel("Period End Date")
        plt.ylabel("EPS (USD)")
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.tight_layout()
        # plt.show()  # <-- Remove or comment out this line
    except Exception as e:
        print(f"Error plotting EPS: {e}")


def plot_ebitda_over_time(facts):
    """Plot EBITDA over time if possible."""
    try:
        op_income_facts = facts["facts"]["us-gaap"]["OperatingIncomeLoss"]["units"][
            "USD"
        ]
        dep_facts = (
            facts["facts"]["us-gaap"]
            .get("Depreciation", {})
            .get("units", {})
            .get("USD", [])
        )
        op_income_dict = {
            fact["end"]: fact["val"]
            for fact in op_income_facts
            if "end" in fact and "val" in fact
        }
        dep_dict = {
            fact["end"]: fact["val"]
            for fact in dep_facts
            if "end" in fact and "val" in fact
        }
        periods = sorted(set(op_income_dict.keys()) & set(dep_dict.keys()))
        if not periods:
            print("No overlapping periods for EBITDA calculation.")
            return
        ebitda_values = [op_income_dict[p] + dep_dict[p] for p in periods]
        dates = [pd.to_datetime(p) for p in periods]
        plt.figure(figsize=(10, 6))
        plt.plot(dates, ebitda_values, marker="o", linewidth=2)
        plt.title("EBITDA Over Time")
        plt.xlabel("Period End Date")
        plt.ylabel("EBITDA (USD)")
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.tight_layout()
        # plt.show()  # <-- Remove or comment out this line
    except Exception as e:
        print(f"Error plotting EBITDA: {e}")


def plot_gross_profit_over_time(facts):
    """Plot Gross Profit over time, always calculated as Revenues - CostOfRevenue."""
    try:
        us_gaap = facts["facts"]["us-gaap"]
        # Always calculate from Revenues and CostOfRevenue
        if (
            "Revenues" in us_gaap
            and "CostOfRevenue" in us_gaap
            and "USD" in us_gaap["Revenues"]["units"]
            and "USD" in us_gaap["CostOfRevenue"]["units"]
        ):
            rev_facts = us_gaap["Revenues"]["units"]["USD"]
            cost_facts = us_gaap["CostOfRevenue"]["units"]["USD"]
            rev_dict = {
                fact["end"]: fact["val"]
                for fact in rev_facts
                if "end" in fact and "val" in fact
            }
            cost_dict = {
                fact["end"]: fact["val"]
                for fact in cost_facts
                if "end" in fact and "val" in fact
            }
            periods = sorted(set(rev_dict.keys()) & set(cost_dict.keys()))
            data = [(p, rev_dict[p] - cost_dict[p]) for p in periods]
        else:
            print(
                "Cannot calculate Gross Profit: missing Revenues or CostOfRevenue data."
            )
            return

        if not data:
            print("No data for Gross Profit")
            return
        data.sort()
        dates = [pd.to_datetime(d[0]) for d in data]
        values = [d[1] for d in data]
        plt.figure(figsize=(10, 6))
        plt.plot(dates, values, marker="o", linewidth=2)
        plt.title("Gross Profit Over Time (Calculated)")
        plt.xlabel("Period End Date")
        plt.ylabel("Gross Profit (USD)")
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.tight_layout()
        # plt.show()  # <-- Remove or comment out this line
    except Exception as e:
        print(f"Error plotting Gross Profit: {e}")


# # Example usage:
# ticker = "GOOG"
# cik = get_cik_from_ticker(ticker)
# if cik:
#     facts = fetch_company_facts(cik)
#     plot_metric_over_time(facts, "Revenues", label="Revenue")
#     plot_metric_over_time(facts, "GrossProfit", label="Gross Profit")
#     plot_metric_over_time(facts, "OperatingIncomeLoss", label="Operating Income")
#     plot_metric_over_time(facts, "NetIncomeLoss", label="Net Income")
#     plot_metric_over_time(facts, "CommonStockSharesOutstanding", label="Shares Outstanding", unit="shares")
#     plot_eps_over_time(facts)
#     plot_gross_profit_over_time(facts)
# else:
#     print(f"CIK not found for ticker {ticker}")
