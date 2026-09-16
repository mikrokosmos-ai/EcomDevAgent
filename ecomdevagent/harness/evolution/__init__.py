"""EcomDevAgent Agent 自进化子系统。

实现真正的自主进化能力：
- 执行轨迹收集与持久化
- 失败模式自动分类
- 失败驱动的 Skill 自动生成
- Skill 元数据管理与自动废弃
- 文件备份与回滚
- 基于量化指标的进化评估
- 6 阶段自主进化决策循环
"""

from ecomdevagent.harness.evolution.models import (
    EvalResult,
    EvolutionCycle,
    EvolutionRecord,
    EvolutionStatus,
    ExecutionTrace,
    FailurePattern,
    ProblemCategory,
    SkillGenResult,
    SkillStatus,
    SuccessSignal,
)
from ecomdevagent.harness.evolution.backup import BackupManager
from ecomdevagent.harness.evolution.trace_store import ExecutionTraceStore, TraceCollector
from ecomdevagent.harness.evolution.skill_meta import SkillMetaManager
from ecomdevagent.harness.evolution.problem_classifier import ProblemClassifier
from ecomdevagent.harness.evolution.skill_generator import SkillGenerator
from ecomdevagent.harness.evolution.evaluator import EvolutionEvaluator
from ecomdevagent.harness.evolution.decision_loop import EvolutionDecisionLoop
from ecomdevagent.harness.evolution.manager import EvolutionManager
from ecomdevagent.harness.evolution.success_detector import SuccessDetector
from ecomdevagent.harness.evolution.success_generator import SuccessSkillGenerator
from ecomdevagent.harness.evolution.skill_matcher import SkillMatcher
from ecomdevagent.harness.evolution.tools import (
    TriggerEvolutionTool,
    ListEvolutionsTool,
    GetEvolutionDetailTool,
    ListAutoSkillsTool,
    DeprecateSkillTool,
)

__all__ = [
    # Models
    "EvalResult",
    "EvolutionCycle",
    "EvolutionRecord",
    "EvolutionStatus",
    "ExecutionTrace",
    "FailurePattern",
    "ProblemCategory",
    "SkillGenResult",
    "SkillStatus",
    "SuccessSignal",
    # Core
    "BackupManager",
    "ExecutionTraceStore",
    "TraceCollector",
    "SkillMetaManager",
    # Intelligence
    "ProblemClassifier",
    "SkillGenerator",
    "EvolutionEvaluator",
    "SuccessDetector",
    "SuccessSkillGenerator",
    "SkillMatcher",
    # Orchestration
    "EvolutionDecisionLoop",
    "EvolutionManager",
    # Tools
    "TriggerEvolutionTool",
    "ListEvolutionsTool",
    "GetEvolutionDetailTool",
    "ListAutoSkillsTool",
    "DeprecateSkillTool",
]
