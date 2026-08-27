import React from 'react';

/**
 * Button Component
 * Primary (Deep Navy), Secondary (Teal/Outline), Destructive (Red), and Ghost variants
 */
export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  icon,
  iconRight,
  disabled = false,
  className = '',
  onClick,
  type = 'button',
  ...props
}) {
  const baseStyles = 'inline-flex items-center justify-center font-label-md font-bold rounded transition-all duration-150 focus:ring-2 focus:ring-offset-2 outline-none disabled:opacity-50 disabled:cursor-not-allowed';

  const variants = {
    primary: 'bg-primary-container text-on-primary hover:bg-primary focus:ring-primary',
    secondary: 'bg-transparent border border-primary text-primary hover:bg-primary-container/10 focus:ring-primary',
    teal: 'bg-secondary text-on-secondary hover:bg-secondary-fixed-dim hover:text-on-secondary-fixed focus:ring-secondary',
    destructive: 'bg-error text-on-error hover:bg-red-700 focus:ring-error',
    ghost: 'bg-transparent text-on-surface-variant hover:bg-surface-container-highest hover:text-on-surface focus:ring-outline',
    outline: 'bg-surface-container-lowest border border-outline text-on-surface hover:bg-surface-container focus:ring-primary'
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-label-sm gap-1.5',
    md: 'px-4 py-2.5 text-label-md gap-2',
    lg: 'px-6 py-3.5 text-body-md gap-2.5'
  };

  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={`${baseStyles} ${variants[variant] || variants.primary} ${sizes[size] || sizes.md} ${className}`}
      {...props}
    >
      {icon && <span className="material-symbols-outlined text-[18px]">{icon}</span>}
      <span>{children}</span>
      {iconRight && <span className="material-symbols-outlined text-[18px]">{iconRight}</span>}
    </button>
  );
}
