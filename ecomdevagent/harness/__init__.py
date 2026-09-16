"""EcomDevAgent Agent 自配置子系统。

允许 Agent 在运行时（受元权限控制）修改自身 Harness 行为：
- Hook 增删改
- 配置项更新
- 权限规则管理
- Memory 条目管理
"""

from ecomdevagent.harness.hook_manager import HookManager
from ecomdevagent.harness.config_manager import ConfigManager
from ecomdevagent.harness.permission_manager import PermissionManager

# 自进化子系统
from ecomdevagent.harness.evolution.manager import EvolutionManager
from ecomdevagent.harness.evolution.models import (
    EvalResult,
    EvolutionCycle,
    EvolutionRecord,
    EvolutionStatus,
    ExecutionTrace,
    FailurePattern,
    ProblemCategory,
    SkillGenResult,
)
from ecomdevagent.harness.evolution.backup import BackupManager
from ecomdevagent.harness.evolution.trace_store import ExecutionTraceStore, TraceCollector
from ecomdevagent.harness.evolution.skill_meta import SkillMetaManager
from ecomdevagent.harness.evolution.tools import (
    TriggerEvolutionTool,
    ListEvolutionsTool,
    GetEvolutionDetailTool,
    ListAutoSkillsTool,
    DeprecateSkillTool,
)

__all__ = [
    "HookManager",
    "ConfigManager",
    "PermissionManager",
    # Evolution
    "EvolutionManager",
    "EvalResult",
    "EvolutionCycle",
    "EvolutionRecord",
    "EvolutionStatus",
    "ExecutionTrace",
    "FailurePattern",
    "ProblemCategory",
    "SkillGenResult",
    "BackupManager",
    "ExecutionTraceStore",
    "TraceCollector",
    "SkillMetaManager",
    "TriggerEvolutionTool",
    "ListEvolutionsTool",
    "GetEvolutionDetailTool",
    "ListAutoSkillsTool",
    "DeprecateSkillTool",
]
