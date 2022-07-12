import os

databaseUrl = os.environ["DATABASE_URL"]


class Configuration:
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseUrl}/market"
    REDIS_HOST = "redis"
    REDIS_PRODUCTS_LIST = "products"
