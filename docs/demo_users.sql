-- =====================================================================
-- Link the 5 demo logins to their roles. First create the 5 users in
-- Authentication > Users > Add user (tick Auto Confirm User), then run.
-- =====================================================================
insert into users (id, company_id, email, full_name, role)
select au.id, c.id, au.email, v.full_name, v.role
  from auth.users au
  join (values
         ('somchai@example.com', 'Khun Somchai', 'admin'),
         ('nok@example.com',     'Nok',          'sales'),
         ('ploy@example.com',    'Ploy',         'sales'),
         ('lek@example.com',     'Lek',          'warehouse'),
         ('fon@example.com',     'Fon',          'accountant')
       ) v(email, full_name, role) on v.email = au.email
  cross join companies c
 where c.name = 'Siam Bean Co.';

-- Check: this should list 5 rows.
select email, role from users order by role;
