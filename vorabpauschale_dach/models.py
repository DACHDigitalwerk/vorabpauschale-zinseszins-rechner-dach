# -*- coding: utf-8 -*-
"""
Data models and Enums for DACH Vorabpauschale, ETF-Steuer & Zinseszins Rechner 2026.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class FundType(str, Enum):
    """
    Fondskategorien gem. § 20 InvStG für die Teilfreistellung (TFS).
    """
    EQUITY = "equity"  # Aktienfonds (mind. 51 % Aktienquote -> 30 % TFS)
    MIXED = "mixed"  # Mischfonds (mind. 25 % Aktienquote -> 15 % TFS)
    REAL_ESTATE = "real_estate"  # Immobilienfonds Inland (60 % TFS)
    REAL_ESTATE_FOREIGN = "real_estate_foreign"  # Auslandsimmobilien (80 % TFS)
    OTHER = "other"  # Rentenfonds, Geldmarktfonds, Rohstoffe, Krypto (0 % TFS)

    @property
    def teilfreistellung_percent(self) -> float:
        mapping = {
            FundType.EQUITY: 30.0,
            FundType.MIXED: 15.0,
            FundType.REAL_ESTATE: 60.0,
            FundType.REAL_ESTATE_FOREIGN: 80.0,
            FundType.OTHER: 0.0,
        }
        return mapping[self]

    @property
    def description_de(self) -> str:
        mapping = {
            FundType.EQUITY: "Aktienfonds (mind. 51 % Aktien, 30 % TFS)",
            FundType.MIXED: "Mischfonds (mind. 25 % Aktien, 15 % TFS)",
            FundType.REAL_ESTATE: "Immobilienfonds Inland (60 % TFS)",
            FundType.REAL_ESTATE_FOREIGN: "Auslandsimmobilienfonds (80 % TFS)",
            FundType.OTHER: "Sonstige / Renten- & Geldmarktfonds (0 % TFS)",
        }
        return mapping[self]


class ChurchTax(str, Enum):
    """
    Kirchensteuersatz nach Bundesländern.
    """
    NONE = "none"  # Keine Kirchensteuer
    BAYERN_BW = "bayern_bw"  # Bayern / Baden-Württemberg (8 %)
    OTHER_STATES = "other"  # Übrige Bundesländer (9 %)

    @property
    def rate_multiplier(self) -> float:
        """
        Effektiver Steuersatz inklusive Abzugsfähigkeit der Kirchensteuer nach § 32d Abs. 1 EStG:
        e = (0.25 * (1 + 0.055)) / (1 + 0.25 * kirchensteuersatz)
        Formel: (25% + Soli + KiSt)/ (1 + KiSt * 25%)
        """
        if self == ChurchTax.NONE:
            return 0.26375  # 25% + 5.5% Soli auf 25% = 26.375%
        elif self == ChurchTax.BAYERN_BW:
            # 8% Kirchensteuer -> ca. 27.8186%
            # e = (0.25 + 0.055*0.25 + 0.08*0.25) / (1 + 0.08 * 0.25) = (0.25 + 0.01375 + 0.02) / 1.02 = 0.28375 / 1.02 ≈ 0.278186
            return 0.278186
        else:
            # 9% Kirchensteuer -> ca. 27.9951%
            # e = (0.25 + 0.01375 + 0.0225) / (1 + 0.09 * 0.25) = 0.28625 / 1.0225 ≈ 0.279951
            return 0.279951


class Country(str, Enum):
    DE = "DE"
    AT = "AT"
    CH = "CH"


@dataclass
class VorabpauschaleResultDE:
    """
    Ergebnis der Vorabpauschale nach § 18 InvStG für Deutschland.
    """
    start_value: float  # Rücknahmepreis/Portfoliowert zu Jahresbeginn
    end_value: float  # Portfoliowert zum Jahresende
    distributions: float  # Ausgeschüttete Erträge im Kalenderjahr
    base_interest_rate: float  # Basiszins der Bundesbank (z. B. 0.0255 für 2,55 %)
    raw_base_income: float  # 70 % des Basiszinses * Startwert
    actual_value_increase: float  # Endwert - Startwert + Ausschüttungen
    is_capped: bool  # True wenn Wertsteigerung < Basisertrag
    capped_base_income: float  # Gedeckelter Basisertrag
    vorabpauschale: float  # Capped Base Income - Ausschüttungen (mind. 0)
    fund_type: FundType
    teilfreistellung_percent: float
    taxable_base: float  # Nach Teilfreistellung
    allowance_available: float  # Verfügbarer Sparerpauschbetrag
    allowance_used: float  # Verrechneter Sparerpauschbetrag
    taxable_amount_after_allowance: float  # Zu versteuernder Betrag
    kapest: float  # 25 % Kapitalertragsteuer
    soli: float  # 5,5 % Soli auf KapESt
    church_tax_amount: float
    total_tax: float
    effective_tax_rate: float  # Total Tax / Vorabpauschale


@dataclass
class SavingsPlanYear:
    """
    Einzelnes Jahresergebnis einer Zinseszins-Sparplan-Simulation.
    """
    year: int
    portfolio_start: float
    annual_contribution: float
    gross_growth: float
    annual_distribution: float
    vorabpauschale: float
    tax_paid: float
    portfolio_end: float
    invested_cumulative: float


@dataclass
class SavingsPlanResult:
    """
    Gesamtergebnis der langfristigen ETF-Sparplan- und Zinseszins-Simulation.
    """
    years: List[SavingsPlanYear]
    total_years: int
    monthly_contribution: float
    annual_return_rate: float
    final_portfolio_gross: float
    final_portfolio_net: float
    total_invested: float
    total_taxes_paid: float
    compound_interest_gain: float


@dataclass
class AustriaResult:
    """
    Ergebnis für Österreich (KESt 27,5 %, ausschüttungsgleiche Erträge OeKB).
    """
    portfolio_value: float
    annual_return: float
    distributions: float
    kest_rate: float = 0.275
    tax_on_distributions: float = 0.0
    tax_on_deemed_distributed_income: float = 0.0
    total_kest: float = 0.0


@dataclass
class SwissResult:
    """
    Ergebnis für die Schweiz (steuerfreie Kursgewinne, Vermögenssteuer, Verrechnungssteuer 35 %).
    """
    portfolio_value: float
    capital_gain: float  # Grundsätzlich steuerfrei für Privatanleger gem. Art. 16 Abs. 3 DBG
    taxable_dividend_or_interest: float  # Ertragskomponente (ICTax)
    wealth_tax_estimate: float  # z. B. 0.3 % kantonal/kommunal
    withholding_tax_reclaimable: float  # 35 % Verrechnungssteuer
