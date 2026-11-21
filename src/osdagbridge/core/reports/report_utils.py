"""
report_utils.py
---------------
Utility helpers for LaTeX report generation in OsdagBridge.
Provides safe LaTeX escaping, value formatting, robust LongTable generation with repeated headers,
figure embedding, and status badge rendering.
"""

from typing import List, Optional, Tuple, Dict, Any
from osdagbridge.core.utils.common import (
    KEY_MP_GD_MEMBER_ID,
    KEY_MP_GD_SELECT_GIRDER,
    KEY_MP_GIRDER_DEPTH,
    KEY_TS_NO_OF_GIRDERS,
)
from osdagbridge.core.reports.styles import (
    COLOR_STATUS_PASS,
    COLOR_STATUS_WARN,
    COLOR_STATUS_FAIL,
    COLOR_STATUS_NA,
)


def _tex(value) -> str:
    """Escape a Python value for safe LaTeX embedding."""
    s = str(value) if value is not None else ""
    if not s:
        return r""
    # Normalise non-ASCII glyphs from section designations (e.g. "∠ 100 ⅹ 100ⅹ 10")
    # that pdflatex cannot render.
    for uni, ascii_ in [("∠", "L"), ("ⅹ", "x"), ("×", "x"), ("≤", r"$\le$"), ("≥", r"$\ge$"), ("±", r"$\pm$")]:
        s = s.replace(uni, ascii_)
    s = s.replace("\\", r"\textbackslash{}")
    for ch, esc in [
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("_", r"\_\allowbreak{}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\^{}"),
    ]:
        s = s.replace(ch, esc)
    s = s.replace(":", r":\allowbreak{}")
    return s


def _render_value(source_dict: dict, key: str, unit: str = "") -> str:
    """Extract a value from dictionary and render it safely escaped with an optional unit."""
    val = source_dict.get(key)
    if val in ("", None):
        return ""
    return _tex(val) + unit


def render_status_badge(status_text: str) -> str:
    """
    Render a clean, color-coded status badge for PASS, WARN, FAIL in tables.
    """
    clean = str(status_text).strip().upper()
    if "PASS" in clean or "OK" in clean:
        return r"\textbf{\textcolor{passGreen}{PASS}}"
    elif "WARN" in clean:
        return r"\textbf{\textcolor{warnOrange}{WARN}}"
    elif "FAIL" in clean:
        return r"\textbf{\textcolor{failRed}{FAIL}}"
    elif clean in ("N/A", "---", "--"):
        return r"\textcolor{mutedGrey}{---}"
    return _tex(status_text)


def build_longtable(
    caption: str,
    headers: List[str],
    rows: List[str],
    col_spec: str,
    label: Optional[str] = None,
    note: Optional[str] = None,
    num_cols: Optional[int] = None,
    pre_vspace: str = "0.8em",
) -> str:
    """
    Construct a production-grade LongTable environment with:
      - First-page header (\\endfirsthead) with caption
      - Continuation-page header (\\endhead) with 'Continued from previous page' note
      - Page footer (\\endfoot) with 'Continued on next page' note
      - Final page footer (\\endlastfoot)
      - Row coloring and robust borders
    """
    n_cols = num_cols if num_cols is not None else len(headers)
    lbl_tex = f"\\label{{{label}}}" if label else ""
    cap_line = f"\\caption{{\\textbf{{{caption}}}}}{lbl_tex}\\\\"
    header_line = " & ".join([f"\\textbf{{{_tex(h)}}}" for h in headers]) + r" \\[6pt]"

    # Continuation banner spanning all columns
    cont_head_banner = (
        r"\multicolumn{"
        + str(n_cols)
        + r"}{c}{\small\itshape\color{slateDark}\textbf{"
        + _tex(caption)
        + r"} (Continued from previous page)} \\[4pt]"
    )
    cont_foot_banner = (
        r"\multicolumn{"
        + str(n_cols)
        + r"}{r}{\footnotesize\itshape\color{mutedGrey}Continued on next page\dots} \\"
    )

    body = "\n".join(rows)
    note_str = f"\n\\noindent\\textit{{\\footnotesize Note: {note}}}\n" if note else ""

    tex = f"""
\\needspace{{4\\baselineskip}}
\\vspace{{{pre_vspace}}}
\\begin{{longtable}}{{{col_spec}}}
{cap_line}
\\hline
\\rowcolor{{headerBg}}
{header_line}
\\hline
\\endfirsthead

\\hline
\\rowcolor{{headerBg}}
{cont_head_banner}
\\hline
{header_line}
\\hline
\\endhead

\\hline
{cont_foot_banner}
\\endfoot

\\hline
\\endlastfoot

{body}
\\end{{longtable}}
{note_str}
"""
    return tex


def get_girder_entries(input_dict: dict) -> List[Tuple[str, str]]:
    """Retrieve all girder labels and member IDs from backend keys."""
    n = int(input_dict.get(KEY_TS_NO_OF_GIRDERS, 0))
    entries = []
    for i in range(1, n + 1):
        lbl = input_dict.get(f"{KEY_MP_GD_SELECT_GIRDER}.G{i}", f"Girder {i}")
        mid = input_dict.get(f"{KEY_MP_GD_MEMBER_ID}.G{i}.M1", f"G{i}M1")
        entries.append((lbl, mid))
    return entries


def _fig_or_placeholder(path: Optional[str], caption: str, width: str = r"0.9\textwidth") -> str:
    """Embed figure if path is provided, else render formatted placeholder box."""
    if path:
        p = path.replace("\\", "/")
        return (
            r"\begin{figure}[H]" + "\n"
            r"\centering" + "\n"
            r"\includegraphics[width=" + width + "]{" + p + "}\n"
            r"\caption*{" + caption + "}\n"
            r"\end{figure}"
        )
    return (
        r"\begin{figure}[H]" + "\n"
        r"\centering" + "\n"
        r"\fbox{\parbox{0.97\textwidth}{" + "\n"
        r"\centering\vspace{1em}\textit{[ PLACEHOLDER: " + caption + r" ]}\vspace{1em}" + "\n"
        r"}}" + "\n"
        r"\caption*{" + caption + "}\n"
        r"\end{figure}"
    )


def _fig_embed(path: Optional[str], caption: str, width: str = r"\textwidth", height: Optional[str] = None) -> str:
    """Embed a real figure when path is provided; otherwise use an fbox placeholder."""
    if path:
        p = path.replace("\\", "/")
        opts = "width=" + width
        if height:
            opts += ",height=" + height + ",keepaspectratio"
        return (
            r"\begin{figure}[H]" + "\n"
            r"\vspace{-0.3em}" + "\n"
            r"\centering" + "\n"
            r"\includegraphics[" + opts + "]{" + p + "}\n"
            r"\vspace{0.4em}" + "\n"
            r"\caption*{\small\textbf{" + caption + "}}\n"
            r"\vspace{-0.3em}" + "\n"
            r"\end{figure}"
        )
    return (
        r"\noindent\fbox{\parbox{0.97\textwidth}{" + "\n"
        r"\centering\vspace{1em}\textit{[ PLACEHOLDER: " + caption + r" ]}\vspace{1em}" + "\n"
        r"}}"
    )
