from dataclasses import dataclass, field
import os
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

Action = Literal["EXPLAIN", "CHECK_TAG", "REPOSITION", "REMOVE_AND_REPLACE", "RECAPTURE", "ESCALATE_TO_HUMAN"]


class ExplainRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    purpose: Literal["explain_violation", "next_safe_step", "summarize_correction"] = "explain_violation"
    event_id: str | None = Field(default=None, pattern=r"^evt-[0-9]{5}$")


class ModelAdvice(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    action: Action
    summary: str = Field(min_length=10, max_length=650)
    steps: list[str] = Field(min_length=1, max_length=3)
    evidence_event_ids: list[str] = Field(min_length=1, max_length=8)
    rule_ids: list[str] = Field(min_length=1, max_length=12)


@dataclass(frozen=True)
class AgentConfig:
    enabled: bool = False
    api_key: str = field(default="", repr=False)
    model: str = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B"
    base_url: str = "https://api.tokenfactory.nebius.com/v1"
    timeout_seconds: float = 20
    calls_per_session: int = 4
    calls_per_process: int = 40

    @classmethod
    def from_env(cls):
        return cls(enabled=os.getenv("ENABLE_NEBIUS_AGENT", "0").lower() in {"1", "true"},
                   api_key=os.getenv("NEBIUS_API_KEY", ""),
                   model=os.getenv("NEBIUS_NVIDIA_MODEL", cls.model),
                   base_url=os.getenv("NEBIUS_BASE_URL", cls.base_url).rstrip("/"))

    @property
    def configured(self):
        return self.enabled and bool(self.api_key) and self.model.lower().startswith("nvidia/") and self.base_url in {
            "https://api.tokenfactory.nebius.com/v1", "https://api.tokenfactory.us-central1.nebius.com/v1"}
