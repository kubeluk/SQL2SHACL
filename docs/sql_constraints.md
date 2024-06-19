# Constraints

SQL allows you to define constraints on columns and tables. Constraints give you as much control over the data in your tables as you wish. If a user attempts to store data in a column that would violate a constraint, an error is raised.

- column constraint: `product_no integer UNIQUE`
- table constraints: `UNIQUE (product_no)`
- constraints can have names: `price numeric CONSTRAINT positive_price CHECK (price > 0)`

# Unique constraints

- still possible to have multiple null values
    - this behavior can be changed: `product_no integer UNIQUE NULLS NOT DISTINCT`

## handled

- uniqueness of single column
- column and table constraint style

## un-handled

- `NULLS NOT DISTINCT` add-on
- definition of a unique constraint for a group of columns

```
CREATE TABLE example (
    a integer,
    b integer,
    c integer,
    UNIQUE (a, c)
);
```

This specifies that the combination of values in the indicated columns is unique across the whole table, though any one of the columns need not be (and ordinarily isn't) unique.

# Not-Null constraints

- can only be column constraints

# Primary keys

- `PRIMARY KEY` is the same as `UNIQUE NOT NULL`

Primary keys can be defined like:

```
CREATE TABLE products (
    product_no integer UNIQUE NOT NULL,
    name text,
    price numeric
);
```

or like:

```
CREATE TABLE products (
    product_no integer PRIMARY KEY,
    name text,
    price numeric
);
```

or like:

```
CREATE TABLE example (
    a integer,
    b integer,
    c integer,
    PRIMARY KEY (a, c)
);
```

# Foreign keys

## short form

```
CREATE TABLE orders (
    order_id integer PRIMARY KEY,
    product_no integer REFERENCES products (product_no),
    quantity integer
);
```

can be shortened to (in this case the primary key of products is used as reference):

```
CREATE TABLE orders (
    order_id integer PRIMARY KEY,
    product_no integer REFERENCES products,
    quantity integer
);
```

## group of columns as foreign key

A foreign key can also constrain and reference a group of columns:

```
CREATE TABLE t1 (
  a integer PRIMARY KEY,
  b integer,
  c integer,
  FOREIGN KEY (b, c) REFERENCES other_table (c1, c2)
);
```

## multiple foreign keys

-  used to implement many-to-many relationships between tables

```
CREATE TABLE products (
    product_no integer PRIMARY KEY,
    name text,
    price numeric
);
```

```
CREATE TABLE orders (
    order_id integer PRIMARY KEY,
    shipping_address text,
    ...
);
```

```
CREATE TABLE order_items (
    product_no integer REFERENCES products,
    order_id integer REFERENCES orders,
    quantity integer,
    PRIMARY KEY (product_no, order_id)
);
```

- notice that the primary key overlaps with the foreign keys in the last table

# Check constraint

...

# Exclusion constraint

...