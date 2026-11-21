"""
visualizations package
----------------------
Matplotlib-based engineering visualizations for OsdagBridge reports.
"""

from .ur_dashboard import generate_ur_dashboard
from .boq_analytics import generate_boq_charts

__all__ = ["generate_ur_dashboard", "generate_boq_charts"]

