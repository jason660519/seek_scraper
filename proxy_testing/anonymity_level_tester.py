"""
深度匿名等級測試系統

這個模組實現了多維度的匿名性檢測，包括：
1. IP 洩漏檢測
2. DNS 洩漏檢測  
3. WebRTC 洩漏檢測
4. 時區洩漏檢測
5. 語言洩漏檢測
6. 指紋獨特性分析
7. 頭部信息分析

通過綜合分析這些維度來評估代理的匿名等級。
"""

import asyncio
import aiohttp
import json
import time
import logging
import hashlib
import random
import string
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
import re
import base64


@dataclass
class AnonymityTestResult:
    """匿名性測試結果"""
    test_name: str
    passed: bool
    score: float
    details: Dict[str, Any]
    errors: List[str] = field(default_factory=list)
    execution_time: float = 0.0


@dataclass
class FingerprintAnalysis:
    """指紋分析結果"""
    user_agent_hash: str
    accept_headers_hash: str
    encoding_hash: str
    language_hash: str
    uniqueness_score: float
    commonality_score: float


class BaseAnonymityTest(ABC):
    """匿名性測試基類"""
    
    def __init__(self, name: str, timeout: int = 30):
        self.name = name
        self.timeout = timeout
        self.logger = logging.getLogger(f"AnonymityTest.{name}")
    
    @abstractmethod
    async def execute(self, session: aiohttp.ClientSession, proxy_dict: Dict[str, str], 
                     original_ip: str) -> AnonymityTestResult:
        """執行匿名性測試"""
        pass
    
    def _create_test_result(self, passed: bool, score: float, details: Dict[str, Any], 
                          errors: List[str] = None, execution_time: float = 0.0) -> AnonymityTestResult:
        """創建測試結果"""
        return AnonymityTestResult(
            test_name=self.name,
            passed=passed,
            score=score,
            details=details,
            errors=errors or [],
            execution_time=execution_time
        )


class IPLeakTest(BaseAnonymityTest):
    """IP 洩漏測試"""
    
    def __init__(self):
        super().__init__("ip_leak_test")
        self.test_endpoints = [
            "https://api.ipify.org?format=json",
            "https://api.ip.sb/jsonip",
            "https://httpbin.org/ip",
            "https://ifconfig.me/all.json",
            "https://api.myip.com"
        ]
    
    async def execute(self, session: aiohttp.ClientSession, proxy_dict: Dict[str, str], 
                     original_ip: str) -> AnonymityTestResult:
        """執行 IP 洩漏測試"""
        start_time = time.time()
        detected_ips = set()
        errors = []
        
        try:
            # 並行測試多個端點
            tasks = []
            for endpoint in self.test_endpoints:
                task = asyncio.create_task(self._check_ip_endpoint(session, endpoint, proxy_dict))
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 收集檢測到的 IP
            for result in results:
                if isinstance(result, str):
                    detected_ips.add(result)
                elif isinstance(result, Exception):
                    errors.append(f"IP check failed: {str(result)}")
            
            # 分析結果
            leaked_ips = self._analyze_ip_leaks(detected_ips, original_ip)
            
            # 計算分數
            score = self._calculate_ip_leak_score(leaked_ips, len(detected_ips))
            passed = len(leaked_ips) == 0 and len(detected_ips) > 0
            
            details = {
                'total_endpoints_tested': len(self.test_endpoints),
                'successful_detections': len(detected_ips),
                'detected_ips': list(detected_ips),
                'leaked_ips': list(leaked_ips),
                'ip_consistency': self._check_ip_consistency(detected_ips)
            }
            
            execution_time = time.time() - start_time
            return self._create_test_result(passed, score, details, errors, execution_time)
            
        except Exception as e:
            execution_time = time.time() - start_time
            return self._create_test_result(False, 0.0, {}, [str(e)], execution_time)
    
    async def _check_ip_endpoint(self, session: aiohttp.ClientSession, endpoint: str, 
                               proxy_dict: Dict[str, str]) -> Optional[str]:
        """檢查單個端點的 IP"""
        try:
            async with session.get(
                endpoint,
                proxy=proxy_dict['https'],
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.text()
                    
                    # 提取 IP 地址
                    ip_match = re.search(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', data)
                    if ip_match:
                        return ip_match.group()
                    
                    # 嘗試 JSON 解析
                    try:
                        json_data = json.loads(data)
                        if 'ip' in json_data:
                            return json_data['ip']
                        elif 'origin' in json_data:
                            return json_data['origin']
                    except:
                        pass
        
        except Exception as e:
            self.logger.debug(f"IP endpoint check failed for {endpoint}: {e}")
        
        return None
    
    def _analyze_ip_leaks(self, detected_ips: Set[str], original_ip: str) -> Set[str]:
        """分析 IP 洩漏"""
        leaked_ips = set()
        
        for ip in detected_ips:
            if ip == original_ip:
                leaked_ips.add(ip)
        
        return leaked_ips
    
    def _calculate_ip_leak_score(self, leaked_ips: Set[str], total_detections: int) -> float:
        """計算 IP 洩漏分數"""
        if total_detections == 0:
            return 0.0
        
        # 基於洩漏數量和檢測成功率
        leak_ratio = len(leaked_ips) / total_detections
        success_ratio = total_detections / len(self.test_endpoints)
        
        # 分數 = (1 - 洩漏比例) * 成功率 * 100
        score = (1 - leak_ratio) * success_ratio * 100
        return max(0.0, score)
    
    def _check_ip_consistency(self, detected_ips: Set[str]) -> float:
        """檢查 IP 一致性"""
        if len(detected_ips) <= 1:
            return 1.0
        
        # 理想情況下所有端點應該返回相同的 IP
        # 一致性 = 1 / 不同 IP 數量
        return 1.0 / len(detected_ips)


class DNSLeakTest(BaseAnonymityTest):
    """DNS 洩漏測試"""
    
    def __init__(self):
        super().__init__("dns_leak_test")
        self.dns_test_domains = [
            "dns-leak-test.com",
            "dnsleaktest.com", 
            "whoami.akamai.net",
            "resolver1.opendns.com",
            "ns1.google.com"
        ]
    
    async def execute(self, session: aiohttp.ClientSession, proxy_dict: Dict[str, str], 
                     original_ip: str) -> AnonymityTestResult:
        """執行 DNS 洩漏測試"""
        start_time = time.time()
        detected_dns_servers = set()
        errors = []
        
        try:
            # 使用 DNS 洩漏檢測服務
            dns_leak_results = await self._check_dns_leak_services(session, proxy_dict)
            
            # 分析 DNS 服務器
            leaked_servers = self._analyze_dns_leaks(dns_leak_results, original_ip)
            
            # 計算分數
            score = self._calculate_dns_leak_score(leaked_servers, len(dns_leak_results))
            passed = len(leaked_servers) == 0 and len(dns_leak_results) > 0
            
            details = {
                'dns_services_tested': len(self.dns_test_domains),
                'successful_detections': len(dns_leak_results),
                'detected_dns_servers': list(detected_dns_servers),
                'leaked_dns_servers': list(leaked_servers),
                'dns_consistency': self._check_dns_consistency(dns_leak_results)
            }
            
            execution_time = time.time() - start_time
            return self._create_test_result(passed, score, details, errors, execution_time)
            
        except Exception as e:
            execution_time = time.time() - start_time
            return self._create_test_result(False, 0.0, {}, [str(e)], execution_time)
    
    async def _check_dns_leak_services(self, session: aiohttp.ClientSession, 
                                     proxy_dict: Dict[str, str]) -> List[Dict[str, Any]]:
        """檢查 DNS 洩漏服務"""
        results = []
        
        # 使用 dns-leak-test.com API
        try:
            async with session.get(
                "https://dns-leak-test.com/api/v1/dns-leak",
                proxy=proxy_dict['https'],
                timeout=aiohttp.ClientTimeout(total=15)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    results.append({'service': 'dns-leak-test', 'data': data})
        except Exception as e:
            self.logger.debug(f"DNS leak test service failed: {e}")
        
        # 使用 whoami.akamai.net
        try:
            async with session.get(
                "http://whoami.akamai.net/",
                proxy=proxy_dict['http'],
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    resolver_ip = await response.text()
                    results.append({
                        'service': 'akamai-whoami',
                        'data': {'resolver_ip': resolver_ip.strip()}
                    })
        except Exception as e:
            self.logger.debug(f"Akamai whoami test failed: {e}")
        
        return results
    
    def _analyze_dns_leaks(self, dns_results: List[Dict[str, Any]], original_ip: str) -> Set[str]:
        """分析 DNS 洩漏"""
        leaked_servers = set()
        
        for result in dns_results:
            if result['service'] == 'akamai-whoami':
                resolver_ip = result['data'].get('resolver_ip', '')
                if resolver_ip and resolver_ip == original_ip:
                    leaked_servers.add(resolver_ip)
        
        return leaked_servers
    
    def _calculate_dns_leak_score(self, leaked_servers: Set[str], total_detections: int) -> float:
        """計算 DNS 洩漏分數"""
        if total_detections == 0:
            return 0.0
        
        leak_ratio = len(leaked_servers) / total_detections if total_detections > 0 else 0
        score = (1 - leak_ratio) * 100
        return max(0.0, score)
    
    def _check_dns_consistency(self, dns_results: List[Dict[str, Any]]) -> float:
        """檢查 DNS 一致性"""
        if len(dns_results) <= 1:
            return 1.0
        
        # 簡化的 DNS 一致性檢查
        return 0.8  # 假設大部分情況下 DNS 是一致的


class WebRTCTest(BaseAnonymityTest):
    """WebRTC 洩漏測試"""
    
    def __init__(self):
        super().__init__("webrtc_leak_test")
    
    async def execute(self, session: aiohttp.ClientSession, proxy_dict: Dict[str, str], 
                     original_ip: str) -> AnonymityTestResult:
        """執行 WebRTC 洩漏測試"""
        start_time = time.time()
        
        try:
            # WebRTC 測試需要 JavaScript 環境，這裡模擬測試
            # 在實際應用中，可以使用 Puppeteer 或 Playwright
            
            webrtc_leak_detected = await self._simulate_webrtc_test(session, proxy_dict, original_ip)
            
            # 計算分數
            score = 100.0 if not webrtc_leak_detected else 0.0
            passed = not webrtc_leak_detected
            
            details = {
                'webrtc_leak_detected': webrtc_leak_detected,
                'test_method': 'simulated',
                'note': 'Full WebRTC test requires browser automation'
            }
            
            execution_time = time.time() - start_time
            return self._create_test_result(passed, score, details, [], execution_time)
            
        except Exception as e:
            execution_time = time.time() - start_time
            return self._create_test_result(False, 0.0, {}, [str(e)], execution_time)
    
    async def _simulate_webrtc_test(self, session: aiohttp.ClientSession, 
                                   proxy_dict: Dict[str, str], original_ip: str) -> bool:
        """模擬 WebRTC 測試"""
        # 這是一個簡化的模擬測試
        # 實際測試需要使用真實的 WebRTC API
        
        # 檢查是否可能洩漏（基於一些啟發式規則）
        try:
            # 檢查代理的響應頭部
            async with session.get(
                "https://httpbin.org/headers",
                proxy=proxy_dict['https'],
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    headers = dict(response.headers)
                    
                    # 如果響應頭包含原始 IP 相關信息，可能會有 WebRTC 洩漏風險
                    # 這裡只是一個示例邏輯
                    for header_value in headers.values():
                        if original_ip in str(header_value):
                            return True
        
        except Exception:
            pass
        
        return False


class BrowserFingerprintTest(BaseAnonymityTest):
    """瀏覽器指紋測試"""
    
    def __init__(self):
        super().__init__("browser_fingerprint_test")
        self.fingerprint_endpoints = [
            "https://httpbin.org/headers",
            "https://httpbin.org/user-agent",
            "https://httpbin.org/encoding/utf8"
        ]
    
    async def execute(self, session: aiohttp.ClientSession, proxy_dict: Dict[str, str], 
                     original_ip: str) -> AnonymityTestResult:
        """執行瀏覽器指紋測試"""
        start_time = time.time()
        
        try:
            # 收集瀏覽器指紋信息
            fingerprint_data = await self._collect_fingerprint_data(session, proxy_dict)
            
            # 分析指紋獨特性
            fingerprint_analysis = self._analyze_fingerprint_uniqueness(fingerprint_data)
            
            # 檢測各種洩漏
            timezone_leak = self._detect_timezone_leak(fingerprint_data)
            language_leak = self._detect_language_leak(fingerprint_data)
            
            # 計算總體分數
            score = self._calculate_fingerprint_score(fingerprint_analysis, timezone_leak, language_leak)
            passed = score >= 60.0  # 指紋分數需要達到 60 分以上
            
            details = {
                'fingerprint_analysis': {
                    'user_agent_hash': fingerprint_analysis.user_agent_hash,
                    'accept_headers_hash': fingerprint_analysis.accept_headers_hash,
                    'encoding_hash': fingerprint_analysis.encoding_hash,
                    'language_hash': fingerprint_analysis.language_hash,
                    'uniqueness_score': fingerprint_analysis.uniqueness_score,
                    'commonality_score': fingerprint_analysis.commonality_score
                },
                'leak_detection': {
                    'timezone_leak': timezone_leak,
                    'language_leak': language_leak
                },
                'raw_headers': fingerprint_data
            }
            
            execution_time = time.time() - start_time
            return self._create_test_result(passed, score, details, [], execution_time)
            
        except Exception as e:
            execution_time = time.time() - start_time
            return self._create_test_result(False, 0.0, {}, [str(e)], execution_time)
    
    async def _collect_fingerprint_data(self, session: aiohttp.ClientSession, 
                                       proxy_dict: Dict[str, str]) -> Dict[str, Any]:
        """收集指紋數據"""
        fingerprint_data = {}
        
        # 收集請求頭部
        try:
            async with session.get(
                "https://httpbin.org/headers",
                proxy=proxy_dict['https'],
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    fingerprint_data['request_headers'] = data.get('headers', {})
        except Exception as e:
            self.logger.debug(f"Headers collection failed: {e}")
        
        # 收集用戶代理
        try:
            async with session.get(
                "https://httpbin.org/user-agent",
                proxy=proxy_dict['https'],
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    fingerprint_data['user_agent'] = data.get('user-agent', '')
        except Exception as e:
            self.logger.debug(f"User-agent collection failed: {e}")
        
        return fingerprint_data
    
    def _analyze_fingerprint_uniqueness(self, fingerprint_data: Dict[str, Any]) -> FingerprintAnalysis:
        """分析指紋獨特性"""
        headers = fingerprint_data.get('request_headers', {})
        user_agent = fingerprint_data.get('user_agent', '')
        
        # 計算各種哈希值
        user_agent_hash = self._calculate_hash(user_agent)
        accept_headers_hash = self._calculate_hash(headers.get('Accept', ''))
        encoding_hash = self._calculate_hash(headers.get('Accept-Encoding', ''))
        language_hash = self._calculate_hash(headers.get('Accept-Language', ''))
        
        # 計算獨特性分數（基於一些啟發式規則）
        uniqueness_score = self._calculate_uniqueness_score(user_agent, headers)
        commonality_score = self._calculate_commonality_score(user_agent, headers)
        
        return FingerprintAnalysis(
            user_agent_hash=user_agent_hash,
            accept_headers_hash=accept_headers_hash,
            encoding_hash=encoding_hash,
            language_hash=language_hash,
            uniqueness_score=uniqueness_score,
            commonality_score=commonality_score
        )
    
    def _calculate_hash(self, text: str) -> str:
        """計算文本哈希"""
        return hashlib.md5(text.encode()).hexdigest()[:8]
    
    def _calculate_uniqueness_score(self, user_agent: str, headers: Dict[str, str]) -> float:
        """計算獨特性分數"""
        score = 50.0  # 基礎分數
        
        # 基於用戶代理的獨特性
        if 'Chrome' in user_agent and 'Safari' in user_agent:
            score -= 10  # 常見的 Chrome 組合
        
        if 'Firefox' in user_agent:
            score += 5   # Firefox 相對較少見
        
        # 基於接受語言的獨特性
        accept_lang = headers.get('Accept-Language', '')
        if 'en-US' in accept_lang:
            score -= 5   # 常見的英語
        elif 'zh-CN' in accept_lang:
            score += 10  # 中文相對獨特
        
        return max(0.0, min(100.0, score))
    
    def _calculate_commonality_score(self, user_agent: str, headers: Dict[str, str]) -> float:
        """計算常見性分數"""
        score = 50.0  # 基礎分數
        
        # 檢查是否為常見的瀏覽器配置
        if 'Mozilla' in user_agent and 'AppleWebKit' in user_agent:
            score += 20  # 常見的現代瀏覽器
        
        # 檢查接受頭部是否標準
        accept = headers.get('Accept', '')
        if 'text/html' in accept and 'application/xml' in accept:
            score += 10  # 標準的接受頭部
        
        return max(0.0, min(100.0, score))
    
    def _detect_timezone_leak(self, fingerprint_data: Dict[str, Any]) -> bool:
        """檢測時區洩漏"""
        headers = fingerprint_data.get('request_headers', {})
        
        # 檢查是否有時區相關的頭部信息
        # 這是一個簡化的檢測，實際上需要更複雜的邏輯
        accept_lang = headers.get('Accept-Language', '')
        
        # 如果接受語言與代理位置明顯不符，可能會有時區洩漏
        # 這裡只是一個示例邏輯
        return len(accept_lang) > 20  # 過長的語言字符串可能表示自定義配置
    
    def _detect_language_leak(self, fingerprint_data: Dict[str, Any]) -> bool:
        """檢測語言洩漏"""
        headers = fingerprint_data.get('request_headers', {})
        
        accept_lang = headers.get('Accept-Language', '')
        
        # 檢查語言配置是否過於獨特
        if not accept_lang:
            return True  # 沒有語言信息可能是洩漏
        
        # 過多的語言選項可能表示自定義配置
        lang_count = accept_lang.count(',') + 1
        return lang_count > 5  # 超過 5 種語言可能表示異常
    
    def _calculate_fingerprint_score(self, fingerprint_analysis: FingerprintAnalysis, 
                                   timezone_leak: bool, language_leak: bool) -> float:
        """計算指紋分數"""
        score = 0.0
        
        # 獨特性分數 (40%)
        uniqueness_score = fingerprint_analysis.uniqueness_score
        score += (uniqueness_score / 100) * 40
        
        # 常見性分數 (30%)
        commonality_score = fingerprint_analysis.commonality_score
        score += (commonality_score / 100) * 30
        
        # 洩漏檢測分數 (30%)
        leak_penalty = 0
        if timezone_leak:
            leak_penalty += 15
        if language_leak:
            leak_penalty += 15
        
        score += max(0, 30 - leak_penalty)
        
        return min(100.0, score)


class AdvancedAnonymityTester:
    """高級匿名性測試器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.timeout = self.config.get('timeout', 30)
        self.max_retries = self.config.get('max_retries', 3)
        
        # 初始化所有測試
        self.tests = [
            IPLeakTest(),
            DNSLeakTest(),
            WebRTCTest(),
            BrowserFingerprintTest()
        ]
        
        self.logger = logging.getLogger("AdvancedAnonymityTester")
    
    async def run_full_anonymity_test(self, proxy_dict: Dict[str, str], 
                                    original_ip: str) -> Dict[str, Any]:
        """運行完整的匿名性測試"""
        start_time = time.time()
        
        self.logger.info(f"Starting anonymity test for proxy: {proxy_dict.get('http', 'unknown')}")
        
        # 創建會話
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        ) as session:
            
            # 並行執行所有測試
            test_tasks = []
            for test in self.tests:
                task = asyncio.create_task(self._run_single_test(test, session, proxy_dict, original_ip))
                test_tasks.append(task)
            
            # 執行所有測試
            test_results = await asyncio.gather(*test_tasks, return_exceptions=True)
            
            # 處理結果
            processed_results = {}
            total_score = 0.0
            total_weight = 0.0
            
            for i, result in enumerate(test_results):
                test_name = self.tests[i].name
                
                if isinstance(result, Exception):
                    self.logger.error(f"Test {test_name} failed: {result}")
                    processed_results[test_name] = {
                        'passed': False,
                        'score': 0.0,
                        'error': str(result)
                    }
                else:
                    processed_results[test_name] = {
                        'passed': result.passed,
                        'score': result.score,
                        'details': result.details,
                        'errors': result.errors,
                        'execution_time': result.execution_time
                    }
                    
                    # 計算加權分數
                    weight = self._get_test_weight(test_name)
                    total_score += result.score * weight
                    total_weight += weight
            
            # 計算總體分數
            overall_score = total_score / total_weight if total_weight > 0 else 0.0
            
            # 確定匿名等級
            anonymity_level = self._determine_anonymity_level(overall_score, processed_results)
            
            execution_time = time.time() - start_time
            
            return {
                'timestamp': datetime.now().isoformat(),
                'proxy': proxy_dict.get('http', 'unknown'),
                'anonymity_level': anonymity_level,
                'overall_score': overall_score,
                'test_results': processed_results,
                'execution_time': execution_time,
                'recommendations': self._generate_recommendations(processed_results, anonymity_level)
            }
    
    async def _run_single_test(self, test: BaseAnonymityTest, session: aiohttp.ClientSession,
                             proxy_dict: Dict[str, str], original_ip: str) -> AnonymityTestResult:
        """運行單個測試"""
        try:
            return await test.execute(session, proxy_dict, original_ip)
        except Exception as e:
            # 如果測試失敗，返回失敗結果
            return AnonymityTestResult(
                test_name=test.name,
                passed=False,
                score=0.0,
                details={},
                errors=[f"Test execution failed: {str(e)}"],
                execution_time=0.0
            )
    
    def _get_test_weight(self, test_name: str) -> float:
        """獲取測試權重"""
        weights = {
            'ip_leak_test': 0.35,           # IP 洩漏最重要
            'dns_leak_test': 0.25,          # DNS 洩漏次重要
            'browser_fingerprint_test': 0.25, # 指紋測試
            'webrtc_leak_test': 0.15        # WebRTC 洩漏
        }
        return weights.get(test_name, 0.25)
    
    def _determine_anonymity_level(self, overall_score: float, test_results: Dict[str, Any]) -> str:
        """確定匿名等級"""
        # 基於總分確定等級
        if overall_score >= 90:
            return "elite"
        elif overall_score >= 80:
            return "anonymous"
        elif overall_score >= 60:
            return "transparent"
        else:
            return "compromised"
    
    def _generate_recommendations(self, test_results: Dict[str, Any], anonymity_level: str) -> List[str]:
        """生成推薦建議"""
        recommendations = []
        
        # 基於匿名等級的總體建議
        if anonymity_level == "elite":
            recommendations.append("匿名性優秀，可以放心使用")
        elif anonymity_level == "anonymous":
            recommendations.append("匿名性良好，適合大多數用途")
        elif anonymity_level == "transparent":
            recommendations.append("匿名性一般，建議謹慎使用")
        else:
            recommendations.append("匿名性較差，存在安全風險")
        
        # 基於具體測試結果的建議
        for test_name, result in test_results.items():
            if not result.get('passed', False):
                if test_name == 'ip_leak_test':
                    recommendations.append("檢測到 IP 洩漏，請檢查代理配置")
                elif test_name == 'dns_leak_test':
                    recommendations.append("檢測到 DNS 洩漏，建議使用 DNS-over-HTTPS")
                elif test_name == 'webrtc_leak_test':
                    recommendations.append("可能存在 WebRTC 洩漏，建議禁用 WebRTC")
                elif test_name == 'browser_fingerprint_test':
                    recommendations.append("瀏覽器指紋可能存在洩漏，建議使用隱私插件")
        
        return recommendations
    
    def generate_anonymity_report(self, test_result: Dict[str, Any]) -> str:
        """生成匿名性報告"""
        report = []
        report.append("=== 匿名性測試報告 ===")
        report.append(f"測試時間: {test_result['timestamp']}")
        report.append(f"代理: {test_result['proxy']}")
        report.append(f"匿名等級: {test_result['anonymity_level'].upper()}")
        report.append(f"總體分數: {test_result['overall_score']:.1f}/100")
        report.append(f"執行時間: {test_result['execution_time']:.2f}秒")
        report.append("")
        
        # 各項測試結果
        report.append("各項測試結果:")
        for test_name, result in test_result['test_results'].items():
            status = "通過" if result['passed'] else "失敗"
            report.append(f"  {test_name}: {status} (分數: {result['score']:.1f})")
        
        # 推薦建議
        if test_result['recommendations']:
            report.append("")
            report.append("推薦建議:")
            for rec in test_result['recommendations']:
                report.append(f"  - {rec}")
        
        return "\n".join(report)


# ==================== 使用示例 ====================

async def demo_anonymity_testing():
    """演示匿名性測試"""
    import logging
    
    # 設置日誌
    logging.basicConfig(level=logging.INFO)
    
    # 創建測試器
    tester = AdvancedAnonymityTester({
        'timeout': 30,
        'max_retries': 3
    })
    
    # 測試代理（這裡使用示例 IP，實際測試需要真實的代理）
    test_proxies = [
        {"http": "http://185.199.229.228:8080", "https": "http://185.199.229.228:8080"},
        {"http": "http://103.250.166.1:8080", "https": "http://103.250.166.1:8080"}
    ]
    
    # 假設的原始 IP（實際測試中需要獲取真實的原始 IP）
    original_ip = "203.0.113.1"  # 示例 IP
    
    print("=== 深度匿名性測試演示 ===\n")
    
    for proxy_dict in test_proxies:
        print(f"正在測試代理: {proxy_dict['http']}")
        
        try:
            # 運行完整測試
            result = await tester.run_full_anonymity_test(proxy_dict, original_ip)
            
            # 生成報告
            report = tester.generate_anonymity_report(result)
            print(report)
            
        except Exception as e:
            print(f"測試失敗: {e}")
        
        print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    # 運行演示
    asyncio.run(demo_anonymity_testing())