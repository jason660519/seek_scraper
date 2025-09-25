"""
代理管理自動化調度器
提供定時任務調度和自動化管理功能
"""

import asyncio
import schedule
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import json
import threading
from concurrent.futures import ThreadPoolExecutor

from proxy_management.core.comprehensive_proxy_manager import ComprehensiveProxyManager
from proxy_management.core.proxy_lifecycle_manager import ProxyLifecycleManager

logger = logging.getLogger(__name__)


class ProxyAutomationScheduler:
    """代理管理自動化調度器"""
    
    def __init__(self, config_file: str = None):
        # 初始化管理器
        self.proxy_manager = ComprehensiveProxyManager()
        self.lifecycle_manager = ProxyLifecycleManager(self.proxy_manager)
        
        # 配置參數
        self.config = self._load_config(config_file)
        
        # 調度狀態
        self.is_running = False
        self.scheduler_thread = None
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        # 任務狀態追蹤
        self.task_status = {
            'last_fetch_time': None,
            'last_validation_time': None,
            'last_cleanup_time': None,
            'last_report_time': None,
            'task_history': []
        }
        
        # 設置日誌
        self._setup_logging()
        
        logger.info("代理管理自動化調度器初始化完成")
    
    def _load_config(self, config_file: str = None) -> Dict:
        """加載配置"""
        default_config = {
            'fetch_schedule': {
                'enabled': True,
                'interval_hours': 6,           # 每6小時獲取一次
                'max_proxies_per_fetch': 1000,  # 每次最多獲取1000個
                'retry_failed_interval_hours': 2 # 失敗重試間隔
            },
            'validation_schedule': {
                'enabled': True,
                'interval_hours': 3,           # 每3小時驗證一次
                'batch_size': 100,              # 每批驗證100個
                'retry_temp_invalid_interval_hours': 6  # 重試暫時無效代理間隔
            },
            'cleanup_schedule': {
                'enabled': True,
                'interval_hours': 24,          # 每天清理一次
                'max_proxy_age_days': 30       # 代理最大年齡30天
            },
            'report_schedule': {
                'enabled': True,
                'interval_hours': 12,          # 每12小時生成報告
                'formats': ['json', 'csv']     # 報告格式
            },
            'notification_config': {
                'enabled': False,
                'webhook_url': None,
                'email_config': None,
                'notify_on_errors': True,
                'notify_on_low_proxies': True,
                'min_valid_proxies_threshold': 50  # 有效代理少於50個時通知
            },
            'performance_config': {
                'max_concurrent_validations': 50,  # 最大並發驗證數
                'validation_timeout_seconds': 15,   # 驗證超時時間
                'retry_attempts': 3               # 重試次數
            }
        }
        
        if config_file and Path(config_file).exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # 合併配置
                    default_config.update(user_config)
                    logger.info(f"從 {config_file} 加載用戶配置")
            except Exception as e:
                logger.error(f"加載配置文件失敗: {e}，使用默認配置")
        
        return default_config
    
    def _setup_logging(self):
        """設置日誌"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # 文件日誌
        log_file = log_dir / f"proxy_scheduler_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 控制台日誌
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 日誌格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 設置根日誌
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
    
    def _add_task_history(self, task_name: str, status: str, details: Dict = None):
        """添加任務歷史記錄"""
        task_record = {
            'task_name': task_name,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        
        self.task_status['task_history'].append(task_record)
        
        # 限制歷史記錄數量
        if len(self.task_status['task_history']) > 1000:
            self.task_status['task_history'] = self.task_status['task_history'][-1000:]
        
        # 保存任務狀態
        self._save_task_status()
    
    def _save_task_status(self):
        """保存任務狀態"""
        try:
            status_file = self.proxy_manager.data_dir / "scheduler_status.json"
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(self.task_status, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            logger.error(f"保存任務狀態失敗: {e}")
    
    def _load_task_status(self):
        """加載任務狀態"""
        try:
            status_file = self.proxy_manager.data_dir / "scheduler_status.json"
            if status_file.exists():
                with open(status_file, 'r', encoding='utf-8') as f:
                    self.task_status = json.load(f)
        except Exception as e:
            logger.error(f"加載任務狀態失敗: {e}")
    
    def fetch_proxies_task(self):
        """獲取代理任務"""
        try:
            logger.info("開始執行獲取代理任務")
            
            # 獲取新代理
            new_proxies = self.proxy_manager.fetch_proxies_from_multiple_sources()
            
            # 限制數量
            if len(new_proxies) > self.config['fetch_schedule']['max_proxies_per_fetch']:
                new_proxies = new_proxies[:self.config['fetch_schedule']['max_proxies_per_fetch']]
            
            # 追蹤生命週期
            self.lifecycle_manager.track_proxy_fetching(new_proxies)
            
            # 驗證新代理
            validated_proxies = self.proxy_manager.validate_proxy_batch(
                new_proxies, 
                batch_size=self.config['validation_schedule']['batch_size']
            )
            
            # 保存結果
            self.proxy_manager._save_proxies(validated_proxies)
            
            # 更新任務狀態
            self.task_status['last_fetch_time'] = datetime.now().isoformat()
            
            # 記錄任務歷史
            self._add_task_history(
                'fetch_proxies',
                'success',
                {
                    'new_proxies_count': len(new_proxies),
                    'validated_proxies_count': len(validated_proxies),
                    'valid_proxies_count': len([p for p in validated_proxies if p.status.value == 'valid'])
                }
            )
            
            logger.info(f"獲取代理任務完成：獲取 {len(new_proxies)} 個，驗證 {len(validated_proxies)} 個")
            
        except Exception as e:
            logger.error(f"獲取代理任務失敗: {e}")
            self._add_task_history('fetch_proxies', 'failed', {'error': str(e)})
            
            # 如果啟用通知，發送錯誤通知
            if self.config['notification_config']['enabled'] and self.config['notification_config']['notify_on_errors']:
                self._send_notification(f"獲取代理任務失敗: {e}", 'error')
    
    def validate_proxies_task(self):
        """驗證代理任務"""
        try:
            logger.info("開始執行驗證代理任務")
            
            # 重試暫時無效代理
            retried_proxies = self.proxy_manager.retry_temp_invalid_proxies()
            
            # 加載未測試代理
            untested_proxies = self.proxy_manager._load_proxies(self.proxy_manager.ProxyStatus.UNTESTED)
            
            # 合併需要驗證的代理
            all_proxies_to_validate = retried_proxies + untested_proxies
            
            if all_proxies_to_validate:
                # 批量驗證
                validated_proxies = self.proxy_manager.validate_proxy_batch(
                    all_proxies_to_validate,
                    batch_size=self.config['validation_schedule']['batch_size']
                )
                
                # 追蹤生命週期
                self.lifecycle_manager.track_proxy_validation(validated_proxies)
                
                # 追蹤狀態變化
                for proxy in validated_proxies:
                    if proxy.status != self.proxy_manager.ProxyStatus.UNTESTED:
                        self.lifecycle_manager.track_status_change(
                            proxy, 
                            self.proxy_manager.ProxyStatus.UNTESTED, 
                            proxy.status
                        )
                
                # 保存結果
                self.proxy_manager._save_proxies(validated_proxies)
                
                # 更新統計
                stats = self.proxy_manager.get_proxy_statistics()
                self.proxy_manager._save_stats(stats)
                
                logger.info(f"驗證代理任務完成：驗證 {len(validated_proxies)} 個代理")
            else:
                logger.info("沒有需要驗證的代理")
            
            # 更新任務狀態
            self.task_status['last_validation_time'] = datetime.now().isoformat()
            
            # 記錄任務歷史
            self._add_task_history(
                'validate_proxies',
                'success',
                {
                    'validated_proxies_count': len(all_proxies_to_validate) if all_proxies_to_validate else 0,
                    'retried_proxies_count': len(retried_proxies)
                }
            )
            
            # 檢查是否需要通知（有效代理數量過低）
            if self.config['notification_config']['enabled'] and self.config['notification_config']['notify_on_low_proxies']:
                valid_proxies = self.proxy_manager._load_proxies(self.proxy_manager.ProxyStatus.VALID)
                if len(valid_proxies) < self.config['notification_config']['min_valid_proxies_threshold']:
                    self._send_notification(
                        f"警告：有效代理數量過低 ({len(valid_proxies)} 個)", 
                        'warning'
                    )
            
        except Exception as e:
            logger.error(f"驗證代理任務失敗: {e}")
            self._add_task_history('validate_proxies', 'failed', {'error': str(e)})
            
            if self.config['notification_config']['enabled'] and self.config['notification_config']['notify_on_errors']:
                self._send_notification(f"驗證代理任務失敗: {e}", 'error')
    
    def cleanup_task(self):
        """清理任務"""
        try:
            logger.info("開始執行清理任務")
            
            # 清理舊代理
            cleaned_count = self.lifecycle_manager.cleanup_old_proxies()
            
            # 更新任務狀態
            self.task_status['last_cleanup_time'] = datetime.now().isoformat()
            
            # 記錄任務歷史
            self._add_task_history(
                'cleanup_proxies',
                'success',
                {'cleaned_proxies_count': cleaned_count}
            )
            
            logger.info(f"清理任務完成：清理 {cleaned_count} 個舊代理")
            
        except Exception as e:
            logger.error(f"清理任務失敗: {e}")
            self._add_task_history('cleanup_proxies', 'failed', {'error': str(e)})
    
    def generate_report_task(self):
        """生成報告任務"""
        try:
            logger.info("開始執行生成報告任務")
            
            # 獲取代理統計
            proxy_stats = self.proxy_manager.get_proxy_statistics()
            
            # 獲取生命週期分析
            lifecycle_analytics = self.lifecycle_manager.get_lifecycle_analytics()
            
            # 生成綜合報告
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'proxy_statistics': proxy_stats,
                'lifecycle_analytics': lifecycle_analytics,
                'task_status': self.task_status,
                'system_status': {
                    'is_running': self.is_running,
                    'uptime_hours': self._get_uptime_hours(),
                    'last_error': self._get_last_error()
                }
            }
            
            # 導出報告
            for format_type in self.config['report_schedule']['formats']:
                if format_type == 'json':
                    report_file = self.proxy_manager.data_dir / "reports" / f"proxy_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    report_file.parent.mkdir(exist_ok=True)
                    with open(report_file, 'w', encoding='utf-8') as f:
                        json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)
                    
                    logger.info(f"JSON報告已生成: {report_file}")
                
                elif format_type == 'csv':
                    # 導出有效代理CSV
                    csv_file = self.proxy_manager.export_proxies('csv', self.proxy_manager.ProxyStatus.VALID)
                    logger.info(f"CSV報告已生成: {csv_file}")
            
            # 導出生命週期報告
            lifecycle_report = self.lifecycle_manager.export_lifecycle_report('json')
            logger.info(f"生命週期報告已生成: {lifecycle_report}")
            
            # 更新任務狀態
            self.task_status['last_report_time'] = datetime.now().isoformat()
            
            # 記錄任務歷史
            self._add_task_history('generate_report', 'success', {'formats': self.config['report_schedule']['formats']})
            
            logger.info("生成報告任務完成")
            
        except Exception as e:
            logger.error(f"生成報告任務失敗: {e}")
            self._add_task_history('generate_report', 'failed', {'error': str(e)})
    
    def _get_uptime_hours(self) -> float:
        """獲取運行時間（小時）"""
        # 這裡可以實現更複雜的運行時間追蹤
        return 0.0
    
    def _get_last_error(self) -> Optional[str]:
        """獲取最後一個錯誤"""
        for record in reversed(self.task_status['task_history']):
            if record['status'] == 'failed':
                return record['details'].get('error', 'Unknown error')
        return None
    
    def _send_notification(self, message: str, level: str = 'info'):
        """發送通知"""
        try:
            # 這裡可以實現各種通知方式（Webhook、郵件等）
            logger.info(f"通知 [{level}]: {message}")
            
            # Webhook通知
            webhook_url = self.config['notification_config'].get('webhook_url')
            if webhook_url:
                # 實現Webhook通知邏輯
                pass
            
            # 郵件通知
            email_config = self.config['notification_config'].get('email_config')
            if email_config:
                # 實現郵件通知邏輯
                pass
                
        except Exception as e:
            logger.error(f"發送通知失敗: {e}")
    
    def setup_schedules(self):
        """設置定時任務"""
        # 清除現有任務
        schedule.clear()
        
        # 獲取代理任務
        if self.config['fetch_schedule']['enabled']:
            hours = self.config['fetch_schedule']['interval_hours']
            schedule.every(hours).hours.do(self.fetch_proxies_task)
            logger.info(f"設置獲取代理任務：每 {hours} 小時執行一次")
        
        # 驗證代理任務
        if self.config['validation_schedule']['enabled']:
            hours = self.config['validation_schedule']['interval_hours']
            schedule.every(hours).hours.do(self.validate_proxies_task)
            logger.info(f"設置驗證代理任務：每 {hours} 小時執行一次")
        
        # 清理任務
        if self.config['cleanup_schedule']['enabled']:
            hours = self.config['cleanup_schedule']['interval_hours']
            schedule.every(hours).hours.do(self.cleanup_task)
            logger.info(f"設置清理任務：每 {hours} 小時執行一次")
        
        # 生成報告任務
        if self.config['report_schedule']['enabled']:
            hours = self.config['report_schedule']['interval_hours']
            schedule.every(hours).hours.do(self.generate_report_task)
            logger.info(f"設置生成報告任務：每 {hours} 小時執行一次")
    
    def run_scheduler(self):
        """運行調度器"""
        self.is_running = True
        self._load_task_status()
        
        logger.info("代理管理自動化調度器開始運行")
        
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # 每分鐘檢查一次
            except KeyboardInterrupt:
                logger.info("接收到中斷信號，正在停止調度器...")
                self.stop_scheduler()
                break
            except Exception as e:
                logger.error(f"調度器運行錯誤: {e}")
                time.sleep(60)  # 出錯後等待一分鐘再繼續
    
    def start_scheduler(self):
        """啟動調度器"""
        if self.is_running:
            logger.warning("調度器已在運行中")
            return
        
        self.setup_schedules()
        
        # 啟動調度器線程
        self.scheduler_thread = threading.Thread(target=self.run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        logger.info("代理管理自動化調度器已啟動")
    
    def stop_scheduler(self):
        """停止調度器"""
        self.is_running = False
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=10)
        
        # 關閉線程池
        self.executor.shutdown(wait=True)
        
        logger.info("代理管理自動化調度器已停止")
    
    def get_status(self) -> Dict:
        """獲取調度器狀態"""
        return {
            'is_running': self.is_running,
            'uptime_hours': self._get_uptime_hours(),
            'next_tasks': self._get_next_tasks(),
            'task_status': self.task_status,
            'config': self.config,
            'last_updated': datetime.now().isoformat()
        }
    
    def _get_next_tasks(self) -> List[Dict]:
        """獲取下一個任務列表"""
        next_tasks = []
        for job in schedule.jobs:
            next_run = job.next_run
            if next_run:
                next_tasks.append({
                    'job_function': job.job_func.__name__,
                    'next_run': next_run.strftime('%Y-%m-%d %H:%M:%S'),
                    'interval': str(job.interval)
                })
        return next_tasks
    
    def run_task_now(self, task_name: str):
        """立即執行指定任務"""
        task_map = {
            'fetch': self.fetch_proxies_task,
            'validate': self.validate_proxies_task,
            'cleanup': self.cleanup_task,
            'report': self.generate_report_task
        }
        
        if task_name in task_map:
            logger.info(f"手動執行任務: {task_name}")
            task_map[task_name]()
        else:
            logger.error(f"未知的任務: {task_name}")
    
    def export_config(self, file_path: str):
        """導出當前配置"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            logger.info(f"配置已導出到: {file_path}")
        except Exception as e:
            logger.error(f"導出配置失敗: {e}")


if __name__ == "__main__":
    # 測試自動化調度器
    scheduler = ProxyAutomationScheduler()
    
    # 顯示狀態
    status = scheduler.get_status()
    print("調度器狀態:")
    print(f"運行狀態: {status['is_running']}")
    print(f"下一個任務: {status['next_tasks']}")
    
    # 手動執行一次任務
    print("\n手動執行獲取代理任務...")
    scheduler.run_task_now('fetch')
    
    # 啟動調度器（簡短測試）
    print("\n啟動調度器進行測試...")
    scheduler.start_scheduler()
    
    # 運行30秒後停止
    try:
        time.sleep(30)
    except KeyboardInterrupt:
        pass
    
    scheduler.stop_scheduler()
    print("\n調度器測試完成")