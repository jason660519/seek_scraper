"""
整合版 SEEK ETL 測試腳本

測試增強版 ETL 流程的各個組件：
1. Proxy 管理系統
2. 反爬蟲機制
3. 資料擷取與處理
4. 錯誤處理與重試機制
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.enhanced_seek_etl import EnhancedSeekETLWithProxy
from src.proxy_integration import ProxyRotator
from src.utils.logger import get_logger


class EnhancedETLTester:
    """
    增強版 ETL 測試器
    """
    
    def __init__(self):
        """初始化測試器"""
        self.logger = get_logger('enhanced_etl_tester')
        self.test_results = {}
        
        # 測試配置
        self.test_config = {
            'data_dir': 'data',
            'headless': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'scraper_config': {
                'base_url': 'https://www.seek.com.au',
                'timeout': 30,
                'request_delay': 2.0,
                'max_retries': 3,
                'max_pages': 1
            },
            'proxy_config': {
                'rotation_interval': 2,
                'failure_threshold': 1,
                'cooldown_period': 60,
                'max_consecutive_failures': 2,
                'max_fail_count': 2,
                'temp_invalid_retry_hours': 1,
                'validation_timeout': 5,
                'test_urls': [
                    'https://www.seek.com.au',
                    'https://httpbin.org/ip'
                ]
            },
            'anti_bot_config': {
                'enable_delay': True,
                'min_delay': 2.0,
                'max_delay': 5.0,
                'randomize_delay': True,
                'enable_user_agent_rotation': True,
                'enable_viewport_randomization': True
            },
            'batch_config': {
                'batch_size': 1,  # 測試用較小批次
                'batch_delay': 5,
                'max_concurrent': 1
            }
        }
    
    async def test_proxy_system(self) -> bool:
        """
        測試 Proxy 管理系統
        
        Returns:
            bool: 測試是否通過
        """
        self.logger.info("開始測試 Proxy 管理系統...")
        
        try:
            # 初始化 Proxy 輪換器
            rotator = ProxyRotator(self.test_config['proxy_config'], self.logger)
            await rotator.initialize()
            
            # 測試 proxy 獲取
            proxy = await rotator.get_next_proxy()
            self.logger.info(f"獲取到 proxy: {proxy}")
            
            # 測試 proxy 健康檢查
            is_healthy = await rotator.check_proxy_health(proxy)
            self.logger.info(f"Proxy 健康狀態: {is_healthy}")
            
            # 測試 proxy 輪換
            new_proxy = await rotator.get_next_proxy()
            self.logger.info(f"輪換後的 proxy: {new_proxy}")
            
            # 獲取統計資訊
            stats = rotator.get_statistics()
            self.logger.info(f"Proxy 統計: {stats}")
            
            self.test_results['proxy_system'] = {
                'status': 'passed',
                'proxy': proxy,
                'is_healthy': is_healthy,
                'stats': stats
            }
            
            return True
            
        except Exception as e:
            self.logger.error(f"Proxy 系統測試失敗: {e}")
            self.test_results['proxy_system'] = {
                'status': 'failed',
                'error': str(e)
            }
            return False
        
        finally:
            await rotator.close()
    
    async def test_anti_bot_mechanisms(self) -> bool:
        """
        測試反爬蟲機制
        
        Returns:
            bool: 測試是否通過
        """
        self.logger.info("開始測試反爬蟲機制...")
        
        try:
            # 初始化增強版 ETL
            async with EnhancedSeekETLWithProxy(self.test_config, self.logger) as etl:
                # 測試 User Agent 輪換
                user_agents = []
                for _ in range(5):
                    ua = etl._get_random_user_agent()
                    user_agents.append(ua)
                    self.logger.info(f"User Agent: {ua}")
                
                # 測試視窗大小隨機化
                viewports = []
                for _ in range(5):
                    vp = etl._get_random_viewport()
                    viewports.append(vp)
                    self.logger.info(f"Viewport: {vp}")
                
                # 測試延遲機制
                delays = []
                for _ in range(5):
                    delay = etl._get_random_delay()
                    delays.append(delay)
                    self.logger.info(f"延遲: {delay:.2f} 秒")
                
                self.test_results['anti_bot'] = {
                    'status': 'passed',
                    'user_agents': user_agents,
                    'viewports': viewports,
                    'delays': delays
                }
                
                return True
                
        except Exception as e:
            self.logger.error(f"反爬蟲機制測試失敗: {e}")
            self.test_results['anti_bot'] = {
                'status': 'failed',
                'error': str(e)
            }
            return False
    
    async def test_data_extraction(self) -> bool:
        """
        測試資料擷取功能
        
        Returns:
            bool: 測試是否通過
        """
        self.logger.info("開始測試資料擷取功能...")
        
        # 測試 URL（使用真實的 SEEK 職位頁面）
        test_urls = [
            'https://www.seek.com.au/job/12345678',  # 這是範例 URL，實際使用時需要真實的職位 URL
            'https://www.seek.com.au/job/87654321'
        ]
        
        try:
            async with EnhancedSeekETLWithProxy(self.test_config, self.logger) as etl:
                results = []
                
                for url in test_urls:
                    self.logger.info(f"測試擷取: {url}")
                    
                    try:
                        # 嘗試擷取 raw 資料
                        raw_data = await etl.extract_raw_data(url)
                        
                        if raw_data:
                            self.logger.info(f"成功擷取 raw 資料: {url}")
                            
                            # 嘗試解析資料
                            processed_data = etl.parse_job_data(raw_data['html_content'], url)
                            
                            if processed_data:
                                self.logger.info(f"成功解析資料: {url}")
                                results.append({
                                    'url': url,
                                    'status': 'success',
                                    'raw_data_size': len(raw_data['html_content']),
                                    'processed_data': processed_data
                                })
                            else:
                                self.logger.warning(f"解析失敗: {url}")
                                results.append({
                                    'url': url,
                                    'status': 'parse_failed'
                                })
                        else:
                            self.logger.warning(f"擷取失敗: {url}")
                            results.append({
                                'url': url,
                                'status': 'extraction_failed'
                            })
                        
                        # 批次間延遲
                        await asyncio.sleep(3)
                        
                    except Exception as e:
                        self.logger.error(f"處理 {url} 時發生錯誤: {e}")
                        results.append({
                            'url': url,
                            'status': 'error',
                            'error': str(e)
                        })
                
                self.test_results['data_extraction'] = {
                    'status': 'completed',
                    'total_urls': len(test_urls),
                    'successful_extractions': len([r for r in results if r['status'] == 'success']),
                    'results': results
                }
                
                return len([r for r in results if r['status'] == 'success']) > 0
                
        except Exception as e:
            self.logger.error(f"資料擷取測試失敗: {e}")
            self.test_results['data_extraction'] = {
                'status': 'failed',
                'error': str(e)
            }
            return False
    
    async def test_error_handling(self) -> bool:
        """
        測試錯誤處理機制
        
        Returns:
            bool: 測試是否通過
        """
        self.logger.info("開始測試錯誤處理機制...")
        
        try:
            # 測試無效 URL 處理
            invalid_urls = [
                'https://invalid-url-12345.com',
                'https://www.seek.com.au/job/invalid-job-id-12345'
            ]
            
            async with EnhancedSeekETLWithProxy(self.test_config, self.logger) as etl:
                error_results = []
                
                for url in invalid_urls:
                    try:
                        result = await etl.process_single_job_with_retry(url, max_retries=1)
                        error_results.append({
                            'url': url,
                            'result': result,
                            'expected_failure': True
                        })
                    except Exception as e:
                        error_results.append({
                            'url': url,
                            'error': str(e),
                            'expected_failure': True
                        })
                
                # 測試重試機制
                self.logger.info("測試重試機制...")
                
                retry_test_url = 'https://invalid-url-for-retry-test.com'
                start_time = datetime.now()
                
                result = await etl.process_single_job_with_retry(retry_test_url, max_retries=2)
                
                end_time = datetime.now()
                retry_time = (end_time - start_time).total_seconds()
                
                error_results.append({
                    'test': 'retry_mechanism',
                    'url': retry_test_url,
                    'result': result,
                    'retry_time': retry_time,
                    'expected_failure': True
                })
                
                self.test_results['error_handling'] = {
                    'status': 'passed',
                    'error_results': error_results,
                    'retry_time': retry_time
                }
                
                return True
                
        except Exception as e:
            self.logger.error(f"錯誤處理測試失敗: {e}")
            self.test_results['error_handling'] = {
                'status': 'failed',
                'error': str(e)
            }
            return False
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """
        執行所有測試
        
        Returns:
            Dict[str, Any]: 測試結果
        """
        self.logger.info("開始執行所有測試...")
        
        start_time = datetime.now()
        
        # 執行各項測試
        tests = [
            ('Proxy 系統', self.test_proxy_system),
            ('反爬蟲機制', self.test_anti_bot_mechanisms),
            ('資料擷取', self.test_data_extraction),
            ('錯誤處理', self.test_error_handling)
        ]
        
        test_results = {}
        
        for test_name, test_func in tests:
            try:
                self.logger.info(f"執行測試: {test_name}")
                result = await test_func()
                test_results[test_name] = result
                self.logger.info(f"測試 {test_name}: {'通過' if result else '失敗'}")
                
            except Exception as e:
                self.logger.error(f"測試 {test_name} 發生異常: {e}")
                test_results[test_name] = False
                self.test_results[test_name.lower().replace(' ', '_')] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        # 統計結果
        total_tests = len(tests)
        passed_tests = sum(1 for result in test_results.values() if result)
        failed_tests = total_tests - passed_tests
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        summary = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': passed_tests / total_tests if total_tests > 0 else 0,
            'total_time': total_time,
            'test_results': test_results,
            'detailed_results': self.test_results,
            'timestamp': start_time.isoformat()
        }
        
        # 儲存測試結果
        results_file = Path('data/stats') / f'enhanced_etl_test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
        
        self.logger.info(f"所有測試完成，結果已儲存: {results_file}")
        
        return summary
    
    def print_test_summary(self, summary: Dict[str, Any]):
        """列印測試摘要"""
        print("\n" + "="*60)
        print("增強版 SEEK ETL 測試摘要")
        print("="*60)
        
        print(f"總測試數: {summary['total_tests']}")
        print(f"通過測試: {summary['passed_tests']}")
        print(f"失敗測試: {summary['failed_tests']}")
        print(f"成功率: {summary['success_rate']:.1%}")
        print(f"總耗時: {summary['total_time']:.1f} 秒")
        
        print(f"\n詳細結果:")
        for test_name, result in summary['test_results'].items():
            status = "✓ 通過" if result else "✗ 失敗"
            print(f"  {test_name}: {status}")
        
        print(f"\n測試時間: {summary['timestamp']}")
        print("="*60)


async def main():
    """主函數"""
    print("開始執行增強版 SEEK ETL 測試...")
    
    tester = EnhancedETLTester()
    
    try:
        # 執行所有測試
        results = await tester.run_all_tests()
        
        # 列印摘要
        tester.print_test_summary(results)
        
        # 返回測試狀態
        return results['success_rate'] >= 0.5  # 50% 通過率即為成功
        
    except KeyboardInterrupt:
        print("\n使用者中斷測試")
        return False
    except Exception as e:
        print(f"\n測試執行失敗: {e}")
        tester.logger.error(f"測試執行失敗: {e}", exc_info=True)
        return False


if __name__ == '__main__':
    # 檢查虛擬環境
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("已進入虛擬環境 ✓")
    else:
        print("警告：未進入虛擬環境，建議使用 `uv shell` 啟動虛擬環境")
    
    # 執行測試
    success = asyncio.run(main())
    
    # 退出碼
    sys.exit(0 if success else 1)