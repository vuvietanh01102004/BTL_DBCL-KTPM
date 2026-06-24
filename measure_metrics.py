"""
Module: measure_metrics.py
Description: Công cụ phân tích cú pháp tĩnh (Static AST Analyzer) 
để tính toán định lượng các chỉ số phần mềm hướng đối tượng (WMC, NoM).
"""

import ast

def gather_class_metrics(filename: str) -> list:
    results = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except FileNotFoundError:
        return results

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
            num_methods = len(methods)
            
            wmc_score = 0
            method_details = []
            for m in methods:
                cc = 1
                for subnode in ast.walk(m):
                    if isinstance(subnode, (ast.If, ast.While, ast.For, ast.Try, ast.ExceptHandler)):
                        cc += 1
                wmc_score += cc
                method_details.append((m.name, cc))
            
            avg_cc = round(wmc_score / num_methods, 2) if num_methods > 0 else 0
            results.append({
                "class": class_name,
                "nom": num_methods,
                "wmc": wmc_score,
                "avg_cc": avg_cc,
                "details": method_details
            })
    return results

def render_dashboard():
    bad_metrics = gather_class_metrics("order_system_bad.py")
    good_metrics = gather_class_metrics("order_system_good.py")

    print("\n" + "╔" + "═"*78 + "╗")
    print("║" + " BẢNG ĐIỀU KHIỂN ĐO LƯỜNG METRIC HƯỚNG ĐỐI TƯỢNG VÀ ĐÁNH GIÁ TESTABILITY ".center(78) + "║")
    print("╚" + "═"*78 + "╝")
    
    print("\n📊 1. KIẾN TRÚC MÃ NGUỒN CŨ (LACK OF TESTABILITY):")
    print("╒" + "═"*30 + "╤" + "═"*12 + "╤" + "═"*12 + "╤" + "═"*18 + "╕")
    print("│ Tên Lớp (Class Name)         │ Chỉ số NoM │ Tổng WMC   │ Độ phức tạp TB/Hàm │")
    print("╞" + "═"*30 + "╪" + "═"*12 + "╪" + "═"*12 + "╪" + "═"*18 + "╪")
    for data in bad_metrics:
        print(f"│ {data['class']:<28} │ {data['nom']:^10} │ {data['wmc']:^10} │ {data['avg_cc']:^18} │")
    print("╘" + "═"*30 + "╧" + "═"*12 + "╧" + "═"*12 + "╧" + "═"*18 + "╛")

    print("\n🚀 2. KIẾN TRÚC MÃ NGUỒN MỚI SAU KHI TỐI ƯU (HIGH TESTABILITY):")
    print("╒" + "═"*30 + "╤" + "═"*12 + "╤" + "═"*12 + "╤" + "═"*18 + "╕")
    print("│ Tên Lớp (Class Name)         │ Chỉ số NoM │ Tổng WMC   │ Độ phức tạp TB/Hàm │")
    print("╞" + "═"*30 + "╪" + "═"*12 + "╪" + "═"*12 + "╪" + "═"*18 + "╪")
    for data in good_metrics:
        print(f"│ {data['class']:<28} │ {data['nom']:^10} │ {data['wmc']:^10} │ {data['avg_cc']:^18} │")
    print("╘" + "═"*30 + "╧" + "═"*12 + "╧" + "═"*12 + "╧" + "═"*18 + "╛")

    print("\n💡 THUYẾT MINH PHÂN TÍCH KIẾN TRÚC:")
    print(" - Nhờ áp dụng chia nhỏ cấu trúc (Tăng Cohesion), lớp 'ModernOrderProcessor' có NoM tăng lên.")
    print(" - Tuy nhiên độ phức tạp trung bình của từng hàm riêng lẻ được kéo thấp xuống.")
    print(" - Điều này làm giảm đáng kể gánh nặng thiết kế ca kiểm thử (Hạ thấp Test Effort).\n")

if __name__ == "__main__":
    render_dashboard()