import os

databaseUrl = os.environ["DATABASE_URL"]


class Configuration:
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseUrl}/market"
    JWT_SECRET_KEY = "jwt-secret-ket-iep"
