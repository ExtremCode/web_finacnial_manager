# import psycopg2 as psg


# conn = psg.connect(host="localhost",
#                    database="financial",
#                    user="postgres",
#                    password="rootroot")
# cursor = conn.cursor()
# cursor.execute("""create table person (
# person_id serial primary key,
# login varchar(50) not null,
# password varchar(300) not null,
# expense_lim bigint default 0,
# credit_lim bigint default 0,
# unique(login),
# constraint exp_lim_check check (expense_lim between 0 and 10^10),
# constraint cred_lim_check check(credit_lim between 0 and 10^10)
# );

# create table income_category(
# cat_id smallserial primary key,
# cat_name varchar(50) not null,
# unique(cat_name)
# );

# create table expense_category(
# cat_id smallserial primary key,
# cat_name varchar(50) not null,
# unique(cat_name)
# );

# create table credit_category(
# cat_id smallserial primary key,
# cat_name varchar(50) not null,
# unique(cat_name)
# );

# create table income (
# inc_id serial primary key,
# amount int not null,
# rec_date date not null,
# cat_id smallint not null,
# person_id int not null,
# foreign key (person_id) references person (person_id) on delete cascade on update cascade,
# foreign key (cat_id) references income_category (cat_id) on delete cascade on update cascade,
# constraint amount_check check (amount between 0 and 10^10),
# constraint rec_date_check check (rec_date <= current_date)
# );

# create table expense (
# exp_id serial primary key,
# amount int not null,
# rec_date date not null,
# cat_id smallint not null,
# person_id int not null,
# foreign key (person_id) references person (person_id) on delete cascade on update cascade,
# foreign key (cat_id) references expense_category (cat_id) on delete cascade on update cascade,
# constraint amount_check check (amount between 0 and 10^10),
# constraint rec_date_check check (rec_date <= current_date)
# );

# create table credit (
# cred_id smallserial primary key,
# amount int not null,
# cat_id smallint not null,
# person_id int not null,
# foreign key (person_id) references person (person_id) on delete cascade on update cascade,
# foreign key (cat_id) references credit_category (cat_id) on delete cascade on update cascade,
# constraint amount_check check (amount between 0 and 10^10)
# );

# create table account (
# acc_id smallserial primary key,
# acc_name varchar(50) not null,
# amount int not null,
# person_id int not null,
# foreign key (person_id) references person (person_id) on delete cascade on update cascade,
# constraint amount_check check (amount between 0 and 10^10)
# );

# insert into person(login, password, expense_lim, credit_lim)
# values ('admin', 'scrypt:32768:8:1$gXFGNU30qa3gXRYd$a66a18a0929e26288a3732a7919bf62a65cda191b0c6b89a47bc7d9cdb817c0778a460dbd7604c1b88cb007d877699cc3dc845df17e585badcea5427b1942e24',\
#                300, 1000),
# ('guest', 'scrypt:32768:8:1$JU0xTEJxVikuRBJo$0322f66bbc4aba626f883e076df9c8c27449f348dc8f53f225d25ea2036517d4e8d469b48ee1e30a3521dca321f800b4d9339bfb384860ce2e3e55600f1a71e3',\
#                100, 300);

# insert into income_category(cat_name)
# values ('salary'),
# ('premiums'),
# ('investments'),
# ('another');

# insert into expense_category(cat_name)
# values ('groceries'),
# ('restaurants'),
# ('hobby'),
# ('medicine'),
# ('transport'),
# ('sport'),
# ('rental'),
# ('another');

# insert into credit_category(cat_name)
# values ('consumer credit'),
# ('mortgage'),
# ('car loan');

# insert into income(amount, rec_date, cat_id, person_id)
# values (100, '2023-11-11', 1, 1),
# (234, '2022-10-20', 1, 2);

# insert into expense(amount, rec_date, cat_id, person_id)
# values (990, '2023-11-11', 2, 1),
# (100, '2022-10-20', 1, 2);

# insert into credit(amount, cat_id, person_id)
# values (990, 2, 1),
# (100, 1, 2);

# insert into account(acc_name, amount, person_id)
# values ('first', 99900, 1),
# ('second', 2000, 1),
# ('their', 500, 2);""")

# conn.commit()
# cursor.close()
# conn.close()

from yoyo import read_migrations
from yoyo import get_backend
import psycopg2 as psg

backend = get_backend('postgres://postgres:rootroot@localhost/financial')
migrations = read_migrations('web_financial_manager/backend/database/migrations')

def rollback():
    with backend.lock():
        backend.rollback_migrations(backend.to_rollback(migrations))

def apply():
    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))

def init_db():
    apply()
    try:
        conn = psg.connect(host="localhost",
                    database="financial",
                    user="postgres",
                    password="rootroot")
        cursor = conn.cursor()
        cursor.execute("""
        insert into income_category(cat_name)
        values ('salary'),
        ('premiums'),
        ('investments'),
        ('another');

        insert into expense_category(cat_name)
        values ('groceries'),
        ('restaurants'),
        ('hobby'),
        ('medicine'),
        ('transport'),
        ('sport'),
        ('rental'),
        ('another');

        insert into credit_category(cat_name)
        values ('consumer credit'),
        ('mortgage'),
        ('car loan');""")
    except:
        print("inserting categories cannot be finished")
    conn.commit()
    cursor.close()
    conn.close()
