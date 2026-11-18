-- Book Scraper schema (safe to run repeatedly)
create table if not exists public.books (
    upc                text primary key,
    title              text not null,
    category           text,
    price_gbp          numeric(10,2),
    price_incl_tax_gbp numeric(10,2),
    tax_gbp            numeric(10,2),
    in_stock           boolean,
    stock_count        integer,
    rating             smallint check (rating between 1 and 5),
    num_reviews        integer,
    description        text,
    image_url          text,
    product_url        text,
    scraped_at         timestamptz default now()
);

create index if not exists books_category_idx on public.books (category);

alter table public.books enable row level security;

-- Anyone (anon + logged-in) can read; no insert/update/delete policies for them.
drop policy if exists "Public can read books" on public.books;
create policy "Public can read books"
    on public.books for select
    to anon, authenticated
    using (true);

-- service_role bypasses RLS, so backend writes work without extra policies.
grant usage on schema public to anon, authenticated, service_role;
grant all on public.books to service_role;
grant select on public.books to anon, authenticated;
notify pgrst, 'reload schema';
