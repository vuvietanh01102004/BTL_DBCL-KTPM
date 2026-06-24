"""
Module: order_system_bad.py
Description: Hệ thống quản lý đơn hàng Legacy (Chưa tối ưu Testability).
Vi phạm nghiêm trọng: High Coupling, Low Cohesion, Low Observability, Low Controllability.
"""

from datetime import datetime
import time

class LegacyOrderProcessor:
    def __init__(self):
        # HARD-CODED DEPENDENCIES (Coupling rất cao)
        self.db_url = "postgresql://prod_user:secure_password@192.168.1.50:5432/db_prod"
        self.payment_gateway_api = "https://api.stripe.com/v3/charges"
        self.inventory_status = {"LAPTOP-01": 5, "MOUSE-02": 100}
        self.order_history = []

    def execute_process_order(self, customer_id: str, item_id: str, quantity: int, price: float) -> dict:
        """
        Một hàm ôm đồm tất cả logic: Validate, Kiểm tra kho, Tính tiền, Thanh toán, Lưu DB, Gửi Mail.
        LOW COHESION & CYCLOMATIC COMPLEXITY CAO
        """
        # 1. Validation dữ liệu
        if not customer_id or not item_id:
            return {"status": "FAILED", "code": 400} # Low Observability: Không biết trống trường nào
            
        if quantity <= 0 or price <= 0:
            return {"status": "FAILED", "code": 401}

        # 2. Kiểm tra kho (Gắn cứng logic kho báu vào hàm)
        if item_id not in self.inventory_status or self.inventory_status[item_id] < quantity:
            return {"status": "FAILED", "code": 402}

        # 3. Tính toán tài chính phức tạp
        subtotal = quantity * price
        discount = 0.0
        if subtotal > 2000:
            discount = subtotal * 0.15 # Giảm giá 15% cho đơn lớn
        elif subtotal > 1000:
            discount = subtotal * 0.10 # Giảm giá 10%
            
        tax = (subtotal - discount) * 0.08 # Thuế VAT 8%
        final_amount = subtotal - discount + tax

        # 4. Gọi API Thanh toán bên thứ ba (Nếu mất mạng khi chạy Test -> Hàm này sập luôn)
        print(f"[API] Kết nối tới cổng thanh toán {self.payment_gateway_api}...")
        payment_success = True  # Giả định gọi API thật

        if not payment_success:
            return {"status": "PAYMENT_ERR", "code": 500}

        # 5. Cập nhật kho và lưu dữ liệu vào DB cứng
        self.inventory_status[item_id] -= quantity
        
        # LOW CONTROLLABILITY: Lấy giờ hệ thống trực tiếp, không thể ép ngày để test logic giảm giá
        order_date = datetime.now() 
        
        order_record = {
            "order_id": f"ORD-{int(time.time())}",
            "customer": customer_id,
            "item": item_id,
            "amount": final_amount,
            "created_at": order_date,
            "db_target": self.db_url
        }
        self.order_history.append(order_record)

        # 6. Thông báo
        print(f"[SYSTEM PRINT] Đơn hàng xử lý thành công tại database: {self.db_url}")
        
        return {"status": "SUCCESS", "data": order_record}

if __name__ == "__main__":
    processor = LegacyOrderProcessor()
    res = processor.execute_process_order("CUST-999", "LAPTOP-01", 1, 1500.0)
    print("Kết quả:", res)