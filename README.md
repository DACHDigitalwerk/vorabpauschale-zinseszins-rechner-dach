# DACH Vorabpauschale-, ETF-Steuer- & Zinseszins-Rechner 2026 📈

[![CI Matrix](https://github.com/DACHDigitalwerk/vorabpauschale-zinseszins-rechner-dach/actions/workflows/ci.yml/badge.svg)](https://github.com/DACHDigitalwerk/vorabpauschale-zinseszins-rechner-dach/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Platform: Web App](https://img.shields.io/badge/Live%20App-DACH%20Digitalwerk-emerald.svg)](https://dachdigitalwerk.github.io/vorabpauschale-etf-rechner/)

Rechtskonformer und performanter Python- und CLI-Präzisionsrechner zur Ermittlung der **Vorabpauschale gem. § 18 InvStG**, der **Teilfreistellung nach § 20 InvStG**, langfristiger **Zinseszins-Sparpläne** sowie Vergleichsberechnungen für Österreich (KESt 27,5 % & OeKB Meldefonds) und die Schweiz (steuerfreie Kursgewinne gem. Art. 16 Abs. 3 DBG & ICTax Vermögenssteuer).

---

## 🌟 Kernfunktionen

1. **Vorabpauschale 2026 nach § 18 InvStG (Deutschland):**
   - Basisertrag = 70 % des Basiszinses der Deutschen Bundesbank (2026: 2,55 %) * Rücknahmepreis zu Jahresbeginn.
   - Gesetzliche Deckelung auf die tatsächliche Wertsteigerung (bei Kursverlusten = 0,00 €).
   - Abzug von tatsächlich ausgeschütteten Erträgen im Kalenderjahr.
2. **Teilfreistellung (TFS) gem. § 20 InvStG:**
   - **Aktienfonds (mind. 51 % Aktienquote):** 30 % steuerfrei.
   - **Mischfonds (mind. 25 % Aktienquote):** 15 % steuerfrei.
   - **Immobilienfonds:** 60 % (Inland) bzw. 80 % (Auslandsimmobilien) steuerfrei.
   - **Sonstige / Rentenfonds:** 0 % steuerfrei.
3. **Kapitalertragsteuer & Freibeträge:**
   - 25 % KapESt + 5,5 % Solidaritätszuschlag (= 26,375 %).
   - Berücksichtigung von Kirchensteuer (Bayern / BW 8 % -> 27,82 %, andere Bundesländer 9 % -> 27,99 %).
   - Automatischer Abzug des Sparerpauschbetrags (1.000 € Einzel / 2.000 € Zusammenveranlagung).
4. **Zinseszins-Sparplan-Simulator über bis zu 30 Jahre:**
   - Monatliche Sparraten, historische Renditeerwartung (z.B. MSCI World / ACWI mit 7 % p.a.).
   - Dynamische Berücksichtigung der jährlich anfallenden Vorabsteuer.
5. **DACH-Ländervergleich:**
   - **Österreich:** 27,5 % KESt auf Ausschüttungen und ausschüttungsgleiche Erträge via OeKB-Meldung.
   - **Schweiz:** Steuerfreie private Kursgewinne gem. Art. 16 Abs. 3 DBG, steuerbare Ertragskomponente (ICTax ESTV), kantonale Vermögenssteuer und 35 % rückforderbare Eidgenössische Verrechnungssteuer.

---

## 🚀 Installation

```bash
pip install .
```

Oder im Entwicklermodus:
```bash
git clone https://github.com/DACHDigitalwerk/vorabpauschale-zinseszins-rechner-dach.git
cd vorabpauschale-zinseszins-rechner-dach
pip install -e ".[dev]"
```

---

## 💻 CLI-Nutzung (`dach-vorabpauschale`)

### 1. Standard-Vorabpauschale berechnen
```bash
dach-vorabpauschale --start-value 10000 --end-value 11000 --fund-type equity --allowance 1000
```

### 2. Ausgabe als maschinenlesbares JSON
```bash
dach-vorabpauschale --start-value 25000 --end-value 27500 --fund-type equity --allowance 0 --json
```

### 3. ETF-Sparplan über 20 Jahre simulieren
```bash
dach-vorabpauschale --start-value 10000 --monthly-savings 500 --simulate-years 20
```

### 4. Österreich oder Schweiz analysieren
```bash
dach-vorabpauschale --country AT --start-value 10000 --end-value 10700 --distributions 150
dach-vorabpauschale --country CH --start-value 50000 --end-value 53500
```

---

## 🐍 Python-API

```python
from vorabpauschale_dach import calculate_vorabpauschale, FundType, ChurchTax

res = calculate_vorabpauschale(
    start_value=15000.0,
    end_value=16200.0,
    distributions=0.0,
    base_interest_rate=0.0255, # 2,55 % in 2026
    fund_type=FundType.EQUITY, # 30 % Teilfreistellung
    allowance=1000.0,          # 1.000 € Sparerpauschbetrag
    church_tax=ChurchTax.NONE
)

print(f"Vorabpauschale: {res.vorabpauschale:.2f} €")
print(f"Steuerpflichtiger Anteil: {res.taxable_base:.2f} €")
print(f"Steuerlast: {res.total_tax:.2f} €")
```

---

## 🧪 Tests

```bash
pytest tests/ -v
```

---

## ⚖️ Lizenz & Haftungsausschluss

Veröffentlicht unter der [MIT License](LICENSE).

**Rechtlicher Hinweis (BGH Smartlaw Az. I ZR 113/20 & I ZR 226/20):**
Dieses Tool stellt ein unverbindliches technisches Hilfsmittel dar und ersetzt keine steuerliche Beratung durch einen Steuerberater oder eine Wirtschaftsprüfungsgesellschaft. Alle Berechnungen erfolgen auf Basis des Investmentsteuergesetzes 2026 ohne Gewähr.
