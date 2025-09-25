"""
高級可靠性測試模組

這個模組實現了代理 IP 的高級可靠性測試，包括：
1. 穩定性測試（長時間連接穩定性）
2. 負載測試（高並發請求處理能力）
3. 故障恢復測試（自動重連和恢復能力）
4. 資源使用測試（內存和連接數管理）
5. 網絡質量測試（延遲抖動和丟包率）
6. 可用性測試（持續可用性監控）

通過綜合分析這些維度來評估代理的可靠性等級。
"""

import asyncio
import aiohttp
import json
import time
import logging
import statistics
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil
import gc


@dataclass
class ReliabilityMetric:
    """可靠性指標"""
    metric_name: str
    value: float
    unit: str
    threshold: float
    passed: bool
    details: Dict[str, Any]


@dataclass
class ReliabilityTestResult:
    """可靠性測試結果"""
    test_name: str
    passed: bool
    score: float
    metrics: List[ReliabilityMetric]
    execution_time: float
    errors: List[str] = field(default_factory=list)


@dataclass
class ConnectionStats:
    """連接統計"""
    total_attempts: int = 0
    successful_connections: int = 0
    failed_connections: int = 0
    connection_errors: List[str] = field(default_factory=list)
    response_times: List[float] = field(default_factory=list)
    connection_durations: List[float] = field(default_factory=list)


class BaseReliabilityTest(ABC):
    """可靠性測試基類"""
    
    def __init__(self, name: str, timeout: int = 60):
        self.name = name
        self.timeout = timeout
        self.logger = logging.getLogger(f"ReliabilityTest.{name}")
    
    @abstractmethod
    async def execute(self, session: aiohttp.ClientSession, proxy_dict: Dict[str, str]) -> ReliabilityTestResult:
        """執行可靠性測試"""
        pass
    
    def _create_test_result(self, passed: bool, score: float, metrics: List[ReliabilityMetric], 
                          execution_time: float, errors: List[str] = None) -> ReliabilityTestResult:
        """創建測試結果"""
        return ReliabilityTestResult(
            test_name=self.name,
            passed=passed,
            score=score,
            metrics=metrics,
            execution_time=execution_time,
            errors=errors or []
        )


class StabilityTest(BaseReliabilityTest):
    """穩定性測試"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("stability_test", timeout=300)  # 5 分鐘超時
        self.config = config or {}
        self.test_duration = self.config.get('stability_test_duration', 180)  # 3 分鐘
        self.check_interval = self.config.get('stability_check_interval', 10)  # 10 秒
        self.success_threshold = self.config.get('stability_success_threshold', 0.95)  # 95% 成功率
    
    async def execute(self, session: aiohttp.ClientSession, proxy_dict: Dict[str, str]) -> ReliabilityTestResult:
        """執行穩定性測試"""
        start_time = time.time()
        stats = ConnectionStats()
        errors = []
        
        try:
            self.logger.info(f"Starting stability test for {self.test_duration} seconds")
            
            # 持續測試指定時間
            test_end_time = time.time() + self.test_duration
            check_count = 0
            
            while time.time() < test_end_time:
                check_count += 1
                check_start = time.time()
                
                try:
                    # 執行連接測試
                    success, response_time = await self._perform_connection_test(session, proxy_dict)
                    
                    stats.total_attempts += 1
                    if success:
                        stats.successful_connections += 1
                        stats.response_times.append(response_time)
                    else:
                        stats.failed_connections += 1
                    
                except Exception as e:
                    stats.total_attempts += 1
                    stats.failed_connections += 1
                    stats.connection_errors.append(str(e))
                    errors.append(f"Connection check {check_count} failed: {str(e)}")
                
                # 等待下一次檢查
                await asyncio.sleep(self.check_interval)
            
            # 計算指標
            metrics = self._calculate_stability_metrics(stats)
            
            # 計算分數
            success_rate = stats.successful_connections / stats.total_attempts if stats.total_attempts > 0 else 0
            score = success_rate * 100
            passed = success_rate >= self.success_threshold
            
            execution_time = time.time() - start_time
            return self._create_test_result(passed, score, metrics, execution_time, errors)
            
        except Exception as e:
            execution_time = time.time() - start_time
            return self._create_test_result(False, 0.0, [], execution_time, [str(e)])
    
    async def _perform_connection_test(self, session: aiohttp.ClientSession, 
                                     proxy_dict: Dict[str, str]) -> Tuple[bool, float]:
        """執行單次連接測試"""
        start_time = time.time()
        
        try:
            async with session.get(
                "https://httpbin.org/status/200",
                proxy=proxy_dict['https'],
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    return True, response_time
                else:
                    return False, response_time
                    
        except Exception as e:
            response_time = time.time() - start_time
            self.logger.debug(f"Connection test failed: {e}")
            return False, response_time
    
    def _calculate_stability_metrics(self, stats: ConnectionStats) -> List[ReliabilityMetric]:
        """計算穩定性指標"""
        metrics = []
        
        # 成功率
        success_rate = stats.successful_connections / stats.total_attempts if stats.total_attempts > 0 else 0
        metrics.append(ReliabilityMetric(
            metric_name="success_rate",
            value=success_rate * 100,
            unit="%",
            threshold=self.success_threshold * 100,
            passed=success_rate >= self.success_threshold,
            details={'total_attempts': stats.total_attempts, 'successful': stats.successful_connections}
        ))
        
        # 平均響應時間
        if stats.response_times:
            avg_response_time = statistics.mean(stats.response_times)
            metrics.append(ReliabilityMetric(
                metric_name="avg_response_time",
                value=avg_response_time,
                unit="seconds",
                threshold=5.0,  # 5 秒閾值
                passed=avg_response_time <= 5.0,
                details={'response_times': stats.response_times}
            ))
        
        # 響應時間標準差（穩定性指標）
        if len(stats.response_times) > 1:
            response_time_std = statistics.stdev(stats.response_times)
            metrics.append(ReliabilityMetric(
                metric_name="response_time_stability",
                value=response_time_std,
                unit="seconds",
                threshold=2.0,  # 2 秒閾值
                passed=response_time_std <= 2.0,
                details={'std_dev': response_time_std}
            ))
        
        return metrics


class LoadTest(BaseReliabilityTest):
    """負載測試"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("load_test", timeout=180)  # 3 分鐘超時
        self.config = config or {}
        self.concurrent_requests = self.config.get('load_concurrent_requests', 50)
        self.requests_per_second = self.config.get('load_requests_per_second', 10)
        self.test_duration = self.config.get('load_test_duration', 60)  # 1 分鐘
        self.response_time_threshold = self.config.get('load_response_time_threshold', 5.0)  # 5 秒
    
    async def execute(self, session: aiohttp.ClientSession, proxy_dict: Dict[str, str]) -> ReliabilityTestResult:
        """執行負載測試"""
        start_time = time.time()
        stats = ConnectionStats()
        errors = []
        
        try:
            self.logger.info(f"Starting load test: {self.concurrent_requests} concurrent requests")
            
            # 使用信號量控制並發數
            semaphore = asyncio.Semaphore(self.concurrent_requests)
            
            # 創建請求任務
            tasks = []
            total_requests = self.requests_per_second * self.test_duration
            
            for i in range(total_requests):
                task = asyncio.create_task(
                    self._perform_load_request(session, proxy_dict, semaphore, i)
                )
                tasks.append(task)
                
                # 控制請求速率
                if (i + 1) % self.requests_per_second == 0:
                    await asyncio.sleep(1)
            
            # 等待所有請求完成
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 統計結果
            for result in results:
                stats.total_attempts += 1
                
                if isinstance(result, tuple) and len(result) == 2:
                    success, response_time = result
                    if success:
                        stats.successful_connections += 1
                        stats.response_times.append(response_time)
                    else:
                        stats.failed_connections += 1
                else:
                    stats.failed_connections += 1
                    if isinstance(result, Exception):
                        errors.append(f"Request failed: {str(result)}")
            
            # 計算指標
            metrics = self._calculate_load_metrics(stats)
            
            # 計算分數
            success_rate = stats.successful_connections / stats.total_attempts if stats.total_attempts > 0 else 0
            score = success_rate * 100
            passed = success_rate >= 0.9  # 90% 成功率
            
            execution_time = time.time() - start_time
            return self._create_test_result(passed, score, metrics, execution_time, errors)
            
        except Exception as e:
            execution_time = time.time() - start_time
            return self._create_test_result(False, 0.0, [], execution_time, [str(e)])
    
    async def _perform_load_request(self, session: aiohttp.ClientSession, 
                                  proxy_dict: Dict[str, str], semaphore: asyncio.Semaphore,
                                  request_id: int) -> Tuple[bool, float]:
        """執行單個負載請求"""
        async with semaphore:
            start_time = time.time()
            
            try:
                async with session.get(
                    f"https://httpbin.org/status/200?id={request_id}",
                    proxy=proxy_dict['https'],
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        return True, response_time
                    else:
                        return False, response_time
                        
            except Exception as e:
                response_time = time.time() - start_time
                self.logger.debug(f"Load request {request_id} failed: {e}")
                return False, response_time
    
    def _calculate_load_metrics(self, stats: ConnectionStats) -> List[ReliabilityMetric]:
        """計算負載指標"""
        metrics = []
        
        # 成功率
        success_rate = stats.successful_connections / stats.total_attempts if stats.total_attempts > 0 else 0
        metrics.append(ReliabilityMetric(
            metric_name="load_success_rate",
            value=success_rate * 100,
            unit="%",
            threshold=90.0,
            passed=success_rate >= 0.9,
            details={'total_requests': stats.total_attempts, 'successful': stats.successful_connections}
        ))
        
        # 平均響應時間
        if stats.response_times:
            avg_response_time = statistics.mean(stats.response_times)
            metrics.append(ReliabilityMetric(
                metric_name="load_avg_response_time",
                value=avg_response_time,
                unit="seconds",
                threshold=self.response_time_threshold,
                passed=avg_response_time <= self.response_time_threshold,
                details={'avg_time': avg_response_time}
            ))
        
        # 響應時間百分位數（P95）
        if stats.response_times:
            p95_response_time = statistics.quantiles(stats.response_times, n=20)[18]  # 第95百分位
            metrics.append(ReliabilityMetric(
                metric_name="load_p95_response_time",
                value=p95_response_time,
                unit="seconds",
                threshold=self.response_time_threshold * 2,
                passed=p95_response_time <= self.response_time_threshold * 2,
                details={'p95_time': p95_response_time}
            ))
        
        return metrics


class FaultRecoveryTest(BaseReliabilityTest):
    """故障恢復測試"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("fault_recovery_test", timeout=300)  # 5 分鐘超時
        self.config = config or {}
        self.recovery_attempts = self.config.get('recovery_attempts', 5)
        self.recovery_interval = self.config.get('recovery_interval', 30)  # 30 秒
        self.recovery_threshold = self.config.get('recovery_threshold', 0.8)  # 80% 恢復率
    
    async def execute(self, session: aiohttp.ClientSession, proxy_dict: Dict[str, str]) -> ReliabilityTestResult:
        """執行故障恢復測試"""
        start_time = time.time()
        stats = ConnectionStats()
        errors = []
        
        try:
            self.logger.info("Starting fault recovery test")
            
            # 第一步：建立正常連接
            initial_success = await self._test_initial_connection(session, proxy_dict)
            if not initial_success:
                return self._create_test_result(False, 0.0, [], time.time() - start_time, 
                                              ["Initial connection failed"])
            
            # 第二步：模擬故障（這裡模擬網絡延遲或超時）
            self.logger.info("Simulating network fault...")
            await asyncio.sleep(5)  # 模擬網絡中斷
            
            # 第三步：測試恢復能力
            recovery_results = []
            
            for attempt in range(self.recovery_attempts):
                self.logger.info(f"Recovery attempt {attempt + 1}/{self.recovery_attempts}")
                
                attempt_start = time.time()
                
                try:
                    # 嘗試恢復連接
                    success, response_time = await self._perform_connection_test(session, proxy_dict)
                    
                    recovery_results.append({
                        'attempt': attempt + 1,
                        'success': success,
                        'response_time': response_time,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    stats.total_attempts += 1
                    if success:
                        stats.successful_connections += 1
                        stats.response_times.append(response_time)
                    else:
                        stats.failed_connections += 1
                    
                except Exception as e:
                    recovery_results.append({
                        'attempt': attempt + 1,
                        'success': False,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    stats.total_attempts += 1
                    stats.failed_connections += 1
                    errors.append(f"Recovery attempt {attempt + 1} failed: {str(e)}")
                
                # 等待下一次嘗試
                if attempt < self.recovery_attempts - 1:
                    await asyncio.sleep(self.recovery_interval)
            
            # 計算指標
            metrics = self._calculate_recovery_metrics(stats, recovery_results)
            
            # 計算分數
            recovery_rate = stats.successful_connections / stats.total_attempts if stats.total_attempts > 0 else 0
            score = recovery_rate * 100
            passed = recovery_rate >= self.recovery_threshold
            
            execution_time = time.time() - start_time
            return self._create_test_result(passed, score, metrics, execution_time, errors)
            
        except Exception as e:
            execution_time = time.time() - start_time
            return self._create_test_result(False, 0.0, [], execution_time, [str(e)])
    
    async def _test_initial_connection(self, session: aiohttp.ClientSession, 
                                     proxy_dict: Dict[str, str]) -> bool:
        """測試初始連接"""
        try:
            async with session.get(
                "https://httpbin.org/status/200",
                proxy=proxy_dict['https'],
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                return response.status == 200
        except Exception:
            return False
    
    async def _perform_connection_test(self, session: aiohttp.ClientSession, 
                                       proxy_dict: Dict[str, str]) -> Tuple[bool, float]:
        """執行連接測試"""
        start_time = time.time()
        
        try:
            async with session.get(
                "https://httpbin.org/status/200",
                proxy=proxy_dict['https'],
                timeout=aiohttp.ClientTimeout(total=15)  # 恢復測試使用更長的超時
            ) as response:
                response_time = time.time() - start_time
                return response.status == 200, response_time
                
        except Exception as e:
            response_time = time.time() - start_time
            self.logger.debug(f"Connection test failed: {e}")
            return False, response_time
    
    def _calculate_recovery_metrics(self, stats: ConnectionStats, 
                                  recovery_results: List[Dict[str, Any]]) -> List[ReliabilityMetric]:
        """計算恢復指標"""
        metrics = []
        
        # 恢復成功率
        recovery_rate = stats.successful_connections / stats.total_attempts if stats.total_attempts > 0 else 0
        metrics.append(ReliabilityMetric(
            metric_name="recovery_success_rate",
            value=recovery_rate * 100,
            unit="%",
            threshold=self.recovery_threshold * 100,
            passed=recovery_rate >= self.recovery_threshold,
            details={'total_attempts': stats.total_attempts, 'successful': stats.successful_connections}
        ))
        
        # 平均恢復時間
        if stats.response_times:
            avg_recovery_time = statistics.mean(stats.response_times)
            metrics.append(ReliabilityMetric(
                metric_name="avg_recovery_time",
                value=avg_recovery_time,
                unit="seconds",
                threshold=10.0,  # 10 秒閾值
                passed=avg_recovery_time <= 10.0,
                details={'avg_time': avg_recovery_time}
            ))
        
        # 首次成功恢復時間
        first_success_time = None
        for result in recovery_results:
            if result.get('success', False) and 'response_time' in result:
                first_success_time = result['response_time']
                break
        
        if first_success_time is not None:
            metrics.append(ReliabilityMetric(
                metric_name="first_recovery_time",
                value=first_success_time,
                unit="seconds",
                threshold=30.0,  # 30 秒閾值
                passed=first_success_time <= 30.0,
                details={'first_success_time': first_success_time}
            ))
        
        return metrics


class NetworkQualityTest(BaseReliabilityTest):
    """網絡質量測試"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("network_quality_test", timeout=180)  # 3 分鐘超時
        self.config = config or {}
        self.ping_count = self.config.get('network_ping_count', 100)
        self.jitter_threshold = self.config.get('network_jitter_threshold', 50)  # 50ms
        self.packet_loss_threshold = self.config.get('network_packet_loss_threshold', 5)  # 5%
    
    async def execute(self, session: aiohttp.ClientSession, proxy_dict: Dict[str, str]) -> ReliabilityTestResult:
        """執行網絡質量測試"""
        start_time = time.time()
        stats = ConnectionStats()
        errors = []
        
        try:
            self.logger.info(f"Starting network quality test with {self.ping_count} pings")
            
            # 執行多次 ping 測試
            ping_tasks = []
            for i in range(self.ping_count):
                task = asyncio.create_task(self._perform_ping_test(session, proxy_dict, i))
                ping_tasks.append(task)
                
                # 控制測試速率
                await asyncio.sleep(0.1)  # 100ms 間隔
            
            # 等待所有 ping 完成
            ping_results = await asyncio.gather(*ping_tasks, return_exceptions=True)
            
            # 統計結果
            response_times = []
            packet_loss_count = 0
            
            for result in ping_results:
                stats.total_attempts += 1
                
                if isinstance(result, tuple) and len(result) == 2:
                    success, response_time = result
                    if success:
                        stats.successful_connections += 1
                        response_times.append(response_time)
                        stats.response_times.append(response_time)
                    else:
                        stats.failed_connections += 1
                        packet_loss_count += 1
                else:
                    stats.failed_connections += 1
                    packet_loss_count += 1
                    if isinstance(result, Exception):
                        errors.append(f"Ping failed: {str(result)}")
            
            # 計算指標
            metrics = self._calculate_network_metrics(response_times, packet_loss_count, stats)
            
            # 計算分數
            packet_loss_rate = packet_loss_count / self.ping_count if self.ping_count > 0 else 0
            
            # 基於丟包率和抖動計算分數
            packet_loss_score = max(0, (1 - packet_loss_rate) * 60)  # 丟包率佔 60%
            
            if response_times:
                jitter = statistics.stdev(response_times) if len(response_times) > 1 else 0
                jitter_score = max(0, (1 - min(jitter / 100, 1)) * 40)  # 抖動佔 40%
            else:
                jitter_score = 0
            
            score = packet_loss_score + jitter_score
            passed = packet_loss_rate <= (self.packet_loss_threshold / 100) and \
                    (not response_times or statistics.stdev(response_times) <= self.jitter_threshold)
            
            execution_time = time.time() - start_time
            return self._create_test_result(passed, score, metrics, execution_time, errors)
            
        except Exception as e:
            execution_time = time.time() - start_time
            return self._create_test_result(False, 0.0, [], execution_time, [str(e)])
    
    async def _perform_ping_test(self, session: aiohttp.ClientSession, 
                                proxy_dict: Dict[str, str], ping_id: int) -> Tuple[bool, float]:
        """執行單次 ping 測試"""
        start_time = time.time()
        
        try:
            async with session.get(
                f"https://httpbin.org/status/200?ping={ping_id}",
                proxy=proxy_dict['https'],
                timeout=aiohttp.ClientTimeout(total=5)  # 5 秒超時
            ) as response:
                response_time = (time.time() - start_time) * 1000  # 轉換為毫秒
                
                if response.status == 200:
                    return True, response_time
                else:
                    return False, response_time
                    
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.logger.debug(f"Ping {ping_id} failed: {e}")
            return False, response_time
    
    def _calculate_network_metrics(self, response_times: List[float], 
                                 packet_loss_count: int, stats: ConnectionStats) -> List[ReliabilityMetric]:
        """計算網絡指標"""
        metrics = []
        
        # 丟包率
        packet_loss_rate = packet_loss_count / self.ping_count if self.ping_count > 0 else 0
        metrics.append(ReliabilityMetric(
            metric_name="packet_loss_rate",
            value=packet_loss_rate * 100,
            unit="%",
            threshold=self.packet_loss_threshold,
            passed=packet_loss_rate <= (self.packet_loss_threshold / 100),
            details={'lost_packets': packet_loss_count, 'total_packets': self.ping_count}
        ))
        
        # 平均延遲
        if response_times:
            avg_latency = statistics.mean(response_times)
            metrics.append(ReliabilityMetric(
                metric_name="avg_latency",
                value=avg_latency,
                unit="ms",
                threshold=200,  # 200ms 閾值
                passed=avg_latency <= 200,
                details={'avg_latency': avg_latency}
            ))
        
        # 延遲抖動（標準差）
        if len(response_times) > 1:
            jitter = statistics.stdev(response_times)
            metrics.append(ReliabilityMetric(
                metric_name="jitter",
                value=jitter,
                unit="ms",
                threshold=self.jitter_threshold,
                passed=jitter <= self.jitter_threshold,
                details={'jitter': jitter}
            ))
        
        # 最小/最大延遲
        if response_times:
            min_latency = min(response_times)
            max_latency = max(response_times)
            metrics.append(ReliabilityMetric(
                metric_name="latency_range",
                value=max_latency - min_latency,
                unit="ms",
                threshold=100,  # 100ms 範圍閾值
                passed=(max_latency - min_latency) <= 100,
                details={'min_latency': min_latency, 'max_latency': max_latency}
            ))
        
        return metrics


class ResourceUsageTest(BaseReliabilityTest):
    """資源使用測試"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("resource_usage_test", timeout=120)  # 2 分鐘超時
        self.config = config or {}
        self.memory_threshold = self.config.get('resource_memory_threshold', 500)  # 500MB
        self.connection_threshold = self.config.get('resource_connection_threshold', 100)  # 100 連接
    
    async def execute(self, session: aiohttp.ClientSession, proxy_dict: Dict[str, str]) -> ReliabilityTestResult:
        """執行資源使用測試"""
        start_time = time.time()
        stats = ConnectionStats()
        errors = []
        
        try:
            self.logger.info("Starting resource usage test")
            
            # 記錄初始資源使用情況
            initial_memory = psutil.virtual_memory().used / (1024 * 1024)  # MB
            initial_connections = self._count_connections()
            
            # 執行大量請求來測試資源使用
            resource_test_tasks = []
            for i in range(50):  # 50 個並發請求
                task = asyncio.create_task(
                    self._perform_resource_test_request(session, proxy_dict, i)
                )
                resource_test_tasks.append(task)
            
            # 等待所有請求完成
            await asyncio.gather(*resource_test_tasks, return_exceptions=True)
            
            # 等待一段時間讓資源釋放
            await asyncio.sleep(5)
            
            # 記錄最終資源使用情況
            final_memory = psutil.virtual_memory().used / (1024 * 1024)  # MB
            final_connections = self._count_connections()
            
            # 計算指標
            metrics = self._calculate_resource_metrics(
                initial_memory, final_memory, 
                initial_connections, final_connections
            )
            
            # 計算分數
            memory_increase = final_memory - initial_memory
            connection_increase = final_connections - initial_connections
            
            # 基於資源增長計算分數
            memory_score = max(0, (1 - min(memory_increase / self.memory_threshold, 1)) * 50)
            connection_score = max(0, (1 - min(connection_increase / self.connection_threshold, 1)) * 50)
            
            score = memory_score + connection_score
            passed = memory_increase <= self.memory_threshold and connection_increase <= self.connection_threshold
            
            execution_time = time.time() - start_time
            return self._create_test_result(passed, score, metrics, execution_time, errors)
            
        except Exception as e:
            execution_time = time.time() - start_time
            return self._create_test_result(False, 0.0, [], execution_time, [str(e)])
    
    async def _perform_resource_test_request(self, session: aiohttp.ClientSession, 
                                           proxy_dict: Dict[str, str], request_id: int) -> None:
        """執行資源測試請求"""
        try:
            async with session.get(
                f"https://httpbin.org/delay/1?id={request_id}",
                proxy=proxy_dict['https'],
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    # 讀取響應內容以確保連接被使用
                    await response.text()
        except Exception as e:
            self.logger.debug(f"Resource test request {request_id} failed: {e}")
    
    def _count_connections(self) -> int:
        """統計連接數"""
        try:
            connections = psutil.net_connections()
            return len([conn for conn in connections if conn.status == 'ESTABLISHED'])
        except Exception:
            return 0
    
    def _calculate_resource_metrics(self, initial_memory: float, final_memory: float,
                                  initial_connections: int, final_connections: int) -> List[ReliabilityMetric]:
        """計算資源指標"""
        metrics = []
        
        # 內存增長
        memory_increase = final_memory - initial_memory
        metrics.append(ReliabilityMetric(
            metric_name="memory_increase",
            value=memory_increase,
            unit="MB",
            threshold=self.memory_threshold,
            passed=memory_increase <= self.memory_threshold,
            details={'initial_memory': initial_memory, 'final_memory': final_memory}
        ))
        
        # 連接數增長
        connection_increase = final_connections - initial_connections
        metrics.append(ReliabilityMetric(
            metric_name="connection_increase",
            value=connection_increase,
            unit="connections",
            threshold=self.connection_threshold,
            passed=connection_increase <= self.connection_threshold,
            details={'initial_connections': initial_connections, 'final_connections': final_connections}
        ))
        
        # 內存洩漏檢測（簡化版）
        memory_leak_detected = memory_increase > (self.memory_threshold * 0.5)  # 超過 50% 閾值認為有洩漏
        metrics.append(ReliabilityMetric(
            metric_name="memory_leak_risk",
            value=1.0 if memory_leak_detected else 0.0,
            unit="boolean",
            threshold=0.5,
            passed=not memory_leak_detected,
            details={'memory_increase': memory_increase, 'threshold': self.memory_threshold * 0.5}
        ))
        
        return metrics


class AdvancedReliabilityTester:
    """高級可靠性測試器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.timeout = self.config.get('reliability_timeout', 300)
        self.max_retries = self.config.get('reliability_max_retries', 3)
        
        # 初始化所有測試
        self.tests = [
            StabilityTest(self.config),
            LoadTest(self.config),
            FaultRecoveryTest(self.config),
            NetworkQualityTest(self.config),
            ResourceUsageTest(self.config)
        ]
        
        self.logger = logging.getLogger("AdvancedReliabilityTester")
    
    async def run_full_reliability_test(self, proxy_dict: Dict[str, str]) -> Dict[str, Any]:
        """運行完整的可靠性測試"""
        start_time = time.time()
        
        self.logger.info(f"Starting full reliability test for proxy: {proxy_dict.get('http', 'unknown')}")
        
        # 並行執行所有測試
        test_tasks = []
        for test in self.tests:
            task = asyncio.create_task(self._run_single_test(test, session, proxy_dict))
            test_tasks.append(task)
        
        # 創建會話
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        ) as session:
            
            # 執行所有測試
            test_results = await asyncio.gather(*test_tasks, return_exceptions=True)
            
            # 處理結果
            processed_results = {}
            total_score = 0.0
            total_weight = 0.0
            all_metrics = []
            all_errors = []
            
            for i, result in enumerate(test_results):
                test_name = self.tests[i].name
                
                if isinstance(result, Exception):
                    self.logger.error(f"Test {test_name} failed: {result}")
                    processed_results[test_name] = {
                        'passed': False,
                        'score': 0.0,
                        'error': str(result)
                    }
                    all_errors.append(f"{test_name}: {str(result)}")
                else:
                    processed_results[test_name] = {
                        'passed': result.passed,
                        'score': result.score,
                        'metrics': self._format_metrics(result.metrics),
                        'execution_time': result.execution_time,
                        'errors': result.errors
                    }
                    
                    all_metrics.extend(result.metrics)
                    all_errors.extend(result.errors)
                    
                    # 計算加權分數
                    weight = self._get_test_weight(test_name)
                    total_score += result.score * weight
                    total_weight += weight
            
            # 計算總體分數
            overall_score = total_score / total_weight if total_weight > 0 else 0.0
            
            # 確定可靠性等級
            reliability_level = self._determine_reliability_level(overall_score, processed_results)
            
            execution_time = time.time() - start_time
            
            return {
                'timestamp': datetime.now().isoformat(),
                'proxy': proxy_dict.get('http', 'unknown'),
                'reliability_level': reliability_level,
                'overall_score': overall_score,
                'test_results': processed_results,
                'summary_metrics': self._generate_summary_metrics(all_metrics),
                'execution_time': execution_time,
                'errors': all_errors,
                'recommendations': self._generate_recommendations(processed_results, reliability_level)
            }
    
    async def _run_single_test(self, test: BaseReliabilityTest, session: aiohttp.ClientSession,
                             proxy_dict: Dict[str, str]) -> ReliabilityTestResult:
        """運行單個測試"""
        try:
            return await test.execute(session, proxy_dict)
        except Exception as e:
            # 如果測試失敗，返回失敗結果
            return ReliabilityTestResult(
                test_name=test.name,
                passed=False,
                score=0.0,
                metrics=[],
                execution_time=0.0,
                errors=[f"Test execution failed: {str(e)}"]
            )
    
    def _get_test_weight(self, test_name: str) -> float:
        """獲取測試權重"""
        weights = {
            'stability_test': 0.25,           # 穩定性最重要
            'load_test': 0.20,                # 負載能力次重要
            'fault_recovery_test': 0.20,      # 故障恢復能力
            'network_quality_test': 0.20,     # 網絡質量
            'resource_usage_test': 0.15       # 資源使用效率
        }
        return weights.get(test_name, 0.20)
    
    def _determine_reliability_level(self, overall_score: float, test_results: Dict[str, Any]) -> str:
        """確定可靠性等級"""
        # 基於總分確定等級
        if overall_score >= 90:
            return "enterprise"
        elif overall_score >= 80:
            return "professional"
        elif overall_score >= 70:
            return "standard"
        elif overall_score >= 60:
            return "basic"
        else:
            return "unreliable"
    
    def _format_metrics(self, metrics: List[ReliabilityMetric]) -> List[Dict[str, Any]]:
        """格式化指標"""
        return [
            {
                'name': metric.metric_name,
                'value': metric.value,
                'unit': metric.unit,
                'threshold': metric.threshold,
                'passed': metric.passed,
                'details': metric.details
            }
            for metric in metrics
        ]
    
    def _generate_summary_metrics(self, all_metrics: List[ReliabilityMetric]) -> Dict[str, Any]:
        """生成摘要指標"""
        summary = {
            'total_metrics': len(all_metrics),
            'passed_metrics': sum(1 for m in all_metrics if m.passed),
            'failed_metrics': sum(1 for m in all_metrics if not m.passed)
        }
        
        # 計算關鍵指標的平均值
        key_metrics = ['success_rate', 'avg_response_time', 'packet_loss_rate', 'jitter']
        for key_metric in key_metrics:
            relevant_metrics = [m for m in all_metrics if key_metric in m.metric_name]
            if relevant_metrics:
                avg_value = statistics.mean([m.value for m in relevant_metrics])
                summary[f'avg_{key_metric}'] = avg_value
        
        return summary
    
    def _generate_recommendations(self, test_results: Dict[str, Any], reliability_level: str) -> List[str]:
        """生成推薦建議"""
        recommendations = []
        
        # 基於可靠性等級的總體建議
        if reliability_level == "enterprise":
            recommendations.append("可靠性極佳，適合企業級應用")
        elif reliability_level == "professional":
            recommendations.append("可靠性優秀，適合專業應用")
        elif reliability_level == "standard":
            recommendations.append("可靠性良好，適合標準應用")
        elif reliability_level == "basic":
            recommendations.append("可靠性一般，建議謹慎使用")
        else:
            recommendations.append("可靠性較差，存在穩定性風險")
        
        # 基於具體測試結果的建議
        for test_name, result in test_results.items():
            if not result.get('passed', False):
                if test_name == 'stability_test':
                    recommendations.append("穩定性不足，建議優化網絡環境")
                elif test_name == 'load_test':
                    recommendations.append("負載能力不足，建議降低並發量")
                elif test_name == 'fault_recovery_test':
                    recommendations.append("故障恢復能力弱，建議增加冗餘")
                elif test_name == 'network_quality_test':
                    recommendations.append("網絡質量較差，建議更換網絡路徑")
                elif test_name == 'resource_usage_test':
                    recommendations.append("資源使用效率低，建議優化配置")
        
        return recommendations
    
    def generate_reliability_report(self, test_result: Dict[str, Any]) -> str:
        """生成可靠性報告"""
        report = []
        report.append("=== 高級可靠性測試報告 ===")
        report.append(f"測試時間: {test_result['timestamp']}")
        report.append(f"代理: {test_result['proxy']}")
        report.append(f"可靠性等級: {test_result['reliability_level'].upper()}")
        report.append(f"總體分數: {test_result['overall_score']:.1f}/100")
        report.append(f"執行時間: {test_result['execution_time']:.2f}秒")
        report.append("")
        
        # 各項測試結果
        report.append("各項測試結果:")
        for test_name, result in test_result['test_results'].items():
            status = "通過" if result['passed'] else "失敗"
            report.append(f"  {test_name}: {status} (分數: {result['score']:.1f})")
        
        # 摘要指標
        if test_result['summary_metrics']:
            report.append("")
            report.append("關鍵指標摘要:")
            summary = test_result['summary_metrics']
            report.append(f"  總指標數: {summary['total_metrics']}")
            report.append(f"  通過指標: {summary['passed_metrics']}")
            report.append(f"  失敗指標: {summary['failed_metrics']}")
            
            for key, value in summary.items():
                if key.startswith('avg_'):
                    metric_name = key.replace('avg_', '').replace('_', ' ').title()
                    report.append(f"  平均{metric_name}: {value:.2f}")
        
        # 推薦建議
        if test_result['recommendations']:
            report.append("")
            report.append("推薦建議:")
            for rec in test_result['recommendations']:
                report.append(f"  - {rec}")
        
        # 錯誤信息
        if test_result['errors']:
            report.append("")
            report.append("錯誤信息:")
            for error in test_result['errors']:
                report.append(f"  - {error}")
        
        return "\n".join(report)


# ==================== 使用示例 ====================

async def demo_reliability_testing():
    """演示可靠性測試"""
    import logging
    
    # 設置日誌
    logging.basicConfig(level=logging.INFO)
    
    # 創建測試器
    tester = AdvancedReliabilityTester({
        'reliability_timeout': 300,
        'stability_test_duration': 60,  # 1 分鐘演示
        'load_concurrent_requests': 20,  # 20 個並發請求演示
        'network_ping_count': 50  # 50 個 ping 演示
    })
    
    # 測試代理（這裡使用示例 IP，實際測試需要真實的代理）
    test_proxies = [
        {"http": "http://185.199.229.228:8080", "https": "http://185.199.229.228:8080"},
        {"http": "http://103.250.166.1:8080", "https": "http://103.250.166.1:8080"}
    ]
    
    print("=== 高級可靠性測試演示 ===\n")
    
    for proxy_dict in test_proxies:
        print(f"正在測試代理: {proxy_dict['http']}")
        
        try:
            # 運行完整測試
            result = await tester.run_full_reliability_test(proxy_dict)
            
            # 生成報告
            report = tester.generate_reliability_report(result)
            print(report)
            
        except Exception as e:
            print(f"測試失敗: {e}")
        
        print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    # 運行演示
    asyncio.run(demo_reliability_testing())