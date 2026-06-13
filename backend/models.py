"""Schemas Pydantic para a API do simulador."""

from pydantic import BaseModel


class SimulateRequest(BaseModel):
    context: dict[str, str]
    decisions: dict[str, str]


class PathMCStats(BaseModel):
    mean: float
    std: float
    p5: float
    p95: float
    p_below: float


class PathItem(BaseModel):
    d1: str
    d1_adj: float
    d4: str
    d4_adj: float
    d5: str
    d5_adj: float
    path_base: float
    interactions: float = 0.0
    mc: PathMCStats | None = None


class CriterionResult(BaseModel):
    path_idx: int
    value: float
    criterion_values: list[float]


class UserSelection(BaseModel):
    d1: str
    d4: str
    d5: str
    yields: list[float]
    ev: float


class TriangularParam(BaseModel):
    min: float
    mode: float
    max: float


class MonteCarloRequest(BaseModel):
    context:   dict[str, str]
    decisions: dict[str, str]
    params:    dict[str, TriangularParam]
    n_iter:    int = 2000
    threshold: float = 60.0


class TornadoEntry(BaseModel):
    correlation: float
    variance_share: float


class MonteCarloResponse(BaseModel):
    yields:     list[float]
    n_iter:     int
    fixed_base: float
    mean:       float
    std:        float
    p5:         float
    p95:        float
    threshold:  float
    p_below:    float
    tornado:    dict[str, TornadoEntry]


class SimulateResponse(BaseModel):
    baseline: float
    context_adj: float
    context_base: float
    fixed_adj: float
    base_effective: float
    rain_states: list[str]
    rain_probs: list[float]
    paths: list[PathItem]
    matrix: list[list[float]]
    criteria: dict[str, CriterionResult]
    user_selection: UserSelection
    upgrade_potential: dict | None = None
