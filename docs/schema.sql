-- =====================================================================
-- Siam Bean Co. Mini ERP: database schema
-- Run once in the Supabase SQL Editor. One project serves the app and the tests.
-- =====================================================================

-- ---------- Master data ----------------------------------------------
create table companies (
  id      bigint generated always as identity primary key,
  name    text not null,
  tax_id  text not null
);

create table users (
  id          uuid primary key references auth.users (id) on delete cascade,
  company_id  bigint not null references companies (id),
  email       text not null unique,
  full_name   text not null,
  role        text not null
              check (role in ('admin', 'sales', 'warehouse', 'accountant')),
  created_at  timestamptz not null default now()
);

create table customers (
  id                  bigint generated always as identity primary key,
  company_id          bigint not null references companies (id),
  name                text not null check (length(trim(name)) > 0),
  tax_id              text not null check (length(trim(tax_id)) > 0),
  payment_terms_days  integer not null default 0 check (payment_terms_days >= 0),
  active              boolean not null default true,
  created_by          uuid references users (id),
  created_at          timestamptz not null default now()
);

create table suppliers (
  id                  bigint generated always as identity primary key,
  company_id          bigint not null references companies (id),
  name                text not null check (length(trim(name)) > 0),
  location            text,
  lead_time_days      integer not null default 0 check (lead_time_days >= 0),
  payment_terms_days  integer not null default 0 check (payment_terms_days >= 0),
  active              boolean not null default true
);

create table products (
  id             bigint generated always as identity primary key,
  company_id     bigint not null references companies (id),
  sku            text not null check (length(trim(sku)) > 0),
  name           text not null check (length(trim(name)) > 0),
  unit           text not null default 'kg',
  cost           numeric(12,2) not null check (cost >= 0),
  price          numeric(12,2) not null check (price >= 0),
  reorder_level  integer not null default 0 check (reorder_level >= 0),
  active         boolean not null default true,
  created_at     timestamptz not null default now(),
  unique (company_id, sku)
);

-- ---------- Stock: every change is a row, on hand = sum ----------------
create table stock_movements (
  id          bigint generated always as identity primary key,
  company_id  bigint not null references companies (id),
  product_id  bigint not null references products (id),
  quantity    integer not null check (quantity <> 0),
  ref_doc     text not null,
  created_by  uuid references users (id),
  created_at  timestamptz not null default now()
);

-- ---------- Document numbers: SO-0001, INV-0001, PO-0001 --------------
create table doc_counters (
  company_id  bigint not null references companies (id),
  doc_type    text not null check (doc_type in ('SO', 'INV', 'PO')),
  last_no     integer not null default 0,
  primary key (company_id, doc_type)
);

-- ---------- Sales ------------------------------------------------------
create table sales_orders (
  id            bigint generated always as identity primary key,
  company_id    bigint not null references companies (id),
  number        text not null,
  customer_id   bigint not null references customers (id),
  status        text not null default 'draft'
                check (status in ('draft', 'confirmed', 'cancelled')),
  order_date    date not null default (now() at time zone 'Asia/Bangkok')::date,
  created_by    uuid references users (id),
  confirmed_at  timestamptz,
  unique (company_id, number)
);

create table order_items (
  id          bigint generated always as identity primary key,
  order_id    bigint not null references sales_orders (id) on delete cascade,
  product_id  bigint not null references products (id),
  quantity    integer not null check (quantity > 0),
  unit_price  numeric(12,2) not null check (unit_price >= 0),
  unit_cost   numeric(12,2) not null check (unit_cost >= 0)
);

create table invoices (
  id           bigint generated always as identity primary key,
  company_id   bigint not null references companies (id),
  number       text not null,
  order_id     bigint not null unique references sales_orders (id),
  customer_id  bigint not null references customers (id),
  subtotal     numeric(12,2) not null,
  vat          numeric(12,2) not null,
  total        numeric(12,2) not null,
  status       text not null default 'open'
               check (status in ('open', 'paid', 'cancelled')),
  issue_date   date not null default (now() at time zone 'Asia/Bangkok')::date,
  due_date     date,
  created_by   uuid references users (id),
  created_at   timestamptz not null default now(),
  unique (company_id, number)
);

create table payments (
  id          bigint generated always as identity primary key,
  company_id  bigint not null references companies (id),
  invoice_id  bigint not null references invoices (id),
  amount      numeric(12,2) not null check (amount > 0),
  paid_at     timestamptz not null default now(),
  created_by  uuid references users (id)
);

-- ---------- Purchasing (bonus) -----------------------------------------
create table purchase_orders (
  id           bigint generated always as identity primary key,
  company_id   bigint not null references companies (id),
  number       text not null,
  supplier_id  bigint not null references suppliers (id),
  status       text not null default 'draft'
               check (status in ('draft', 'received', 'cancelled')),
  order_date   date not null default (now() at time zone 'Asia/Bangkok')::date,
  received_at  timestamptz,
  created_by   uuid references users (id),
  unique (company_id, number)
);

create table po_items (
  id          bigint generated always as identity primary key,
  po_id       bigint not null references purchase_orders (id) on delete cascade,
  product_id  bigint not null references products (id),
  quantity    integer not null check (quantity > 0),
  unit_cost   numeric(12,2) not null check (unit_cost >= 0)
);

-- ---------- Stock on hand view ----------------------------------------
create view stock_on_hand as
select p.id as product_id, p.company_id, p.sku, p.name, p.unit,
       p.reorder_level, p.active,
       coalesce(sum(m.quantity), 0)::integer as on_hand,
       coalesce(sum(m.quantity), 0) < p.reorder_level as low_stock
from products p
left join stock_movements m on m.product_id = p.id
group by p.id;

-- ---------- Functions --------------------------------------------------
-- Next document number. Runs inside the caller's transaction, so a
-- failed confirm never uses up a number.
create or replace function next_doc_number(p_company bigint, p_type text)
returns text language plpgsql as $$
declare n integer;
begin
  insert into doc_counters (company_id, doc_type, last_no)
  values (p_company, p_type, 1)
  on conflict (company_id, doc_type)
  do update set last_no = doc_counters.last_no + 1
  returning last_no into n;
  return p_type || '-' || lpad(n::text, 4, '0');
end $$;

-- Confirm a draft sales order: stock check, stock out, invoice. One
-- transaction: any error undoes everything (business rules 2, 3, 5).
-- Error codes: SB404 not found, SB409 not enough stock, SB422 bad state.
create or replace function confirm_order(p_order_id bigint, p_user uuid)
returns jsonb language plpgsql as $$
declare
  o        sales_orders%rowtype;
  short    record;
  v_sub    numeric(12,2);
  v_vat    numeric(12,2);
  v_terms  integer;
  v_inv    text;
  v_inv_id bigint;
begin
  select * into o from sales_orders where id = p_order_id for update;
  if not found then
    raise exception 'Order not found' using errcode = 'SB404';
  end if;
  if o.status <> 'draft' then
    raise exception 'Only draft orders can be confirmed' using errcode = 'SB422';
  end if;
  if not exists (select 1 from order_items where order_id = p_order_id) then
    raise exception 'Add at least one line before confirming' using errcode = 'SB422';
  end if;

  -- Lock these products so two people cannot sell the same beans at once.
  perform 1 from products
   where id in (select product_id from order_items where order_id = p_order_id)
   for update;

  select p.sku into short
  from (select product_id, sum(quantity) as need
          from order_items where order_id = p_order_id
         group by product_id) l
  join products p on p.id = l.product_id
  left join (select product_id, sum(quantity) as on_hand
               from stock_movements group by product_id) s
         on s.product_id = l.product_id
  where coalesce(s.on_hand, 0) < l.need
  order by p.sku
  limit 1;
  if found then
    raise exception 'Not enough stock for %', short.sku using errcode = 'SB409';
  end if;

  insert into stock_movements (company_id, product_id, quantity, ref_doc, created_by)
  select o.company_id, product_id, -quantity, o.number, p_user
    from order_items where order_id = p_order_id;

  select coalesce(sum(round(quantity * unit_price, 2)), 0) into v_sub
    from order_items where order_id = p_order_id;
  v_vat := round(v_sub * 0.07, 2);

  select payment_terms_days into v_terms from customers where id = o.customer_id;
  v_inv := next_doc_number(o.company_id, 'INV');

  insert into invoices (company_id, number, order_id, customer_id,
                        subtotal, vat, total, due_date, created_by)
  values (o.company_id, v_inv, o.id, o.customer_id, v_sub, v_vat, v_sub + v_vat,
          (now() at time zone 'Asia/Bangkok')::date + coalesce(v_terms, 0), p_user)
  returning id into v_inv_id;

  update sales_orders set status = 'confirmed', confirmed_at = now()
   where id = o.id;

  return jsonb_build_object(
    'order_number', o.number, 'invoice_id', v_inv_id, 'invoice_number', v_inv,
    'subtotal', v_sub, 'vat', v_vat, 'total', v_sub + v_vat);
end $$;

-- Record a payment. When payments reach the total, the invoice is Paid.
create or replace function record_payment(p_invoice_id bigint, p_amount numeric,
                                          p_user uuid)
returns jsonb language plpgsql as $$
declare
  inv     invoices%rowtype;
  v_paid  numeric(12,2);
  v_left  numeric(12,2);
begin
  select * into inv from invoices where id = p_invoice_id for update;
  if not found then
    raise exception 'Invoice not found' using errcode = 'SB404';
  end if;
  if inv.status <> 'open' then
    raise exception 'Invoice % is already %', inv.number, inv.status
      using errcode = 'SB422';
  end if;
  select coalesce(sum(amount), 0) into v_paid from payments where invoice_id = inv.id;
  v_left := inv.total - v_paid;
  if p_amount is null or p_amount <= 0 or p_amount > v_left then
    raise exception 'Amount must be between 0.01 and % THB', v_left
      using errcode = 'SB422';
  end if;

  insert into payments (company_id, invoice_id, amount, created_by)
  values (inv.company_id, inv.id, p_amount, p_user);

  if v_paid + p_amount >= inv.total then
    update invoices set status = 'paid' where id = inv.id;
  end if;

  return jsonb_build_object(
    'invoice_number', inv.number,
    'status', case when v_paid + p_amount >= inv.total then 'paid' else 'open' end,
    'outstanding', inv.total - v_paid - p_amount);
end $$;

-- Receive a purchase order (bonus): adds stock, only once.
create or replace function receive_po(p_po_id bigint, p_user uuid)
returns jsonb language plpgsql as $$
declare po purchase_orders%rowtype;
begin
  select * into po from purchase_orders where id = p_po_id for update;
  if not found then
    raise exception 'Purchase order not found' using errcode = 'SB404';
  end if;
  if po.status <> 'draft' then
    raise exception 'Purchase order % was already received', po.number
      using errcode = 'SB422';
  end if;
  if not exists (select 1 from po_items where po_id = p_po_id) then
    raise exception 'Add at least one line before receiving' using errcode = 'SB422';
  end if;

  insert into stock_movements (company_id, product_id, quantity, ref_doc, created_by)
  select po.company_id, product_id, quantity, po.number, p_user
    from po_items where po_id = p_po_id;

  update purchase_orders set status = 'received', received_at = now()
   where id = po.id;

  return jsonb_build_object('po_number', po.number, 'status', 'received');
end $$;

-- The three-plus live numbers for the dashboard.
create or replace function dashboard_numbers(p_company bigint)
returns jsonb language sql stable as $$
  select jsonb_build_object(
    'sales_today', (
      select coalesce(sum(total), 0) from invoices
       where company_id = p_company and status <> 'cancelled'
         and issue_date = (now() at time zone 'Asia/Bangkok')::date),
    'low_stock_count', (
      select count(*) from stock_on_hand
       where company_id = p_company and active and low_stock),
    'open_invoices_count', (
      select count(*) from invoices
       where company_id = p_company and status = 'open'),
    'open_receivables', (
      select coalesce(sum(i.total - coalesce(
               (select sum(amount) from payments p where p.invoice_id = i.id), 0)), 0)
        from invoices i
       where i.company_id = p_company and i.status = 'open'),
    'stock_value', (
      select coalesce(sum(s.on_hand * p.cost), 0)
        from stock_on_hand s join products p on p.id = s.product_id
       where s.company_id = p_company and s.active));
$$;

-- Put the data back to the demo starting point: master data as in the
-- scenario, no documents, opening stock only. Tests call this before
-- each test (wiping app data); run it once right before the demo.
create or replace function reset_demo_data(p_confirm text)
returns void language plpgsql security definer set search_path = public as $$
begin
  if p_confirm is distinct from 'yes-reset' then
    raise exception 'Pass yes-reset to confirm';
  end if;

  truncate payments, invoices, order_items, sales_orders, po_items,
           purchase_orders, stock_movements, doc_counters restart identity;

  delete from products
   where sku not in ('ARB-1KG', 'ROB-1KG', 'BLD-1KG', 'DRP-10');
  delete from customers
   where tax_id not in ('0105561000011', '0105562000022', '0105563000033');
  delete from suppliers
   where name not in ('Doi Chang Farm', 'Nan Highland Coffee');

  update products p
     set name = v.name, unit = v.unit, cost = v.cost, price = v.price,
         reorder_level = v.rl, active = true
    from (values
      ('ARB-1KG', 'Arabica, 1 kg bag',     'kg',  320, 450,  50),
      ('ROB-1KG', 'Robusta, 1 kg bag',     'kg',  220, 320,  40),
      ('BLD-1KG', 'House Blend, 1 kg bag', 'kg',  260, 380,  30),
      ('DRP-10',  'Drip bags, box of 10',  'box',  90, 150, 100)
    ) v(sku, name, unit, cost, price, rl)
   where p.sku = v.sku;

  update customers c
     set name = v.name, payment_terms_days = v.terms, active = true
    from (values
      ('0105561000011', 'Café Lune',             30),
      ('0105562000022', 'Brew Lab Ari',           0),
      ('0105563000033', 'Sukhumvit Corner Café', 15)
    ) v(tax_id, name, terms)
   where c.tax_id = v.tax_id;

  update suppliers set active = true;

  insert into stock_movements (company_id, product_id, quantity, ref_doc)
  select p.company_id, p.id, v.qty, 'OPENING'
    from products p
    join (values ('ARB-1KG', 170), ('ROB-1KG', 35),
                 ('BLD-1KG', 90),  ('DRP-10', 240)) v(sku, qty)
      on v.sku = p.sku;
end $$;

-- ---------- Security ---------------------------------------------------
-- Only the FastAPI backend (secret key) talks to these tables and
-- functions. RLS on with no policies blocks the public keys entirely.
alter table companies        enable row level security;
alter table users            enable row level security;
alter table customers        enable row level security;
alter table suppliers        enable row level security;
alter table products         enable row level security;
alter table stock_movements  enable row level security;
alter table doc_counters     enable row level security;
alter table sales_orders     enable row level security;
alter table order_items      enable row level security;
alter table invoices         enable row level security;
alter table payments         enable row level security;
alter table purchase_orders  enable row level security;
alter table po_items         enable row level security;

revoke execute on function next_doc_number(bigint, text)          from public, anon, authenticated;
revoke execute on function confirm_order(bigint, uuid)            from public, anon, authenticated;
revoke execute on function record_payment(bigint, numeric, uuid)  from public, anon, authenticated;
revoke execute on function receive_po(bigint, uuid)               from public, anon, authenticated;
revoke execute on function dashboard_numbers(bigint)              from public, anon, authenticated;
revoke execute on function reset_demo_data(text)                  from public, anon, authenticated;
revoke all on stock_on_hand from anon, authenticated;
