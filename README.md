# SQL2SHACL

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

SQL2SHACL implements the constraint rewriting proposed in the paper "A Source-to-Target Constraint rewriting for Direct Mapping" by Ratan Bahadur Thapa and Martin Giese in two versions:
1. based on a Direct Mapping as defined by [Sequeda et al.](https://doi.org/10.1145/2187836.2187924)
2. based on the W3C Recommendation [A Direct Mapping of Relational Data to RDF](https://www.w3.org/TR/rdb-direct-mapping/)

## Component diagram

![Architecture diagram](/assets/sql2shacl_arch_dark.svg "Architecture diagram")

## Prerequisites

Install poetry (see [official documentation](https://python-poetry.org/docs/#installing-with-the-official-installer))

```
curl -sSL https://install.python-poetry.org | python3 -
```

Install the dependencies

```
poetry install
```

## Usage

Activate the virtual environment:

```
poetry shell
```

Provide a file containing SQL DDL statements and apply the constraint rewriting:

```
python -m sql2shacl path/to/file.sql
```

Specify the log-level:

```
python -m sql2shacl --loglevel INFO path/to/file.sql
```

Write the generated SHACL shapes to a file:

```
python -m sql2shacl path/to/file.sql --mode w3c|thapa --outfile path/to/out.ttl
```

Provide a custom base IRI:

```
python -m sql2shacl --base-iri http://example.com/base/ path/to/file.sql 
```

## Run tests

```
poetry run pytest
```

## General

- SQL2SHACL is in principle non-validating, meaning the user has to take care providing correct SQL syntax
- The intention is to provide hints when
    - expressions are skipped due to containing wrong syntax
    - important information is missing (e.g. missing data type for column)

### Supported SQL constraints

The following column and table constraints are supported:
- NOT NULL
- UNIQUE
- PRIMARY KEY
- REFERENCES

### Supported SQL data types

- binary
- binary varying
- binary large object
- numeric
- decimal
- smallint
- integer
- int
- bigint
- character
- char
- character varying
- character large object
- varchar
- float
- real
- double precision
- boolean
- date
- time

See the mapping file (`src/components/sqldatatype2xmlschema.json`) for their respective XMLSchema mapping

### N-ary relations

- currently only binary relations are supported when using "thapa" constraint rewriting mode
