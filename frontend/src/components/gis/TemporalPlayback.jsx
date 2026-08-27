import React, { useState, useEffect } from 'react';

/**
 * TemporalPlayback Component
 * Scrubbing and timeline animation controller for historical vessel tracks vs slick observation
 */
export default function TemporalPlayback({
  timelinePoints = [],
  currentIndex = 3,
  onChangeIndex
}) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);

  useEffect(() => {
    let timer;
    if (isPlaying) {
      timer = setInterval(() => {
        onChangeIndex((prev) => {
          if (prev >= timelinePoints.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, 1500 / playbackSpeed);
    }
    return () => clearInterval(timer);
  }, [isPlaying, playbackSpeed, timelinePoints.length, onChangeIndex]);

  const currentPoint = timelinePoints[currentIndex] || {};

  return (
    <div className="bg-surface-container-lowest border border-outline-variant rounded-lg p-4 shadow-sm flex flex-col gap-3">
      {/* Top Header & Current Point Telemetry */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-outline-variant pb-2">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-secondary text-[20px]">history_toggle_off</span>
          <span className="text-label-sm font-bold text-primary uppercase tracking-wider">
            Spatial-Temporal AIS Playback
          </span>
        </div>

        <div className="flex items-center gap-2 text-label-sm">
          <span className="text-on-surface-variant">Timestamp:</span>
          <strong className="text-primary font-mono bg-surface-container-high px-2 py-0.5 rounded border border-outline-variant">
            {currentPoint.time || '2026-08-26 23:15 UTC'}
          </strong>
        </div>
      </div>

      {/* Scrubber Range Slider */}
      <div className="flex flex-col gap-1.5">
        <input
          type="range"
          min="0"
          max={Math.max(0, timelinePoints.length - 1)}
          value={currentIndex}
          onChange={(e) => onChangeIndex(parseInt(e.target.value, 10))}
          className="w-full h-2 bg-surface-container-high rounded-lg appearance-none cursor-pointer accent-primary"
        />

        <div className="flex justify-between text-[10px] text-on-surface-variant font-mono">
          <span>{timelinePoints[0]?.time?.substring(11, 16) || '21:00'} (Approach)</span>
          <span className="text-error font-bold font-sans">
            {currentPoint.speed ? `Speed: ${currentPoint.speed} kts | Hdg: ${currentPoint.heading}°` : 'Discharge Zone'}
          </span>
          <span>{timelinePoints[timelinePoints.length - 1]?.time?.substring(11, 16) || '02:00'} (Transit)</span>
        </div>
      </div>

      {/* Transport Controls (Play/Pause, Step Back, Step Forward, Speed) */}
      <div className="flex items-center justify-between pt-1">
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => onChangeIndex(prev => Math.max(0, prev - 1))}
            disabled={currentIndex === 0}
            className="p-1.5 rounded border border-outline-variant bg-surface-container-low hover:bg-surface-container disabled:opacity-40 transition-colors"
            title="Step Previous Waypoint"
          >
            <span className="material-symbols-outlined text-[18px]">skip_previous</span>
          </button>

          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="px-3 py-1.5 rounded bg-primary-container text-on-primary font-bold text-label-sm hover:bg-primary transition-colors flex items-center gap-1"
          >
            <span className="material-symbols-outlined text-[18px]">
              {isPlaying ? 'pause' : 'play_arrow'}
            </span>
            <span>{isPlaying ? 'Pause' : 'Play Timeline'}</span>
          </button>

          <button
            onClick={() => onChangeIndex(prev => Math.min(timelinePoints.length - 1, prev + 1))}
            disabled={currentIndex === timelinePoints.length - 1}
            className="p-1.5 rounded border border-outline-variant bg-surface-container-low hover:bg-surface-container disabled:opacity-40 transition-colors"
            title="Step Next Waypoint"
          >
            <span className="material-symbols-outlined text-[18px]">skip_next</span>
          </button>
        </div>

        {/* Speed Selector */}
        <div className="flex items-center gap-1">
          <span className="text-[11px] text-on-surface-variant font-semibold mr-1">Speed:</span>
          {[1, 2, 5].map((spd) => (
            <button
              key={spd}
              onClick={() => setPlaybackSpeed(spd)}
              className={`px-2 py-0.5 rounded text-[11px] font-bold transition-colors ${
                playbackSpeed === spd
                  ? 'bg-secondary text-on-secondary'
                  : 'bg-surface-container-high text-on-surface-variant hover:text-on-surface'
              }`}
            >
              {spd}x
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
