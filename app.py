from flask import Flask, render_template, request
from stock_analysis import (
    get_cik_from_ticker,
    fetch_company_facts,
    plot_metric_over_time,
    plot_gross_profit_over_time,
    plot_eps_over_time,
    get_latest_eps_and_year,
    get_latest_revenue_and_year,
    get_latest_gross_profit_and_year,
)
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import plotly.graph_objs as go
import plotly.io as pio

app = Flask(__name__)


def create_plot_image():
    """Helper function to convert matplotlib plot to base64 image"""
    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    plt.close()
    return image_base64


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        ticker = request.form["ticker"].strip()
        if not ticker:
            return render_template("index.html", error="Please enter a ticker symbol")

        cik = get_cik_from_ticker(ticker)

        if not cik:
            return render_template(
                "index.html", error=f"CIK not found for ticker {ticker}"
            )

        try:
            facts = fetch_company_facts(cik)
            if not facts:
                return render_template(
                    "index.html", error=f"Financial data not found for {ticker}"
                )

            # Generate all requested plots
            plot_images = {}

            try:
                plot_metric_over_time(facts, "Revenues", label="Revenue")
                plot_images["revenue"] = create_plot_image()
            except Exception as e:
                plot_images["revenue"] = None
                print(f"Error generating revenue plot: {e}")

            try:
                plot_metric_over_time(facts, "GrossProfit", label="Gross Profit")
                plot_images["gross_profit"] = create_plot_image()
            except Exception as e:
                plot_images["gross_profit"] = None
                print(f"Error generating gross profit plot: {e}")

            try:
                plot_metric_over_time(
                    facts, "OperatingIncomeLoss", label="Operating Income"
                )
                plot_images["operating_income"] = create_plot_image()
            except Exception as e:
                plot_images["operating_income"] = None
                print(f"Error generating operating income plot: {e}")

            try:
                plot_metric_over_time(facts, "NetIncomeLoss", label="Net Income")
                plot_images["net_income"] = create_plot_image()
            except Exception as e:
                plot_images["net_income"] = None
                print(f"Error generating net income plot: {e}")

            try:
                plot_metric_over_time(
                    facts,
                    "CommonStockSharesOutstanding",
                    label="Shares Outstanding",
                    unit="shares",
                )
                plot_images["shares_outstanding"] = create_plot_image()
            except Exception as e:
                plot_images["shares_outstanding"] = None
                print(f"Error generating shares outstanding plot: {e}")

            try:
                plot_eps_over_time(facts)
                plot_images["eps"] = create_plot_image()
            except Exception as e:
                plot_images["eps"] = None
                print(f"Error generating EPS plot: {e}")

            try:
                plot_gross_profit_over_time(facts)
                plot_images["gross_profit_calc"] = create_plot_image()
            except Exception as e:
                plot_images["gross_profit_calc"] = None
                print(f"Error generating calculated gross profit plot: {e}")

            # Get key metrics (unchanged)
            eps, _ = (
                get_latest_eps_and_year(facts)
                if "NetIncomeLoss" in facts.get("facts", {}).get("us-gaap", {})
                else (None, None)
            )
            revenue, _ = (
                get_latest_revenue_and_year(facts)
                if "Revenues" in facts.get("facts", {}).get("us-gaap", {})
                else (None, None)
            )
            gross_profit, _ = (
                get_latest_gross_profit_and_year(facts)
                if "GrossProfit" in facts.get("facts", {}).get("us-gaap", {})
                else (None, None)
            )

            return render_template(
                "results.html",
                ticker=ticker.upper(),
                eps=eps,
                revenue=revenue,
                gross_profit=gross_profit,
                plot_images=plot_images,
            )

        except Exception as e:
            return render_template(
                "index.html", error=f"Error processing request: {str(e)}"
            )

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
