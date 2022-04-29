import time

from redis.exceptions import ResponseError

from main import redis, Order

st_key = "refund_order"
st_group = "payment_group"

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
                order = Order.get(obj["pk"])
                order.status = "refunded"
                order.save()
    except ResponseError as e:
        print(e)
    else:
        time.sleep(1)
