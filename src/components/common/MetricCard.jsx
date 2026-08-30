import React from 'react';

/**
 * MetricCard Component
 * Operational KPI card with value, label, trend badge, and optional icon
 */
export default function MetricCard({
  label,
  value,
  change,
  subtext,
  icon,
  accent = 'primary',
  onClick,
  className = ''
}) {
  const accentColors = {
    primary: 'text-primary bg-primary/5 border-primary/20',
    secondary: 'text-secondary bg-secondary/5 border-secondary/20',
    error: 'text-error bg-error-container/30 border-error-container',
    neutral: 'text-on-surface bg-surface-container border-outline-variant'
  };

  return (
    <div
      onClick={onClick}
      className={`bg-surface-container-lowest border border-outline-variant rounded p-5 transition-all duration-150 ${
        onClick ? 'cursor-pointer hover:border-primary hover:shadow-sm active:scale-[0.99]' : ''
      } ${className}`}
    >
      <div className="flex items-start justify-between mb-3">
        <span className="text-label-sm font-semibold uppercase tracking-wider text-on-surface-variant">
          {label}
        </span>
        {icon && (
          <div className={`w-8 h-8 rounded flex items-center justify-center ${accentColors[accent] || accentColors.primary}`}>
            <span className="material-symbols-outlined text-[18px]">{icon}</span>
          </div>
        )}
      </div>

      <div className="flex items-baseline gap-3">
        <span className="text-[28px] font-bold text-primary tracking-tight font-sans">
          {value}
        </span>
        {change && (
          <span className="text-label-sm font-semibold text-secondary flex items-center gap-0.5">
            <span className="material-symbols-outlined text-[14px]">trending_up</span>
            {change}
          </span>
        )}
      </div>

      {subtext && (
        <p className="text-label-sm text-on-surface-variant mt-2 border-t border-outline-variant/50 pt-2">
          {subtext}
        </p>
      )}
    </div>
  );
}
