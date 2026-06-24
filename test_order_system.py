"""
Module: test_order_system.py
Description: Bộ Unit Test tự động nâng cao sử dụng kỹ thuật Mocking.
Chứng minh tính tăng cường rõ rệt của Controllability và Coupling thấp.
"""

import unittest
from unittest.mock import MagicMock
from datetime import datetime
import os

from order_system_good import (
    ModernOrderProcessor, IInventoryService, IPaymentGateway, 
    IOrderRepository, ITimeProvider, InvalidOrderDataException, OutOfStockException
)

class EnterpriseOrderProcessorTestSuite(unittest.TestCase):
    def setUp(self):
        """Khởi tạo môi trường Test Cô lập (Sandbox Isolation) bằng Mocks"""
        self.mock_inventory = MagicMock(spec=IInventoryService)
        self.mock_payment = MagicMock(spec=IPaymentGateway)
        self.mock_repo = MagicMock(spec=IOrderRepository)
        self.mock_time = MagicMock(spec=ITimeProvider)

        # Thiết lập giả lập thời gian cố định (Tối ưu hóa Controllability)
        self.frozen_time = datetime(2026, 6, 24, 10, 0, 0)
        self.mock_time.get_time.return_value = self.frozen_time

        # Khởi tạo đối tượng kiểm thử mục tiêu với Mock Dependencies injected
        self.processor = ModernOrderProcessor(
            inventory_service=self.mock_inventory,
            payment_gateway=self.mock_payment,
            repository=self.mock_repo,
            time_provider=self.mock_time
        )

    def test_order_processing_happy_path_with_discount(self):
        """Kịch bản thành công: Đơn hàng số lượng lớn nhận ưu đãi 15% và thanh toán mượt mà"""
        # Cài đặt hành vi cho các Mock (Stubbing)
        self.mock_inventory.check_stock.return_value = True
        self.mock_payment.process.return_value = True
        self.mock_repo.save_order.return_value = True

        # Thực thi hàm (Mua 3 sản phẩm giá 1000đ -> Tổng gốc 3000đ -> Giảm 15% còn 2550đ -> Thuế 8% = 2754đ)
        result = self.processor.process_order("VIP-USER", "ENTERPRISE-SERVER", 3, 1000.0)

        # Kiểm chứng Assertions (Xác minh tính đúng đắn)
        self.assertTrue(result["success"])
        self.assertEqual(result["payload"]["total_paid"], 2754.0)
        self.assertEqual(result["payload"]["processed_at"], self.frozen_time)

        # Xác minh hành vi tương tác (Verify Behavior) - Minh chứng Low Coupling
        self.mock_inventory.check_stock.assert_called_once_with("ENTERPRISE-SERVER", 3)
        self.mock_payment.process.assert_called_once_with(2754.0)
        self.mock_repo.save_order.assert_called_once()

    def test_order_processing_failure_due_to_insufficient_stock(self):
        """Kịch bản thất bại: Đơn hàng bị chặn ngay từ vòng kiểm kho khi kho hết hàng"""
        # Giả lập kho báo hết hàng
        self.mock_inventory.check_stock.return_value = False

        result = self.processor.process_order("USER-01", "IPHONE-18", 1, 1200.0)

        # Kiểm chứng
        self.assertFalse(result["success"])
        self.assertIn("đã hết hàng hoặc không đủ số lượng", result["reason"])
        
        # Kiểm chứng luồng xử lý bị ngắt sớm (Tối ưu hóa tài nguyên hệ thống)
        self.mock_payment.process.assert_not_called()
        self.mock_repo.save_order.assert_not_called()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 ĐANG KHỞI CHẠY BỘ KIỂM THỬ TỰ ĐỘNG CHUẨN DOANH NGHIỆP...")
    print("="*60)
    unittest.main()