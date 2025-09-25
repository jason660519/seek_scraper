"""
多層次代理 IP 驗證體系

這個模組實現了文檔中定義的六層驗證架構：
1. 基礎連接性驗證
2. 響應性能分析  
3. 地理位置精準驗證
4. 匿名等級深度測試
5. 可靠性綜合評估
6. 智能評分與分類

每個層次都有獨立的驗證器，支持並行執行和模塊化配置。
"""

import asyncio
import aiohttp
import json
import time
import logging
import statistics
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import numpy as np
from abc import ABC, abstractmethod


# ==================== 基礎數據結構 ====================

@dataclass
class ValidationConfig:
    """驗證配置類"""
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    concurrent_limit: int = 50
    enable_caching: bool = True
    cache_ttl: int = 3600  # 秒


@dataclass
class ValidationResult:
    """基礎驗證結果"""
    layer_name: str
    proxy_str: str
    success: bool
    score: float
    details: Dict[str, Any]
    errors: List[str]
    execution_time: float
    timestamp: datetime


@dataclass
class Layer1ConnectivityResult(ValidationResult):
    """第一層：連接性驗證結果"""
    http_success: bool = False
    https_success: bool = False
    http_response_time: float = float('inf')
    https_response_time: float = float('inf')
    dns_resolution_time: float = float('inf')
    tcp_connection_time: float = float('inf')


@dataclass
class Layer2PerformanceResult(ValidationResult):
    """第二層：性能分析結果"""
    download_speeds: Dict[str, float] = None  # kbps
    response_times: Dict[str, float] = None  # seconds
    consistency_score: float = 0.0
    jitter_coefficient: float = 1.0
    throughput_stability: float = 0.0
    
    def __post_init__(self):
        if self.download_speeds is None:
            self.download_speeds = {}
        if self.response_times is None:
            self.response_times = {}


@dataclass
class Layer3GeolocationResult(ValidationResult):
    """第三層：地理位置驗證結果"""
    country_consensus: Optional[str] = None
    city_consensus: Optional[str] = None
    coordinate_consensus: Tuple[float, float] = None
    country_consistency: float = 0.0
    city_consistency: float = 0.0
    coordinate_precision: float = 0.0  # 公里
    services_successful: int = 0
    total_services: int = 0
    location_accuracy_score: float = 0.0


@dataclass
class Layer4AnonymityResult(ValidationResult):
    """第四層：匿名性測試結果"""
    anonymity_level: str = "unknown"
    leak_count: int = 0
    headers_leaked: List[str] = None
    dns_leak_detected: bool = False
    webrtc_leak_detected: bool = False
    timezone_leak_detected: bool = False
    language_leak_detected: bool = False
    ip_leak_detected: bool = False
    fingerprint_uniqueness: float = 0.0
    
    def __post_init__(self):
        if self.headers_leaked is None:
            self.headers_leaked = []


@dataclass
class Layer5ReliabilityResult(ValidationResult):
    """第五層：可靠性評估結果"""
    connection_stability: float = 0.0
    load_handling_score: float = 0.0
    error_recovery_rate: float = 0.0
    uptime_percentage: float = 0.0
    mean_time_between_failures: float = float('inf')
    failure_rate: float = 1.0
    stress_test_passed: bool = False
    endurance_test_passed: bool = False


@dataclass
class Layer6ClassificationResult(ValidationResult):
    """第六層：智能分類結果"""
    final_grade: str = "F"
    classification: str = "unusable"
    confidence_score: float = 0.0
    recommendation: str = "not_recommended"
    use_case_suitability: Dict[str, float] = None
    risk_assessment: str = "high_risk"
    
    def __post_init__(self):
        if self.use_case_suitability is None:
            self.use_case_suitability = {}


# ==================== 抽象驗證器基類 ====================

class BaseValidator(ABC):
    """驗證器基類"""
    
    def __init__(self, config: ValidationConfig, logger: logging.Logger = None):
        self.config = config
        self.logger = logger or self._setup_logger()
        self.session = None
        
    def _setup_logger(self) -> logging.Logger:
        """設置日誌記錄器"""
        logger = logging.getLogger(f"{self.__class__.__name__}")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    @abstractmethod
    async def validate(self, proxy_info: 'ProxyInfo') -> ValidationResult:
        """執行驗證"""
        pass
    
    async def __aenter__(self):
        """異步上下文管理器進入"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            connector=aiohttp.TCPConnector(limit=self.config.concurrent_limit)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """異步上下文管理器退出"""
        if self.session:
            await self.session.close()


# ==================== 第一層：基礎連接性驗證 ====================

class ConnectivityValidator(BaseValidator):
    """基礎連接性驗證器"""
    
    def __init__(self, config: ValidationConfig):
        super().__init__(config)
        self.test_endpoints = {
            'http': 'http://httpbin.org/ip',
            'https': 'https://www.google.com/generate_204',
            'dns': 'http://httpbin.org/uuid',
            'tcp': 'http://httpbin.org/headers'
        }
    
    async def validate(self, proxy_info: 'ProxyInfo') -> Layer1ConnectivityResult:
        """執行連接性驗證"""
        start_time = time.time()
        proxy_str = str(proxy_info)
        
        results = {
            'http_success': False,
            'https_success': False,
            'http_response_time': float('inf'),
            'https_response_time': float('inf'),
            'dns_resolution_time': float('inf'),
            'tcp_connection_time': float('inf')
        }
        
        errors = []
        
        try:
            # HTTP 連接測試
            http_result = await self._test_http_connectivity(proxy_info)
            results.update(http_result)
            
            # HTTPS 連接測試
            https_result = await self._test_https_connectivity(proxy_info)
            results.update(https_result)
            
            # DNS 解析測試
            dns_result = await self._test_dns_resolution(proxy_info)
            results.update(dns_result)
            
            # TCP 連接測試
            tcp_result = await self._test_tcp_connection(proxy_info)
            results.update(tcp_result)
            
        except Exception as e:
            errors.append(f"Connectivity validation error: {str(e)}")
            self.logger.error(f"Connectivity validation failed for {proxy_str}: {e}")
        
        # 計算分數
        score = self._calculate_connectivity_score(results)
        success = results['http_success'] or results['https_success']
        
        execution_time = time.time() - start_time
        
        return Layer1ConnectivityResult(
            layer_name="Connectivity",
            proxy_str=proxy_str,
            success=success,
            score=score,
            details=results,
            errors=errors,
            execution_time=execution_time,
            timestamp=datetime.now(),
            **results
        )
    
    async def _test_http_connectivity(self, proxy_info: 'ProxyInfo') -> Dict[str, Any]:
        """測試 HTTP 連接"""
        proxy_dict = self._get_proxy_dict(proxy_info)
        
        for attempt in range(self.config.max_retries):
            try:
                start_time = time.time()
                async with self.session.get(
                    self.test_endpoints['http'],
                    proxy=proxy_dict['http'],
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        return {
                            'http_success': True,
                            'http_response_time': response_time
                        }
                    
            except Exception as e:
                self.logger.warning(f"HTTP connectivity test attempt {attempt + 1} failed: {e}")
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(self.config.retry_delay)
        
        return {'http_success': False, 'http_response_time': float('inf')}
    
    async def _test_https_connectivity(self, proxy_info: 'ProxyInfo') -> Dict[str, Any]:
        """測試 HTTPS 連接"""
        proxy_dict = self._get_proxy_dict(proxy_info)
        
        for attempt in range(self.config.max_retries):
            try:
                start_time = time.time()
                async with self.session.get(
                    self.test_endpoints['https'],
                    proxy=proxy_dict['https'],
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 204:  # Google generate_204 returns 204
                        return {
                            'https_success': True,
                            'https_response_time': response_time
                        }
                    
            except Exception as e:
                self.logger.warning(f"HTTPS connectivity test attempt {attempt + 1} failed: {e}")
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(self.config.retry_delay)
        
        return {'https_success': False, 'https_response_time': float('inf')}
    
    async def _test_dns_resolution(self, proxy_info: 'ProxyInfo') -> Dict[str, Any]:
        """測試 DNS 解析"""
        proxy_dict = self._get_proxy_dict(proxy_info)
        
        try:
            start_time = time.time()
            async with self.session.get(
                self.test_endpoints['dns'],
                proxy=proxy_dict['http'],
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    return {'dns_resolution_time': response_time}
                    
        except Exception as e:
            self.logger.warning(f"DNS resolution test failed: {e}")
        
        return {'dns_resolution_time': float('inf')}
    
    async def _test_tcp_connection(self, proxy_info: 'ProxyInfo') -> Dict[str, Any]:
        """測試 TCP 連接"""
        proxy_dict = self._get_proxy_dict(proxy_info)
        
        try:
            start_time = time.time()
            async with self.session.get(
                self.test_endpoints['tcp'],
                proxy=proxy_dict['http'],
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    return {'tcp_connection_time': response_time}
                    
        except Exception as e:
            self.logger.warning(f"TCP connection test failed: {e}")
        
        return {'tcp_connection_time': float('inf')}
    
    def _get_proxy_dict(self, proxy_info: 'ProxyInfo') -> Dict[str, str]:
        """生成代理字典"""
        proxy_url = f"{proxy_info.type}://{proxy_info.ip}:{proxy_info.port}"
        return {
            'http': proxy_url,
            'https': proxy_url
        }
    
    def _calculate_connectivity_score(self, results: Dict[str, Any]) -> float:
        """計算連接性分數"""
        score = 0.0
        
        # HTTP 連接分數 (30%)
        if results['http_success']:
            http_time = results['http_response_time']
            if http_time <= 1.0:
                score += 30.0
            elif http_time <= 3.0:
                score += 25.0
            elif http_time <= 5.0:
                score += 20.0
            else:
                score += 15.0
        
        # HTTPS 連接分數 (30%)
        if results['https_success']:
            https_time = results['https_response_time']
            if https_time <= 1.0:
                score += 30.0
            elif https_time <= 3.0:
                score += 25.0
            elif https_time <= 5.0:
                score += 20.0
            else:
                score += 15.0
        
        # DNS 解析分數 (20%)
        dns_time = results['dns_resolution_time']
        if dns_time != float('inf'):
            if dns_time <= 0.5:
                score += 20.0
            elif dns_time <= 1.0:
                score += 15.0
            else:
                score += 10.0
        
        # TCP 連接分數 (20%)
        tcp_time = results['tcp_connection_time']
        if tcp_time != float('inf'):
            if tcp_time <= 0.3:
                score += 20.0
            elif tcp_time <= 0.5:
                score += 15.0
            else:
                score += 10.0
        
        return min(100.0, score)


# ==================== 第二層：響應性能分析 ====================

class PerformanceValidator(BaseValidator):
    """性能分析驗證器"""
    
    def __init__(self, config: ValidationConfig):
        super().__init__(config)
        self.file_sizes = {
            'tiny': 1024,      # 1KB
            'small': 10240,    # 10KB
            'medium': 102400,  # 100KB
            'large': 512000,   # 500KB
            'xlarge': 1048576  # 1MB
        }
        
        self.performance_endpoints = {
            size: f'http://httpbin.org/bytes/{byte_size}'
            for size, byte_size in self.file_sizes.items()
        }
    
    async def validate(self, proxy_info: 'ProxyInfo') -> Layer2PerformanceResult:
        """執行性能分析"""
        start_time = time.time()
        proxy_str = str(proxy_info)
        
        download_speeds = {}
        response_times = {}
        consistency_score = 0.0
        jitter_coefficient = 1.0
        throughput_stability = 0.0
        
        errors = []
        
        try:
            # 逐級文件下載測試
            for size, endpoint in self.performance_endpoints.items():
                speed, response_time = await self._test_file_download(proxy_info, endpoint, size)
                download_speeds[size] = speed
                response_times[size] = response_time
            
            # 計算性能指標
            consistency_score = self._calculate_consistency(download_speeds)
            jitter_coefficient = self._calculate_jitter(response_times)
            throughput_stability = self._calculate_throughput_stability(download_speeds)
            
        except Exception as e:
            errors.append(f"Performance validation error: {str(e)}")
            self.logger.error(f"Performance validation failed for {proxy_str}: {e}")
        
        # 計算分數
        score = self._calculate_performance_score(download_speeds, response_times, 
                                               consistency_score, jitter_coefficient)
        success = any(speed > 0 for speed in download_speeds.values())
        
        execution_time = time.time() - start_time
        
        details = {
            'download_speeds': download_speeds,
            'response_times': response_times,
            'consistency_score': consistency_score,
            'jitter_coefficient': jitter_coefficient,
            'throughput_stability': throughput_stability
        }
        
        return Layer2PerformanceResult(
            layer_name="Performance",
            proxy_str=proxy_str,
            success=success,
            score=score,
            details=details,
            errors=errors,
            execution_time=execution_time,
            timestamp=datetime.now(),
            download_speeds=download_speeds,
            response_times=response_times,
            consistency_score=consistency_score,
            jitter_coefficient=jitter_coefficient,
            throughput_stability=throughput_stability
        )
    
    async def _test_file_download(self, proxy_info: 'ProxyInfo', endpoint: str, size: str) -> Tuple[float, float]:
        """測試文件下載"""
        proxy_dict = self._get_proxy_dict(proxy_info)
        download_speeds = []
        response_times = []
        
        # 進行多次測試取平均值
        test_runs = 3
        
        for attempt in range(test_runs):
            try:
                start_time = time.time()
                async with self.session.get(
                    endpoint,
                    proxy=proxy_dict['http'],
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        content = await response.read()
                        download_time = time.time() - start_time
                        
                        # 計算下載速度 (kbps)
                        file_size_kb = len(content) / 1024
                        speed_kbps = (file_size_kb * 8) / download_time if download_time > 0 else 0
                        
                        download_speeds.append(speed_kbps)
                        response_times.append(download_time)
                        
            except Exception as e:
                self.logger.warning(f"File download test failed for {size} (attempt {attempt + 1}): {e}")
        
        # 返回平均值
        avg_speed = statistics.mean(download_speeds) if download_speeds else 0
        avg_time = statistics.mean(response_times) if response_times else float('inf')
        
        return avg_speed, avg_time
    
    def _calculate_consistency(self, speeds: Dict[str, float]) -> float:
        """計算一致性分數"""
        valid_speeds = [speed for speed in speeds.values() if speed > 0]
        
        if len(valid_speeds) < 2:
            return 0.0
        
        # 理想情況下，速度應該與文件大小成正比
        expected_ratios = [1, 10, 100, 500, 1000]  # 對應文件大小比例
        actual_speeds = []
        
        for size in ['tiny', 'small', 'medium', 'large', 'xlarge']:
            if size in speeds and speeds[size] > 0:
                actual_speeds.append(speeds[size])
        
        if len(actual_speeds) < 2:
            return 0.5
        
        # 計算速度的一致性（基於變異係數）
        mean_speed = statistics.mean(actual_speeds)
        if mean_speed == 0:
            return 0.0
        
        std_dev = statistics.stdev(actual_speeds)
        coefficient_of_variation = std_dev / mean_speed
        
        # 一致性分數 = 1 - 變異係數
        consistency = max(0, 1 - coefficient_of_variation)
        return consistency * 100
    
    def _calculate_jitter(self, response_times: Dict[str, float]) -> float:
        """計算抖動係數"""
        valid_times = [time for time in response_times.values() if time != float('inf')]
        
        if len(valid_times) < 2:
            return 1.0
        
        # 計算變異係數
        mean_time = statistics.mean(valid_times)
        if mean_time == 0:
            return 1.0
        
        std_dev = statistics.stdev(valid_times)
        coefficient_of_variation = std_dev / mean_time
        
        return coefficient_of_variation
    
    def _calculate_throughput_stability(self, speeds: Dict[str, float]) -> float:
        """計算吞吐量穩定性"""
        valid_speeds = [speed for speed in speeds.values() if speed > 0]
        
        if len(valid_speeds) < 2:
            return 0.0
        
        # 計算速度的穩定性（基於移動平均）
        if len(valid_speeds) >= 3:
            # 簡單的移動平均比較
            recent_avg = statistics.mean(valid_speeds[-3:])
            overall_avg = statistics.mean(valid_speeds)
            
            if overall_avg > 0:
                stability = 1 - abs(recent_avg - overall_avg) / overall_avg
                return max(0, stability) * 100
        
        return 50.0  # 默認中等穩定性
    
    def _calculate_performance_score(self, speeds: Dict[str, float], 
                                     response_times: Dict[str, float],
                                     consistency: float, 
                                     jitter: float) -> float:
        """計算性能分數"""
        score = 0.0
        
        # 速度分數 (40%)
        valid_speeds = [speed for speed in speeds.values() if speed > 0]
        if valid_speeds:
            avg_speed = statistics.mean(valid_speeds)
            if avg_speed >= 1000:  # Excellent
                score += 40.0
            elif avg_speed >= 500:  # Good
                score += 32.0
            elif avg_speed >= 100:  # Fair
                score += 24.0
            elif avg_speed >= 50:  # Poor
                score += 16.0
            else:
                score += 8.0
        
        # 響應時間分數 (30%)
        valid_times = [time for time in response_times.values() if time != float('inf')]
        if valid_times:
            avg_time = statistics.mean(valid_times)
            if avg_time <= 1.0:
                score += 30.0
            elif avg_time <= 3.0:
                score += 24.0
            elif avg_time <= 5.0:
                score += 18.0
            else:
                score += 12.0
        
        # 一致性分數 (20%)
        score += (consistency / 100) * 20.0
        
        # 穩定性分數 (10%)
        stability_score = max(0, 1 - jitter) * 10.0
        score += stability_score
        
        return min(100.0, score)
    
    def _get_proxy_dict(self, proxy_info: 'ProxyInfo') -> Dict[str, str]:
        """生成代理字典"""
        proxy_url = f"{proxy_info.type}://{proxy_info.ip}:{proxy_info.port}"
        return {
            'http': proxy_url,
            'https': proxy_url
        }


# ==================== 多層次驗證管理器 ====================

class MultiLayerValidationSystem:
    """多層次驗證系統管理器"""
    
    def __init__(self, config: ValidationConfig = None):
        self.config = config or ValidationConfig()
        self.logger = self._setup_logger()
        
        # 初始化各層驗證器
        self.validators = {
            'connectivity': ConnectivityValidator(self.config),
            'performance': PerformanceValidator(self.config),
            # 其他驗證器將在後續實現
        }
        
        # 層次權重配置
        self.layer_weights = {
            'connectivity': 0.25,
            'performance': 0.20,
            'geolocation': 0.15,
            'anonymity': 0.20,
            'reliability': 0.20
        }
        
        self.logger.info("MultiLayerValidationSystem initialized")
    
    def _setup_logger(self) -> logging.Logger:
        """設置日誌記錄器"""
        logger = logging.getLogger('MultiLayerValidationSystem')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def validate_single_layer(self, proxy_info: 'ProxyInfo', layer: str) -> ValidationResult:
        """驗證單個層次"""
        if layer not in self.validators:
            raise ValueError(f"Unknown validation layer: {layer}")
        
        validator = self.validators[layer]
        
        async with validator:
            return await validator.validate(proxy_info)
    
    async def validate_all_layers(self, proxy_info: 'ProxyInfo') -> Dict[str, ValidationResult]:
        """驗證所有層次"""
        results = {}
        
        for layer_name, validator in self.validators.items():
            try:
                async with validator:
                    result = await validator.validate(proxy_info)
                    results[layer_name] = result
                    
            except Exception as e:
                self.logger.error(f"Layer {layer_name} validation failed for {proxy_info}: {e}")
                results[layer_name] = None
        
        return results
    
    def calculate_weighted_score(self, layer_results: Dict[str, ValidationResult]) -> float:
        """計算加權總分"""
        total_score = 0.0
        total_weight = 0.0
        
        for layer, result in layer_results.items():
            if result and layer in self.layer_weights:
                weight = self.layer_weights[layer]
                total_score += result.score * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def generate_layer_summary(self, layer_results: Dict[str, ValidationResult]) -> Dict[str, Any]:
        """生成層次匯總報告"""
        summary = {
            'timestamp': datetime.now().isoformat(),
            'proxy_info': None,
            'layer_scores': {},
            'weighted_total_score': 0.0,
            'validation_status': 'partial',
            'recommendations': []
        }
        
        if not layer_results:
            return summary
        
        # 提取代理信息
        first_result = next(iter(layer_results.values()))
        if first_result:
            summary['proxy_info'] = first_result.proxy_str
        
        # 統計各層得分
        for layer, result in layer_results.items():
            if result:
                summary['layer_scores'][layer] = {
                    'score': result.score,
                    'success': result.success,
                    'execution_time': result.execution_time
                }
        
        # 計算加權總分
        summary['weighted_total_score'] = self.calculate_weighted_score(layer_results)
        
        # 確定驗證狀態
        successful_layers = sum(1 for r in layer_results.values() if r and r.success)
        total_layers = len(layer_results)
        
        if successful_layers == total_layers:
            summary['validation_status'] = 'complete'
        elif successful_layers > total_layers // 2:
            summary['validation_status'] = 'majority'
        else:
            summary['validation_status'] = 'minority'
        
        # 生成推薦
        summary['recommendations'] = self._generate_recommendations(layer_results)
        
        return summary
    
    def _generate_recommendations(self, layer_results: Dict[str, ValidationResult]) -> List[str]:
        """生成推薦建議"""
        recommendations = []
        
        # 基於各層結果生成具體建議
        for layer, result in layer_results.items():
            if not result or not result.success:
                continue
            
            if layer == 'connectivity' and isinstance(result, Layer1ConnectivityResult):
                if result.score < 60:
                    recommendations.append("基礎連接性較差，建議檢查網絡配置")
                elif result.http_response_time > 5:
                    recommendations.append("HTTP響應時間較長，可能影響使用體驗")
            
            elif layer == 'performance' and isinstance(result, Layer2PerformanceResult):
                if result.score < 50:
                    recommendations.append("性能表現不佳，不適合高頻率使用")
                elif result.jitter_coefficient > 0.5:
                    recommendations.append("網絡抖動較大，穩定性有待提升")
        
        return recommendations


# ==================== 使用示例 ====================

async def demo_multi_layer_validation():
    """演示多層次驗證系統"""
    from dataclasses import dataclass
    
    @dataclass
    class ProxyInfo:
        ip: str
        port: int
        type: str = 'http'
        
        def __str__(self):
            return f"{self.ip}:{self.port}"
    
    # 創建驗證系統
    config = ValidationConfig(
        timeout=30,
        max_retries=3,
        concurrent_limit=10
    )
    
    validation_system = MultiLayerValidationSystem(config)
    
    # 測試代理
    test_proxies = [
        ProxyInfo("185.199.229.228", 8080),
        ProxyInfo("103.250.166.1", 8080),
        ProxyInfo("51.222.12.245", 80)
    ]
    
    print("=== 多層次代理驗證系統演示 ===\n")
    
    for proxy in test_proxies:
        print(f"正在驗證代理: {proxy}")
        
        # 執行所有層次驗證
        results = await validation_system.validate_all_layers(proxy)
        
        # 生成匯總報告
        summary = validation_system.generate_layer_summary(results)
        
        print(f"加權總分: {summary['weighted_total_score']:.1f}")
        print(f"驗證狀態: {summary['validation_status']}")
        
        # 打印各層得分
        print("各層得分:")
        for layer, score_info in summary['layer_scores'].items():
            print(f"  {layer}: {score_info['score']:.1f} (成功: {score_info['success']})")
        
        # 打印推薦
        if summary['recommendations']:
            print("推薦建議:")
            for rec in summary['recommendations']:
                print(f"  - {rec}")
        
        print("-" * 50)


if __name__ == "__main__":
    # 運行演示
    asyncio.run(demo_multi_layer_validation())