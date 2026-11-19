# Verification protocol

Unit tests exercise statistical formulas and strict boundaries. Independent reference verification requires at least 20 timestamps with source rows and separately calculated values for all indicators and classifications. Record the platform/build, data source, timestamps, observed values, tolerance, and discrepancy disposition; freeze accepted values in `tests/regression/`. Current regression fixtures are empty because no historical reference dataset or MT terminal observations were supplied. Do not treat unit test success as verification.
