# -*- coding: utf-8 -*-
"""
Unit tests for Vorabpauschale and ETF tax calculations.
"""

import pytest
from vorabpauschale_dach.models import FundType, ChurchTax
from vorabpauschale_dach.calculator import (
    calculate_vorabpauschale,
    simulate_savings_plan,
    calculate_austria_etf,
    calculate_swiss_etf,
)


def test_standard_vorabpauschale_with_full_allowance():
    # 10.000 € start, 11.000 € end, 2.55% interest, equity fund (30% TFS), 1000 € allowance
    res = calculate_vorabpauschale(
        start_value=10000.0,
        end_value=11000.0,
        distributions=0.0,
        base_interest_rate=0.0255,
        fund_type=FundType.EQUITY,
        allowance=1000.0,
        church_tax=ChurchTax.NONE,
    )
    # raw_base_income = 10000 * 0.0255 * 0.7 = 178.50
    assert res.raw_base_income == 178.50
    assert res.actual_value_increase == 1000.0
    assert res.is_capped is False
    assert res.vorabpauschale == 178.50
    # 30% TFS -> taxable_base = 178.50 * 0.7 = 124.95
    assert res.taxable_base == 124.95
    assert res.allowance_used == 124.95
    assert res.taxable_amount_after_allowance == 0.0
    assert res.total_tax == 0.0


def test_vorabpauschale_tax_without_allowance():
    res = calculate_vorabpauschale(
        start_value=10000.0,
        end_value=11000.0,
        distributions=0.0,
        base_interest_rate=0.0255,
        fund_type=FundType.EQUITY,
        allowance=0.0,
        church_tax=ChurchTax.NONE,
    )
    assert res.vorabpauschale == 178.50
    assert res.taxable_base == 124.95
    assert res.taxable_amount_after_allowance == 124.95
    # KapESt 25% = 31.2375 -> 31.24
    assert res.kapest == pytest.approx(31.24, 0.02)
    # Soli 5.5% on KapESt = 1.718 -> 1.72
    assert res.soli == pytest.approx(1.72, 0.02)
    assert res.total_tax == pytest.approx(32.96, 0.05)


def test_capped_vorabpauschale_low_gain():
    # Gain is only 100 €, which is less than 178.50 €
    res = calculate_vorabpauschale(
        start_value=10000.0,
        end_value=10100.0,
        distributions=0.0,
        base_interest_rate=0.0255,
        fund_type=FundType.EQUITY,
        allowance=0.0,
    )
    assert res.is_capped is True
    assert res.capped_base_income == 100.0
    assert res.vorabpauschale == 100.0
    assert res.taxable_base == 70.0  # 30% TFS


def test_negative_performance_no_vorabpauschale():
    # Value drops from 10.000 to 9.000 (-1.000 €)
    res = calculate_vorabpauschale(
        start_value=10000.0,
        end_value=9000.0,
        distributions=0.0,
        base_interest_rate=0.0255,
    )
    assert res.is_capped is True
    assert res.vorabpauschale == 0.0
    assert res.total_tax == 0.0


def test_distributing_etf_high_payout():
    # Distributions (200 €) exceed base income (178.50 €)
    res = calculate_vorabpauschale(
        start_value=10000.0,
        end_value=10500.0,
        distributions=200.0,
        base_interest_rate=0.0255,
    )
    assert res.raw_base_income == 178.50
    # Vorabpauschale = max(0, 178.50 - 200) = 0.0
    assert res.vorabpauschale == 0.0
    assert res.total_tax == 0.0


def test_distributing_etf_partial_offset():
    # Distributions 100 € < 178.50 €
    res = calculate_vorabpauschale(
        start_value=10000.0,
        end_value=11000.0,
        distributions=100.0,
        base_interest_rate=0.0255,
        allowance=0.0,
    )
    assert res.vorabpauschale == 78.50
    assert res.taxable_base == pytest.approx(78.50 * 0.70, 0.01)


def test_fund_types_teilfreistellung():
    # Mixed fund: 15% TFS
    res_mixed = calculate_vorabpauschale(
        start_value=10000.0,
        end_value=11000.0,
        fund_type=FundType.MIXED,
        allowance=0.0,
    )
    assert res_mixed.teilfreistellung_percent == 15.0
    assert res_mixed.taxable_base == round(178.50 * 0.85, 2)

    # Real estate fund: 60% TFS
    res_re = calculate_vorabpauschale(
        start_value=10000.0,
        end_value=11000.0,
        fund_type=FundType.REAL_ESTATE,
        allowance=0.0,
    )
    assert res_re.teilfreistellung_percent == 60.0
    assert res_re.taxable_base == round(178.50 * 0.40, 2)

    # Other (bond fund): 0% TFS
    res_other = calculate_vorabpauschale(
        start_value=10000.0,
        end_value=11000.0,
        fund_type=FundType.OTHER,
        allowance=0.0,
    )
    assert res_other.teilfreistellung_percent == 0.0
    assert res_other.taxable_base == 178.50


def test_church_tax_calculation():
    # Church tax Bayern / BW (8%)
    res_by = calculate_vorabpauschale(
        start_value=10000.0,
        end_value=11000.0,
        fund_type=FundType.EQUITY,
        allowance=0.0,
        church_tax=ChurchTax.BAYERN_BW,
    )
    assert res_by.church_tax_amount > 0.0
    # Effective rate is approx 27.82% of taxable base
    effective_rate = res_by.total_tax / res_by.taxable_base
    assert effective_rate == pytest.approx(0.2782, 0.005)


def test_savings_plan_simulation():
    res_sim = simulate_savings_plan(
        initial_capital=5000.0,
        monthly_contribution=300.0,
        years=10,
        annual_growth_rate=0.07,
        annual_allowance=1000.0,
    )
    assert res_sim.total_years == 10
    assert len(res_sim.years) == 10
    # Total invested = 5000 + 300 * 12 * 10 = 41000 €
    assert res_sim.total_invested == 41000.0
    assert res_sim.final_portfolio_net > res_sim.total_invested
    assert res_sim.compound_interest_gain > 0.0


def test_austria_etf_calculation():
    res_at = calculate_austria_etf(
        portfolio_value=10000.0,
        annual_return=700.0,
        distributions=100.0,
    )
    assert res_at.kest_rate == 0.275
    assert res_at.tax_on_distributions == 27.50
    assert res_at.tax_on_deemed_distributed_income > 0.0
    assert res_at.total_kest > 27.50


def test_swiss_etf_calculation():
    res_ch = calculate_swiss_etf(
        portfolio_value=50000.0,
        capital_gain=3500.0,
        dividend_yield_pct=2.0,
        wealth_tax_rate_pct=0.30,
    )
    assert res_ch.capital_gain == 3500.0
    assert res_ch.taxable_dividend_or_interest == 1000.0  # 2% of 50k
    assert res_ch.wealth_tax_estimate == 150.0  # 0.3% of 50k
    assert res_ch.withholding_tax_reclaimable == 350.0  # 35% of 1000
