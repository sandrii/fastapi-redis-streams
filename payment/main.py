import time

import requests
from fastapi import BackgroundTasks
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel
from starlette.requests import Request

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"]
)

redis = get_redis_connection(
    host="redis-19929.c250.eu-central-1-1.ec2.cloud.redislabs.com",
    port=19929,
    password="4XmeosbHzIi0cnZkqSLKbbecKqY4B9l3",
    decode_responses=True
)


class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str  # pending, completed, refunded

    class Meta:
        database = redis


@app.get("/orders/{pk}")
def get_order(pk: str):
    return Order.get(pk)


@app.post("/orders", status_code=status.HTTP_201_CREATED)
async def create_order(request: Request, background_task: BackgroundTasks):
    body = await request.json()
    product = requests.get(f"http://localhost:8000/products/{body['id']}").json()
    order = Order(
        product_id=body["id"],
        price=product["price"],
        fee=0.2 * product["price"],
        total=1.2 * product["price"],
        quantity=body["quantity"],
        status="pending"
    )
    order.save()
    background_task.add_task(order_completed, order)
    return order


def order_completed(order: Order):
    time.sleep(5)
    order.status = "completed"
    order.save()
    redis.xadd("order_completed", order.dict(), "*")
