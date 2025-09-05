"""
토큰 모니터링 모듈
다른 프로젝트에서도 재사용 가능한 독립적인 토큰 사용량 모니터링 시스템
"""

from .core.auto_monitor import AutoTokenMonitor
from .core.config import TokenMonitorConfig
from .core.monitor import TokenLimits, TokenMonitor, TokenUsage
from .utils.aggregator import GlobalTokenMonitor, TokenUsageAggregator
from .utils.export import TokenDataExporter
from .utils.import_ import TokenDataImporter
from .utils.sync_service import ProjectTokenSync, TokenSyncService

__version__ = "1.0.0"
__author__ = "HireMe Team"

# 기본 인스턴스들
default_config = TokenMonitorConfig()
token_monitor = TokenMonitor(config=default_config)
auto_monitor = AutoTokenMonitor(token_monitor=token_monitor)

__all__ = [
    "TokenMonitor",
    "TokenUsage",
    "TokenLimits",
    "AutoTokenMonitor",
    "TokenMonitorConfig",
    "TokenDataExporter",
    "TokenDataImporter",
    "TokenUsageAggregator",
    "GlobalTokenMonitor",
    "TokenSyncService",
    "ProjectTokenSync",
    "token_monitor",
    "auto_monitor",
    "default_config"
]
