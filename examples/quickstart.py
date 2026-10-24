# -*- coding: utf-8 -*-
"""
Quickstart Example: DACH Vorabpauschale & ETF-Steuerrechner 2026.
"""

import sys
import os

# Add package root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from vorabpauschale_dach import (
    calculate_vorabpauschale,
    simulate_savings_plan,
    FundType,
    ChurchTax,
)


def main():
    print("--- 1. Vorabpauschale 2026 für thesaurierenden Welt-ETF (Aktienfonds) ---")
    res_de = calculate_vorabpauschale(
        start_value=25000.0,
        end_value=27500.0,
        distributions=0.0,
        base_interest_rate=0.0255,  # 2,55 %
        fund_type=FundType.EQUITY,  # 30 % Teilfreistellung
        allowance=1000.0,  # 1.000 € Sparerpauschbetrag
        church_tax=ChurchTax.NONE,
    )
    print(f"Portfoliowert zu Jahresbeginn: {res_de.start_value:.2f} €")
    print(f"Portfoliowert zum Jahresende : {res_de.end_value:.2f} € (Wertzuwachs: +{res_de.actual_value_increase:.2f} €)")
    print(f"Basisertrag (70 % v. 2,55 %) : {res_de.raw_base_income:.2f} €")
    print(f"Vorabpauschale ermittelt     : {res_de.vorabpauschale:.2f} €")
    print(f"Nach 30 % Teilfreistellung   : {res_de.taxable_base:.2f} €")
    print(f"Freibetrag aufgebraucht      : {res_de.allowance_used:.2f} €")
    print(f"Fällige Steuerlast           : {res_de.total_tax:.2f} €")

    print("\n--- 2. Zinseszins-Sparplan-Simulation (20 Jahre, 500 € mtl., 7 % p.a.) ---")
    sim = simulate_savings_plan(
        initial_capital=10000.0,
        monthly_contribution=500.0,
        years=20,
        annual_growth_rate=0.07,
        annual_allowance=1000.0,
    )
    print(f"Gesamt eingezahlt            : {sim.total_invested:.2f} €")
    print(f"Endvermögen (nach Steuern)   : {sim.final_portfolio_net:.2f} €")
    print(f"Erwirtschafteter Zinseszins  : {sim.compound_interest_gain:.2f} €")
    print(f"Kumulierte Vorabsteuer       : {sim.total_taxes_paid:.2f} €")


if __name__ == "__main__":
    main()
