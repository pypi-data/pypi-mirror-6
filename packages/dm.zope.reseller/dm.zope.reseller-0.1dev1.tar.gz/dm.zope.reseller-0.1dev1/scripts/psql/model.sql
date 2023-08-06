create schema reseller;

set search_path = reseller, public;

comment on schema reseller is '
Schema supporting a simple reselling activity.

We assume a single (implicit) provider, a single (implicit) reseller
and several "client"s.

The provider provides "article"s which the clients can buy.

Clients buy articles in "unit"s; the provider provides them
in "packet"s which contain an integral number of "unit"s. If
the "packet_size" is different from 1, then the reseller repackages
the delivered articles for its clients.

The reseller continously collects "client_order_item"s and
periodically issues "order"s to the provider consisting of
"provider_order_item"s.

The reseller occationally receives a "provider_delivery" for an order
consisting of "provider_delivery_item"s and splits them into
"client_delivery_item"s.

There is a special client, used as stock. It can be used to
balance orders and deliveries. It (and it alone) can have
negative "unit" values in its "client_delivery_items" - indicating
that units have been taken out of the stock.

Usually, we do not delete items. Instead, we mark them as not "active".
This is in order not to break references.

Note: We give `active` the values `true` and `null`
(rather than `true` and `false`) in order to use the peculiar
`unique` feature that `null` values are considered different.
Thus, the unique requirements apply to active elements only.

Note: We would like to use foreign keys. However, a postgres bug
prevents us from doing so.
';


create table item(
  id serial primary key,
  -- `active` has values `TRUE` and `NULL`
  active boolean default true -- whether this is visible
  );


create table article(
  provider_order_no text not null,
  tax_code int not null, -- identifies a tax category
  catalog_price decimal(10,2) not null, -- without tax
  price_ratio int not null, -- ratio between package and catalog price
  unit text not null, -- description of selling units
  package_size int default 1 not null, -- number of selling units contained in a provided package
  title text not null,
  description text,
  max_stock_units int default 0,
  constraint "non unique article" unique(provider_order_no, active)
) inherits(item);

create table client(
  title text not null,
  description text,
  email text,
  phone text, -- may contain more than one phone number
  address text,
  -- `active` has values `TRUE` and `NULL`
  constraint "non unique client" unique(active, title)
) inherits(item);


create table provider_order(
  title text, -- in fact the target date
  order_date timestamp
) inherits(item);

create table client_order_item(
  client_id int not null, --  references client(id),
  article_id int not null, --  references article(id),
  order_id int, --  references provider_order(id), -- can be null, when not yet assigned
  units int not null, -- number of units the client wants to buy
  max_units int, -- maximal number of units; default "units"
  note text, -- a comment for this order item
  unit_price decimal(10,2), -- at order time (with tax)
  order_date timestamp default current_timestamp
) inherits(item);

create table provider_order_item(
  order_id int not null, --  references provider_order(id),
  article_id int not null, --  references article(id),
  packages int not null, -- number of ordered packages
  catalog_price decimal(10,2) -- at order time (without tax)
) inherits(item);


create table provider_delivery(
  order_id int not null, --  references provider_order(id), -- the order this is a delivery for
  title date default current_date -- actually `delivery_date`
) inherits(item);

create table provider_delivery_item(
  delivery_id int not null, --  references provider_delivery(id),
  article_id int not null, --  references article(id),
  packages int, -- number of delivered packages
  catalog_price decimal(10,2) -- at delivery time (without tax)
) inherits(item);


create table client_delivery(
  client_id int not null, --  references client(id),
  provider_delivery_id int not null, --  references provider_delivery(id),
  delivery_date date
) inherits(item);
  

create table client_delivery_item(
  client_delivery_id int not null, --  references client_delivery(id),
  provider_delivery_item_id int not null, --  references provider_delivery_item(id),
  units int not null, -- number of delivered units; may come from stock
  unit_price decimal(10,2), -- at delivery time (with tax)
  state int default 0 -- delivery state: 0 (proposed), 1 (assigned), 2 (confirmed)
) inherits(item);


create table tax(
  code int not null primary key,
  percent decimal(4,2)
);

insert into tax values (1, 5.5), (3, 20);


-- the special client used as stock
insert into client(id, title, active) values (1000000, 'STOCK', FALSE);

  
  
