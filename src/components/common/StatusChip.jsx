import React from 'react';

/**
 * StatusChip Component
 * Semantic pill/chip for statuses (Critical, High, Medium, Clear, Attributed, Investigating)
 */
export default function StatusChip({ status, label, icon, size = 'sm', className = '' }) {
  const normalized = (status || label || '').toLowerCase();
  
  let styles = 'bg-surface-container-high text-on-surface border border-outline-variant';
  let dotColor = 'bg-outline';

  if (normalized.includes('critical') || normalized.includes('danger') || normalized.includes('high risk')) {
    styles = 'bg-error-container text-on-error-container border border-error-container';
    dotColor = 'bg-error';
  } else if (normalized.includes('high') || normalized.includes('investigating')) {
    styles = 'bg-tertiary-fixed text-on-tertiary-fixed border border-tertiary-container/30';
    dotColor = 'bg-tertiary-container';
  } else if (normalized.includes('attributed') || normalized.includes('success') || normalized.includes('primary')) {
    styles = 'bg-secondary-container text-on-secondary-container border border-secondary/30';
    dotColor = 'bg-secondary';
  } else if (normalized.includes('clear') || normalized.includes('natural') || normalized.includes('closed')) {
    styles = 'bg-surface-container-high text-on-surface-variant border border-outline-variant';
    dotColor = 'bg-outline-variant';
  } else if (normalized.includes('medium') || normalized.includes('moderate')) {
    styles = 'bg-primary-fixed text-on-primary-fixed border border-primary-fixed-dim';
    dotColor = 'bg-primary';
  }

  const sizeClasses = size === 'sm' 
    ? 'px-2 py-0.5 text-[11px] leading-4 tracking-wider uppercase font-bold' 
    : 'px-3 py-1 text-label-sm font-semibold tracking-wide';

  return (
    <span className={`inline-flex items-center gap-1.5 rounded ${sizeClasses} ${styles} ${className}`}>
      {icon ? (
        <span className="material-symbols-outlined text-[13px]">{icon}</span>
      ) : (
        <span className={`w-1.5 h-1.5 rounded-full ${dotColor}`}></span>
      )}
      <span>{label || status}</span>
    </span>
  );
}
