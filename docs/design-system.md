# VIRA Design System

## Concept
VIRA's core feature is the **Growth Path**: a concrete route from a candidate's
current skills to a target role. The visual identity is built around that idea
literally, rather than a generic "AI orb." The signature element — **"The Route"**
(`components/vira/RouteVisual.tsx`) — is a topographic contour-line path with
waypoints marking skills to learn, reused across the landing page and the Growth
Path screen.

## Palette
| Token | Hex | Use |
|---|---|---|
| `ink` | `#14181F` | Primary background (graphite, not pure black) |
| `ink-surface` | `#1B212B` | Card/panel surfaces |
| `ink-raised` | `#222A36` | Inputs, progress track backgrounds |
| `ink-border` | `#2E3745` | Hairline borders |
| `paper` | `#EFEBE2` | Primary text on dark surfaces |
| `gold` | `#C9A227` | Primary accent — CTAs, scores, the Route's waypoints |
| `sage` | `#4F7A5A` | Growth / positive signals (strengths, improvement) |
| `rust` | `#B5563A` | Gaps / missing requirements — used sparingly, never as a primary accent |
| `mist` | `#A9AFBD` | Secondary text |

This intentionally avoids the two most common "AI product" defaults: a cream +
terracotta editorial palette, and a near-black + neon-purple gradient palette.

## Typography
- **Display** (`font-display`): Space Grotesk — headlines, section titles
- **Body** (`font-body`): Inter — everything else
- **Data** (`font-mono`): IBM Plex Mono — scores, percentages, anything evidence-based

(In this sandbox, system-font fallbacks are used at build time due to no outbound
network access to Google Fonts — see the README for restoring `next/font/google`.)

## Shape & elevation
- 14px card radius (`rounded-card`), pill-shaped buttons/badges
- Two shadow levels: `shadow-soft` (cards) and `shadow-lift` (modals/popovers)
- No harsh borders — hairline `ink-border` only

## Components
Button, Card, Badge, Input/Textarea/Label, ScoreBar, OverallScoreRing, Skeleton,
EmptyState, ErrorState — all in `components/ui/`. All match colors are driven by
score thresholds (gold/sage/rust) rather than a single fixed accent, so the UI
reads as evidence-based rather than decorative.
