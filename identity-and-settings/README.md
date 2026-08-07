# Identity and Settings Facades

> OpenMetadata 2.0 RC1 only. This example performs live writes for identities
> and live reads for Settings. CI validates it offline against the exact RC1 SDK.

This scenario demonstrates `Teams`, `Users`, and the read-only `Settings`
facade. It creates one non-joinable group and one non-admin user, retrieves them
during the guarded upsert, converts both to `EntityReference` values, and reads
glossary relation settings and relation types. It prints only counts and safe
entity identifiers.

## Run

```bash
python -m pip install -r requirements-sdk.txt
export OPENMETADATA_HOST=http://localhost:8585/api
export OPENMETADATA_JWT_TOKEN='<token>'
export OPENMETADATA_DEMO_NAMESPACE=demo
export OPENMETADATA_DEMO_USER_EMAIL=demo.user@example.com
python identity-and-settings/identity_and_settings.py
```

Admin permissions are likely required to create users and teams. These
identities remain after the run; no cleanup is included. Full PUT upserts are
allowed only when the existing description contains the exact
`[openmetadata-demo:<namespace>:identity-and-settings]` marker.

The script never sets a password, grants admin access, or calls
`Settings.define_glossary_relation_type()`. Credentials are environment-only
and are never printed.
