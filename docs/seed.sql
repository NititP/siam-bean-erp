-- =====================================================================
-- Siam Bean Co. sample data. Run once, after schema.sql, in the project.
-- =====================================================================
insert into companies (name, tax_id) values ('Siam Bean Co.', '0105560000000');

insert into products (company_id, sku, name, unit, cost, price, reorder_level)
select c.id, v.sku, v.name, v.unit, v.cost, v.price, v.rl
  from companies c,
       (values
         ('ARB-1KG', 'Arabica, 1 kg bag',     'kg',  320, 450,  50),
         ('ROB-1KG', 'Robusta, 1 kg bag',     'kg',  220, 320,  40),
         ('BLD-1KG', 'House Blend, 1 kg bag', 'kg',  260, 380,  30),
         ('DRP-10',  'Drip bags, box of 10',  'box',  90, 150, 100)
       ) v(sku, name, unit, cost, price, rl)
 where c.name = 'Siam Bean Co.';

insert into customers (company_id, name, tax_id, payment_terms_days)
select c.id, v.name, v.tax_id, v.terms
  from companies c,
       (values
         ('Café Lune',             '0105561000011', 30),
         ('Brew Lab Ari',          '0105562000022',  0),
         ('Sukhumvit Corner Café', '0105563000033', 15)
       ) v(name, tax_id, terms)
 where c.name = 'Siam Bean Co.';

insert into suppliers (company_id, name, location, lead_time_days, payment_terms_days)
select c.id, v.name, v.loc, v.lead, v.terms
  from companies c,
       (values
         ('Doi Chang Farm',      'Chiang Rai',  7, 30),
         ('Nan Highland Coffee', 'Nan',        14, 60)
       ) v(name, loc, lead, terms)
 where c.name = 'Siam Bean Co.';

-- Opening stock (ARB 170, ROB 35, BLD 90, DRP 240) as stock movements.
select reset_demo_data('yes-reset');
