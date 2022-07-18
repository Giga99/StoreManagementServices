from redis import Redis

from configuration import Configuration
from commons.exceptions import BadRequestException


class WorkerController:

    def update_products(self, reader):
        index = 0
        products = []
        for row in reader:
            if len(row) != 4:
                raise BadRequestException("Incorrect number of values on line {}.".format(index))

            try:
                if int(row[2]) <= 0:
                    raise BadRequestException("Incorrect quantity on line {}.".format(index))
            except ValueError:
                raise BadRequestException("Incorrect quantity on line {}.".format(index))

            try:
                if float(row[3]) <= 0:
                    raise BadRequestException("Incorrect price on line {}.".format(index))
            except ValueError:
                raise BadRequestException("Incorrect price on line {}.".format(index))

            products.append(row)
            index = index + 1

        for row in products:
            with Redis(host=Configuration.REDIS_HOST) as redis:
                redis.rpush(Configuration.REDIS_PRODUCTS_LIST, ",".join(row))

        return index
