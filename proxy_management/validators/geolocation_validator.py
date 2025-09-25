"""
地理位置精準驗證器

這個模組實現了多服務交叉驗證的地理位置檢測系統，
通過多個地理位置服務的交叉驗證來提高準確性。
"""

import asyncio
import aiohttp
import json
import time
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
from abc import ABC, abstractmethod
import statistics
import math


@dataclass
class LocationInfo:
    """地理位置信息"""
    country: str
    country_code: str
    city: str
    region: str
    latitude: float
    longitude: float
    timezone: str
    accuracy_radius: float = 0.0
    confidence: float = 0.0
    source: str = "unknown"
    
    def distance_to(self, other: 'LocationInfo') -> float:
        """計算兩個位置之間的距離（公里）"""
        return self._haversine_distance(
            self.latitude, self.longitude,
            other.latitude, other.longitude
        )
    
    @staticmethod
    def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """使用 Haversine 公式計算兩點間距離"""
        # 將緯度經度轉換為弧度
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine 公式
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # 地球半徑（公里）
        r = 6371
        return c * r
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            'country': self.country,
            'country_code': self.country_code,
            'city': self.city,
            'region': self.region,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'timezone': self.timezone,
            'accuracy_radius': self.accuracy_radius,
            'confidence': self.confidence,
            'source': self.source
        }


class GeolocationService(ABC):
    """地理位置服務基類"""
    
    def __init__(self, name: str, timeout: int = 10):
        self.name = name
        self.timeout = timeout
        self.logger = logging.getLogger(f"GeolocationService.{name}")
    
    @abstractmethod
    async def get_location(self, session: aiohttp.ClientSession, proxy_dict: Dict[str, str]) -> Optional[LocationInfo]:
        """獲取地理位置信息"""
        pass
    
    def _calculate_confidence(self, data: Dict[str, Any]) -> float:
        """計算位置置信度"""
        return 0.5  # 默認置信度


class IPApiService(GeolocationService):
    """IP-API 服務"""
    
    def __init__(self):
        super().__init__("ip-api")
        self.endpoint = "http://ip-api.com/json"
    
    async def get_location(self, session: aiohttp.ClientSession, proxy_dict: Dict[str, str]) -> Optional[LocationInfo]:
        """從 IP-API 獲取位置"""
        try:
            async with session.get(
                self.endpoint,
                proxy=proxy_dict['http'],
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('status') == 'success':
                        return LocationInfo(
                            country=data.get('country', ''),
                            country_code=data.get('countryCode', ''),
                            city=data.get('city', ''),
                            region=data.get('regionName', ''),
                            latitude=float(data.get('lat', 0)),
                            longitude=float(data.get('lon', 0)),
                            timezone=data.get('timezone', ''),
                            confidence=self._calculate_confidence(data),
                            source=self.name
                        )
        except Exception as e:
            self.logger.warning(f"IP-API service failed: {e}")
        
        return None


class IPInfoService(GeolocationService):
    """IPInfo 服務"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("ipinfo")
        self.endpoint = "https://ipinfo.io/json"
        self.api_key = api_key
    
    async def get_location(self, session: aiohttp.ClientSession, proxy_dict: Dict[str, str]) -> Optional[LocationInfo]:
        """從 IPInfo 獲取位置"""
        try:
            headers = {}
            if self.api_key:
                headers['Authorization'] = f"Bearer {self.api_key}"
            
            async with session.get(
                self.endpoint,
                headers=headers,
                proxy=proxy_dict['https'],
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # 解析坐標
                    loc = data.get('loc', '0,0').split(',')
                    lat = float(loc[0]) if len(loc) > 0 else 0
                    lon = float(loc[1]) if len(loc) > 1 else 0
                    
                    return LocationInfo(
                        country=data.get('country', ''),
                        country_code=data.get('country', ''),
                        city=data.get('city', ''),
                        region=data.get('region', ''),
                        latitude=lat,
                        longitude=lon,
                        timezone=data.get('timezone', ''),
                        confidence=self._calculate_confidence(data),
                        source=self.name
                    )
        except Exception as e:
            self.logger.warning(f"IPInfo service failed: {e}")
        
        return None


class FreeGeoIPService(GeolocationService):
    """FreeGeoIP 服務"""
    
    def __init__(self):
        super().__init__("freegeoip")
        self.endpoint = "https://freegeoip.app/json/"
    
    async def get_location(self, session: aiohttp.ClientSession, proxy_dict: Dict[str, str]) -> Optional[LocationInfo]:
        """從 FreeGeoIP 獲取位置"""
        try:
            async with session.get(
                self.endpoint,
                proxy=proxy_dict['https'],
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return LocationInfo(
                        country=data.get('country_name', ''),
                        country_code=data.get('country_code', ''),
                        city=data.get('city', ''),
                        region=data.get('region_name', ''),
                        latitude=float(data.get('latitude', 0)),
                        longitude=float(data.get('longitude', 0)),
                        timezone=data.get('time_zone', ''),
                        accuracy_radius=float(data.get('accuracy_radius', 0)),
                        confidence=self._calculate_confidence(data),
                        source=self.name
                    )
        except Exception as e:
            self.logger.warning(f"FreeGeoIP service failed: {e}")
        
        return None


class ExtremeIPService(GeolocationService):
    """ExtremeIP 服務"""
    
    def __init__(self):
        super().__init__("extreme-ip-lookup")
        self.endpoint = "https://extreme-ip-lookup.com/json/"
    
    async def get_location(self, session: aiohttp.ClientSession, proxy_dict: Dict[str, str]) -> Optional[LocationInfo]:
        """從 ExtremeIP 獲取位置"""
        try:
            async with session.get(
                self.endpoint,
                proxy=proxy_dict['https'],
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return LocationInfo(
                        country=data.get('country', ''),
                        country_code=data.get('countryCode', ''),
                        city=data.get('city', ''),
                        region=data.get('region', ''),
                        latitude=float(data.get('lat', 0)),
                        longitude=float(data.get('lon', 0)),
                        timezone=data.get('timezone', ''),
                        confidence=self._calculate_confidence(data),
                        source=self.name
                    )
        except Exception as e:
            self.logger.warning(f"ExtremeIP service failed: {e}")
        
        return None


class GeolocationConsensusEngine:
    """地理位置共識引擎"""
    
    def __init__(self):
        self.logger = logging.getLogger("GeolocationConsensusEngine")
        self.consensus_thresholds = {
            'country': 0.6,      # 60% 一致性閾值
            'city': 0.5,         # 50% 一致性閾值
            'coordinate': 50.0     # 50km 距離閾值
        }
    
    def find_consensus(self, locations: List[LocationInfo]) -> Dict[str, Any]:
        """找出地理位置共識"""
        if not locations:
            return {
                'country_consensus': None,
                'city_consensus': None,
                'coordinate_consensus': None,
                'country_consistency': 0.0,
                'city_consistency': 0.0,
                'coordinate_precision': 0.0,
                'total_services': 0,
                'services_successful': 0
            }
        
        # 國家共識
        country_consensus, country_consistency = self._find_country_consensus(locations)
        
        # 城市共識
        city_consensus, city_consistency = self._find_city_consensus(locations)
        
        # 坐標共識
        coordinate_consensus, coordinate_precision = self._find_coordinate_consensus(locations)
        
        return {
            'country_consensus': country_consensus,
            'city_consensus': city_consensus,
            'coordinate_consensus': coordinate_consensus,
            'country_consistency': country_consistency,
            'city_consistency': city_consistency,
            'coordinate_precision': coordinate_precision,
            'total_services': len(locations),
            'services_successful': len([l for l in locations if l.confidence > 0])
        }
    
    def _find_country_consensus(self, locations: List[LocationInfo]) -> Tuple[Optional[str], float]:
        """找出國家共識"""
        country_counts = {}
        total_weight = 0.0
        
        for location in locations:
            if location.country:
                confidence = max(0.1, location.confidence)  # 最小置信度
                country_counts[location.country] = country_counts.get(location.country, 0) + confidence
                total_weight += confidence
        
        if not country_counts:
            return None, 0.0
        
        # 找出最高得分的國家
        consensus_country = max(country_counts.items(), key=lambda x: x[1])
        consistency = consensus_country[1] / total_weight if total_weight > 0 else 0.0
        
        return consensus_country[0] if consistency >= self.consensus_thresholds['country'] else None, consistency
    
    def _find_city_consensus(self, locations: List[LocationInfo]) -> Tuple[Optional[str], float]:
        """找出城市共識"""
        city_counts = {}
        total_weight = 0.0
        
        for location in locations:
            if location.city:
                confidence = max(0.1, location.confidence)
                city_key = f"{location.city},{location.country}"
                city_counts[city_key] = city_counts.get(city_key, 0) + confidence
                total_weight += confidence
        
        if not city_counts:
            return None, 0.0
        
        consensus_city = max(city_counts.items(), key=lambda x: x[1])
        consistency = consensus_city[1] / total_weight if total_weight > 0 else 0.0
        
        return consensus_city[0] if consistency >= self.consensus_thresholds['city'] else None, consistency
    
    def _find_coordinate_consensus(self, locations: List[LocationInfo]) -> Tuple[Optional[Tuple[float, float]], float]:
        """找出坐標共識"""
        valid_locations = [l for l in locations if l.latitude != 0 or l.longitude != 0]
        
        if len(valid_locations) < 2:
            return None, float('inf')
        
        # 計算坐標中心點
        center_lat = statistics.mean(l.latitude for l in valid_locations)
        center_lon = statistics.mean(l.longitude for l in valid_locations)
        
        # 計算所有點到中心的平均距離
        center_location = LocationInfo(
            country="", city="", region="",
            latitude=center_lat, longitude=center_lon,
            country_code="", timezone=""
        )
        
        distances = [center_location.distance_to(l) for l in valid_locations]
        avg_distance = statistics.mean(distances)
        
        # 如果平均距離在閾值內，則認為有共識
        if avg_distance <= self.consensus_thresholds['coordinate']:
            return (center_lat, center_lon), avg_distance
        else:
            return None, avg_distance


class PrecisionGeolocationValidator:
    """精準地理位置驗證器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.timeout = self.config.get('timeout', 10)
        self.max_retries = self.config.get('max_retries', 3)
        
        # 初始化服務
        self.services = [
            IPApiService(),
            IPInfoService(),
            FreeGeoIPService(),
            ExtremeIPService()
        ]
        
        self.consensus_engine = GeolocationConsensusEngine()
        self.logger = logging.getLogger("PrecisionGeolocationValidator")
    
    async def validate_location(self, proxy_dict: Dict[str, str]) -> Dict[str, Any]:
        """驗證代理的地理位置"""
        start_time = time.time()
        
        # 並行查詢所有服務
        locations = await self._query_all_services(proxy_dict)
        
        # 找出共識
        consensus = self.consensus_engine.find_consensus(locations)
        
        # 計算位置準確性分數
        accuracy_score = self._calculate_accuracy_score(locations, consensus)
        
        execution_time = time.time() - start_time
        
        return {
            'locations': [loc.to_dict() for loc in locations],
            'consensus': consensus,
            'accuracy_score': accuracy_score,
            'execution_time': execution_time,
            'timestamp': datetime.now().isoformat()
        }
    
    async def _query_all_services(self, proxy_dict: Dict[str, str]) -> List[LocationInfo]:
        """並行查詢所有地理位置服務"""
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        ) as session:
            
            tasks = []
            for service in self.services:
                task = asyncio.create_task(
                    self._query_service_with_retry(session, service, proxy_dict)
                )
                tasks.append(task)
            
            # 等待所有查詢完成
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 過濾掉異常結果
            locations = []
            for result in results:
                if isinstance(result, LocationInfo):
                    locations.append(result)
                elif isinstance(result, Exception):
                    self.logger.warning(f"Service query failed: {result}")
            
            return locations
    
    async def _query_service_with_retry(self, session: aiohttp.ClientSession, 
                                      service: GeolocationService, 
                                      proxy_dict: Dict[str, str]) -> Optional[LocationInfo]:
        """帶重試的服務查詢"""
        for attempt in range(self.max_retries):
            try:
                location = await service.get_location(session, proxy_dict)
                if location:
                    return location
            except Exception as e:
                self.logger.warning(f"Service {service.name} attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(0.5 * (attempt + 1))  # 指數退避
        
        return None
    
    def _calculate_accuracy_score(self, locations: List[LocationInfo], consensus: Dict[str, Any]) -> float:
        """計算位置準確性分數"""
        if not locations:
            return 0.0
        
        score = 0.0
        
        # 基於共識的一致性 (60%)
        country_consistency = consensus.get('country_consistency', 0)
        city_consistency = consensus.get('city_consistency', 0)
        coordinate_precision = consensus.get('coordinate_precision', float('inf'))
        
        # 國家一致性分數 (30%)
        if country_consistency >= 0.8:
            score += 30.0
        elif country_consistency >= 0.6:
            score += 24.0
        elif country_consistency >= 0.4:
            score += 18.0
        else:
            score += 12.0
        
        # 城市一致性分數 (20%)
        if city_consistency >= 0.7:
            score += 20.0
        elif city_consistency >= 0.5:
            score += 16.0
        elif city_consistency >= 0.3:
            score += 12.0
        else:
            score += 8.0
        
        # 坐標精確度分數 (10%)
        if coordinate_precision <= 10:  # 10km 內
            score += 10.0
        elif coordinate_precision <= 50:  # 50km 內
            score += 8.0
        elif coordinate_precision <= 100:  # 100km 內
            score += 6.0
        else:
            score += 4.0
        
        # 服務成功率 (20%)
        total_services = consensus.get('total_services', 0)
        successful_services = consensus.get('services_successful', 0)
        
        if total_services > 0:
            success_rate = successful_services / total_services
            score += success_rate * 20.0
        
        # 置信度平均值 (20%)
        if locations:
            avg_confidence = statistics.mean([l.confidence for l in locations])
            score += avg_confidence * 20.0
        
        return min(100.0, score)
    
    def generate_location_report(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成地理位置驗證報告"""
        consensus = validation_result.get('consensus', {})
        locations = validation_result.get('locations', [])
        
        report = {
            'summary': {
                'total_services_queried': consensus.get('total_services', 0),
                'successful_services': consensus.get('services_successful', 0),
                'accuracy_score': validation_result.get('accuracy_score', 0),
                'consensus_status': 'unknown'
            },
            'location_consensus': {
                'country': consensus.get('country_consensus'),
                'city': consensus.get('city_consensus'),
                'coordinates': consensus.get('coordinate_consensus'),
                'consistency_scores': {
                    'country': consensus.get('country_consistency', 0),
                    'city': consensus.get('city_consistency', 0),
                    'coordinate_precision_km': consensus.get('coordinate_precision', 0)
                }
            },
            'detailed_locations': [],
            'recommendations': []
        }
        
        # 確定共識狀態
        country_consensus = consensus.get('country_consensus')
        city_consensus = consensus.get('city_consensus')
        
        if country_consensus and city_consensus:
            report['summary']['consensus_status'] = 'full'
        elif country_consensus:
            report['summary']['consensus_status'] = 'country_only'
        else:
            report['summary']['consensus_status'] = 'no_consensus'
        
        # 詳細位置信息
        for loc_data in locations:
            report['detailed_locations'].append({
                'source': loc_data.get('source', 'unknown'),
                'country': loc_data.get('country', ''),
                'city': loc_data.get('city', ''),
                'coordinates': {
                    'latitude': loc_data.get('latitude', 0),
                    'longitude': loc_data.get('longitude', 0)
                },
                'confidence': loc_data.get('confidence', 0)
            })
        
        # 生成推薦
        accuracy_score = validation_result.get('accuracy_score', 0)
        
        if accuracy_score >= 80:
            report['recommendations'].append("地理位置驗證結果優秀，可以信賴")
        elif accuracy_score >= 60:
            report['recommendations'].append("地理位置驗證結果良好，基本可信")
        elif accuracy_score >= 40:
            report['recommendations'].append("地理位置驗證結果一般，需要謹慎使用")
        else:
            report['recommendations'].append("地理位置驗證結果較差，不建議依賴")
        
        if not country_consensus:
            report['recommendations'].append("國家位置無共識，可能存在定位問題")
        
        if consensus.get('coordinate_precision', 0) > 100:
            report['recommendations'].append("坐標精度較差，位置可能不準確")
        
        return report


# ==================== 使用示例 ====================

async def demo_geolocation_validation():
    """演示地理位置驗證"""
    import logging
    
    # 設置日誌
    logging.basicConfig(level=logging.INFO)
    
    # 創建驗證器
    validator = PrecisionGeolocationValidator({
        'timeout': 15,
        'max_retries': 3
    })
    
    # 測試代理
    test_proxies = [
        {"http": "http://185.199.229.228:8080", "https": "http://185.199.229.228:8080"},
        {"http": "http://103.250.166.1:8080", "https": "http://103.250.166.1:8080"},
        {"http": "http://51.222.12.245:80", "https": "http://51.222.12.245:80"}
    ]
    
    print("=== 精準地理位置驗證演示 ===\n")
    
    for proxy_dict in test_proxies:
        print(f"正在驗證代理: {proxy_dict['http']}")
        
        try:
            # 執行地理位置驗證
            result = await validator.validate_location(proxy_dict)
            
            # 生成報告
            report = validator.generate_location_report(result)
            
            # 打印結果
            summary = report['summary']
            print(f"準確性分數: {summary['accuracy_score']:.1f}/100")
            print(f"共識狀態: {summary['consensus_status']}")
            print(f"服務成功率: {summary['successful_services']}/{summary['total_services_queried']}")
            
            # 打印共識結果
            consensus = report['location_consensus']
            if consensus['country']:
                print(f"國家共識: {consensus['country']}")
            if consensus['city']:
                print(f"城市共識: {consensus['city']}")
            if consensus['coordinates']:
                lat, lon = consensus['coordinates']
                print(f"坐標共識: {lat:.4f}, {lon:.4f}")
            
            # 打印推薦
            if report['recommendations']:
                print("推薦建議:")
                for rec in report['recommendations']:
                    print(f"  - {rec}")
            
            print(f"執行時間: {result['execution_time']:.2f}秒")
            
        except Exception as e:
            print(f"驗證失敗: {e}")
        
        print("-" * 60)


if __name__ == "__main__":
    # 運行演示
    asyncio.run(demo_geolocation_validation())