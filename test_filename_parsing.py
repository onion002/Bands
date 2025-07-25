#!/usr/bin/env python3
"""
测试文件名解析逻辑
"""

def test_filename_parsing():
    """测试文件名解析逻辑"""
    test_files = [
        "20250725150704_ComfyUI_00127_.png",  # 实际存在的文件
        "band_测试乐队_20250725150704.jpg",    # 格式1
        "20250725150704_image.jpg",           # 格式2
        "random_file.png",                    # 其他格式
        "band_test_band_20250725.png",        # 格式1
        "1234567890_test.jpg",                # 格式2（10位时间戳）
        "12345678_test.jpg",                  # 格式2（8位时间戳）
        "1234567_test.jpg",                   # 不符合格式2（7位）
    ]
    
    print("文件名解析测试:")
    print("=" * 60)
    
    for filename in test_files:
        print(f"\n文件: {filename}")
        
        # 测试格式1识别
        if filename.startswith("band_"):
            print("  ✓ 识别为格式1 (band_name_timestamp)")
        
        # 测试格式2识别
        parts = filename.split('_', 1)
        if len(parts) == 2 and parts[0].isdigit() and len(parts[0]) >= 8:
            print(f"  ✓ 识别为格式2 (timestamp_filename)")
            print(f"    时间戳: {parts[0]} (长度: {len(parts[0])})")
            print(f"    文件名: {parts[1]}")
        else:
            print("  ✗ 不符合格式2")
            if len(parts) == 2:
                print(f"    第一部分: {parts[0]} (是数字: {parts[0].isdigit()}, 长度: {len(parts[0])})")
        
        # 检查是否为图片文件
        if any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
            print("  ✓ 是图片文件")
        else:
            print("  ✗ 不是图片文件")

if __name__ == "__main__":
    test_filename_parsing()
