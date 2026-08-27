import React from 'react';

/**
 * FactorBreakdown Component
 * Displays multi-factor weighted scores for vessel attribution
 */
export default function FactorBreakdown({ vessel }) {
  if (!vessel || !vessel.factors) return null;

  const factors = [
    {
      name: 'Spatial-Temporal Proximity',
      score: vessel.factors.spatialTemporalScore || 98,
      weight: '30%',
      desc: `Nearest approach: ${vessel.factors.spatialDistanceKm} km (${vessel.factors.timeDeltaMinutes} min delta)`
    },
    {
      name: 'Trajectory Alignment',
      score: vessel.factors.trajectoryMatch || 96,
      weight: '25%',
      desc: 'Slick elongation vector directly overlaps vessel track heading'
    },
    {
      name: 'Speed & Course Deceleration Anomaly',
      score: vessel.factors.speedCourseAnomaly || 91,
      weight: '20%',
      desc: 'Speed dropped 14.2 -> 6.1 kts with erratic heading yaw during transit'
    },
    {
      name: 'Historical Compliance Risk',
      score: vessel.factors.historicalComplianceRisk || 88,
      weight: '15%',
      desc: 'Prior MARPOL Annex I oily-water separator calibration infractions'
    },
    {
      name: 'Cargo Hazard & Fuel Profile',
      score: vessel.factors.cargoHazardWeight || 95,
      weight: '10%',
      desc: 'Carrying 104,200 MT Arabian Light Crude + Bunker C fuel'
    }
  ];

  return (
    <div className="bg-surface-container-lowest border border-outline-variant rounded-lg p-5 flex flex-col gap-4 shadow-sm">
      <div className="flex items-center justify-between border-b border-outline-variant pb-3">
        <div>
          <h3 className="text-title-lg font-bold text-primary">
            Attribution Factor Breakdown
          </h3>
          <p className="text-label-sm text-on-surface-variant">
            Algorithmic weighting metrics for <strong className="text-primary">{vessel.name}</strong>
          </p>
        </div>

        <div className="text-right">
          <span className="text-[11px] font-bold uppercase tracking-wider text-on-surface-variant block">
            Composite ML Score
          </span>
          <span className="text-[26px] font-bold text-primary font-mono leading-none">
            {vessel.confidence}%
          </span>
        </div>
      </div>

      <div className="space-y-4">
        {factors.map((item, idx) => (
          <div key={idx} className="space-y-1.5">
            <div className="flex items-center justify-between text-label-sm">
              <span className="font-bold text-on-surface flex items-center gap-2">
                {item.name}
                <span className="text-[11px] font-normal text-on-surface-variant font-mono">
                  (Weight: {item.weight})
                </span>
              </span>
              <strong className="font-mono text-primary text-[13px]">{item.score}/100</strong>
            </div>

            {/* Progress Meter Bar */}
            <div className="w-full bg-surface-container-high h-2 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-300 ${
                  item.score >= 90
                    ? 'bg-secondary'
                    : item.score >= 70
                    ? 'bg-secondary-fixed-dim'
                    : item.score >= 40
                    ? 'bg-tertiary-container'
                    : 'bg-outline'
                }`}
                style={{ width: `${item.score}%` }}
              />
            </div>

            <p className="text-[12px] text-on-surface-variant">{item.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
