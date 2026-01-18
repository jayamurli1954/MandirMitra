import psycopg2
from app.core.config import settings


def parse_database_url(url):
    url = url.replace("postgresql://", "")
    if "@" in url:
        auth, rest = url.split("@", 1)
        user, password = auth.split(":", 1)
    else:
        user = "postgres"
        password = ""
        rest = url

    if "/" in rest:
        host_port, database = rest.split("/", 1)
    else:
        host_port = rest
        database = "temple_db"

    if ":" in host_port:
        host, port = host_port.split(":")
    else:
        host = host_port
        port = "5432"

    return {"host": host, "port": port, "database": database, "user": user, "password": password}


conn = psycopg2.connect(**parse_database_url(settings.DATABASE_URL))
cur = conn.cursor()
cur.execute(
    "SELECT enumlabel FROM pg_enum WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'transactiontype') ORDER BY enumsortorder"
)
values = [row[0] for row in cur.fetchall()]
print("TransactionType enum values:", values)
print("Has inventory_purchase:", "inventory_purchase" in values)
print("Has inventory_issue:", "inventory_issue" in values)
cur.close()
conn.close()
