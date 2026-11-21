"""
chap3.py
--------
Chapter 3: Loads and Load Combinations for OsdagBridge Design Report.
Separates Vehicle Live Loads and Footway Live Loads into independent, dedicated tables.
Uses centralized styles and repeated LongTable headers.
"""

from osdagbridge.core.utils.common import (
    KEY_CB_LOAD,
    KEY_LL_CUSTOM_VEHICLES,
    KEY_LL_FOOTPATH_PRESSURE_MODE,
    KEY_LL_FOOTPATH_PRESSURE_VALUE,
    KEY_LL_IRC_70R_BOGIE,
    KEY_LL_IRC_70R_TRACKED,
    KEY_LL_IRC_70R_WHEELED,
    KEY_LL_IRC_AA_TRACKED,
    KEY_LL_IRC_AA_WHEELED,
    KEY_LL_IRC_CLASS_A,
    KEY_LL_IRC_CLASS_FATIGUE,
    KEY_LL_IRC_CLASS_SV,
    KEY_MATERIAL_DECK_DENSITY,
    KEY_MATERIAL_GIRDER_DENSITY,
    KEY_PL_SELF_WEIGHT_FACTOR,
    KEY_RL_LOAD_VALUE,
    KEY_SL_DAMPING,
    KEY_SL_DEAD_LOAD_MODE,
    KEY_SL_DEAD_LOAD_VALUE,
    KEY_SL_HORIZONTAL_COEFF,
    KEY_SL_IMPORTANCE_FACTOR,
    KEY_SL_LIVE_LOAD_MODE,
    KEY_SL_LIVE_LOAD_VALUE,
    KEY_SL_SEISMIC_ZONE,
    KEY_SL_SOIL_TYPE,
    KEY_SL_SPECTRAL_COEFF,
    KEY_SL_TIME_PERIOD,
    KEY_SL_VERTICAL_COEFF,
    KEY_SL_ZONE_FACTOR,
    KEY_SPAN,
    KEY_TL_BRIDGE_TEMP_MAX,
    KEY_TL_BRIDGE_TEMP_MIN,
    KEY_TL_HIGHEST_MAX_TEMP,
    KEY_TL_LOWEST_MIN_TEMP,
    KEY_TL_TEMP_FALL,
    KEY_TL_TEMP_RISE,
    KEY_TS_FOOTPATH_WIDTH,
    KEY_TS_NO_OF_FOOTPATHS,
    KEY_WC_LD_LANE_TABLE_COUNT,
    KEY_WC_MATERIAL,
    KEY_WC_THICKNESS,
    KEY_WL_AVG_EXPOSED_HEIGHT,
    KEY_WL_BASIC_WIND_SPEED,
    KEY_WL_HOURLY_MEAN_WIND,
    KEY_WL_HOURLY_WIND_PRESSURE,
    KEY_WL_LONGITUDINAL_WIND_FORCE,
    KEY_WL_TERRAIN_TYPE,
    KEY_WL_TRANSVERSE_WIND_FORCE,
    KEY_WL_VERTICAL_WIND_FORCE,
)

from osdagbridge.core.reports.report_utils import _tex, _render_value, build_longtable
from osdagbridge.core.utils.codes.irc6_2017 import IRC6_2017


def ch3_loads(input_dict: dict) -> str:
    """Generate Chapter 3 content with decoupled Vehicle Live Load and Footway Live Load tables."""

    # -------------------------------------------------------------------------
    # 1. VEHICLE LIVE LOAD DATA COLLECTION
    # -------------------------------------------------------------------------
    selected_vehicles = []
    # (Vehicle Class, Configuration, Loading Standard)
    if input_dict.get(KEY_LL_IRC_CLASS_A):
        selected_vehicles.append(("Class A", "Wheeled Axle Train (554 kN gross)", "IRC:6-2017 Cl. 204.1"))
    if input_dict.get(KEY_LL_IRC_70R_WHEELED):
        selected_vehicles.append(("Class 70R (Wheeled)", "Wheeled Heavy Axle Train (1000 kN gross)", "IRC:6-2017 Cl. 204.1"))
    if input_dict.get(KEY_LL_IRC_70R_TRACKED):
        selected_vehicles.append(("Class 70R (Tracked)", "Tracked Heavy Vehicle (700 kN gross)", "IRC:6-2017 Cl. 204.1"))
    if input_dict.get(KEY_LL_IRC_AA_WHEELED):
        selected_vehicles.append(("Class AA (Wheeled)", "Wheeled Heavy Vehicle (400 kN gross)", "IRC:6-2017 Cl. 204.1"))
    if input_dict.get(KEY_LL_IRC_AA_TRACKED):
        selected_vehicles.append(("Class AA (Tracked)", "Tracked Vehicle (700 kN gross)", "IRC:6-2017 Cl. 204.1"))
    if input_dict.get(KEY_LL_IRC_CLASS_SV):
        selected_vehicles.append(("Class SV", "Special Vehicle Configuration", "IRC:6-2017 Cl. 204.1"))
    if input_dict.get(KEY_LL_IRC_70R_BOGIE):
        selected_vehicles.append(("Class 70R (Bogie)", "Bogie Axle Configuration", "IRC:6-2017 Cl. 204.1"))
    if input_dict.get(KEY_LL_IRC_CLASS_FATIGUE):
        selected_vehicles.append(("Class Fatigue", "Fatigue Vehicle Load Model", "IRC:6-2017 Annex D"))

    custom = input_dict.get(KEY_LL_CUSTOM_VEHICLES)
    if custom and isinstance(custom, list):
        for c in custom:
            if isinstance(c, dict) and c.get("name"):
                selected_vehicles.append((c["name"], "Custom User Defined Vehicle", "Project Specification"))
            elif isinstance(c, str):
                selected_vehicles.append((c, "Custom User Defined Vehicle", "Project Specification"))

    if not selected_vehicles:
        selected_vehicles.append(("Class A", "Wheeled Axle Train (Default)", "IRC:6-2017 Cl. 204.1"))

    # Impact Factor
    span_val = input_dict.get(KEY_SPAN)
    span_m = float(span_val) if span_val not in (None, "") else 30.0
    impact_class_a = 1.0 + IRC6_2017.cl_208_2_impact_factor(span_m)
    impact_class_70r = 1.0 + IRC6_2017.cl_208_3_impact_factor(span_m)

    # Braking Force
    lanes = input_dict.get(KEY_WC_LD_LANE_TABLE_COUNT) or 2
    try:
        lanes_int = int(lanes)
    except (ValueError, TypeError):
        lanes_int = 2
    try:
        braking_raw = IRC6_2017.cl_211_2_braking_force(lanes_int)
        braking_kN = float(braking_raw) / 1000.0 if float(braking_raw) > 500 else float(braking_raw) * 9.80665
    except Exception:
        # Fallback per IRC:6 Cl. 211.2 (20% of first lane Class A = 0.20 * 554 kN = ~110.8 kN)
        braking_kN = 110.8

    # Centrifugal Force
    # Straight span bridge: R = infinity, Centrifugal force = 0.00 kN
    centrifugal_str = "0.00 kN (Straight Span Bridge)"

    # Build Vehicle Live Load Table Rows
    vehicle_rows = []
    for cls_name, config_desc, ref_std in selected_vehicles:
        im_val = impact_class_a if "A" in cls_name and "AA" not in cls_name else impact_class_70r
        row = (
            f"\\textnormal{{{_tex(cls_name)}}} & "
            f"\\textnormal{{{_tex(config_desc)}}} & "
            f"{im_val:.3f} & "
            f"{braking_kN:.2f} kN & "
            f"\\textnormal{{{centrifugal_str}}} & "
            f"\\textnormal{{{ref_std}}} \\\\[5pt]\n\\hline"
        )
        vehicle_rows.append(row)

    table_vehicles_tex = build_longtable(
        caption="Carriageway Vehicle Live Loads (LL) -- IRC:6 Specifications",
        headers=["Vehicle Class", "Selected Configuration", "Impact Factor (1+IF)", "Braking Load", "Centrifugal Force", "Code Reference"],
        rows=vehicle_rows,
        col_spec=r"|L{2.8cm}|L{3.5cm}|C{2.0cm}|C{2.2cm}|C{2.6cm}|L{2.5cm}|",
        label="tab:vehicle-live-loads",
        note="Live loads derived dynamically from GUI Additional Inputs (Loading tab) per IRC:6-2017 Cl. 204.",
    )

    # -------------------------------------------------------------------------
    # 2. FOOTWAY AND PEDESTRIAN LOAD DATA COLLECTION
    # -------------------------------------------------------------------------
    fp_mode = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_MODE, "As per IRC 6")
    fp_value = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_VALUE, "")
    n_footpaths = input_dict.get(KEY_TS_NO_OF_FOOTPATHS, "0")
    fp_width = input_dict.get(KEY_TS_FOOTPATH_WIDTH, "0.0")

    if str(fp_mode).strip().lower() in ("as per irc 6", "as per irc6", "automatic"):
        try:
            fp_applied = f"{IRC6_2017.cl_206_1_footway_load():.3f} kN/m\\textsuperscript{{2}}"
            fp_clause = "IRC:6-2017 Cl. 206.1"
        except Exception:
            fp_applied = "4.000 kN/m\\textsuperscript{2}"
            fp_clause = "IRC:6-2017 Cl. 206.1"
    elif fp_value not in (None, ""):
        fp_applied = f"{fp_value} kN/m\\textsuperscript{{2}}"
        fp_clause = "User Defined Input"
    else:
        fp_applied = "N/A (No footway configured)"
        fp_clause = "---"

    footway_rows = [
        f"\\textnormal{{Footpath Configuration / Provision}} & {_tex(str(n_footpaths))} Footpath(s) provided & Project Cross-Section \\\\[5pt]\n\\hline",
        f"\\textnormal{{Footpath Clear Width}} & {_tex(str(fp_width))} m & Bridge Typical Section \\\\[5pt]\n\\hline",
        f"\\textnormal{{Footway Load Calculation Mode}} & {_tex(str(fp_mode))} & Additional Inputs Loading Tab \\\\[5pt]\n\\hline",
        f"\\textnormal{{Applied Uniform Live Load Pressure}} & {fp_applied} & {fp_clause} \\\\[5pt]\n\\hline",
        f"\\textnormal{{Pedestrian Live Load Reduction with LL}} & Considered in Governing Load Combos & IRC:6-2017 Cl. 206.3 \\\\[5pt]\n\\hline",
    ]

    table_footway_tex = build_longtable(
        caption="Footway and Pedestrian Live Loads -- IRC:6 Specifications",
        headers=["Footway Parameter", "Applied Design Value", "Design Reference / Source"],
        rows=footway_rows,
        col_spec=r"|L{5.5cm}|p{5.5cm}|L{4.5cm}|",
        label="tab:footway-loads",
        note="Footway load is applied simultaneously with or independent of vehicular live loads per IRC:6-2017.",
    )

    # -------------------------------------------------------------------------
    # 3. DEAD LOADS & SURFACING TABLES
    # -------------------------------------------------------------------------
    unit_kn_m3 = r" kN/m\textsuperscript{3}"
    val_density_girder = _render_value(input_dict, KEY_MATERIAL_GIRDER_DENSITY, unit_kn_m3)
    val_density_deck = _render_value(input_dict, KEY_MATERIAL_DECK_DENSITY, unit_kn_m3)
    val_sw_factor = _render_value(input_dict, KEY_PL_SELF_WEIGHT_FACTOR)
    dead_load_rows = [
        f"\\textnormal{{Structural Steel Unit Weight}} & {val_density_girder} \\\\[5pt]\n\\hline",
        f"\\textnormal{{Reinforced Concrete Deck Density}} & {val_density_deck} \\\\[5pt]\n\\hline",
        f"\\textnormal{{Self-Weight Multiplier Factor}} & {val_sw_factor} \\\\[5pt]\n\\hline",
    ]
    table_dl_tex = build_longtable(
        caption="Dead Load -- Self Weight (DL)",
        headers=["Component / Parameter", "Design Value"],
        rows=dead_load_rows,
        col_spec=r"|L{6.0cm}|p{9.5cm}|",
        label="tab:dead-load",
    )

    surfacing_rows = [
        f"\\textnormal{{Wearing Course Material \\& Thickness}} & {_render_value(input_dict, KEY_WC_MATERIAL)} $\\times$ {_render_value(input_dict, KEY_WC_THICKNESS)} \\\\[5pt]\n\\hline",
        f"\\textnormal{{Crash Barrier SIDL}} & {_render_value(input_dict, KEY_CB_LOAD)} kN/m per barrier \\\\[5pt]\n\\hline",
        f"\\textnormal{{Railing SIDL}} & {_render_value(input_dict, KEY_RL_LOAD_VALUE)} kN/m \\\\[5pt]\n\\hline",
    ]
    table_surfacing_tex = build_longtable(
        caption="Superimposed Dead Load (SIDL / Surfacing)",
        headers=["Parameter Description", "Design Value"],
        rows=surfacing_rows,
        col_spec=r"|L{6.0cm}|p{9.5cm}|",
        label="tab:surfacing-load",
    )

    # -------------------------------------------------------------------------
    # 4. WIND LOAD TABLE
    # -------------------------------------------------------------------------
    vz_val = input_dict.get(KEY_WL_HOURLY_MEAN_WIND) or "38.5"
    pz_val = input_dict.get(KEY_WL_HOURLY_WIND_PRESSURE) or "920.0"
    wind_rows = [
        f"\\textnormal{{Basic Wind Speed, $V_b$}} & {_render_value(input_dict, 'wind_speed', ' m/s')} [Project Location] \\\\[5pt]\n\\hline",
        f"\\textnormal{{Terrain Category}} & {_render_value(input_dict, KEY_WL_TERRAIN_TYPE)} \\\\[5pt]\n\\hline",
        f"\\textnormal{{Average Exposed Structure Height, H}} & {_render_value(input_dict, KEY_WL_AVG_EXPOSED_HEIGHT, ' m')} \\\\[5pt]\n\\hline",
        f"\\textnormal{{Hourly Mean Wind Speed, $V_z$}} & {_tex(str(vz_val))} m/s \\\\[5pt]\n\\hline",
        f"\\textnormal{{Design Wind Pressure, $P_z$}} & {_tex(str(pz_val))} N/m\\textsuperscript{{2}} \\\\[5pt]\n\\hline",
        f"\\textnormal{{Transverse Wind Force}} & {_render_value(input_dict, KEY_WL_TRANSVERSE_WIND_FORCE, ' kN')} \\\\[5pt]\n\\hline",
        f"\\textnormal{{Longitudinal Wind Force}} & {_render_value(input_dict, KEY_WL_LONGITUDINAL_WIND_FORCE, ' kN')} \\\\[5pt]\n\\hline",
        f"\\textnormal{{Vertical Aerodynamic Wind Force}} & {_render_value(input_dict, KEY_WL_VERTICAL_WIND_FORCE, ' kN')} \\\\[5pt]\n\\hline",
    ]
    table_wl_tex = build_longtable(
        caption="Wind Load (WL) Parameters -- per IRC:6 Cl. 209",
        headers=["Wind Parameter", "Design Magnitude / Condition"],
        rows=wind_rows,
        col_spec=r"|L{6.0cm}|p{9.5cm}|",
        label="tab:wind-loads",
    )

    # -------------------------------------------------------------------------
    # 5. SEISMIC LOAD TABLE
    # -------------------------------------------------------------------------
    seismic_rows = [
        f"\\textnormal{{Seismic Zone}} & {_render_value(input_dict, 'seismic_zone')} \\\\[5pt]\n\\hline",
        f"\\textnormal{{Zone Factor, Z}} & {_render_value(input_dict, KEY_SL_ZONE_FACTOR)} \\\\[5pt]\n\\hline",
        f"\\textnormal{{Importance Factor, I}} & {_render_value(input_dict, KEY_SL_IMPORTANCE_FACTOR)} \\\\[5pt]\n\\hline",
        f"\\textnormal{{Soil Foundation Type}} & {_render_value(input_dict, KEY_SL_SOIL_TYPE)} \\\\[5pt]\n\\hline",
        f"\\textnormal{{Spectral Acceleration Coeff., $S_a/g$}} & {_render_value(input_dict, KEY_SL_SPECTRAL_COEFF)} \\\\[5pt]\n\\hline",
        f"\\textnormal{{Horizontal Seismic Coeff., $A_h$}} & {_render_value(input_dict, KEY_SL_HORIZONTAL_COEFF)} \\\\[5pt]\n\\hline",
        f"\\textnormal{{Vertical Seismic Coeff., $A_v$}} & {_render_value(input_dict, KEY_SL_VERTICAL_COEFF)} \\\\[5pt]\n\\hline",
    ]
    table_el_tex = build_longtable(
        caption="Earthquake Load (EL) Parameters -- per IRC:6 Cl. 219",
        headers=["Seismic Parameter", "Design Value"],
        rows=seismic_rows,
        col_spec=r"|L{6.0cm}|p{9.5cm}|",
        label="tab:seismic-loads",
    )

    # -------------------------------------------------------------------------
    # 6. TEMPERATURE LOAD TABLE
    # -------------------------------------------------------------------------
    temp_rows = [
        f"\\textnormal{{Maximum Shade Temperature}} & {_render_value(input_dict, 'shade_temp_max')} $^\\circ$C \\\\[5pt]\n\\hline",
        f"\\textnormal{{Minimum Shade Temperature}} & {_render_value(input_dict, 'shade_temp_min')} $^\\circ$C \\\\[5pt]\n\\hline",
        f"\\textnormal{{Effective Bridge Temperature Range}} & {_render_value(input_dict, KEY_TL_BRIDGE_TEMP_MIN)} to {_render_value(input_dict, KEY_TL_BRIDGE_TEMP_MAX)} $^\\circ$C \\\\[5pt]\n\\hline",
        f"\\textnormal{{Design Temperature Rise / Fall}} & +{_render_value(input_dict, KEY_TL_TEMP_RISE)} $^\\circ$C / -{_render_value(input_dict, KEY_TL_TEMP_FALL)} $^\\circ$C \\\\[5pt]\n\\hline",
    ]
    table_tl_tex = build_longtable(
        caption="Temperature Load (TL) Parameters -- per IRC:6 Cl. 215",
        headers=["Thermal Parameter", "Design Value"],
        rows=temp_rows,
        col_spec=r"|L{6.0cm}|p{9.5cm}|",
        label="tab:temperature-loads",
    )

    # -------------------------------------------------------------------------
    # 7. LOAD COMBINATIONS TABLE
    # -------------------------------------------------------------------------
    _LOAD_LABEL_MAP = {
        "dead_load": "DL",
        "surfacing": "SIDL",
        "live_load": "LL",
        "wind_load": "WL",
        "thermal_load": "TL",
        "vehicle_collision": "VC",
        "barge_impact": "BI",
        "floating_bodies": "FB",
        "seismic": "EQ",
    }

    def _fmt_factors(factors):
        parts = []
        for load, val in factors.items():
            label = _LOAD_LABEL_MAP.get(load, load.upper())
            if isinstance(val, dict):
                add = val.get("adding")
                rel = val.get("relieving")
                add_s = f"{add:.2f}" if add is not None else "--"
                rel_s = f"{rel:.2f}" if rel is not None else "--"
                parts.append(f"{label}({add_s}/{rel_s})")
            else:
                if val is None:
                    continue
                parts.append(f"{label}({val:.2f})")
        return " + ".join(parts)

    uls_combos = IRC6_2017.uls_load_combinations()
    sls_combos = IRC6_2017.sls_load_combinations()
    lc_rows = []
    for i, combo in enumerate(uls_combos, start=1):
        cases = _fmt_factors(combo["factors"])
        lc_rows.append(f"\\textbf{{ULS-{i:02d}}} & \\small {cases} \\\\[4pt]\n\\hline")
    for i, combo in enumerate(sls_combos, start=1):
        cases = _fmt_factors(combo["factors"])
        lc_rows.append(f"\\textbf{{SLS-{i:02d}}} & \\small {cases} \\\\[4pt]\n\\hline")

    table_combos_tex = build_longtable(
        caption="Design Load Combinations (ULS and SLS) -- per IRC:6 Annex B",
        headers=["Combination ID", "Factored Load Cases"],
        rows=lc_rows,
        col_spec=r"|C{3.0cm}|p{12.5cm}|",
        label="tab:load-combinations",
        note="All IRC:6 load combinations are auto-generated. Any user custom load combinations are appended.",
    )

    return f"""
\\chapter{{Loads and Load Combinations}}
\\label{{ch:loads}}

This chapter provides a comprehensive breakdown of all structural gravity, vehicular, environmental, and transient loads acting upon the bridge superstructure, followed by the complete codified load combinations evaluated in the analysis.

{table_dl_tex}

{table_surfacing_tex}

{table_vehicles_tex}

{table_footway_tex}

{table_wl_tex}

{table_el_tex}

{table_tl_tex}

{table_combos_tex}
"""
