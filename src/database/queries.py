"""Common SQL queries for the migrations."""

CREATE_REFRESH_UPDATED_AT_FUNC: str = """
CREATE FUNCTION refresh_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql AS $func$
BEGIN
    NEW.updated_at := now();
    RETURN NEW;
END
$func$;
"""

DROP_REFRESH_UPDATED_AT_FUNC: str = "DROP FUNCTION refresh_updated_at() CASCADE;"

CREATE_UPDATED_AT_TRIGGER: str = """
CREATE TRIGGER trig_{table}_updated_at BEFORE UPDATE ON {table}
FOR EACH ROW EXECUTE PROCEDURE refresh_updated_at();
"""
