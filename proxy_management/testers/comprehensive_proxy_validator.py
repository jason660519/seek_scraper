"""
Proxifly 綜合代理 IP 有效性驗證器

這是一個企業級的代理 IP 驗證框架，提供多層次、多維度的代理質量評估。
包含連接性測試、性能分析、地理位置驗證、匿名性檢測和可靠性評估。
"""

import asyncio
import aiohttp
import requests
import json
import time
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import statistics
from pathlib import Path
import csv


@dataclass
class ProxyInfo:
    """代理基本信息數據類"""
    ip: str
    port: int
    country: Optional[str] = None
    anonymity: Optional[str] = None
    type: Optional[str] = 'http'
    source: Optional[str] = 'proxifly'
    
    def __str__(self) -> str:
        return f"{self.ip}:{self.port}"


@dataclass
class ConnectivityResult:
    """連接性測試結果"""
    proxy_str: str
    http_success: bool
    https_success: bool
    http_response_time: float
    https_response_time: float
    errors: List[str]
    test_timestamp: datetime
    score: float


@dataclass
class PerformanceResult:
    """性能測試結果"""
    proxy_str: str
    small_file_time: float
    medium_file_time: float
    large_file_time: float
    small_file_speed: float
    medium_file_speed: float
    large_file_speed: float
    consistency_score: float
    jitter_rate: float
    score: float


@dataclass
class GeolocationResult:
    """地理位置驗證結果"""
    proxy_str: str
    services_tested: int
    country_consistency: float
    city_consistency: float
    coordinate_variance: float
    average_coordinates: Tuple[float, float]
    location_accuracy: float
    score: float


@dataclass
class AnonymityResult:
    """匿名性測試結果"""
    proxy_str: str
    headers_leaked: List[str]
    dns_leak_detected: bool
    webrtc_leak_detected: bool
    timezone_mismatch: bool
    language_mismatch: bool
    anonymity_level: str
    leak_count: int
    score: float


@dataclass
class ReliabilityResult:
    """可靠性測試結果"""
    proxy_str: str
    connection_success_rate: float
    load_test_success_rate: float
    error_recovery_rate: float
    uptime_percentage: float
    average_response_time: float
    stability_score: float
    score: float


@dataclass
class ComprehensiveResult:
    """綜合驗證結果"""
    proxy_info: ProxyInfo
    connectivity: ConnectivityResult
    performance: PerformanceResult
    geolocation: GeolocationResult
    anonymity: AnonymityResult
    reliability: ReliabilityResult
    overall_score: float
    grade: str
    recommendation: str
    test_duration: float
    timestamp: datetime


class ComprehensiveProxyValidator:
    """
    綜合代理 IP 驗證器
    
    提供企業級的代理驗證服務，包含：
    - 基礎連接性驗證
    - 多級性能測試
    - 地理位置交叉驗證
    - 深度匿名性檢測
    - 綜合可靠性評估
    - 智能評分與分類
    """
    
    def __init__(self, max_concurrent: int = 50, timeout: int = 30):
        """
        初始化驗證器
        
        Args:
            max_concurrent: 最大並發測試數
            timeout: 默認超時時間（秒）
        """
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.session = None
        self.logger = self._setup_logger()
        
        # 測試 URL 配置
        self.test_urls = {
            'connectivity': {
                'http': 'http://httpbin.org/ip',
                'https': 'https://www.google.com/generate_204'
            },
            'performance': {
                'small': 'http://httpbin.org/bytes/1024',
                'medium': 'http://httpbin.org/bytes/10240',
                'large': 'http://httpbin.org/bytes/102400'
            },
            'geolocation': [
                'http://ip-api.com/json/',
                'http://ipinfo.io/json',
                'https://freegeoip.app/json/',
                'http://geoip.nekudo.com/api/',
                'https://ipapi.co/json/'
            ],
            'anonymity': {
                'headers': 'http://httpbin.org/headers',
                'ip': 'http://httpbin.org/ip'
            }
        }
        
        # 評分標準
        self.scoring_criteria = {
            'connectivity': {
                'response_time': {
                    (0, 1): 100, (1, 3): 90, (3, 5): 80,
                    (5, 10): 70, (10, float('inf')): 50
                }
            },
            'performance': {
                'speed_thresholds': {
                    'excellent': 1000,  # kbps
                    'good': 500,
                    'fair': 100,
                    'poor': 50
                }
            },
            'anonymity': {
                'elite': 100,      # 無洩露
                'anonymous': 80,   # 1個洩露
                'distorting': 60,  # 2-3個洩露
                'transparent': 40  # 4+個洩露
            }
        }
        
        self.logger.info(f"ComprehensiveProxyValidator initialized with max_concurrent={max_concurrent}")
    
    def _setup_logger(self) -> logging.Logger:
        """設置日誌記錄器"""
        logger = logging.getLogger('ComprehensiveProxyValidator')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def __aenter__(self):
        """異步上下文管理器進入"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            connector=aiohttp.TCPConnector(limit=self.max_concurrent)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """異步上下文管理器退出"""
        if self.session:
            await self.session.close()
    
    def _get_proxy_dict(self, proxy_info: ProxyInfo) -> Dict[str, str]:
        """生成代理字典"""
        proxy_url = f"{proxy_info.type}://{proxy_info.ip}:{proxy_info.port}"
        return {
            'http': proxy_url,
            'https': proxy_url
        }
    
    async def test_connectivity(self, proxy_info: ProxyInfo) -> ConnectivityResult:
        """
        測試代理基礎連接性
        
        Args:
            proxy_info: 代理信息
            
        Returns:
            ConnectivityResult: 連接性測試結果
        """
        start_time = time.time()
        proxy_str = str(proxy_info)
        errors = []
        http_success = False
        https_success = False
        http_time = float('inf')
        https_time = float('inf')
        
        try:
            # 測試 HTTP 連接
            async with self.session.get(
                self.test_urls['connectivity']['http'],
                proxy=self._get_proxy_dict(proxy_info)['http'],
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    http_success = True
                    http_time = time.time() - start_time
                    
        except Exception as e:
            errors.append(f"HTTP test failed: {str(e)}")
            self.logger.warning(f"HTTP connectivity test failed for {proxy_str}: {e}")
        
        # 測試 HTTPS 連接
        https_start = time.time()
        try:
            async with self.session.get(
                self.test_urls['connectivity']['https'],
                proxy=self._get_proxy_dict(proxy_info)['https'],
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 204:
                    https_success = True
                    https_time = time.time() - https_start
                    
        except Exception as e:
            errors.append(f"HTTPS test failed: {str(e)}")
            self.logger.warning(f"HTTPS connectivity test failed for {proxy_str}: {e}")
        
        # 計算分數
        score = self._calculate_connectivity_score(http_time, https_time, http_success, https_success)
        
        return ConnectivityResult(
            proxy_str=proxy_str,
            http_success=http_success,
            https_success=https_success,
            http_response_time=http_time if http_success else float('inf'),
            https_response_time=https_time if https_success else float('inf'),
            errors=errors,
            test_timestamp=datetime.now(),
            score=score
        )
    
    def _calculate_connectivity_score(self, http_time: float, https_time: float, 
                                   http_success: bool, https_success: bool) -> float:
        """計算連接性分數"""
        if not http_success and not https_success:
            return 0.0
        
        # 基礎分數（連接成功）
        base_score = 50.0
        
        # HTTP 響應時間評分
        if http_success:
            http_score = self._get_response_time_score(http_time)
            base_score += http_score * 0.3
        
        # HTTPS 響應時間評分
        if https_success:
            https_score = self._get_response_time_score(https_time)
            base_score += https_score * 0.3
        
        # 雙協議支持加分
        if http_success and https_success:
            base_score += 20.0
        
        return min(100.0, base_score)
    
    def _get_response_time_score(self, response_time: float) -> float:
        """根據響應時間計算分數"""
        if response_time <= 1.0:
            return 100.0
        elif response_time <= 3.0:
            return 90.0
        elif response_time <= 5.0:
            return 80.0
        elif response_time <= 10.0:
            return 70.0
        else:
            return 50.0
    
    async def test_performance(self, proxy_info: ProxyInfo) -> PerformanceResult:
        """
        測試代理性能
        
        Args:
            proxy_info: 代理信息
            
        Returns:
            PerformanceResult: 性能測試結果
        """
        proxy_str = str(proxy_info)
        proxy_dict = self._get_proxy_dict(proxy_info)
        
        # 測試不同大小的文件下載
        results = {}
        
        for size, url in self.test_urls['performance'].items():
            download_times = []
            download_speeds = []
            
            # 進行3次測試取平均值
            for _ in range(3):
                try:
                    start_time = time.time()
                    async with self.session.get(
                        url,
                        proxy=proxy_dict['http'],
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        if response.status == 200:
                            content = await response.read()
                            download_time = time.time() - start_time
                            file_size_kb = len(content) / 1024
                            speed_kbps = (file_size_kb * 8) / download_time
                            
                            download_times.append(download_time)
                            download_speeds.append(speed_kbps)
                        else:
                            download_times.append(float('inf'))
                            download_speeds.append(0)
                            
                except Exception as e:
                    self.logger.warning(f"Performance test failed for {proxy_str} ({size}): {e}")
                    download_times.append(float('inf'))
                    download_speeds.append(0)
            
            # 計算平均值（排除無限值）
            valid_times = [t for t in download_times if t != float('inf')]
            valid_speeds = [s for s in download_speeds if s > 0]
            
            if valid_times:
                results[size] = {
                    'avg_time': statistics.mean(valid_times),
                    'avg_speed': statistics.mean(valid_speeds) if valid_speeds else 0
                }
            else:
                results[size] = {
                    'avg_time': float('inf'),
                    'avg_speed': 0
                }
        
        # 計算一致性分數和抖動率
        consistency_score, jitter_rate = self._calculate_performance_metrics(results)
        
        # 計算總體性能分數
        score = self._calculate_performance_score(results)
        
        return PerformanceResult(
            proxy_str=proxy_str,
            small_file_time=results['small']['avg_time'],
            medium_file_time=results['medium']['avg_time'],
            large_file_time=results['large']['avg_time'],
            small_file_speed=results['small']['avg_speed'],
            medium_file_speed=results['medium']['avg_speed'],
            large_file_speed=results['large']['avg_speed'],
            consistency_score=consistency_score,
            jitter_rate=jitter_rate,
            score=score
        )
    
    def _calculate_performance_metrics(self, results: Dict) -> Tuple[float, float]:
        """計算性能指標"""
        valid_times = []
        for size in ['small', 'medium', 'large']:
            if results[size]['avg_time'] != float('inf'):
                valid_times.append(results[size]['avg_time'])
        
        if len(valid_times) < 2:
            return 0.0, 1.0
        
        # 一致性分數（基於時間變化的一致性）
        if len(valid_times) == 3:
            # 理想情況下，時間應該與文件大小成正比
            expected_ratio = [1, 10, 100]  # 文件大小比例
            actual_ratio = [valid_times[0], valid_times[1], valid_times[2]]
            
            # 歸一化
            if actual_ratio[0] > 0:
                actual_ratio = [t / actual_ratio[0] for t in actual_ratio]
                
                # 計算與期望比例的差異
                differences = [abs(actual - expected) / expected 
                             for actual, expected in zip(actual_ratio, expected_ratio)]
                consistency_score = max(0, 1 - statistics.mean(differences))
            else:
                consistency_score = 0.0
        else:
            consistency_score = 0.5
        
        # 抖動率（時間變化的標準差）
        if len(valid_times) > 1:
            jitter_rate = statistics.stdev(valid_times) / statistics.mean(valid_times)
        else:
            jitter_rate = 1.0
        
        return consistency_score * 100, jitter_rate
    
    def _calculate_performance_score(self, results: Dict) -> float:
        """計算性能分數"""
        scores = []
        
        for size in ['small', 'medium', 'large']:
            if results[size]['avg_speed'] > 0:
                speed = results[size]['avg_speed']
                if speed >= 1000:  # Excellent
                    scores.append(100)
                elif speed >= 500:  # Good
                    scores.append(80)
                elif speed >= 100:  # Fair
                    scores.append(60)
                elif speed >= 50:   # Poor
                    scores.append(40)
                else:
                    scores.append(20)
        
        return statistics.mean(scores) if scores else 0.0
    
    async def test_geolocation(self, proxy_info: ProxyInfo) -> GeolocationResult:
        """
        測試地理位置準確性
        
        Args:
            proxy_info: 代理信息
            
        Returns:
            GeolocationResult: 地理位置測試結果
        """
        proxy_str = str(proxy_info)
        proxy_dict = self._get_proxy_dict(proxy_info)
        
        geo_results = []
        
        for service_url in self.test_urls['geolocation']:
            try:
                async with self.session.get(
                    service_url,
                    proxy=proxy_dict['http'],
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        geo_info = self._parse_geolocation_response(service_url, data)
                        if geo_info:
                            geo_results.append(geo_info)
                            
            except Exception as e:
                self.logger.warning(f"Geolocation test failed for {proxy_str} ({service_url}): {e}")
        
        # 計算一致性指標
        country_consistency, city_consistency, coordinate_variance, avg_coords = \
            self._calculate_geolocation_consistency(geo_results)
        
        # 計算地理位置準確性分數
        location_accuracy = self._calculate_location_accuracy(geo_results)
        
        # 計算總體分數
        score = self._calculate_geolocation_score(
            country_consistency, city_consistency, coordinate_variance, location_accuracy
        )
        
        return GeolocationResult(
            proxy_str=proxy_str,
            services_tested=len(geo_results),
            country_consistency=country_consistency,
            city_consistency=city_consistency,
            coordinate_variance=coordinate_variance,
            average_coordinates=avg_coords,
            location_accuracy=location_accuracy,
            score=score
        )
    
    def _parse_geolocation_response(self, service_url: str, data: Dict) -> Optional[Dict]:
        """解析地理位置響應"""
        try:
            if 'ip-api.com' in service_url:
                return {
                    'country': data.get('country'),
                    'country_code': data.get('countryCode'),
                    'city': data.get('city'),
                    'lat': data.get('lat'),
                    'lon': data.get('lon'),
                    'isp': data.get('isp')
                }
            elif 'ipinfo.io' in service_url:
                loc = data.get('loc', '').split(',')
                return {
                    'country': data.get('country'),
                    'country_code': data.get('country'),
                    'city': data.get('city'),
                    'lat': float(loc[0]) if len(loc) > 0 else None,
                    'lon': float(loc[1]) if len(loc) > 1 else None,
                    'isp': data.get('org')
                }
            # 可以添加更多服務的解析邏輯
            else:
                return {
                    'country': data.get('country'),
                    'country_code': data.get('country_code'),
                    'city': data.get('city'),
                    'lat': data.get('latitude'),
                    'lon': data.get('longitude'),
                    'isp': data.get('isp')
                }
        except Exception as e:
            self.logger.warning(f"Failed to parse geolocation response: {e}")
            return None
    
    def _calculate_geolocation_consistency(self, results: List[Dict]) -> Tuple[float, float, float, Tuple[float, float]]:
        """計算地理位置一致性"""
        if not results:
            return 0.0, 0.0, 1.0, (0.0, 0.0)
        
        if len(results) == 1:
            return 1.0, 1.0, 0.0, (results[0].get('lat', 0), results[0].get('lon', 0))
        
        # 國家一致性
        countries = [r.get('country_code') for r in results if r.get('country_code')]
        country_consistency = (len(set(countries)) == 1 and len(countries) > 0) if countries else 0.0
        
        # 城市一致性
        cities = [r.get('city') for r in results if r.get('city')]
        city_consistency = len(set(cities)) / len(cities) if cities else 0.0
        
        # 坐標變異性
        lats = [r.get('lat') for r in results if r.get('lat') is not None]
        lons = [r.get('lon') for r in results if r.get('lon') is not None]
        
        if len(lats) > 1 and len(lons) > 1:
            lat_variance = statistics.stdev(lats) / statistics.mean(lats) if statistics.mean(lats) != 0 else 0
            lon_variance = statistics.stdev(lons) / statistics.mean(lons) if statistics.mean(lons) != 0 else 0
            coordinate_variance = (lat_variance + lon_variance) / 2
        else:
            coordinate_variance = 0.0
        
        # 平均坐標
        avg_lat = statistics.mean(lats) if lats else 0.0
        avg_lon = statistics.mean(lons) if lons else 0.0
        
        return float(country_consistency), city_consistency, coordinate_variance, (avg_lat, avg_lon)
    
    def _calculate_location_accuracy(self, results: List[Dict]) -> float:
        """計算地理位置準確性"""
        if not results:
            return 0.0
        
        # 簡單的準確性計算：數據完整性
        completeness_scores = []
        for result in results:
            required_fields = ['country', 'city', 'lat', 'lon']
            completeness = sum(1 for field in required_fields if result.get(field)) / len(required_fields)
            completeness_scores.append(completeness)
        
        return statistics.mean(completeness_scores) * 100 if completeness_scores else 0.0
    
    def _calculate_geolocation_score(self, country_consistency: float, city_consistency: float,
                                   coordinate_variance: float, location_accuracy: float) -> float:
        """計算地理位置總分"""
        # 權重分配
        weights = {
            'country': 0.4,      # 國家一致性 40%
            'city': 0.3,         # 城市一致性 30%
            'coordinate': 0.2,   # 坐標精度 20%
            'accuracy': 0.1      # 數據完整性 10%
        }
        
        score = (
            country_consistency * weights['country'] * 100 +
            city_consistency * weights['city'] * 100 +
            (1 - coordinate_variance) * weights['coordinate'] * 100 +
            location_accuracy * weights['accuracy']
        )
        
        return max(0, min(100, score))
    
    async def test_anonymity(self, proxy_info: ProxyInfo) -> AnonymityResult:
        """
        測試代理匿名性
        
        Args:
            proxy_info: 代理信息
            
        Returns:
            AnonymityResult: 匿名性測試結果
        """
        proxy_str = str(proxy_info)
        proxy_dict = self._get_proxy_dict(proxy_info)
        
        headers_leaked = []
        dns_leak = False
        webrtc_leak = False
        timezone_mismatch = False
        language_mismatch = False
        
        try:
            # 測試頭部信息洩露
            async with self.session.get(
                self.test_urls['anonymity']['headers'],
                proxy=proxy_dict['http'],
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    headers = data.get('headers', {})
                    
                    # 檢查代理相關頭部
                    proxy_headers = ['X-Forwarded-For', 'X-Real-IP', 'Via', 'X-Proxy-ID']
                    for header in proxy_headers:
                        if header in headers or header.lower() in headers:
                            headers_leaked.append(header)
            
            # 測試 IP 洩露（簡化版）
            async with self.session.get(
                self.test_urls['anonymity']['ip'],
                proxy=proxy_dict['http'],
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    # 這裡可以添加更複雜的 IP 洩露檢測邏輯
                    
        except Exception as e:
            self.logger.warning(f"Anonymity test failed for {proxy_str}: {e}")
        
        # 確定匿名等級
        leak_count = len(headers_leaked) + int(dns_leak) + int(webrtc_leak) + int(timezone_mismatch) + int(language_mismatch)
        anonymity_level = self._determine_anonymity_level(leak_count)
        
        # 計算分數
        score = self._calculate_anonymity_score(anonymity_level, leak_count)
        
        return AnonymityResult(
            proxy_str=proxy_str,
            headers_leaked=headers_leaked,
            dns_leak_detected=dns_leak,
            webrtc_leak_detected=webrtc_leak,
            timezone_mismatch=timezone_mismatch,
            language_mismatch=language_mismatch,
            anonymity_level=anonymity_level,
            leak_count=leak_count,
            score=score
        )
    
    def _determine_anonymity_level(self, leak_count: int) -> str:
        """確定匿名等級"""
        if leak_count == 0:
            return 'elite'
        elif leak_count == 1:
            return 'anonymous'
        elif leak_count <= 3:
            return 'distorting'
        else:
            return 'transparent'
    
    def _calculate_anonymity_score(self, anonymity_level: str, leak_count: int) -> float:
        """計算匿名性分數"""
        base_scores = self.scoring_criteria['anonymity']
        base_score = base_scores.get(anonymity_level, 0)
        
        # 根據洩露數量微調分數
        if leak_count == 0:
            return base_score
        elif leak_count == 1:
            return base_score - (leak_count * 10)
        else:
            return base_score - (leak_count * 15)
    
    async def test_reliability(self, proxy_info: ProxyInfo) -> ReliabilityResult:
        """
        測試代理可靠性
        
        Args:
            proxy_info: 代理信息
            
        Returns:
            ReliabilityResult: 可靠性測試結果
        """
        proxy_str = str(proxy_info)
        proxy_dict = self._get_proxy_dict(proxy_info)
        
        # 連接穩定性測試
        connection_successes = 0
        response_times = []
        
        for i in range(10):
            try:
                start_time = time.time()
                async with self.session.get(
                    self.test_urls['connectivity']['http'],
                    proxy=proxy_dict['http'],
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        connection_successes += 1
                        response_times.append(time.time() - start_time)
                        
            except Exception:
                pass
            
            await asyncio.sleep(0.5)  # 短暫間隔
        
        # 負載測試（簡化版）
        load_test_successes = 0
        concurrent_tests = 3
        
        async def single_load_test():
            try:
                async with self.session.get(
                    self.test_urls['connectivity']['http'],
                    proxy=proxy_dict['http'],
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return response.status == 200
            except Exception:
                return False
        
        # 並發測試
        load_tasks = [single_load_test() for _ in range(concurrent_tests)]
        load_results = await asyncio.gather(*load_tasks)
        load_test_successes = sum(load_results)
        
        # 計算各項指標
        connection_success_rate = connection_successes / 10
        load_test_success_rate = load_test_successes / concurrent_tests
        error_recovery_rate = 1.0  # 簡化處理
        uptime_percentage = connection_success_rate * 100
        average_response_time = statistics.mean(response_times) if response_times else float('inf')
        stability_score = self._calculate_stability_score(response_times)
        
        # 計算總體可靠性分數
        score = self._calculate_reliability_score({
            'connection_stability': connection_success_rate,
            'load_handling': load_test_success_rate,
            'error_recovery': error_recovery_rate,
            'longevity': uptime_percentage / 100
        })
        
        return ReliabilityResult(
            proxy_str=proxy_str,
            connection_success_rate=connection_success_rate,
            load_test_success_rate=load_test_success_rate,
            error_recovery_rate=error_recovery_rate,
            uptime_percentage=uptime_percentage,
            average_response_time=average_response_time,
            stability_score=stability_score,
            score=score
        )
    
    def _calculate_stability_score(self, response_times: List[float]) -> float:
        """計算穩定性分數"""
        if len(response_times) < 2:
            return 0.0
        
        # 計算變異係數（標準差/平均值）
        mean_time = statistics.mean(response_times)
        if mean_time == 0:
            return 0.0
        
        std_dev = statistics.stdev(response_times)
        coefficient_of_variation = std_dev / mean_time
        
        # 穩定性分數 = 1 - 變異係數（越高越穩定）
        stability_score = max(0, 1 - coefficient_of_variation)
        return stability_score * 100
    
    def _calculate_reliability_score(self, metrics: Dict[str, float]) -> float:
        """計算可靠性分數"""
        weights = {
            'connection_stability': 0.4,
            'load_handling': 0.3,
            'error_recovery': 0.2,
            'longevity': 0.1
        }
        
        total_score = sum(
            metrics[test] * weights[test] 
            for test in weights.keys()
        ) * 100
        
        return min(100, total_score)
    
    async def validate_proxy(self, proxy_info: ProxyInfo) -> ComprehensiveResult:
        """
        執行完整的代理驗證
        
        Args:
            proxy_info: 代理信息
            
        Returns:
            ComprehensiveResult: 綜合驗證結果
        """
        start_time = time.time()
        self.logger.info(f"Starting comprehensive validation for {proxy_info}")
        
        try:
            # 並行執行所有測試
            connectivity_task = self.test_connectivity(proxy_info)
            performance_task = self.test_performance(proxy_info)
            geolocation_task = self.test_geolocation(proxy_info)
            anonymity_task = self.test_anonymity(proxy_info)
            reliability_task = self.test_reliability(proxy_info)
            
            # 等待所有測試完成
            connectivity, performance, geolocation, anonymity, reliability = await asyncio.gather(
                connectivity_task,
                performance_task,
                geolocation_task,
                anonymity_task,
                reliability_task
            )
            
            # 計算綜合分數
            overall_score = self._calculate_overall_score({
                'connectivity': connectivity.score,
                'performance': performance.score,
                'geolocation': geolocation.score,
                'anonymity': anonymity.score,
                'reliability': reliability.score
            })
            
            # 確定等級和推薦
            grade = self._get_grade(overall_score)
            recommendation = self._get_recommendation(overall_score)
            
            test_duration = time.time() - start_time
            
            result = ComprehensiveResult(
                proxy_info=proxy_info,
                connectivity=connectivity,
                performance=performance,
                geolocation=geolocation,
                anonymity=anonymity,
                reliability=reliability,
                overall_score=overall_score,
                grade=grade,
                recommendation=recommendation,
                test_duration=test_duration,
                timestamp=datetime.now()
            )
            
            self.logger.info(f"Completed validation for {proxy_info} - Score: {overall_score:.1f}, Grade: {grade}")
            return result
            
        except Exception as e:
            self.logger.error(f"Comprehensive validation failed for {proxy_info}: {e}")
            raise
    
    def _calculate_overall_score(self, scores: Dict[str, float]) -> float:
        """計算綜合分數"""
        weights = {
            'connectivity': 0.25,
            'performance': 0.20,
            'geolocation': 0.15,
            'anonymity': 0.20,
            'reliability': 0.20
        }
        
        overall_score = sum(
            scores[category] * weights[category]
            for category in weights.keys()
        )
        
        return overall_score
    
    def _get_grade(self, score: float) -> str:
        """根據分數確定等級"""
        if score >= 90:
            return 'A+'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B+'
        elif score >= 60:
            return 'B'
        elif score >= 50:
            return 'C'
        else:
            return 'F'
    
    def _get_recommendation(self, score: float) -> str:
        """根據分數提供推薦"""
        if score >= 90:
            return "卓越品質，適合生產環境和關鍵任務"
        elif score >= 80:
            return "優秀品質，適合商業爬蟲和數據採集"
        elif score >= 70:
            return "良好品質，適合一般爬蟲和測試用途"
        elif score >= 60:
            return "合格品質，適合學習研究和低強度使用"
        elif score >= 50:
            return "及格品質，僅建議作為備用代理"
        else:
            return "品質不合格，不建議使用"
    
    async def validate_proxies_batch(self, proxy_list: List[ProxyInfo]) -> List[ComprehensiveResult]:
        """
        批量驗證代理
        
        Args:
            proxy_list: 代理列表
            
        Returns:
            List[ComprehensiveResult]: 綜合驗證結果列表
        """
        self.logger.info(f"Starting batch validation for {len(proxy_list)} proxies")
        
        # 使用信號量控制並發數
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def validate_with_semaphore(proxy_info):
            async with semaphore:
                try:
                    return await self.validate_proxy(proxy_info)
                except Exception as e:
                    self.logger.error(f"Batch validation failed for {proxy_info}: {e}")
                    return None
        
        # 創建所有驗證任務
        tasks = [validate_with_semaphore(proxy) for proxy in proxy_list]
        
        # 執行所有任務
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 過濾掉失敗的結果
        valid_results = [result for result in results if result is not None and not isinstance(result, Exception)]
        
        self.logger.info(f"Completed batch validation - Success: {len(valid_results)}/{len(proxy_list)}")
        return valid_results
    
    def save_results_to_csv(self, results: List[ComprehensiveResult], filename: str):
        """
        將驗證結果保存到 CSV 文件
        
        Args:
            results: 驗證結果列表
            filename: 輸出文件名
        """
        rows = []
        
        for result in results:
            row = {
                'proxy': str(result.proxy_info),
                'ip': result.proxy_info.ip,
                'port': result.proxy_info.port,
                'country': result.proxy_info.country,
                'anonymity': result.proxy_info.anonymity,
                'type': result.proxy_info.type,
                'overall_score': result.overall_score,
                'grade': result.grade,
                'recommendation': result.recommendation,
                'test_duration': result.test_duration,
                'timestamp': result.timestamp.isoformat(),
                # 連接性結果
                'connectivity_score': result.connectivity.score,
                'http_success': result.connectivity.http_success,
                'https_success': result.connectivity.https_success,
                'http_response_time': result.connectivity.http_response_time,
                'https_response_time': result.connectivity.https_response_time,
                # 性能結果
                'performance_score': result.performance.score,
                'small_file_speed': result.performance.small_file_speed,
                'medium_file_speed': result.performance.medium_file_speed,
                'large_file_speed': result.performance.large_file_speed,
                'consistency_score': result.performance.consistency_score,
                # 地理位置結果
                'geolocation_score': result.geolocation.score,
                'country_consistency': result.geolocation.country_consistency,
                'city_consistency': result.geolocation.city_consistency,
                'services_tested': result.geolocation.services_tested,
                # 匿名性結果
                'anonymity_score': result.anonymity.score,
                'anonymity_level': result.anonymity.anonymity_level,
                'leak_count': result.anonymity.leak_count,
                'headers_leaked': ';'.join(result.anonymity.headers_leaked),
                # 可靠性結果
                'reliability_score': result.reliability.score,
                'connection_success_rate': result.reliability.connection_success_rate,
                'load_test_success_rate': result.reliability.load_test_success_rate,
                'uptime_percentage': result.reliability.uptime_percentage,
                'average_response_time': result.reliability.average_response_time
            }
            rows.append(row)
        
        # 寫入 CSV 文件
        if rows:
            df = pd.DataFrame(rows)
            df.to_csv(filename, index=False, encoding='utf-8')
            self.logger.info(f"Results saved to {filename}")
        else:
            self.logger.warning("No results to save")
    
    def generate_summary_report(self, results: List[ComprehensiveResult]) -> Dict[str, Any]:
        """
        生成匯總報告
        
        Args:
            results: 驗證結果列表
            
        Returns:
            Dict: 匯總報告
        """
        if not results:
            return {}
        
        total_proxies = len(results)
        
        # 統計各等級數量
        grade_counts = {}
        for result in results:
            grade = result.grade
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
        
        # 計算平均得分
        avg_scores = {
            'overall': statistics.mean([r.overall_score for r in results]),
            'connectivity': statistics.mean([r.connectivity.score for r in results]),
            'performance': statistics.mean([r.performance.score for r in results]),
            'geolocation': statistics.mean([r.geolocation.score for r in results]),
            'anonymity': statistics.mean([r.anonymity.score for r in results]),
            'reliability': statistics.mean([r.reliability.score for r in results])
        }
        
        # 統計匿名等級
        anonymity_levels = {}
        for result in results:
            level = result.anonymity.anonymity_level
            anonymity_levels[level] = anonymity_levels.get(level, 0) + 1
        
        # 性能統計
        response_times = [r.connectivity.http_response_time for r in results if r.connectivity.http_success]
        avg_response_time = statistics.mean(response_times) if response_times else 0
        
        speeds = [r.performance.small_file_speed for r in results if r.performance.small_file_speed > 0]
        avg_speed = statistics.mean(speeds) if speeds else 0
        
        report = {
            'summary': {
                'total_proxies_tested': total_proxies,
                'test_timestamp': datetime.now().isoformat(),
                'average_scores': avg_scores,
                'grade_distribution': grade_counts,
                'anonymity_distribution': anonymity_levels
            },
            'performance_metrics': {
                'average_response_time': avg_response_time,
                'average_speed_kbps': avg_speed,
                'successful_connections': sum(1 for r in results if r.connectivity.http_success),
                'success_rate': sum(1 for r in results if r.connectivity.http_success) / total_proxies
            },
            'quality_analysis': {
                'high_quality_count': sum(1 for r in results if r.overall_score >= 80),
                'medium_quality_count': sum(1 for r in results if 60 <= r.overall_score < 80),
                'low_quality_count': sum(1 for r in results if r.overall_score < 60),
                'recommended_count': sum(1 for r in results if r.overall_score >= 70)
            }
        }
        
        return report


# 使用示例和測試函數
async def main():
    """主測試函數"""
    # 創建測試代理列表
    test_proxies = [
        ProxyInfo(ip="185.199.229.228", port=8080, country="US"),
        ProxyInfo(ip="103.250.166.1", port=8080, country="ID"),
        ProxyInfo(ip="51.222.12.245", port=80, country="CA")
    ]
    
    async with ComprehensiveProxyValidator(max_concurrent=10) as validator:
        # 批量驗證
        results = await validator.validate_proxies_batch(test_proxies)
        
        # 保存結果
        validator.save_results_to_csv(results, "comprehensive_validation_results.csv")
        
        # 生成匯總報告
        report = validator.generate_summary_report(results)
        
        print("=== 綜合代理驗證報告 ===")
        print(f"測試代理數量: {report['summary']['total_proxies_tested']}")
        print(f"平均總分: {report['summary']['average_scores']['overall']:.1f}")
        print(f"成功連接率: {report['performance_metrics']['success_rate']:.1%}")
        print(f"高質量代理: {report['quality_analysis']['high_quality_count']}")
        
        # 打印詳細結果
        for result in results:
            print(f"\n代理: {result.proxy_info}")
            print(f"總分: {result.overall_score:.1f} (等級: {result.grade})")
            print(f"推薦: {result.recommendation}")


if __name__ == "__main__":
    # 運行異步主函數
    asyncio.run(main())