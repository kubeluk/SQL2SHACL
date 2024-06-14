# Unique constraints

Unique constraints can be defined like:

    CREATE TABLE products (
    product_no integer UNIQUE,
    name text,
    price numeric
);

or like:

CREATE TABLE products (
    product_no integer,
    name text,
    price numeric,
    UNIQUE (product_no)
);

# Not-Null constraints

# Primary keys

Primary keys can be defined like:

CREATE TABLE products (
    product_no integer UNIQUE NOT NULL,
    name text,
    price numeric
);

or like:

CREATE TABLE products (
    product_no integer PRIMARY KEY,
    name text,
    price numeric
);

or like:

CREATE TABLE example (
    a integer,
    b integer,
    c integer,
    PRIMARY KEY (a, c)
);

# Foreign keys

# Check constraint

# Exclusion constraint