# Polish bonds data

Monthly offer of Polish retail treasury bonds and consumer price inflation for the Kalkulator
Obligacji app.

The current offer is served at:

```
https://shoorie.github.io/polish-bonds-data/v1/offer.json
```

Every month since November 2016 has its offer in `v1/offers/<month>.json`, and the list of
those months is served at:

```
https://shoorie.github.io/polish-bonds-data/v1/offer-months.json
``` Monthly inflation is served at:

```
https://shoorie.github.io/polish-bonds-data/v1/inflation.json
```

Changes of the NBP reference rate are served at:

```
https://shoorie.github.io/polish-bonds-data/v1/reference-rates.json
```

The bonds guide shown in the app's Knowledge tab comes in a phone layout for reading in the app
(light and dark) and in A4 for sharing and printing:

```
https://shoorie.github.io/polish-bonds-data/v1/guide/guide-phone-light.pdf
https://shoorie.github.io/polish-bonds-data/v1/guide/guide-phone-dark.pdf
https://shoorie.github.io/polish-bonds-data/v1/guide/guide.pdf
```

All three are built from `docs/guide/przewodnik.typ` in the app repository with `docs/guide/build.sh`.

The privacy policy of the app, linked from the stores and the app settings, is served at:

```
https://shoorie.github.io/polish-bonds-data/privacy/
```

## Format (v1)

All amounts are whole cents and all rates are whole basis points (1 bp = 0.01%), so the file
never needs floating point numbers.

```json
{
  "formatVersion": 1,
  "month": "2026-10",
  "referenceRateBasisPoints": 375,
  "series": [
    {
      "code": "EDO",
      "issueCode": "EDO1036",
      "termYears": 10,
      "firstPeriodRateBasisPoints": 535,
      "marginBasisPoints": 200,
      "earlyRedemptionFeeCents": 300,
      "exchangePriceCents": 9990
    }
  ]
}
```

| Field | Meaning |
| --- | --- |
| `month` | Month the offer is sold in |
| `referenceRateBasisPoints` | NBP reference rate in force on the first day of the month |
| `code` | Series sold that month, each once: ROR, DOR, TOS, COI, EDO, ROS, ROD (ROR and DOR from June 2022, TOS from August 2022) |
| `issueCode` | Issue of the series sold this month |
| `termYears` | Term of the series, used only to check the app agrees |
| `firstPeriodRateBasisPoints` | Rate in the first interest period (the whole term for TOS) |
| `marginBasisPoints` | Margin over inflation or the NBP reference rate in later periods |
| `earlyRedemptionFeeCents` | Early redemption fee per bond |
| `exchangePriceCents` | Price of one bond bought in an exchange; nominal 100 PLN for ROS and ROD, which have no exchange |

A new field may be added without changing `formatVersion`. Changing or removing a field needs
`v2`.

## Offer archive

`v1/offer-months.json` lists the months that have an offer file, in order and with no gaps, and
`v1/offer.json` is the same as the file of the last month.

```json
{
  "formatVersion": 1,
  "months": ["2016-11", "2016-12", "2026-10"]
}
```

The archive was filled once with `scripts/backfill_offers.py` from the issue letters on
obligacjeskarbowe.pl: issues still held by someone are under **Listy emisyjne** and redeemed ones
under **Archiwum listów emisyjnych**. The script takes each issue's address from the page, because
a few of them have typos (EDO1028 lives under `edo01028`), checks that the letter names the
expected issue and month of sale, and prints any other document next to the letter, such as an
amendment, so it can be checked by hand. Series sold before 2022 that are no longer offered (DOS,
TOZ) are not in the archive: nobody holds them any more.

Letters before May 2017 give a separate margin for the first period and a fixed margin for the
later ones; `marginBasisPoints` is always the fixed one. The exchange price comes from each letter,
because some months had a promotion (EDO bought in an exchange for 99,40 zł in summer 2023).

## Inflation format (v1)

Consumer price inflation published by GUS, month by month from January 2010, in whole basis
points over the same month of the previous year. Months without a final value (estimates,
forecasts, preliminary data) are left out.

```json
{
  "formatVersion": 1,
  "months": [
    {
      "month": "2026-09",
      "yearOnYearBasisPoints": 410
    }
  ]
}
```

Months come in order with no gaps, so the last one is the latest published inflation.

## Reference rates format (v1)

Every change of the NBP reference rate with the day it took effect, starting with the rate in
force on 1 November 2016, the first month of the offer archive. Rates are whole basis points.

```json
{
  "formatVersion": 1,
  "changes": [
    {
      "effectiveFrom": "2026-03-05",
      "basisPoints": 375
    }
  ]
}
```

Changes come in order of the day and each one differs from the previous rate, so the rate on any
day is the last change on or before it. ROR and DOR need the exact day, because their interest
follows the rate in force on the tenth working day before the month a period starts.

## Updates

The **Update offer** workflow runs every day. It reads each series page on
obligacjeskarbowe.pl, parses the current issue letter, takes the NBP reference rate in force on
the first day of the month from `v1/reference-rates.json`, and opens a pull request when anything
changed. Check the numbers against the letters before merging.

The **Update inflation** workflow runs every day too. It reads the GUS SDP API (indicator 1832
up to 2025 and 2728, which follows COICOP 2018, from 2026) and opens a pull request when a new
month was published.

The **Update reference rates** workflow runs every day as well. The NBP website does not answer
scripts, so the history comes from the daily central bank policy rates that BIS publishes from
NBP data, and the latest decision from the current rates file on static.nbp.pl, which shows a new
decision before BIS does. A decision that contradicts the history stops the workflow.

The **Validate** workflow tests the parsers and checks every offer file, the offer archive, the
inflation file and the reference rates file on each pull request.

Run it locally (needs `pdftotext` from poppler):

```
python3 scripts/fetch_offer.py
python3 scripts/fetch_inflation.py
python3 scripts/fetch_reference_rates.py
python3 scripts/validate_offer.py v1/offer.json v1/offers/*.json
python3 scripts/validate_offer_archive.py v1
python3 scripts/validate_inflation.py v1/inflation.json
python3 scripts/validate_reference_rates.py v1/reference-rates.json
python3 -m unittest discover -s scripts/tests -t scripts
```
