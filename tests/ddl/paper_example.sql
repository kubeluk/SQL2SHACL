CREATE TABLE Emp (
    E_id integer PRIMARY KEY,
    Name varchar NOT NULL,
    Post varchar
);
CREATE TABLE Acc (
    A_id integer PRIMARY KEY,
    Name char UNIQUE
);
CREATE TABLE Prj (
    P_id integer PRIMARY KEY,
    Name varchar NOT NULL,
    ToAcc integer NOT NULL UNIQUE REFERENCES Acc(A_id)
);
CREATE TABLE Asg (
    ToEmp integer REFERENCES Emp(E_id),
    ToPrj integer REFERENCES Prj(P_id),
    PRIMARY KEY (ToEmp,ToPrj)
);