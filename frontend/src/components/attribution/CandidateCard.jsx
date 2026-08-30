import React from 'react';
import StatusChip from '../common/StatusChip';
import Button from '../common/Button';

export default function CandidateCard({
  vessel,
  isSelected,
  onSelect,
  onInspectProfile,
  onViewGIS
}) {
  const isPrimary = vessel.rank === 1;

  return (
    <div
      onClick={onSelect}
      className={`p-5 rounded-lg border transition-all cursor-pointer flex flex-col justify-between ${
        isSelected
          ? 'bg-surface-container-lowest border-2 border-primary shadow-md ring-2 ring-primary/10'
          : isPrimary
          ? 'bg-surface-container-lowest border-2 border-secondary/40 hover:border-secondary'
          : 'bg-surface-container-low border-outline-variant hover:border-primary/50'
      }`}
    >
      <div>
        {/* Top Header Row */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <span
              className={`w-7 h-7 rounded-full flex items-center justify-center font-bold text-label-sm font-mono ${
                isPrimary
                  ? 'bg-error-container text-on-error-container'
                  : 'bg-surface-container-high text-on-surface'
              }`}
            >
              #{vessel.rank}
            </span>
            <span className="text-[12px] font-semibold text-on-surface-variant">
              {vessel.flag} ({vessel.flagCode})
            </span>
          </div>

          <StatusChip
            status={isPrimary ? 'Critical' : vessel.riskCategory}
            label={`${vessel.confidence}% Match`}
          />
        </div>

        {/* Vessel Name & Type */}
        <h4 className="text-title-lg font-bold text-primary mb-1">{vessel.name}</h4>
        <p className="text-label-sm text-on-surface-variant mb-3">
          {vessel.type} • {vessel.dwt?.toLocaleString()} DWT
        </p>

        {/* Telemetry / Event Summary */}
        <div className="p-3 bg-surface-container rounded border border-outline-variant/60 text-[12px] text-on-surface leading-relaxed mb-3">
          <strong className="text-primary block text-[11px] uppercase tracking-wider mb-0.5">
            AIS Event Log:
          </strong>
          {vessel.aisEvent}
        </div>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-2 gap-2 text-[12px] border-t border-outline-variant/40 pt-2 mb-4">
          <div>
            <span className="text-on-surface-variant block text-[11px]">IMO / MMSI</span>
            <strong className="text-primary font-mono">{vessel.imo} / {vessel.mmsi}</strong>
          </div>
          <div>
            <span className="text-on-surface-variant block text-[11px]">Proximity</span>
            <strong className="text-primary font-mono">{vessel.factors?.spatialDistanceKm} km</strong>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center gap-2 pt-2 border-t border-outline-variant/50">
        <Button
          size="sm"
          variant="primary"
          icon="directions_boat"
          onClick={(e) => {
            e.stopPropagation();
            onInspectProfile(vessel.name);
          }}
          className="flex-1"
        >
          Forensic Profile
        </Button>
        <Button
          size="sm"
          variant="teal"
          icon="map"
          onClick={(e) => {
            e.stopPropagation();
            onViewGIS();
          }}
          className="flex-1"
        >
          View on Map
        </Button>
      </div>
    </div>
  );
}
