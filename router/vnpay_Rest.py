
from fastapi import APIRouter
from config.vnpay_config import VNPayConfig
from fastapi import Request
from hashlib import sha512
import hmac
import urllib.parse
from fastapi.responses import RedirectResponse
from datetime import datetime

router = APIRouter()

def create_vnpay_payment_url(order_id, amount):
    vnp_TmnCode = VNPayConfig['vnp_TmnCode']
    vnp_HashSecret = VNPayConfig['vnp_HashSecret']
    vnp_Url = VNPayConfig['vnp_Url']
    vnp_ReturnUrl = VNPayConfig['vnp_ReturnUrl']

    vnp_Params = {
        'vnp_Version': '2.1.0',
        'vnp_Command': 'pay',
        'vnp_TmnCode': vnp_TmnCode,
        'vnp_Amount': int(amount) ,  # VND to smallest currency unit
        'vnp_CurrCode': 'VND',
        'vnp_TxnRef': order_id,
        'vnp_OrderInfo': f"Payment for Order {order_id}",
        'vnp_OrderType': 'billpayment',
        'vnp_Locale': 'vn',
        'vnp_ReturnUrl': vnp_ReturnUrl,
        'vnp_IpAddr': '127.0.0.1',
        'vnp_CreateDate': datetime.now().strftime('%Y%m%d%H%M%S')
    }

    # Sort the parameters and create the query string
    sorted_params = sorted(vnp_Params.items())
    query_string = urllib.parse.urlencode(sorted_params)

    # Generate the secure hash using HMAC SHA-256
    hash_data = hmac.new(vnp_HashSecret.encode(), query_string.encode(), sha512).hexdigest()
    vnp_Url += f"?{query_string}&vnp_SecureHashType=SHA256&vnp_SecureHash={hash_data}"

    return vnp_Url

@router.post("/vnpay_payment",tags=["VNPAY"])
async def create_payment(request: Request):
    data = await request.json()
    order_id = data.get("order_id")
    amount = data.get("amount")

    payment_url = create_vnpay_payment_url(order_id, amount)
    return {"payment_url": payment_url}

# Handle VNPay return URL callback
@router.get("/vnpay_return",tags=["VNPAY"])
async def vnpay_return(request: Request):
    # Lấy query parameters từ VNPay
    query_params = request.query_params
    vnp_ResponseCode = query_params.get("vnp_ResponseCode")
    
    # Kiểm tra mã kết quả
    if vnp_ResponseCode == "00":
        # Thanh toán thành công, redirect về frontend với trạng thái thành công
        return RedirectResponse(url="http://localhost:5173/sanpham?status=success")
    else:
        # Thanh toán thất bại, redirect về frontend với trạng thái thất bại
        return RedirectResponse(url="http://localhost:5173/sanpham?status=fail")