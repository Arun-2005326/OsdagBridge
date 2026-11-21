"""
styles.py
---------
Centralized design system and single source of truth for OsdagBridge design reports.
Provides color palettes, typography specifications, document geometry, table configurations,
and Matplotlib styling presets.
"""

from typing import Dict, Any, List


# =============================================================================
# COLOR PALETTE
# =============================================================================

# Brand and Accent Colors
COLOR_OSDAG_GREEN = "#91B014"
COLOR_OSDAG_GREEN_DARK = "#6D850E"
COLOR_NAVY_PRIMARY = "#1B365D"
COLOR_SLATE_DARK = "#2C3E50"
COLOR_GREY_TEXT = "#4A4A4A"
COLOR_GREY_LIGHT = "#F8F9FA"
COLOR_GREY_BORDER = "#D5D8DC"
COLOR_HEADER_BG = "#EAEDED"

# Engineering Status Colors
COLOR_STATUS_PASS = "#27AE60"    # Forest / Emerald Green (UR <= 1.0)
COLOR_STATUS_WARN = "#E67E22"    # Amber / Orange (0.90 <= UR < 1.0)
COLOR_STATUS_FAIL = "#C0392B"    # Strong Crimson / Red (UR > 1.0)
COLOR_STATUS_NA = "#7F8C8D"      # Muted Grey for N/A or unapplicable checks

# Matplotlib Chart Color Cycles
CHART_BAR_PASS = "#2ECC71"
CHART_BAR_FAIL = "#E74C3C"
CHART_THRESHOLD_LINE = "#C0392B"
CHART_STEEL_SERIES = ["#2980B9", "#3498DB", "#5DADE2", "#85C1E9"]
CHART_CONCRETE_SERIES = ["#16A085", "#E67E22"]


# =============================================================================
# DOCUMENT GEOMETRY & PAGE LAYOUT
# =============================================================================

# Centralized geometry options for LaTeX \usepackage[...]{geometry}
# Generous bottom margin (30mm) and footskip (15mm) directly prevent footer overlapping
PAGE_GEOMETRY_OPTIONS = (
    "a4paper, top=25mm, bottom=32mm, left=20mm, right=20mm, headheight=16pt, footskip=14mm"
)

# Table layout dimensions
TABLE_TABCOLSEP = "5.0pt"
TABLE_ARRAYSTRETCH = 1.22
TABLE_LTPRE = "2pt"
TABLE_LTPOST = "6pt"


# =============================================================================
# LATEX ENVIRONMENT & PREAMBLE DEFINITIONS
# =============================================================================

def get_latex_color_definitions() -> str:
    """Return LaTeX \\definecolor statements for inclusion in document preamble."""
    return r"""
% --- Centralized OsdagBridge Color Definitions ---
\definecolor{osdagGreen}{HTML}{91B014}
\definecolor{osdagGreenDark}{HTML}{6D850E}
\definecolor{navyPrimary}{HTML}{1B365D}
\definecolor{slateDark}{HTML}{2C3E50}
\definecolor{greyBorder}{HTML}{D5D8DC}
\definecolor{headerBg}{HTML}{EAEDED}
\definecolor{rowLight}{HTML}{F8F9FA}
\definecolor{passGreen}{HTML}{27AE60}
\definecolor{warnOrange}{HTML}{E67E22}
\definecolor{failRed}{HTML}{C0392B}
\definecolor{mutedGrey}{HTML}{7F8C8D}
"""


def get_latex_column_types() -> str:
    """Return custom LaTeX column type definitions with auto text wrapping."""
    return r"""
% --- Compatibility for colortbl / array in MikTeX ---
\makeatletter
\providecommand{\insert@pcolumn}{\insert@column}
\providecommand{\UseTaggingSocket}[1]{}
\providecommand{\CT@tbl@gdecr@row@count}{}
\makeatother
\ExplSyntaxOn
\cs_if_exist:NF \tbl_gdecr_row_count: { \cs_new:Nn \tbl_gdecr_row_count: {} }
\cs_if_exist:NF \tag_mc_end: { \cs_new:Nn \tag_mc_end: {} }
\ExplSyntaxOff

% --- Custom Column Types for LongTable ---
\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}
\newcolumntype{C}[1]{>{\centering\arraybackslash}p{#1}}
\newcolumntype{R}[1]{>{\raggedleft\arraybackslash}p{#1}}
"""


def get_header_footer_setup() -> str:
    """Return fancyhdr configuration with safe spacing to avoid overlap."""
    return r"""
% --- Header and Footer Styling (fancyhdr) ---
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0.5pt}
\renewcommand{\footrulewidth}{0.4pt}
\renewcommand{\headrule}{\hbox to\headwidth{\color{greyBorder}\leaders\hrule height \headrulewidth\hfill}}
\renewcommand{\footrule}{\hbox to\headwidth{\color{greyBorder}\leaders\hrule height \footrulewidth\hfill}}

\fancyhead[L]{\small\color{slateDark}\textbf{\ReportProjectName{}} \textbar{} \ReportJobNumber{}}
\fancyhead[R]{\small\color{slateDark}\ReportDate{} \textbar{} \ReportVersion{}}
\fancyfoot[L]{\footnotesize\color{mutedGrey}\textbf{OsdagBridge} -- Short-Span Steel Bridge Design}
\fancyfoot[C]{\footnotesize\color{mutedGrey}\thepage\ of \pageref{LastPage}}
\fancyfoot[R]{\footnotesize\color{osdagGreenDark}\textbf{FOSSEE, IIT Bombay}}
"""


# =============================================================================
# DATA VISUALIZATION / MATPLOTLIB THEME
# =============================================================================

def get_matplotlib_rc_params() -> Dict[str, Any]:
    """Return dictionary of Matplotlib rcParams for publication-grade report charts."""
    return {
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
        "font.size": 9.5,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
        "axes.labelsize": 10,
        "axes.labelweight": "semibold",
        "axes.edgecolor": COLOR_GREY_BORDER,
        "axes.linewidth": 0.8,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": "#E5E7E9",
        "grid.linestyle": "--",
        "grid.linewidth": 0.6,
        "grid.alpha": 0.8,
        "legend.fontsize": 8.5,
        "legend.frameon": True,
        "legend.edgecolor": COLOR_GREY_BORDER,
        "xtick.labelsize": 8.5,
        "ytick.labelsize": 8.5,
        "figure.facecolor": "white",
        "figure.autolayout": True,
    }

