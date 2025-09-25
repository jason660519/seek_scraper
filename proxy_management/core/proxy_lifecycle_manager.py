"""
代理生命週期管理器
管理代理從獲取到失效的完整生命週期
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
import logging

from proxy_management.core.comprehensive_proxy_manager import ComprehensiveProxyManager, ProxyInfo, ProxyStatus

logger = logging.getLogger(__name__)


class LifecycleEvent(Enum):
    """生命週期事件"""
    FETCHED = "fetched"           # 代理被獲取
    VALIDATED = "validated"       # 代理被驗證
    BECAME_VALID = "became_valid"     # 代理變為有效
    BECAME_TEMP_INVALID = "became_temp_invalid"  # 代理變為暫時無效
    BECAME_INVALID = "became_invalid"    # 代理變為永久失效
    RETRIED = "retried"           # 代理被重試
    CLEANED_UP = "cleaned_up"     # 代理被清理


@dataclass
class LifecycleRecord:
    """生命週期記錄"""
    proxy_key: str  # ip:port:protocol
    event: LifecycleEvent
    timestamp: datetime
    details: Dict
    previous_status: Optional[ProxyStatus] = None
    new_status: Optional[ProxyStatus] = None


class ProxyLifecycleManager:
    """代理生命週期管理器"""
    
    def __init__(self, manager: ComprehensiveProxyManager):
        self.manager = manager
        self.data_dir = manager.data_dir
        
        # 生命週期日誌文件
        self.lifecycle_log_file = self.data_dir / "lifecycle_log.json"
        self.lifecycle_stats_file = self.data_dir / "lifecycle_stats.json"
        
        # 配置參數
        self.config = {
            'max_lifecycle_days': 30,      # 代理最大生命週期（天）
            'cleanup_interval_hours': 24,   # 清理間隔（小時）
            'max_log_entries': 10000,      # 最大日誌條目數
            'retention_days': 7            # 日誌保留天數
        }
        
        # 生命週期統計
        self.lifecycle_stats = self._load_lifecycle_stats()
        
        # 代理追蹤字典
        self.proxy_tracker: Dict[str, Dict] = {}
    
    def _load_lifecycle_stats(self) -> Dict:
        """加載生命週期統計"""
        if self.lifecycle_stats_file.exists():
            try:
                with open(self.lifecycle_stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加載生命週期統計失敗: {e}")
        
        return self._create_default_lifecycle_stats()
    
    def _save_lifecycle_stats(self):
        """保存生命週期統計"""
        try:
            with open(self.lifecycle_stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.lifecycle_stats, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            logger.error(f"保存生命週期統計失敗: {e}")
    
    def _create_default_lifecycle_stats(self) -> Dict:
        """創建默認生命週期統計"""
        return {
            'total_proxies_fetched': 0,
            'total_proxies_validated': 0,
            'total_proxies_became_valid': 0,
            'total_proxies_became_temp_invalid': 0,
            'total_proxies_became_invalid': 0,
            'total_proxies_retried': 0,
            'total_proxies_cleaned_up': 0,
            'average_lifecycle_hours': 0,
            'valid_rate_by_protocol': {},
            'valid_rate_by_source': {},
            'lifecycle_events_by_hour': {},
            'last_updated': datetime.now().isoformat()
        }
    
    def _log_lifecycle_event(self, proxy: ProxyInfo, event: LifecycleEvent, 
                            previous_status: ProxyStatus = None, details: Dict = None):
        """記錄生命週期事件"""
        proxy_key = f"{proxy.ip}:{proxy.port}:{proxy.protocol}"
        
        record = LifecycleRecord(
            proxy_key=proxy_key,
            event=event,
            timestamp=datetime.now(),
            details=details or {},
            previous_status=previous_status,
            new_status=proxy.status if event in [LifecycleEvent.BECAME_VALID, 
                                                LifecycleEvent.BECAME_TEMP_INVALID, 
                                                LifecycleEvent.BECAME_INVALID] else None
        )
        
        # 保存到日誌文件
        self._append_to_lifecycle_log(record)
        
        # 更新統計
        self._update_lifecycle_stats(event, proxy)
        
        # 更新代理追蹤
        self._update_proxy_tracker(proxy_key, event, proxy)
        
        logger.info(f"生命週期事件: {event.value} - {proxy_key}")
    
    def _append_to_lifecycle_log(self, record: LifecycleRecord):
        """追加到生命週期日誌"""
        try:
            # 讀取現有日誌
            logs = []
            if self.lifecycle_log_file.exists():
                with open(self.lifecycle_log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            
            # 添加新記錄
            log_entry = {
                'proxy_key': record.proxy_key,
                'event': record.event.value,
                'timestamp': record.timestamp.isoformat(),
                'details': record.details,
                'previous_status': record.previous_status.value if record.previous_status else None,
                'new_status': record.new_status.value if record.new_status else None
            }
            logs.append(log_entry)
            
            # 限制日誌數量
            if len(logs) > self.config['max_log_entries']:
                logs = logs[-self.config['max_log_entries']:]
            
            # 保存日誌
            with open(self.lifecycle_log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"追加生命週期日誌失敗: {e}")
    
    def _update_lifecycle_stats(self, event: LifecycleEvent, proxy: ProxyInfo):
        """更新生命週期統計"""
        event_key = f"total_proxies_{event.value}"
        if event_key in self.lifecycle_stats:
            self.lifecycle_stats[event_key] += 1
        
        # 按小時統計事件
        hour_key = datetime.now().strftime("%Y-%m-%d %H:00")
        event_hour_key = f"{event.value}_count"
        
        if hour_key not in self.lifecycle_stats['lifecycle_events_by_hour']:
            self.lifecycle_stats['lifecycle_events_by_hour'][hour_key] = {}
        
        if event_hour_key not in self.lifecycle_stats['lifecycle_events_by_hour'][hour_key]:
            self.lifecycle_stats['lifecycle_events_by_hour'][hour_key][event_hour_key] = 0
        
        self.lifecycle_stats['lifecycle_events_by_hour'][hour_key][event_hour_key] += 1
        
        # 更新協議有效率和來源有效率
        if event == LifecycleEvent.BECAME_VALID:
            protocol = proxy.protocol
            source = proxy.source
            
            # 協議有效率
            if protocol not in self.lifecycle_stats['valid_rate_by_protocol']:
                self.lifecycle_stats['valid_rate_by_protocol'][protocol] = {'valid': 0, 'total': 0}
            self.lifecycle_stats['valid_rate_by_protocol'][protocol]['valid'] += 1
            
            # 來源有效率
            if source not in self.lifecycle_stats['valid_rate_by_source']:
                self.lifecycle_stats['valid_rate_by_source'][source] = {'valid': 0, 'total': 0}
            self.lifecycle_stats['valid_rate_by_source'][source]['valid'] += 1
        
        # 更新總數
        if event in [LifecycleEvent.VALIDATED, LifecycleEvent.BECAME_VALID, 
                    LifecycleEvent.BECAME_TEMP_INVALID, LifecycleEvent.BECAME_INVALID]:
            protocol = proxy.protocol
            source = proxy.source
            
            if protocol in self.lifecycle_stats['valid_rate_by_protocol']:
                self.lifecycle_stats['valid_rate_by_protocol'][protocol]['total'] += 1
            
            if source in self.lifecycle_stats['valid_rate_by_source']:
                self.lifecycle_stats['valid_rate_by_source'][source]['total'] += 1
        
        self.lifecycle_stats['last_updated'] = datetime.now().isoformat()
        self._save_lifecycle_stats()
    
    def _update_proxy_tracker(self, proxy_key: str, event: LifecycleEvent, proxy: ProxyInfo):
        """更新代理追蹤器"""
        if proxy_key not in self.proxy_tracker:
            self.proxy_tracker[proxy_key] = {
                'first_seen': datetime.now().isoformat(),
                'last_event': None,
                'event_history': [],
                'current_status': proxy.status.value,
                'fail_count': proxy.fail_count,
                'source': proxy.source,
                'protocol': proxy.protocol
            }
        
        tracker = self.proxy_tracker[proxy_key]
        tracker['last_event'] = event.value
        tracker['current_status'] = proxy.status.value
        tracker['fail_count'] = proxy.fail_count
        tracker['event_history'].append({
            'event': event.value,
            'timestamp': datetime.now().isoformat(),
            'status': proxy.status.value
        })
        
        # 限制歷史記錄數量
        if len(tracker['event_history']) > 100:
            tracker['event_history'] = tracker['event_history'][-100:]
    
    def track_proxy_fetching(self, proxies: List[ProxyInfo]):
        """追蹤代理獲取"""
        for proxy in proxies:
            self._log_lifecycle_event(
                proxy, 
                LifecycleEvent.FETCHED,
                details={'source': proxy.source, 'protocol': proxy.protocol}
            )
    
    def track_proxy_validation(self, proxies: List[ProxyInfo]):
        """追蹤代理驗證"""
        for proxy in proxies:
            previous_status = proxy.status
            self._log_lifecycle_event(
                proxy,
                LifecycleEvent.VALIDATED,
                previous_status=previous_status,
                details={'protocol': proxy.protocol, 'source': proxy.source}
            )
    
    def track_status_change(self, proxy: ProxyInfo, old_status: ProxyStatus, new_status: ProxyStatus):
        """追蹤狀態變化"""
        event_map = {
            (ProxyStatus.UNTESTED, ProxyStatus.VALID): LifecycleEvent.BECAME_VALID,
            (ProxyStatus.TEMP_INVALID, ProxyStatus.VALID): LifecycleEvent.BECAME_VALID,
            (ProxyStatus.UNTESTED, ProxyStatus.TEMP_INVALID): LifecycleEvent.BECAME_TEMP_INVALID,
            (ProxyStatus.VALID, ProxyStatus.TEMP_INVALID): LifecycleEvent.BECAME_TEMP_INVALID,
            (ProxyStatus.UNTESTED, ProxyStatus.INVALID): LifecycleEvent.BECAME_INVALID,
            (ProxyStatus.TEMP_INVALID, ProxyStatus.INVALID): LifecycleEvent.BECAME_INVALID,
            (ProxyStatus.VALID, ProxyStatus.INVALID): LifecycleEvent.BECAME_INVALID
        }
        
        event = event_map.get((old_status, new_status))
        if event:
            self._log_lifecycle_event(
                proxy,
                event,
                previous_status=old_status,
                details={'fail_count': proxy.fail_count, 'response_time': proxy.response_time}
            )
    
    def track_proxy_retry(self, proxy: ProxyInfo):
        """追蹤代理重試"""
        self._log_lifecycle_event(
            proxy,
            LifecycleEvent.RETRIED,
            details={'fail_count': proxy.fail_count, 'last_tested': proxy.last_tested.isoformat() if proxy.last_tested else None}
        )
    
    def cleanup_old_proxies(self) -> int:
        """清理舊代理"""
        current_time = datetime.now()
        max_age = timedelta(days=self.config['max_lifecycle_days'])
        
        cleaned_count = 0
        
        # 清理各種狀態的代理
        for status in [ProxyStatus.VALID, ProxyStatus.TEMP_INVALID, ProxyStatus.INVALID]:
            proxies = self.manager._load_proxies(status)
            remaining_proxies = []
            
            for proxy in proxies:
                # 檢查代理年齡
                if proxy.last_tested and (current_time - proxy.last_tested) > max_age:
                    self._log_lifecycle_event(
                        proxy,
                        LifecycleEvent.CLEANED_UP,
                        details={'reason': 'too_old', 'age_days': (current_time - proxy.last_tested).days}
                    )
                    cleaned_count += 1
                else:
                    remaining_proxies.append(proxy)
            
            # 保存剩餘的代理
            self.manager._save_proxies(remaining_proxies, status)
        
        self.lifecycle_stats['total_proxies_cleaned_up'] += cleaned_count
        self._save_lifecycle_stats()
        
        logger.info(f"清理了 {cleaned_count} 個舊代理")
        return cleaned_count
    
    def get_lifecycle_analytics(self) -> Dict:
        """獲取生命週期分析"""
        # 計算平均生命週期
        total_lifecycle_hours = 0
        tracked_proxies = 0
        
        for proxy_key, tracker in self.proxy_tracker.items():
            if tracker['event_history']:
                first_event = datetime.fromisoformat(tracker['first_seen'])
                last_event_time = datetime.fromisoformat(tracker['event_history'][-1]['timestamp'])
                lifecycle_hours = (last_event_time - first_event).total_seconds() / 3600
                total_lifecycle_hours += lifecycle_hours
                tracked_proxies += 1
        
        avg_lifecycle_hours = total_lifecycle_hours / tracked_proxies if tracked_proxies > 0 else 0
        
        # 計算各狀態轉換率
        status_transitions = {}
        for proxy_key, tracker in self.proxy_tracker.items():
            for i, event in enumerate(tracker['event_history']):
                if i < len(tracker['event_history']) - 1:
                    transition = f"{event['status']} -> {tracker['event_history'][i+1]['status']}"
                    status_transitions[transition] = status_transitions.get(transition, 0) + 1
        
        # 計算協議和來源的有效率
        protocol_valid_rates = {}
        for protocol, stats in self.lifecycle_stats['valid_rate_by_protocol'].items():
            if stats['total'] > 0:
                protocol_valid_rates[protocol] = stats['valid'] / stats['total']
        
        source_valid_rates = {}
        for source, stats in self.lifecycle_stats['valid_rate_by_source'].items():
            if stats['total'] > 0:
                source_valid_rates[source] = stats['valid'] / stats['total']
        
        return {
            'average_lifecycle_hours': avg_lifecycle_hours,
            'tracked_proxy_count': len(self.proxy_tracker),
            'status_transitions': status_transitions,
            'protocol_valid_rates': protocol_valid_rates,
            'source_valid_rates': source_valid_rates,
            'lifecycle_stats': self.lifecycle_stats,
            'last_updated': datetime.now().isoformat()
        }
    
    def export_lifecycle_report(self, format_type: str = 'json') -> str:
        """導出生命週期報告"""
        report_data = {
            'lifecycle_stats': self.lifecycle_stats,
            'lifecycle_analytics': self.get_lifecycle_analytics(),
            'proxy_tracker_summary': {
                'total_tracked': len(self.proxy_tracker),
                'by_status': {},
                'by_protocol': {},
                'by_source': {}
            },
            'generated_at': datetime.now().isoformat()
        }
        
        # 統計追蹤的代理
        for proxy_key, tracker in self.proxy_tracker.items():
            status = tracker['current_status']
            protocol = tracker['protocol']
            source = tracker['source']
            
            report_data['proxy_tracker_summary']['by_status'][status] = \
                report_data['proxy_tracker_summary']['by_status'].get(status, 0) + 1
            
            report_data['proxy_tracker_summary']['by_protocol'][protocol] = \
                report_data['proxy_tracker_summary']['by_protocol'].get(protocol, 0) + 1
            
            report_data['proxy_tracker_summary']['by_source'][source] = \
                report_data['proxy_tracker_summary']['by_source'].get(source, 0) + 1
        
        # 導出文件
        export_dir = self.data_dir / "lifecycle_reports"
        export_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"lifecycle_report_{timestamp}.{format_type}"
        file_path = export_dir / filename
        
        if format_type == 'json':
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"導出生命週期報告到 {file_path}")
        return str(file_path)


if __name__ == "__main__":
    # 測試生命週期管理器
    manager = ComprehensiveProxyManager()
    lifecycle_manager = ProxyLifecycleManager(manager)
    
    # 運行完整週期並追蹤
    logger.info("開始代理生命週期管理測試")
    
    # 獲取代理
    new_proxies = manager.fetch_proxies_from_multiple_sources()
    lifecycle_manager.track_proxy_fetching(new_proxies)
    
    # 驗證代理
    validated_proxies = manager.validate_proxy_batch(new_proxies)
    lifecycle_manager.track_proxy_validation(validated_proxies)
    
    # 追蹤狀態變化
    for proxy in validated_proxies:
        if proxy.status != ProxyStatus.UNTESTED:
            lifecycle_manager.track_status_change(proxy, ProxyStatus.UNTESTED, proxy.status)
    
    # 導出分析報告
    analytics = lifecycle_manager.get_lifecycle_analytics()
    report_path = lifecycle_manager.export_lifecycle_report()
    
    print("生命週期分析完成")
    print(f"平均生命週期: {analytics['average_lifecycle_hours']:.2f} 小時")
    print(f"追蹤的代理數: {analytics['tracked_proxy_count']}")
    print(f"報告已導出到: {report_path}")