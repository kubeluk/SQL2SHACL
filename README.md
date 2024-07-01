# SQL2SHACL

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

SQL2SHACL implements the constraint rewriting proposed in the paper "A Source-to-Target Constraint rewriting for Direct Mapping" by Ratan Bahadur Thapa and Martin Giese [[1]](#1).

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
python -m sql2shacl --outfile path/to/out.ttl
```

Provide a custom base IRI:

```
python -m sql2shacl --base-iri http://example.org/base/ path/to/file.sql
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

Caveats:
- groups of attributes as foreign key reference are currently not supported
- ...

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

- currently only binary relations are supported

## References

<a id="1">[1]</a> 
Thapa, R.B., Giese, M. (2021). A Source-to-Target Constraint Rewriting for Direct Mapping. In: Hotho, A., et al. The Semantic Web – ISWC 2021. ISWC 2021. Lecture Notes in Computer Science(), vol 12922. Springer, Cham. https://doi.org/10.1007/978-3-030-88361-4_2