from __future__ import annotations

from pathlib import Path

import pytest

from app.simulation.config import SimulationConfig, load_simulation_config
from app.simulation.generator import run_simulation
from app.utils.paths import repo_root


@pytest.fixture(scope="session")
def simulation_config() -> SimulationConfig:
    return load_simulation_config(repo_root() / "configs" / "simulation_config.yaml")


@pytest.fixture(scope="session")
def simulation_frames(simulation_config: SimulationConfig):
    return run_simulation(simulation_config)
