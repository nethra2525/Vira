"use client";

/**
 * VIRA's signature visual element: "The Route."
 * A topographic contour-line path from a candidate's current skills to a
 * target role, with waypoints representing the skills to learn along the
 * way. This mirrors the product's core Growth Path feature directly,
 * rather than a generic AI orb.
 */
export default function RouteVisual({ compact = false }: { compact?: boolean }) {
  const height = compact ? 220 : 380;

  return (
    <svg
      viewBox="0 0 640 380"
      width="100%"
      height={height}
      className="overflow-visible"
      role="img"
      aria-label="An illustrated path from a candidate's current skills to a target role, with waypoints marking skills to grow"
    >
      {/* Contour rings, evoking a topographic map */}
      {[70, 110, 150, 190].map((r, i) => (
        <ellipse
          key={r}
          cx="150"
          cy="300"
          rx={r * 1.4}
          ry={r}
          fill="none"
          stroke="#2E3745"
          strokeWidth="1"
          opacity={0.5 - i * 0.09}
        />
      ))}
      {[60, 100, 140].map((r, i) => (
        <ellipse
          key={r}
          cx="520"
          cy="90"
          rx={r * 1.3}
          ry={r}
          fill="none"
          stroke="#2E3745"
          strokeWidth="1"
          opacity={0.45 - i * 0.1}
        />
      ))}

      {/* The route itself */}
      <path
        d="M 150 300 C 230 260, 260 220, 320 210 S 420 160, 460 130 S 500 100, 520 90"
        fill="none"
        stroke="#C9A227"
        strokeWidth="2.5"
        strokeDasharray="2 10"
        strokeLinecap="round"
      >
        <animate attributeName="stroke-dashoffset" from="0" to="-24" dur="1.8s" repeatCount="indefinite" />
      </path>

      {/* Start: current skills */}
      <circle cx="150" cy="300" r="7" fill="#1B212B" stroke="#4F7A5A" strokeWidth="2.5" />
      <text x="150" y="326" textAnchor="middle" fontSize="12" fill="#A9AFBD" fontFamily="Inter, ui-sans-serif, system-ui, sans-serif">
        Current skills
      </text>

      {/* Waypoints: skills to grow */}
      <g>
        <circle cx="320" cy="210" r="5.5" fill="#14181F" stroke="#C9A227" strokeWidth="2" />
        <text x="320" y="196" textAnchor="middle" fontSize="11" fill="#C9A227" fontFamily="Inter, ui-sans-serif, system-ui, sans-serif">
          + Data Viz
        </text>
      </g>
      <g>
        <circle cx="460" cy="130" r="5.5" fill="#14181F" stroke="#C9A227" strokeWidth="2" />
        <text x="460" y="116" textAnchor="middle" fontSize="11" fill="#C9A227" fontFamily="Inter, ui-sans-serif, system-ui, sans-serif">
          + Power BI
        </text>
      </g>

      {/* End: target role */}
      <circle cx="520" cy="90" r="8" fill="#C9A227" />
      <circle cx="520" cy="90" r="14" fill="none" stroke="#C9A227" strokeWidth="1.5" opacity="0.5">
        <animate attributeName="r" values="10;18;10" dur="2.4s" repeatCount="indefinite" />
        <animate attributeName="opacity" values="0.6;0;0.6" dur="2.4s" repeatCount="indefinite" />
      </circle>
      <text x="520" y="66" textAnchor="middle" fontSize="12.5" fill="#EFEBE2" fontFamily="'Space Grotesk', ui-sans-serif, system-ui, sans-serif" fontWeight="600">
        Data Analyst
      </text>
    </svg>
  );
}
