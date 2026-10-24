# -*- coding: utf-8 -*-
"""
Command line interface for dach-vorabpauschale.
"""

import argparse
import json
import sys
import os

try:
    from .models import FundType, ChurchTax, Country
    from .calculator import (
        calculate_vorabpauschale,
        simulate_savings_plan,
        calculate_austria_etf,
        calculate_swiss_etf,
    )
except ImportError:
    # Fallback if executed as a direct script
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from vorabpauschale_dach.models import FundType, ChurchTax, Country
    from vorabpauschale_dach.calculator import (
        calculate_vorabpauschale,
        simulate_savings_plan,
        calculate_austria_etf,
        calculate_swiss_etf,
    )


def main():
    parser = argparse.ArgumentParser(
        description="DACH Vorabpauschale-, ETF-Steuer- & Zinseszins-Rechner 2026 (§ 18 InvStG, DE / AT / CH)"
    )
    parser.add_argument(
        "--country",
        choices=["DE", "AT", "CH"],
        default="DE",
        help="Länderregime (DE = InvStG, AT = KESt OeKB, CH = ICTax Vermögenssteuer)",
    )
    parser.add_argument(
        "--start-value",
        type=float,
        default=10000.0,
        help="Portfoliowert / Rücknahmepreis zu Jahresbeginn (€ / CHF)",
    )
    parser.add_argument(
        "--end-value",
        type=float,
        default=11000.0,
        help="Portfoliowert / Rücknahmepreis zum Jahresende (€ / CHF)",
    )
    parser.add_argument(
        "--distributions",
        type=float,
        default=0.0,
        help="Ausgeschüttete Erträge im Kalenderjahr (€ / CHF)",
    )
    parser.add_argument(
        "--basiszins",
        type=float,
        default=0.0255,
        help="Basiszins der Bundesbank (Standard 0.0255 für 2,55 Prozent in 2026)",
    )
    parser.add_argument(
        "--fund-type",
        choices=["equity", "mixed", "real_estate", "real_estate_foreign", "other"],
        default="equity",
        help="Fondskategorie für Teilfreistellung (equity=30 Prozent, mixed=15 Prozent, real_estate=60 Prozent)",
    )
    parser.add_argument(
        "--allowance",
        type=float,
        default=1000.0,
        help="Verfügbarer Sparerpauschbetrag (€)",
    )
    parser.add_argument(
        "--church-tax",
        choices=["none", "bayern_bw", "other"],
        default="none",
        help="Kirchensteuersatz (none, bayern_bw=8 Prozent, other=9 Prozent)",
    )
    parser.add_argument(
        "--simulate-years",
        type=int,
        default=0,
        help="Simulationsdauer in Jahren für ETF-Sparplan (z.B. 10, 20 oder 30 Jahre)",
    )
    parser.add_argument(
        "--monthly-savings",
        type=float,
        default=500.0,
        help="Monatliche Sparrate für Sparplan-Simulation (€ / CHF)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Ergebnis als JSON formatieren",
    )

    args = parser.parse_args()

    fund_type_enum = FundType(args.fund_type)
    church_tax_enum = ChurchTax(args.church_tax)

    if args.simulate_years > 0:
        sim_res = simulate_savings_plan(
            initial_capital=args.start_value,
            monthly_contribution=args.monthly_savings,
            years=args.simulate_years,
            annual_growth_rate=0.07,
            distribution_yield=0.0,
            base_interest_rate=args.basiszins,
            fund_type=fund_type_enum,
            annual_allowance=args.allowance,
            church_tax=church_tax_enum,
        )
        if args.json:
            out_data = {
                "simulation": {
                    "years": sim_res.total_years,
                    "monthly_contribution": sim_res.monthly_contribution,
                    "total_invested": sim_res.total_invested,
                    "final_portfolio_net": sim_res.final_portfolio_net,
                    "total_taxes_paid": sim_res.total_taxes_paid,
                    "compound_interest_gain": sim_res.compound_interest_gain,
                    "details": [y.__dict__ for y in sim_res.years],
                }
            }
            print(json.dumps(out_data, indent=2, ensure_ascii=False))
        else:
            print("======================================================================")
            print("📈 ETF-SPARPLAN & ZINSESZINS-SIMULATION (INVSTG § 18)")
            print("======================================================================")
            print(f"Laufzeit            : {sim_res.total_years} Jahre")
            print(f"Monatliche Sparrate : {sim_res.monthly_contribution:.2f} €")
            print(f"Eigene Einzahlungen : {sim_res.total_invested:.2f} €")
            print(f"Endvermögen (netto) : {sim_res.final_portfolio_net:.2f} €")
            print(f"Gezahlte Steuern    : {sim_res.total_taxes_paid:.2f} €")
            print(f"Zinseszins-Gewinn   : {sim_res.compound_interest_gain:.2f} €")
        return

    if args.country == "DE":
        res = calculate_vorabpauschale(
            start_value=args.start_value,
            end_value=args.end_value,
            distributions=args.distributions,
            base_interest_rate=args.basiszins,
            fund_type=fund_type_enum,
            allowance=args.allowance,
            church_tax=church_tax_enum,
        )
        if args.json:
            data = {
                "country": "DE",
                "start_value": res.start_value,
                "end_value": res.end_value,
                "distributions": res.distributions,
                "base_interest_rate_percent": res.base_interest_rate * 100,
                "raw_base_income": res.raw_base_income,
                "actual_value_increase": res.actual_value_increase,
                "is_capped": res.is_capped,
                "vorabpauschale": res.vorabpauschale,
                "fund_type": res.fund_type.value,
                "teilfreistellung_percent": res.teilfreistellung_percent,
                "taxable_base": res.taxable_base,
                "allowance_used": res.allowance_used,
                "taxable_amount_after_allowance": res.taxable_amount_after_allowance,
                "kapest": res.kapest,
                "soli": res.soli,
                "church_tax": res.church_tax_amount,
                "total_tax": res.total_tax,
                "effective_tax_rate_percent": res.effective_tax_rate * 100,
            }
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print("======================================================================")
            print("🇩🇪 VORABPAUSCHALE-BERECHNUNG 2026 (§ 18 INVSTG)")
            print("======================================================================")
            print(f"Portfoliowert 01.01.: {res.start_value:10.2f} €")
            print(f"Portfoliowert 31.12.: {res.end_value:10.2f} €")
            print(f"Ausschüttungen      : {res.distributions:10.2f} €")
            print(f"Wertsteigerung      : {res.actual_value_increase:10.2f} €")
            print(f"Basiszins (2026)    : {res.base_interest_rate*100:10.2f} %")
            print(f"Basisertrag (70 %)  : {res.raw_base_income:10.2f} €")
            print(f"Gedeckelt auf Zuwachs: {'JA' if res.is_capped else 'NEIN'}")
            print(f"VORABPAUSCHALE      : {res.vorabpauschale:10.2f} €")
            print("----------------------------------------------------------------------")
            print(f"Teilfreistellung    : {res.teilfreistellung_percent:10.1f} % ({res.fund_type.description_de})")
            print(f"Steuerliche Basis   : {res.taxable_base:10.2f} €")
            print(f"Freibetrag genutzt  : {res.allowance_used:10.2f} €")
            print(f"Zu versteuern       : {res.taxable_amount_after_allowance:10.2f} €")
            print("----------------------------------------------------------------------")
            print(f"KapESt (25 %)       : {res.kapest:10.2f} €")
            print(f"Soli (5,5 % KapESt) : {res.soli:10.2f} €")
            if res.church_tax_amount > 0:
                print(f"Kirchensteuer       : {res.church_tax_amount:10.2f} €")
            print(f"GESAMT-STEUERLAST   : {res.total_tax:10.2f} €")
            print("======================================================================")

    elif args.country == "AT":
        gain = args.end_value - args.start_value
        res_at = calculate_austria_etf(
            portfolio_value=args.start_value,
            annual_return=gain,
            distributions=args.distributions,
        )
        if args.json:
            print(json.dumps(res_at.__dict__, indent=2, ensure_ascii=False))
        else:
            print("======================================================================")
            print("🇦🇹 ÖSTERREICH ETF-BESTEUERUNG (KEST 27,5 %)")
            print("======================================================================")
            print(f"Portfoliowert       : {res_at.portfolio_value:.2f} €")
            print(f"Jahresertrag / Zuwachs: {res_at.annual_return:.2f} €")
            print(f"Ausschüttungen      : {res_at.distributions:.2f} €")
            print(f"KESt Ausschüttungen : {res_at.tax_on_distributions:.2f} €")
            print(f"KESt ausschüttungsgleich (OeKB): {res_at.tax_on_deemed_distributed_income:.2f} €")
            print(f"Gesamt-KESt         : {res_at.total_kest:.2f} €")

    elif args.country == "CH":
        gain = args.end_value - args.start_value
        res_ch = calculate_swiss_etf(
            portfolio_value=args.start_value,
            capital_gain=gain,
        )
        if args.json:
            print(json.dumps(res_ch.__dict__, indent=2, ensure_ascii=False))
        else:
            print("======================================================================")
            print("🇨🇭 SCHWEIZ ETF-BESTEUERUNG (ICTAX & VERMÖGENSSTEUER)")
            print("======================================================================")
            print(f"Portfoliowert       : {res_ch.portfolio_value:.2f} CHF")
            print(f"Kursgewinn          : {res_ch.capital_gain:.2f} CHF (STEUERFREI)")
            print(f"Steuerbarer Ertrag (ICTax): {res_ch.taxable_dividend_or_interest:.2f} CHF")
            print(f"Geschätzte Vermögenssteuer: {res_ch.wealth_tax_estimate:.2f} CHF")
            print(f"Rückforderbare Verrechnungssteuer (35 %): {res_ch.withholding_tax_reclaimable:.2f} CHF")


if __name__ == "__main__":
    main()
