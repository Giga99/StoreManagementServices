class Configuration:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@localhost/market"
    REDIS_HOST = "localhost"
    REDIS_PRODUCTS_LIST = "products"
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
