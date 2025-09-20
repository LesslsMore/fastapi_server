from urllib.parse import urlparse


def get_pg_config(postgres_url):
    result = urlparse(postgres_url)
    user = result.username  # postgres.kudppysekvoztpnmsvyt
    password = result.password  # 4Dr2x8zEK1hiOktb
    host = result.hostname  # aws-0-ap-southeast-1.pooler.supabase.com
    port = result.port or 5432  # 6543
    database = result.path[1:] if result.path else None  # postgres
    return database, host, password, port, user
