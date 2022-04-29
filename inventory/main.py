from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel

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


class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis


def products_model(pk: str):
    product = Product.get(pk)
    return {
        "id": product.pk,
        "name": product.name,
        "price": product.price,
        "quantity": product.quantity
    }


@app.get("/products")
def get_products():
    return [products_model(pk) for pk in Product.all_pks()]


@app.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(product: Product):
    return product.save()


@app.get("/products/{pk}")
def get_product(pk: str):
    return Product.get(pk)


@app.delete("/products/{pk}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(pk: str):
    return Product.delete(pk)
