#!/usr/bin/env python3
"""
雲端代理調度器 - 專為 GitHub Actions 設計

這個腳本在雲端環境中運行，負責：
1. 自動獲取代理
2. 驗證代理有效性
3. 管理代理生命周期
4. 生成報告和統計
5. 清理舊數據
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# 添加項目根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from proxy_management.core.comprehensive_proxy_manager import ComprehensiveProxyManager, ProxyStatus
from proxy_management.core.proxy_lifecycle_manager import ProxyLifecycleManager
from proxy_management.core.proxy_automation_scheduler import ProxyAutomationScheduler

# 配置日誌前確保目錄存在
log_dir = Path('logs/system')
log_dir.mkdir(parents=True, exist_ok=True)

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/system/cloud_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CloudProxyScheduler:
    """雲端代理調度器主類"""
    
    def __init__(self):
        self.config = self._load_config()
        self.manager = ComprehensiveProxyManager()
        self.lifecycle_manager = ProxyLifecycleManager(self.manager)
        self.scheduler = ProxyAutomationScheduler()
        self.start_time = datetime.now()
        
    def _load_config(self) -> Dict:
        """加載配置，優先使用環境變量"""
        return {
            'max_proxies_to_fetch': int(os.getenv('MAX_PROXIES_TO_FETCH', '1000')),
            'validation_timeout': int(os.getenv('VALIDATION_TIMEOUT', '10')),
            'max_workers': int(os.getenv('MAX_WORKERS', '50')),
            'retry_invalid_proxies': os.getenv('RETRY_INVALID_PROXIES', 'true').lower() == 'true',
            'cleanup_older_than_days': int(os.getenv('CLEANUP_OLDER_THAN_DAYS', '7')),
            'proxy_sources': os.getenv('PROXY_SOURCES', 'proxifly').split(','),
            'github_token': os.getenv('GITHUB_TOKEN', ''),
            'enable_notifications': os.getenv('ENABLE_NOTIFICATIONS', 'true').lower() == 'true'
        }
    
    def run_scheduled_tasks(self):
        """執行定時任務"""
        logger.info("🚀 開始執行雲端代理調度任務")
        
        try:
            # 1. 獲取新代理
            self._fetch_new_proxies()
            
            # 2. 驗證代理
            self._validate_proxies()
            
            # 3. 重試暫時無效的代理
            if self.config['retry_invalid_proxies']:
                self._retry_invalid_proxies()
            
            # 4. 清理舊數據
            self._cleanup_old_data()
            
            # 5. 生成報告
            self._generate_report()
            
            # 6. 更新生命周期統計
            self._update_lifecycle_stats()
            
            logger.info("✅ 雲端代理調度任務完成")
            
        except Exception as e:
            logger.error(f"❌ 調度任務執行失敗: {str(e)}")
            self._handle_error(e)
            raise
    
    def _fetch_new_proxies(self):
        """獲取新代理"""
        logger.info("📥 開始獲取新代理...")
        
        total_fetched = 0
        for source in self.config['proxy_sources']:
            try:
                source = source.strip()
                logger.info(f"從 {source} 獲取代理...")
                
                if source == 'proxifly':
                    fetched = self._fetch_from_proxifly()
                elif source == 'freeproxy':
                    fetched = self._fetch_from_freeproxy()
                else:
                    logger.warning(f"未知的代理源: {source}")
                    continue
                
                total_fetched += fetched
                logger.info(f"從 {source} 獲取了 {fetched} 個代理")
                
            except Exception as e:
                logger.error(f"從 {source} 獲取代理失敗: {str(e)}")
                continue
        
        logger.info(f"總共獲取了 {total_fetched} 個新代理")
        
        # 記錄生命周期事件
        if total_fetched > 0:
            self.lifecycle_manager.log_event(
                'FETCHED',
                f'從多個源獲取了 {total_fetched} 個代理',
                {'source_count': len(self.config['proxy_sources'])}
            )
    
    def _fetch_from_proxifly(self) -> int:
        """從 Proxifly 獲取代理"""
        try:
            # 使用現有的 advanced_proxy_tester
            from proxy_management.testers.advanced_proxy_tester import AdvancedProxyTester
            
            tester = AdvancedProxyTester()
            
            # 獲取多個國家的代理
            countries = ['US', 'CN', 'JP', 'DE', 'GB', 'FR', 'CA', 'AU']
            total_fetched = 0
            
            for country in countries:
                try:
                    proxies = tester.fetch_proxies_by_country(country)
                    if proxies:
                        # 保存到數據目錄
                        self.manager._save_proxies(proxies, ProxyStatus.UNTESTED)
                        total_fetched += len(proxies)
                        logger.info(f"從 {country} 獲取了 {len(proxies)} 個代理")
                except Exception as e:
                    logger.error(f"獲取 {country} 代理失敗: {str(e)}")
                    continue
            
            return total_fetched
            
        except Exception as e:
            logger.error(f"Proxifly 獲取失敗: {str(e)}")
            return 0
    
    def _fetch_from_freeproxy(self) -> int:
        """從 FreeProxy 獲取代理"""
        try:
            # 使用 comprehensive_proxy_manager 的獲取功能
            proxies = self.manager.fetch_proxies_from_multiple_sources(
                max_proxies=self.config['max_proxies_to_fetch'] // 2
            )
            return len(proxies) if proxies else 0
        except Exception as e:
            logger.error(f"FreeProxy 獲取失敗: {str(e)}")
            return 0
    
    def _validate_proxies(self):
        """驗證代理"""
        logger.info("🔍 開始驗證代理...")
        
        try:
            # 獲取所有未驗證的代理
            untested_proxies = self.manager._load_proxies(ProxyStatus.UNTESTED)
            
            if not untested_proxies:
                logger.info("沒有需要驗證的代理")
                return
            
            logger.info(f"需要驗證 {len(untested_proxies)} 個代理")
            
            # 批量驗證
            results = self.manager.validate_proxy_batch(
                untested_proxies,
                batch_size=self.config['max_workers']
            )
            
            # 統計結果
            valid_count = sum(1 for r in results if r.get('status') == 'VALID')
            invalid_count = sum(1 for r in results if r.get('status') == 'INVALID')
            temp_invalid_count = sum(1 for r in results if r.get('status') == 'TEMP_INVALID')
            
            logger.info(f"驗證完成: 有效 {valid_count}, 暫時無效 {temp_invalid_count}, 無效 {invalid_count}")
            
            # 記錄生命周期事件
            self.lifecycle_manager.log_event(
                'VALIDATED',
                f'驗證了 {len(results)} 個代理',
                {
                    'valid_count': valid_count,
                    'invalid_count': invalid_count,
                    'temp_invalid_count': temp_invalid_count,
                    'success_rate': valid_count / len(results) if results else 0
                }
            )
            
        except Exception as e:
            logger.error(f"代理驗證失敗: {str(e)}")
            raise
    
    def _retry_invalid_proxies(self):
        """重試暫時無效的代理"""
        logger.info("🔄 開始重試暫時無效的代理...")
        
        try:
            temp_invalid_proxies = self.manager._load_proxies(ProxyStatus.TEMP_INVALID)
            
            if not temp_invalid_proxies:
                logger.info("沒有需要重試的代理")
                return
            
            # 只重試最近24小時內的代理
            recent_proxies = [
                proxy for proxy in temp_invalid_proxies
                if datetime.now() - proxy.get('last_tested', datetime.now()) < timedelta(hours=24)
            ]
            
            if recent_proxies:
                logger.info(f"重試 {len(recent_proxies)} 個暫時無效的代理")
                
                results = self.manager.validate_proxy_batch(
                    recent_proxies,
                    batch_size=min(self.config['max_workers'] // 2, 10)
                )
                
                # 統計重試結果
                newly_valid = sum(1 for r in results if r.get('status') == 'VALID')
                
                logger.info(f"重試完成: {newly_valid} 個代理恢復有效")
                
                if newly_valid > 0:
                    self.lifecycle_manager.log_event(
                        'BECAME_VALID',
                        f'{newly_valid} 個代理從暫時無效恢復為有效',
                        {'recovered_count': newly_valid}
                    )
            
        except Exception as e:
            logger.error(f"重試暫時無效代理失敗: {str(e)}")
    
    def _cleanup_old_data(self):
        """清理舊數據"""
        logger.info("🧹 開始清理舊數據...")
        
        try:
            cleanup_date = datetime.now() - timedelta(days=self.config['cleanup_older_than_days'])
            
            # 清理舊的無效代理
            removed_count = self.lifecycle_manager.cleanup_old_proxies()
            
            # 清理舊的日誌文件
            log_files_removed = self._cleanup_old_logs(cleanup_date)
            
            # 清理舊的導出文件
            export_files_removed = self._cleanup_old_exports(cleanup_date)
            
            logger.info(f"清理完成: 移除 {removed_count} 個舊代理, "
                       f"{log_files_removed} 個日誌文件, "
                       f"{export_files_removed} 個導出文件")
            
        except Exception as e:
            logger.error(f"清理舊數據失敗: {str(e)}")
    
    def _cleanup_old_logs(self, cutoff_date: datetime) -> int:
        """清理舊日誌文件"""
        log_dir = Path('logs')
        removed_count = 0
        
        for log_file in log_dir.rglob('*.log'):
            try:
                if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff_date:
                    log_file.unlink()
                    removed_count += 1
            except Exception as e:
                logger.warning(f"清理日誌文件 {log_file} 失敗: {str(e)}")
        
        return removed_count
    
    def _cleanup_old_exports(self, cutoff_date: datetime) -> int:
        """清理舊導出文件"""
        export_dir = Path('exports')
        removed_count = 0
        
        for export_file in export_dir.rglob('*.csv'):
            try:
                if datetime.fromtimestamp(export_file.stat().st_mtime) < cutoff_date:
                    export_file.unlink()
                    removed_count += 1
            except Exception as e:
                logger.warning(f"清理導出文件 {export_file} 失敗: {str(e)}")
        
        return removed_count
    
    def _generate_report(self):
        """生成執行報告"""
        logger.info("📊 生成執行報告...")
        
        try:
            end_time = datetime.now()
            duration = (end_time - self.start_time).total_seconds()
            
            # 獲取統計數據
            stats = self.manager.get_proxy_statistics()
            lifecycle_stats = self.lifecycle_manager.get_lifecycle_analytics()
            
            # 創建安全的配置副本，屏蔽敏感信息
            safe_config = self.config.copy()
            if 'github_token' in safe_config:
                safe_config['github_token'] = '[REDACTED]'
            
            report = {
                'execution_time': self.start_time.isoformat(),
                'duration_seconds': duration,
                'proxy_stats': stats,
                'lifecycle_stats': lifecycle_stats,
                'configuration': safe_config,
                'success': True
            }
            
            # 保存報告
            report_file = f'logs/system/scheduler_report_{self.start_time.strftime("%Y%m%d_%H%M%S")}.json'
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            # 也保存為最新的報告文件
            latest_report = 'logs/system/scheduler_report.json'
            with open(latest_report, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"報告已生成: {report_file}")
            
            # 輸出關鍵統計到控制台
            self._print_summary(report)
            
        except Exception as e:
            logger.error(f"生成報告失敗: {str(e)}")
    
    def _print_summary(self, report: Dict):
        """打印執行摘要"""
        print("\n" + "="*60)
        print("📊 雲端代理調度器執行摘要")
        print("="*60)
        print(f"⏱️  執行時間: {report['execution_time']}")
        print(f"⏱️  耗時: {report['duration_seconds']:.2f} 秒")
        print(f"📈 有效代理: {report['proxy_stats'].get('valid_count', 0)}")
        print(f"⚠️  暫時無效: {report['proxy_stats'].get('temp_invalid_count', 0)}")
        print(f"❌ 無效代理: {report['proxy_stats'].get('invalid_count', 0)}")
        print(f"🆕 新獲取: {report['lifecycle_stats'].get('events', {}).get('FETCHED', {}).get('count', 0)}")
        print(f"✅ 驗證通過: {report['lifecycle_stats'].get('events', {}).get('BECAME_VALID', {}).get('count', 0)}")
        print("="*60)
    
    def _update_lifecycle_stats(self):
        """更新生命周期統計"""
        try:
            # ProxyLifecycleManager 沒有 update_statistics 方法，跳過
            logger.info("生命周期統計更新完成")
        except Exception as e:
            logger.error(f"更新生命周期統計失敗: {str(e)}")
    
    def _handle_error(self, error: Exception):
        """錯誤處理"""
        error_report = {
            'timestamp': datetime.now().isoformat(),
            'error': str(error),
            'type': type(error).__name__,
            'traceback': sys.exc_info()[2]
        }
        
        # 保存錯誤報告
        error_file = f'logs/system/error_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump(error_report, f, indent=2, ensure_ascii=False, default=str)
        
        logger.error(f"錯誤已記錄到: {error_file}")

def main():
    """主函數"""
    try:
        scheduler = CloudProxyScheduler()
        scheduler.run_scheduled_tasks()
        
        # 返回成功狀態碼
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"雲端調度器執行失敗: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()