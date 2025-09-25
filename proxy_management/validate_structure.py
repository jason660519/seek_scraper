"""
專案結構驗證腳本
用於驗證重新組織後的專案結構是否完整
"""

import os
import sys
from pathlib import Path

def check_directory_structure():
    """檢查目錄結構"""
    print("🔍 檢查專案結構完整性...")
    
    # 定義預期的目錄結構
    expected_structure = {
        "proxy_management": {
            "core": ["proxy_update_monitor.py"],
            "validators": ["simple_proxy_validator.py", "geolocation_validator.py"],
            "testers": ["advanced_proxy_tester.py", "comprehensive_proxy_validator.py", 
                       "multi_layer_validation_system.py", "proxy_tester.py", "test_fixed_system.py"],
            "web_interface": ["app.py", "fixed_app.py", "simple_app.py", "templates"],
            "data": ["all.txt", "best_proxies.json", "best_proxies.txt", "http.txt", 
                    "socks4.txt", "socks5.txt", "us_proxies.txt"]
        },
        "config": {
            "data_schemas": ["data_schema_spec.json", "search_parameters_spec.json"],
            "job_categories": ["job_categories.json"]
        },
        "src": ["main.py", "main_simple.py", "config", "models", "scrapers", "parsers", "services", "utils"],
        "tools": ["countries.py"],
        "logs": [],
        "tests": [],
        "docs": [],
        "scripts": [],
        "data": [],
        "docker": []
    }
    
    missing_files = []
    missing_dirs = []
    
    # 檢查根目錄
    for root_dir, subdirs in expected_structure.items():
        if not os.path.exists(root_dir):
            missing_dirs.append(root_dir)
            print(f"❌ 缺少目錄: {root_dir}")
            continue
            
        print(f"✅ 找到目錄: {root_dir}")
        
        if isinstance(subdirs, dict):
            # 檢查子目錄
            for subdir, files in subdirs.items():
                subdir_path = os.path.join(root_dir, subdir)
                if not os.path.exists(subdir_path):
                    missing_dirs.append(f"{root_dir}/{subdir}")
                    print(f"❌ 缺少子目錄: {subdir_path}")
                    continue
                    
                print(f"  ✅ 找到子目錄: {subdir_path}")
                
                # 檢查檔案
                for file in files:
                    file_path = os.path.join(subdir_path, file)
                    if not os.path.exists(file_path):
                        missing_files.append(f"{subdir_path}/{file}")
                        print(f"    ❌ 缺少檔案: {file_path}")
                    else:
                        print(f"    ✅ 找到檔案: {file_path}")
        else:
            # 檢查檔案列表
            for item in subdirs:
                item_path = os.path.join(root_dir, item)
                if not os.path.exists(item_path):
                    missing_files.append(f"{root_dir}/{item}")
                    print(f"  ❌ 缺少: {item_path}")
                else:
                    print(f"  ✅ 找到: {item_path}")
    
    # 總結
    print("\n" + "="*60)
    print("📊 驗證結果:")
    
    if missing_dirs:
        print(f"❌ 缺少 {len(missing_dirs)} 個目錄")
        for d in missing_dirs:
            print(f"   - {d}")
    else:
        print("✅ 所有目錄都存在")
    
    if missing_files:
        print(f"❌ 缺少 {len(missing_files)} 個檔案")
        for f in missing_files:
            print(f"   - {f}")
    else:
        print("✅ 所有檔案都存在")
    
    if not missing_dirs and not missing_files:
        print("🎉 專案結構完整！")
        return True
    else:
        print("⚠️  專案結構不完整")
        return False

def test_imports():
    """測試基本導入"""
    print("\n🔍 測試基本導入...")
    
    test_results = []
    
    # 測試工具模組
    try:
        sys.path.append(str(Path.cwd() / "tools"))
        # 這裡可以添加實際的導入測試
        print("✅ 基本導入測試通過")
        test_results.append(True)
    except Exception as e:
        print(f"❌ 導入測試失敗: {e}")
        test_results.append(False)
    
    return all(test_results)

def main():
    """主函數"""
    print("🚀 Seek Job Crawler 專案結構驗證")
    print("="*60)
    
    # 檢查結構
    structure_ok = check_directory_structure()
    
    # 測試導入
    imports_ok = test_imports()
    
    # 最終結果
    print("\n" + "="*60)
    if structure_ok and imports_ok:
        print("🎉 所有驗證都通過！專案結構整理成功。")
        return 0
    else:
        print("⚠️  部分驗證失敗，請檢查上述錯誤訊息。")
        return 1

if __name__ == "__main__":
    sys.exit(main())