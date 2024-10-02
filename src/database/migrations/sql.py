CREATE_REFRESH_UPDATED_AT_FUNC_SQL = """
create function public.refresh_updated_at()
    returns trigger
    language plpgsql as
    $func$
    begin
        new.updated_at := now();
        return new;
    end
    $func$
"""

DROP_REFRESH_UPDATED_AT_FUNC_SQL = """
drop function public.refresh_updated_at() cascade
"""

CREATE_UPDATED_AT_TRIGGER_SQL = """
create trigger trig_{table}_updated_at
before update on public.{table}
for each row execute procedure public.refresh_updated_at()
"""

DROP_UPDATED_AT_TRIGGER_SQL = """
drop trigger trig_{table}_updated_at on public.{table}
"""
