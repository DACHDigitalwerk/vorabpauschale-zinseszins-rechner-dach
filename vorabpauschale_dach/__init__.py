# -*- coding: utf-8 -*-
"""
DACH Vorabpauschale-, ETF-Steuer- & Zinseszins-Rechner 2026.
"""

from .models import (
    FundType,
    ChurchTax,
    Country,
    VorabpauschaleResultDE,
    SavingsPlanYear,
    SavingsPlanResult,
    AustriaResult,
    SwissResult,
)
from .calculator import (
    calculate_vorabpauschale,
    simulate_savings_plan,
    calculate_austria_etf,
    calculate_swiss_etf,
)

__version__ = "2026.1.0"
__all__ = [
    "FundType",
    "ChurchTax",
    "Country",
    "VorabpauschaleResultDE",
    "SavingsPlanYear",
    "SavingsPlanResult",
    "AustriaResult",
    "SwissResult",
    "calculate_vorabpauschale",
    "simulate_savings_plan",
    "calculate_austria_etf",
    "calculate_swiss_etf",
]
