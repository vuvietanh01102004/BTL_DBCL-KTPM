"""
Module: order_system_good.py
Description: Hệ thống xử lý đơn hàng áp dụng Nguyên lý Thiết kế hướng Kiểm thử (Design for Testability).
Giải pháp: Abstract Interfaces, Dependency Injection, Tách biệt tầng logic, Structured Logging.
"""

import abc
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Thiết lập Logger chuyên nghiệp
logger = logging.getLogger("EnterpriseOrderSystem")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s'))
logger.addHandler(ch)

# ==========================================
# THÀNH PHẦN 1: ĐỊNH NGHĨA CÁC INTERFACES (Tạo các Seams để gắn Mock)
# ==========================================

class IInventoryService(abc.ABC):
    @abc.abstractmethod
    def check_stock(self, item_id: str, quantity: int) -> bool: pass
    @abc.abstractmethod
    def deduct_stock(self, item_id: str, quantity: int) -> None: pass

class IPaymentGateway(abc.ABC):
    @abc.abstractmethod
    def process(self, amount: float) -> bool: pass

class IOrderRepository(abc.ABC):
    @abc.abstractmethod
    def save_order(self, order_data: dict) -> bool: pass

class ITimeProvider(abc.ABC):
    @abc.abstractmethod
    def get_time(self) -> datetime: pass

# ==========================================
# THÀNH PHẦN 2: ĐỊNH NGHĨA CUSTOM EXCEPTIONS (Tăng Observability)
# ==========================================

class OrderDomainException(Exception): """Gốc của mọi lỗi nghiệp vụ"""
class InvalidOrderDataException(OrderDomainException): pass
class OutOfStockException(OrderDomainException): pass
class PaymentFailedException(OrderDomainException): pass

# ==========================================
# THÀNH PHẦN 3: LỚP XỬ LÝ CHÍNH (HIGH COHESION & LOW COUPLING)
# ==========================================

class ModernOrderProcessor:
    def __init__(self, 
                 inventory_service: IInventoryService,
                 payment_gateway: IPaymentGateway,
                 repository: IOrderRepository,
                 time_provider: ITimeProvider):
        # DEPENDENCY INJECTION: Nạp mọi thành phần từ ngoài vào, không gán cứng độc lập
        self._inventory = inventory_service
        self._payment = payment_gateway
        self._repo = repository
        self._time = time_provider

    def validate_inputs(self, customer_id: str, item_id: str, quantity: int, price: float) -> None:
        """Hàm đơn nhiệm kiểm tra tính hợp lệ dữ liệu (High Cohesion)"""
        if not customer_id:
            raise InvalidOrderDataException("Mã khách hàng (customer_id) không được để trống.")
        if not item_id:
            raise InvalidOrderDataException("Mã sản phẩm (item_id) không được để trống.")
        if quantity <= 0:
            raise InvalidOrderDataException("Số lượng đặt hàng phải lớn hơn 0.")
        if price <= 0:
            raise InvalidOrderDataException("Đơn giá sản phẩm phải lớn hơn 0.")

    def calculate_invoice_amount(self, quantity: int, price: float) -> float:
        """Hàm đơn nhiệm xử lý logic tài chính"""
        subtotal = quantity * price
        discount = 0.0
        if subtotal > 2000:
            discount = subtotal * 0.15
        elif subtotal > 1000:
            discount = subtotal * 0.10
            
        tax = (subtotal - discount) * 0.08
        return round(subtotal - discount + tax, 2)

    def process_order(self, customer_id: str, item_id: str, quantity: int, price: float) -> dict:
        """ Luồng điều khiển nghiệp vụ chính sạch sẽ, dễ quan sát, dễ kiểm soát """
        logger.info(f"Bắt đầu xử lý đơn hàng cho Khách hàng: {customer_id} | Sản phẩm: {item_id}")
        
        try:
            # 1. Kiểm tra đầu vào
            self.validate_inputs(customer_id, item_id, quantity, price)
            
            # 2. Kiểm tra kho qua Interface dịch vụ
            if not self._inventory.check_stock(item_id, quantity):
                logger.warning(f"Sản phẩm {item_id} không đủ hàng trong kho để cung ứng.")
                raise OutOfStockException(f"Sản phẩm {item_id} đã hết hàng hoặc không đủ số lượng.")

            # 3. Tính toán số tiền hóa đơn
            final_amount = self.calculate_invoice_amount(quantity, price)
            
            # 4. Tiến hành thanh toán
            if not self._payment.process(final_amount):
                logger.error(f"Giao dịch thanh toán số tiền {final_amount} VND thất bại từ phía Gateway.")
                raise PaymentFailedException("Cổng thanh toán từ chối giao dịch.")

            # 5. Khấu trừ kho và Lưu vết dữ liệu lịch sử
            self._inventory.deduct_stock(item_id, quantity)
            current_time = self._time.get_time()
            
            order_record = {
                "customer_id": customer_id,
                "item_id": item_id,
                "total_paid": final_amount,
                "processed_at": current_time,
                "status": "COMPLETED"
            }
            
            self._repo.save_order(order_record)
            logger.info(f"Đơn hàng hoàn tất thành công! Tổng tiền: {final_amount} VND.")
            return {"success": True, "payload": order_record}

        except OrderDomainException as dex:
            # Tăng cường Observability thông qua việc bắt và ghi nhận lỗi có cấu trúc
            logger.error(f"[DOMAIN ERROR] Quy trình xử lý lỗi nghiệp vụ: {str(dex)}")
            return {"success": False, "reason": str(dex)}