"""
chap7.py
--------
Chapter 7: Material Take-off & Quantity Summary for OsdagBridge Design Report.
Includes:
  - Chart A: Structural Steel Quantities (MT)
  - Chart B: Concrete & Reinforcement Quantities (m³ / MT)
  - Table 7.1: Bill of Materials with repeated LongTable headers.
"""

from typing import Optional, Dict
from osdagbridge.core.reports.report_utils import _tex, build_longtable, _fig_embed


def ch7_quantities(input_dict: dict, fig_paths: Optional[Dict[str, str]] = None) -> str:
    """Generate Chapter 7 Material Take-off with visual analytics and structured BOM."""
    fig_paths = fig_paths or {}

    # Extract BOM rows from input_dict (populated by calculate_material_quantities)
    bom_items = [
        ("1", "Structural Steel (IS 2062) for Girders", "steel_girders"),
        ("2(a)", "Cross Bracing -- Top Chord", "bracing_top"),
        ("2(b)", "Cross Bracing -- Bottom Chord", "bracing_bot"),
        ("2(c)", "Cross Bracing -- Diagonal Chord", "bracing_diag"),
        ("3", "Concrete (M40) for Deck Slab", "concrete_deck"),
        ("4", "Reinforcement Steel (Fe 500)", "rebar_deck"),
        ("5", "Shear Stud Connectors", "shear_studs"),
        ("6", "Crash Barrier (SIDL Component)", "crash_barrier"),
    ]

    table_rows = []
    for sn, desc, key_pfx in bom_items:
        vol_formula = str(input_dict.get(f"{key_pfx}_vol_formula", "N.A."))
        qty = str(input_dict.get(f"{key_pfx}_qty", "N.A."))
        vol_total = str(input_dict.get(f"{key_pfx}_vol_total", "N.A."))
        wt_single = str(input_dict.get(f"{key_pfx}_wt_single", "N.A."))
        wt_total = str(input_dict.get(f"{key_pfx}_wt_total", "N.A."))

        row = (
            f"\\textnormal{{{sn}}} & "
            f"\\textnormal{{{_tex(desc)}}} & "
            f"{vol_formula} & "
            f"\\textnormal{{{_tex(qty)}}} & "
            f"\\textnormal{{{_tex(vol_total)}}} & "
            f"\\textnormal{{{_tex(wt_single)}}} & "
            f"\\textnormal{{{_tex(wt_total)}}} \\\\[5pt]\n\\hline"
        )
        table_rows.append(row)

    table_bom_tex = build_longtable(
        caption="Bill of Materials (Steel, Concrete, and Reinforcement Quantities)",
        headers=["S.N.", "Item Description", "Volume Formula", "Qty", "Total Vol.", "Wt (MT)", "Total Wt (MT)"],
        rows=table_rows,
        col_spec=r"|C{1.0cm}|L{4.2cm}|C{2.6cm}|C{1.4cm}|C{2.0cm}|C{1.8cm}|C{2.0cm}|",
        label="tab:material-takeoff",
        note="Material quantities calculated from geometry and component sizing per IS:2062, IRC:112, and IRC:22.",
    )

    # Embed Visualizations
    chart_a_embed = ""
    chart_b_embed = ""
    if fig_paths.get("boq_steel"):
        chart_a_embed = _fig_embed(
            fig_paths.get("boq_steel"),
            "Figure 7.1: Structural Steel Take-off Breakdown by Component (Metric Tonnes, MT)",
            width=r"0.88\textwidth",
        )
    if fig_paths.get("boq_concrete_rebar"):
        chart_b_embed = _fig_embed(
            fig_paths.get("boq_concrete_rebar"),
            "Figure 7.2: Concrete Volume (m³) and Reinforcement Steel Weight (MT) Summary",
            width=r"0.88\textwidth",
        )

    return f"""
\\chapter{{Material Take-off \\& Quantity Summary}}
\\label{{ch:material-takeoff}}

This chapter summarizes the computed material consumption, structural steel tonnage, concrete volume, and reinforcement quantities evaluated for the bridge superstructure design.

\\section{{Material Quantity Analytics}}
The graphical breakdowns below illustrate the structural steel component weight distribution and concrete-to-reinforcement proportions for procurement estimation.

{chart_a_embed}

{chart_b_embed}

\\section{{Detailed Bill of Materials}}
The tabulated bill of quantities details unit formulas, member item counts, total volumes, and component metric tonnages.

{table_bom_tex}
"""
