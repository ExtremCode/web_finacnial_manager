from yoyo import step


__depends__ = {'000.schema'}
UPGRADE = """
create table if not exists person (
person_id serial primary key,
login varchar(50) not null,
password varchar(300) not null,
expense_lim bigint default 0,
credit_lim bigint default 0,
unique(login),
constraint exp_lim_check check (expense_lim between 0 and 10^10),
constraint cred_lim_check check(credit_lim between 0 and 10^10)
);

create table if not exists income_category(
cat_id smallserial primary key,
cat_name varchar(50) not null,
unique(cat_name)
);

create table if not exists expense_category(
cat_id smallserial primary key,
cat_name varchar(50) not null,
unique(cat_name)
);

create table if not exists credit_category(
cat_id smallserial primary key,
cat_name varchar(50) not null,
unique(cat_name)
);

create table if not exists income (
inc_id serial primary key,
amount int not null,
rec_date date not null,
cat_id smallint not null,
person_id int not null,
foreign key (person_id) references person (person_id) on delete cascade on update cascade,
foreign key (cat_id) references income_category (cat_id) on delete cascade on update cascade,
constraint amount_check check (amount between 0 and 10^10),
constraint rec_date_check check (rec_date <= current_date)
);

create table if not exists expense (
exp_id serial primary key,
amount int not null,
rec_date date not null,
cat_id smallint not null,
person_id int not null,
foreign key (person_id) references person (person_id) on delete cascade on update cascade,
foreign key (cat_id) references expense_category (cat_id) on delete cascade on update cascade,
constraint amount_check check (amount between 0 and 10^10),
constraint rec_date_check check (rec_date <= current_date)
);

create table if not exists credit (
cred_id smallserial primary key,
amount int not null,
cat_id smallint not null,
person_id int not null,
foreign key (person_id) references person (person_id) on delete cascade on update cascade,
foreign key (cat_id) references credit_category (cat_id) on delete cascade on update cascade,
constraint amount_check check (amount between 0 and 10^10)
);

create table if not exists account (
acc_id smallserial primary key,
acc_name varchar(50) not null,
amount int not null,
person_id int not null,
foreign key (person_id) references person (person_id) on delete cascade on update cascade,
constraint amount_check check (amount between 0 and 10^10)
);"""
DOWNGRADE = """
drop table if exists person cascade;
drop table if exists income;
drop table if exists expense;
drop table if exists credit;
drop table if exists account;
drop table if exists income_category cascade;
drop table if exists expense_category cascade;
drop table if exists credit_category cascade;
"""

steps = [
    step(UPGRADE, DOWNGRADE)
]
