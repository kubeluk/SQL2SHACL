# SQL2SHACL

SQL2SHACL implements the constraint rewriting proposed in the paper "A Source-to-Target Constraint rewriting for Direct Mapping" by Ratan Bahadur Thapa and Martin Giese [[1]](#1).

## General

- SQL2SHACL is non-validating, meaning the user has to take care providing correct SQL syntax

### Supported SQL constraints

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

- currently only supports binary relations

## References

<a id="1">[1]</a> 
Thapa, R.B., Giese, M. (2021). A Source-to-Target Constraint Rewriting for Direct Mapping. In: Hotho, A., et al. The Semantic Web – ISWC 2021. ISWC 2021. Lecture Notes in Computer Science(), vol 12922. Springer, Cham. https://doi.org/10.1007/978-3-030-88361-4_2