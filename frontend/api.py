"""HTTP client for the simulator backend API."""

import os
import requests
import streamlit as st

_BASE = os.getenv("BACKEND_URL", "http://localhost:8000")
_TIMEOUT = 60


def _post(endpoint: str, payload: dict) -> dict | None:
    try:
        r = requests.post(f"{_BASE}{endpoint}", json=payload, timeout=_TIMEOUT)
        r.raise_for_status()
        response = r.json()
        st.session_state["_debug_last"] = {
            "method":   "POST",
            "endpoint": endpoint,
            "status":   r.status_code,
            "request":  payload,
            "response": response,
        }
        return response
    except requests.exceptions.ConnectionError:
        st.error("Backend offline. Start with: `uvicorn backend.main:app --reload --port 8000`")
    except requests.exceptions.HTTPError as e:
        detail = e.response.json().get("detail", str(e)) if e.response else str(e)
        st.error(f"API error: {detail}")
    except Exception as e:
        st.error(f"Unexpected error ({endpoint}): {e}")
    return None


def simulate(context: dict[str, str], decisions: dict[str, str]) -> dict | None:
    """POST /api/simulate — sends context and decisions, returns full result."""
    return _post("/api/simulate", {"context": context, "decisions": decisions})


def monte_carlo(
    context:   dict[str, str],
    decisions: dict[str, str],
    params:    dict[str, dict],
    n_iter:    int = 2000,
    threshold: float = 60.0,
) -> dict | None:
    """POST /api/monte_carlo — runs Monte Carlo simulation."""
    return _post("/api/monte_carlo", {
        "context":   context,
        "decisions": decisions,
        "params":    params,
        "n_iter":    n_iter,
        "threshold": threshold,
    })


def get_nodes() -> dict | None:
    """GET /api/nodes — fetches all node options to populate the input form."""
    try:
        r = requests.get(f"{_BASE}/api/nodes", timeout=_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("Backend offline. Start with: `uvicorn backend.main:app --reload --port 8000`")
    except Exception as e:
        st.error(f"Error fetching nodes: {e}")
    return None
