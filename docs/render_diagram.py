"""Renders the BullBear LangGraph state diagram as a high-res PNG."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import numpy as np

# ── Canvas ─────────────────────────────────────────────────────────────────
FIG_W, FIG_H = 18, 22
fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
fig.patch.set_facecolor("#0d1117")
ax.set_facecolor("#0d1117")
ax.set_xlim(0, FIG_W)
ax.set_ylim(0, FIG_H)
ax.axis("off")

# ── Palette ─────────────────────────────────────────────────────────────────
C_BG       = "#0d1117"
C_BORDER   = "#30363d"
C_START    = "#00ff88"
C_DATA     = "#4fc3f7"
C_NEWS     = "#ffa726"
C_BULL     = "#00e676"
C_BEAR     = "#ff5252"
C_SYNTH    = "#ce93d8"
C_TEXT     = "#e6edf3"
C_SUBTEXT  = "#8b949e"
C_ARROW    = "#58a6ff"

# ── Helper: rounded box ──────────────────────────────────────────────────────
def node(ax, cx, cy, w, h, title, subtitle, lines, border_color,
         bg="#161b22", title_color=None):
    title_color = title_color or border_color
    rect = FancyBboxPatch(
        (cx - w/2, cy - h/2), w, h,
        boxstyle="round,pad=0.04",
        linewidth=2.5, edgecolor=border_color,
        facecolor=bg, zorder=3,
    )
    ax.add_patch(rect)
    # Glow border effect
    rect2 = FancyBboxPatch(
        (cx - w/2, cy - h/2), w, h,
        boxstyle="round,pad=0.06",
        linewidth=5, edgecolor=border_color,
        facecolor="none", alpha=0.18, zorder=2,
    )
    ax.add_patch(rect2)

    # Title
    ax.text(cx, cy + h/2 - 0.38, title,
            ha="center", va="top", fontsize=13, fontweight="bold",
            color=title_color, zorder=5,
            fontfamily="monospace")
    # Separator line
    sep_y = cy + h/2 - 0.72
    ax.plot([cx - w/2 + 0.18, cx + w/2 - 0.18], [sep_y, sep_y],
            color=border_color, lw=1.2, alpha=0.5, zorder=5)
    # Subtitle
    ax.text(cx, sep_y - 0.18, subtitle,
            ha="center", va="top", fontsize=9.5, color=C_SUBTEXT,
            style="italic", zorder=5, fontfamily="monospace")
    # Body lines
    for i, line in enumerate(lines):
        ax.text(cx, sep_y - 0.55 - i * 0.38, line,
                ha="center", va="top", fontsize=9, color=C_TEXT,
                zorder=5, fontfamily="monospace")


def terminal_node(ax, cx, cy, label, sublabel, color):
    """Pill-shaped start/end node."""
    w, h = 3.4, 0.9
    rect = FancyBboxPatch(
        (cx - w/2, cy - h/2), w, h,
        boxstyle="round,pad=0.18",
        linewidth=2.5, edgecolor=color,
        facecolor="#0a1a0a" if color == C_START else "#1a0a0a",
        zorder=3,
    )
    ax.add_patch(rect)
    rect2 = FancyBboxPatch(
        (cx - w/2, cy - h/2), w, h,
        boxstyle="round,pad=0.28",
        linewidth=5, edgecolor=color,
        facecolor="none", alpha=0.2, zorder=2,
    )
    ax.add_patch(rect2)
    ax.text(cx, cy + 0.08, label,
            ha="center", va="center", fontsize=13, fontweight="bold",
            color=color, zorder=5, fontfamily="monospace")
    ax.text(cx, cy - 0.25, sublabel,
            ha="center", va="center", fontsize=8.5, color=C_SUBTEXT,
            zorder=5, fontfamily="monospace")


def arrow(ax, x0, y0, x1, y1, label="", color=C_ARROW, style="arc3,rad=0.0"):
    ax.annotate("",
        xy=(x1, y1), xytext=(x0, y0),
        arrowprops=dict(
            arrowstyle="-|>",
            color=color,
            lw=1.8,
            connectionstyle=style,
        ), zorder=4,
    )
    if label:
        mx, my = (x0+x1)/2, (y0+y1)/2
        ax.text(mx + 0.12, my, label, ha="left", va="center",
                fontsize=8, color=C_SUBTEXT, zorder=6, fontfamily="monospace",
                bbox=dict(fc=C_BG, ec="none", pad=1.5))


# ── Layout positions (cx, cy) ────────────────────────────────────────────────
#  Title
ax.text(FIG_W/2, 21.3, "BULLBEAR", ha="center", va="center",
        fontsize=40, fontweight="bold", color=C_START,
        fontfamily="monospace",
        path_effects=[pe.withStroke(linewidth=8, foreground="#003322")])
ax.text(FIG_W/2, 20.7, "LangGraph Multi-Agent Workflow", ha="center",
        va="center", fontsize=14, color=C_SUBTEXT, fontfamily="monospace")
ax.plot([1.5, FIG_W-1.5], [20.38, 20.38], color=C_BORDER, lw=1)

# START
terminal_node(ax, 9, 19.6, ">> START", "Input: ticker symbol", C_START)

# fetch_stock_data  (left branch)
NW, NH = 6.4, 2.6
node(ax, 5.2, 16.0, NW, NH,
     "[1] fetch_stock_data", "yfinance  .  async  .  ~2s",
     ["yfinance.history(period='6mo')",
      "Returns 6-month daily OHLCV",
      "Validates ticker exists"],
     C_DATA)

# news_analyst  (right branch)
node(ax, 12.8, 16.0, NW, NH,
     "[2] news_analyst", "yfinance + LLM  .  ~8s",
     ["Fetches top-15 news headlines",
      "LLM identifies themes & catalysts",
      "Outputs: consensus sentiment"],
     C_NEWS)

# bull_analyst  (left)
node(ax, 5.2, 11.6, NW, 3.0,
     "[3] bull_analyst", "LLM  .  ~18s",
     ["Input: 60-day OHLCV + news",
      "Price structure: HH/HL, breakouts",
      "Institutional accumulation signals",
      "4-6 week upside price target"],
     C_BULL)

# bear_analyst  (right)
node(ax, 12.8, 11.6, NW, 3.0,
     "[4] bear_analyst", "LLM  .  ~18s",
     ["Input: 60-day OHLCV + news",
      "Price structure: LH/LL, breakdowns",
      "Distribution & liquidation signals",
      "4-6 week downside price target"],
     C_BEAR)

# financial_analyst  (centre)
node(ax, 9, 6.5, 8.4, 3.4,
     "[5] financial_analyst  (CIO)", "LLM  .  ~12s",
     ["Reconciles Bull vs Bear thesis",
      "Plain-English executive summary",
      "Risk-reward  &  safety levels",
      "Short & long-term action plan",
      "Formatted investment memo"],
     C_SYNTH, bg="#130020")

# END
terminal_node(ax, 9, 2.8, "[ END ]", "Output: analyses + ratings (JSON)", "#ff5252")

# ── Arrows ───────────────────────────────────────────────────────────────────
# START → fetch
arrow(ax, 7.3, 19.15, 5.9, 17.3, color=C_DATA,  style="arc3,rad=0.15")
# START → news
arrow(ax, 10.7, 19.15, 12.1, 17.3, color=C_NEWS, style="arc3,rad=-0.15")

# fetch → bull
arrow(ax, 5.2, 14.7, 5.2, 13.1,
      label="time_series_data", color=C_DATA)
# fetch → bear
arrow(ax, 7.2, 14.7, 10.5, 13.1,
      color=C_DATA, style="arc3,rad=-0.25")

# news → bull
arrow(ax, 10.5, 14.7, 7.5, 13.1,
      color=C_NEWS, style="arc3,rad=0.25")
# news → bear
arrow(ax, 12.8, 14.7, 12.8, 13.1,
      label="news_analysis", color=C_NEWS)

# bull → financial
arrow(ax, 5.8, 10.1, 7.2, 8.2,
      label="bull_analysis + rating", color=C_BULL, style="arc3,rad=0.2")
# bear → financial
arrow(ax, 12.2, 10.1, 10.8, 8.2,
      label="bear_analysis + rating", color=C_BEAR, style="arc3,rad=-0.2")

# financial → END
arrow(ax, 9, 4.8, 9, 3.25,
      label="financial_analysis + rating", color=C_SYNTH)

# ── Parallel-execution badge ──────────────────────────────────────────────────
for cx in [5.2, 12.8]:
    ax.text(cx, 18.0, "⟵ parallel ⟶" if cx == 9 else ("parallel" if cx == 12.8 else "parallel"),
            ha="center", va="center", fontsize=8, color=C_SUBTEXT,
            fontfamily="monospace")

ax.annotate("", xy=(12.2, 18.0), xytext=(6.4, 18.0),
            arrowprops=dict(arrowstyle="<->", color=C_SUBTEXT, lw=1.2,
                            linestyle="dashed"))
ax.text(9, 18.13, "parallel fork", ha="center", va="bottom",
        fontsize=8.5, color=C_SUBTEXT, fontfamily="monospace",
        style="italic")

for cx in [5.2, 12.8]:
    ax.annotate("", xy=(12.2, 13.55), xytext=(6.4, 13.55),
                arrowprops=dict(arrowstyle="<->", color=C_SUBTEXT, lw=1.2,
                                linestyle="dashed"))
    break
ax.text(9, 13.68, "parallel fanout", ha="center", va="bottom",
        fontsize=8.5, color=C_SUBTEXT, fontfamily="monospace",
        style="italic")

# ── Legend ───────────────────────────────────────────────────────────────────
legend_x, legend_y = 0.7, 5.8
ax.text(legend_x, legend_y, "Legend", fontsize=10, fontweight="bold",
        color=C_TEXT, fontfamily="monospace")
items = [
    (C_DATA,  "Data fetch node  (yfinance)"),
    (C_NEWS,  "News & sentiment node  (LLM)"),
    (C_BULL,  "Bull analyst node  (LLM)"),
    (C_BEAR,  "Bear analyst node  (LLM)"),
    (C_SYNTH, "Synthesis node  (LLM CIO)"),
]
for i, (c, label) in enumerate(items):
    y = legend_y - 0.48 - i * 0.45
    rect = FancyBboxPatch((legend_x, y - 0.14), 0.36, 0.3,
                          boxstyle="round,pad=0.03",
                          lw=1.5, edgecolor=c, facecolor=C_BG, zorder=5)
    ax.add_patch(rect)
    ax.text(legend_x + 0.52, y + 0.01, label,
            ha="left", va="center", fontsize=9, color=C_SUBTEXT,
            fontfamily="monospace")


# ── Footer ───────────────────────────────────────────────────────────────────
ax.plot([1.0, FIG_W-1.0], [1.85, 1.85], color=C_BORDER, lw=0.8)
ax.text(FIG_W/2, 1.55,
        "Built with  LangGraph  |  FastAPI  |  LLM  |  yfinance",
        ha="center", va="center", fontsize=9, color=C_SUBTEXT,
        fontfamily="monospace")
ax.text(FIG_W/2, 1.15,
        "Not financial advice -- for educational purposes only",
        ha="center", va="center", fontsize=8.5, color="#6e4040",
        fontfamily="monospace")

# ── Save ─────────────────────────────────────────────────────────────────────
out = "docs/bullbear_state_diagram.png"
fig.savefig(out, dpi=180, bbox_inches="tight",
            facecolor=fig.get_facecolor())
print(f"Saved → {out}")
plt.close(fig)
