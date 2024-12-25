from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from router import user_Rest, vnpay_Rest
from router import product_Rest
from router import product_item_Rest
from router import cart_Rest
from router import order_Rest
from router import shipment_Rest
from router import voucher_Rest
from router import payment_Rest
from router import feedback_Rest

# Khởi tạo ứng dụng FastAPI
app = FastAPI()

# Công khai thư mục chứa ảnh output
app.mount("/images/San_pham", StaticFiles(directory="images/San_pham"), name="images")

app.include_router(user_Rest.router)
app.include_router(product_Rest.router)
app.include_router(product_item_Rest.router)
app.include_router(cart_Rest.router)
app.include_router(order_Rest.router)
app.include_router(shipment_Rest.router)
app.include_router(voucher_Rest.router)
app.include_router(payment_Rest.router)
app.include_router(feedback_Rest.router)
app.include_router(vnpay_Rest.router)

# Add CORS middleware to allow all origins
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)