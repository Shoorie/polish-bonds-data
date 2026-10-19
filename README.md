# Polish bonds data

Monthly offer of Polish retail treasury bonds for the Kalkulator Obligacji app.

The current offer is served at:

```
https://shoorie.github.io/polish-bonds-data/v1/offer.json
```

Past offers stay in `v1/offers/<month>.json`.

The bonds guide shown in the app's Knowledge tab comes in a phone layout for reading in the app
(light and dark) and in A4 for sharing and printing:

```
https://shoorie.github.io/polish-bonds-data/v1/guide/guide-phone-light.pdf
https://shoorie.github.io/polish-bonds-data/v1/guide/guide-phone-dark.pdf
https://shoorie.github.io/polish-bonds-data/v1/guide/guide.pdf
```

All three are built from `docs/guide/przewodnik.typ` in the app repository with `docs/guide/build.sh`.

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
| `referenceRateBasisPoints` | NBP reference rate when the offer was read |
| `code` | Series: ROR, DOR, TOS, COI, EDO, ROS, ROD (each exactly once) |
| `issueCode` | Issue of the series sold this month |
| `termYears` | Term of the series, used only to check the app agrees |
| `firstPeriodRateBasisPoints` | Rate in the first interest period (the whole term for TOS) |
| `marginBasisPoints` | Margin over inflation or the NBP reference rate in later periods |
| `earlyRedemptionFeeCents` | Early redemption fee per bond |
| `exchangePriceCents` | Price of one bond bought in an exchange; nominal 100 PLN for ROS and ROD, which have no exchange |

A new field may be added without changing `formatVersion`. Changing or removing a field needs
`v2`.

## Updates

The **Update offer** workflow runs every day. It reads each series page on
obligacjeskarbowe.pl, parses the current issue letter and the NBP reference rate, and opens a
pull request when anything changed. Check the numbers against the letters before merging.

The **Validate** workflow tests the parser and checks every offer file on each pull request.

Run it locally (needs `pdftotext` from poppler):

```
python3 scripts/fetch_offer.py
python3 scripts/validate_offer.py v1/offer.json v1/offers/*.json
python3 -m unittest discover -s scripts/tests -t scripts
```
