# Energy provider: E-REDES

This directory contains the tooling to convert data exported from
[E‑REDES](https://balcaodigital.e-redes.pt/) into CSV files suitable for the
generic import scripts used by Home Assistant.

* `ERedesDataPrepare.py` – conversion script which transforms an E‑REDES
  `.xlsx` export into the expected two‑column CSV format.
* `Sample files/` – example `.xlsx` export and the resulting CSV used in tests.
* `tests/` – automated tests for the conversion script.
