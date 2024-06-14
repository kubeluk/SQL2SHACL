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

# Foreign keys

# Check constraint

# Exclusion constraint