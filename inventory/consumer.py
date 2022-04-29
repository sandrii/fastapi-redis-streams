import time

from redis.exceptions import ResponseError
from redis_om.model.model import NotFoundError

from main import redis, Product

st_key = "order_completed"
st_group = "inventory_group"

try:
    redis.xgroup_create(st_key, st_group)
except ResponseError:
    print("Group already exists!")

while True:
    try:
        result = redis.xreadgroup(st_group, st_key, {st_key: ">"}, None)
        if result:
            for res in result:
                obj = res[1][0][1]
                try:
                    prod = Product.get(obj["product_id"])
                    prod.quantity = prod.quantity - int(obj["quantity"])
                    prod.save()
                except NotFoundError:
                    redis.xadd("refund_order", obj, "*")
    except ResponseError as e:
        print(e)
    else:
        time.sleep(1)
