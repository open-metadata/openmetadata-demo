# Rename Service

This is a small utility package that can be used in case you need to rename a service.

We are not going to use the `ometa` client, since we want to keep this validation-agnostic so that it can
be used in case some naming pattern fails.

This has been implemented for OpenMetadata 0.13.


## Disclaimer

This is a first draft implementation and will require further work. Also, it is only implemented for databases.

## How to

Clone the repo, and from this directory run:

1. `make install`
2. `rename -i <service to rename> -o <output name> -c config.yaml`

Where `config.yaml` has the necessary info to connect to your OpenMetadata instance. You can follow the one
in the example `config.yaml` in this same directory.

## Implementation

We support:

- Database Services
- Tags
- Ownership

We can add lineage, usage, queries, etc. and other services on demand.
