
from typing import List, Optional
from pydantic import BaseModel

from model.cart_product_item import CartProductItem
from model.payment import Payment
from model.shipment import Shipment
from model.voucher import Voucher

from sqlalchemy import Column, Integer, String, Float
from dbconnect import Base

class OrderBase(BaseModel):
    orderId: str
    employeeId: Optional[int] = None
    paymentId: int
    shipmentId: int
    voucherId: Optional[int] = None
    cartId: Optional[int] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    totalOrder: Optional[float] = None
    payStatus: Optional[int] = None
    shipAdress: Optional[str] = None
    phone: Optional[str] = None

class Order(Base):
    __tablename__ = 'order'

    id = Column(String(255), primary_key=True)
    employeeId = Column(Integer, nullable=True)
    paymentId = Column(Integer, nullable=True)
    shipmentId = Column(Integer, nullable=True)
    voucherId = Column(Integer, nullable=True)
    cartId = Column(Integer, nullable=True)
    createdAt = Column(String(255), nullable=True)
    updatedAt = Column(String(255), nullable=True)
    payStatus = Column(Integer, nullable=True)
    shipAdress = Column(String(255), nullable=True)
    phone = Column(String(255), nullable=True)


class OrderDetail(Order):

    class Config:
        orm_mode = True