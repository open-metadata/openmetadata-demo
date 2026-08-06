# Data Quality Facades

> OpenMetadata 2.0 RC1 only. This example performs live writes; CI validates
> the models and mocked facade calls offline, without running a test engine.

This scenario demonstrates `TestDefinitions`, `TestSuites`, and `TestCases`.
It retrieves an existing table and built-in test definition, creates an owned
test suite and table test case, then retrieves the case and lists cases with
their latest `testCaseResult` field. It does not execute the test.

The focused request uses the built-in `tableRowCountToEqual` definition with an
expected value of `0`:

```bash
python -m pip install -r requirements-sdk.txt
export OPENMETADATA_HOST=http://localhost:8585/api
export OPENMETADATA_JWT_TOKEN='<token>'
export OPENMETADATA_DEMO_NAMESPACE=demo
export OPENMETADATA_TEST_TABLE_FQN=sample.database.schema.customers
export OPENMETADATA_TEST_DEFINITION_FQN=tableRowCountToEqual
python data-quality/data_quality.py
```

The script builds the canonical entity link
`<#E::table::<table-fqn>>`, verifies both parents before mutation, and guards
PUT upserts with `[openmetadata-demo:<namespace>:data-quality]`. It has no
custom validator, test execution, hard delete, or cleanup behavior.
