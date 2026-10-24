# -*- coding: utf-8 -*-
"""
Calculation engine for DACH Vorabpauschale § 18 InvStG, ETF-Steuern and Zinseszins-Simulation.
"""

from typing import List, Optional
from .models import (
    ChurchTax,
    FundType,
    VorabpauschaleResultDE,
    SavingsPlanYear,
    SavingsPlanResult,
    AustriaResult,
    SwissResult,
)


def calculate_vorabpauschale(
    start_value: float,
    end_value: float,
    distributions: float = 0.0,
    base_interest_rate: float = 0.0255,  # 2.55 % Basiszins der Deutschen Bundesbank für 2026
    fund_type: FundType = FundType.EQUITY,
    allowance: float = 1000.0,  # Sparerpauschbetrag (1.000 € Einzel / 2.000 € Verheiratet)
    church_tax: ChurchTax = ChurchTax.NONE,
) -> VorabpauschaleResultDE:
    """
    Berechnet die Vorabpauschale gem. § 18 InvStG für Deutschland.
    """
    start_val = max(0.0, float(start_value))
    end_val = max(0.0, float(end_value))
    dist = max(0.0, float(distributions))
    rate = max(0.0, float(base_interest_rate))

    # 1. Unbereinigter Basisertrag: 70 % des Basiszinses * Startwert zu Jahresbeginn
    raw_base_income = start_val * rate * 0.70

    # 2. Tatsächliche Wertsteigerung im Kalenderjahr
    actual_increase = (end_val - start_val) + dist

    # 3. Deckelung gem. § 18 Abs. 1 Satz 3 InvStG:
    # Die Vorabpauschale ist auf den tatsächlichen Wertzuwachs begrenzt.
    # Bei Kursverlusten (actual_increase <= 0) ist die Vorabpauschale = 0.
    if actual_increase <= 0:
        capped_base_income = 0.0
        is_capped = True
    elif actual_increase < raw_base_income:
        capped_base_income = actual_increase
        is_capped = True
    else:
        capped_base_income = raw_base_income
        is_capped = False

    # 4. Abzug tatsächlicher Ausschüttungen:
    vorabpauschale = max(0.0, capped_base_income - dist)

    # 5. Teilfreistellung nach § 20 InvStG:
    tfs_pct = fund_type.teilfreistellung_percent
    taxable_base = vorabpauschale * (1.0 - (tfs_pct / 100.0))

    # 6. Sparerpauschbetrag verrechnen (§ 20 Abs. 9 EStG)
    avail_allowance = max(0.0, float(allowance))
    allowance_used = min(avail_allowance, taxable_base)
    taxable_after_allowance = max(0.0, taxable_base - allowance_used)

    # 7. Steuerermittlung (KapESt 25 % + Soli 5,5 % + evtl. Kirchensteuer)
    if church_tax == ChurchTax.NONE:
        kapest = taxable_after_allowance * 0.25
        soli = kapest * 0.055
        church_tax_amount = 0.0
        total_tax = kapest + soli
    else:
        # Gesetzliche Kirchensteuer-Formel gem. § 32d Abs. 1 Satz 3 EStG:
        # e = (0.25) / (1 + 0.25 * k)
        k_rate = 0.08 if church_tax == ChurchTax.BAYERN_BW else 0.09
        effective_kapest_rate = 0.25 / (1.0 + 0.25 * k_rate)
        kapest = taxable_after_allowance * effective_kapest_rate
        soli = kapest * 0.055
        church_tax_amount = kapest * k_rate
        total_tax = kapest + soli + church_tax_amount

    effective_rate = (total_tax / vorabpauschale) if vorabpauschale > 0 else 0.0

    return VorabpauschaleResultDE(
        start_value=start_val,
        end_value=end_val,
        distributions=dist,
        base_interest_rate=rate,
        raw_base_income=round(raw_base_income, 2),
        actual_value_increase=round(actual_increase, 2),
        is_capped=is_capped,
        capped_base_income=round(capped_base_income, 2),
        vorabpauschale=round(vorabpauschale, 2),
        fund_type=fund_type,
        teilfreistellung_percent=tfs_pct,
        taxable_base=round(taxable_base, 2),
        allowance_available=avail_allowance,
        allowance_used=round(allowance_used, 2),
        taxable_amount_after_allowance=round(taxable_after_allowance, 2),
        kapest=round(kapest, 2),
        soli=round(soli, 2),
        church_tax_amount=round(church_tax_amount, 2),
        total_tax=round(total_tax, 2),
        effective_tax_rate=round(effective_rate, 4),
    )


def simulate_savings_plan(
    initial_capital: float = 10000.0,
    monthly_contribution: float = 500.0,
    years: int = 15,
    annual_growth_rate: float = 0.07,  # 7 % p. a. erwartete Gesamtrendite
    distribution_yield: float = 0.0,  # 0 % = Thesaurierend, z. B. 0.02 = Ausschüttend
    base_interest_rate: float = 0.0255,  # 2.55 % Basiszins
    fund_type: FundType = FundType.EQUITY,
    annual_allowance: float = 1000.0,
    church_tax: ChurchTax = ChurchTax.NONE,
    pay_tax_from_portfolio: bool = True,
) -> SavingsPlanResult:
    """
    Simuliert einen ETF-Sparplan über mehrere Jahre unter Berücksichtigung
    des Zinseszins-Effekts und der jährlichen Vorabpauschale.
    """
    current_portfolio = float(initial_capital)
    cum_invested = float(initial_capital)
    total_tax_paid = 0.0
    sim_years: List[SavingsPlanYear] = []

    for y in range(1, years + 1):
        year_start = current_portfolio
        annual_savings = monthly_contribution * 12.0
        cum_invested += annual_savings

        # Vereinfachte unterjährige Zinsberechnung:
        # Startkapital verzinst sich voll, unterjährige Sparraten im Durchschnitt zur Hälfte
        growth = (year_start * annual_growth_rate) + (annual_savings * annual_growth_rate * 0.5)
        dist = (year_start + annual_savings * 0.5) * distribution_yield

        # Endwert vor Steuern
        year_end_pre_tax = year_start + annual_savings + growth

        # Vorabpauschale für das laufende Jahr (bezogen auf Startkapital + halbe Sparrate)
        eff_start = year_start + annual_savings * 0.5
        v_res = calculate_vorabpauschale(
            start_value=eff_start,
            end_value=year_end_pre_tax,
            distributions=dist,
            base_interest_rate=base_interest_rate,
            fund_type=fund_type,
            allowance=annual_allowance,
            church_tax=church_tax,
        )

        tax_due = v_res.total_tax
        total_tax_paid += tax_due

        if pay_tax_from_portfolio:
            current_portfolio = max(0.0, year_end_pre_tax - tax_due)
        else:
            current_portfolio = year_end_pre_tax

        sim_years.append(
            SavingsPlanYear(
                year=y,
                portfolio_start=round(year_start, 2),
                annual_contribution=round(annual_savings, 2),
                gross_growth=round(growth, 2),
                annual_distribution=round(dist, 2),
                vorabpauschale=v_res.vorabpauschale,
                tax_paid=round(tax_due, 2),
                portfolio_end=round(current_portfolio, 2),
                invested_cumulative=round(cum_invested, 2),
            )
        )

    final_gross = (
        current_portfolio + total_tax_paid if pay_tax_from_portfolio else current_portfolio
    )
    compound_gain = current_portfolio - cum_invested

    return SavingsPlanResult(
        years=sim_years,
        total_years=years,
        monthly_contribution=monthly_contribution,
        annual_return_rate=annual_growth_rate,
        final_portfolio_gross=round(final_gross, 2),
        final_portfolio_net=round(current_portfolio, 2),
        total_invested=round(cum_invested, 2),
        total_taxes_paid=round(total_tax_paid, 2),
        compound_interest_gain=round(compound_gain, 2),
    )


def calculate_austria_etf(
    portfolio_value: float,
    annual_return: float,
    distributions: float = 0.0,
    deemed_distributed_rate: float = 0.60,  # ca. 60 % der Kursgewinne gelten als ausschüttungsgleich
) -> AustriaResult:
    """
    ETF-Besteuerung für Österreich (27,5 % KESt).
    """
    p_val = max(0.0, float(portfolio_value))
    ret = max(0.0, float(annual_return))
    dist = max(0.0, float(distributions))

    kest_rate = 0.275
    tax_on_dist = dist * kest_rate

    # Ausschüttungsgleiche Erträge (bei Meldefonds über OeKB):
    # Ca. 60 % der ordentlichen und außerordentlichen Erträge unterliegen der jährlichen KESt.
    retained_gains = max(0.0, ret - dist)
    deemed_income = retained_gains * deemed_distributed_rate
    tax_on_deemed = deemed_income * kest_rate

    return AustriaResult(
        portfolio_value=p_val,
        annual_return=ret,
        distributions=dist,
        kest_rate=kest_rate,
        tax_on_distributions=round(tax_on_dist, 2),
        tax_on_deemed_distributed_income=round(tax_on_deemed, 2),
        total_kest=round(tax_on_dist + tax_on_deemed, 2),
    )


def calculate_swiss_etf(
    portfolio_value: float,
    capital_gain: float,
    dividend_yield_pct: float = 2.0,  # 2 % steuerbare Ertragskomponente (ICTax)
    wealth_tax_rate_pct: float = 0.30,  # 0,3 % kantonale/kommunale Vermögenssteuer
) -> SwissResult:
    """
    ETF-Besteuerung für die Schweiz:
    - Kursgewinne für private Anleger sind steuerfrei (Art. 16 Abs. 3 DBG).
    - Ertragskomponente (Dividenden/Zinsen laut ICTax-Liste) ist als Einkommen steuerbar.
    - Vermögenssteuer auf Gesamtwert.
    - Eidgenössische Verrechnungssteuer (35 %) ist vollständig rückforderbar (DA-1 / Wertschriftenverzeichnis).
    """
    p_val = max(0.0, float(portfolio_value))
    gain = float(capital_gain)

    taxable_yield = p_val * (dividend_yield_pct / 100.0)
    wealth_tax = p_val * (wealth_tax_rate_pct / 100.0)
    vst_reclaimable = taxable_yield * 0.35

    return SwissResult(
        portfolio_value=p_val,
        capital_gain=round(gain, 2),
        taxable_dividend_or_interest=round(taxable_yield, 2),
        wealth_tax_estimate=round(wealth_tax, 2),
        withholding_tax_reclaimable=round(vst_reclaimable, 2),
    )
