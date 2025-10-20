/**
 * Reusable Badge Component
 * For status indicators, labels, and tags
 */

/**
 * Badge variants with colors
 */
const badgeVariants = {
  primary: {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white'
  },
  success: {
    background: 'linear-gradient(135deg, #4ade80 0%, #22c55e 100%)',
    color: 'white'
  },
  danger: {
    background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
    color: 'white'
  },
  warning: {
    background: 'linear-gradient(135deg, #f59e0b 0%, #f97316 100%)',
    color: 'white'
  },
  info: {
    background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
    color: 'white'
  },
  secondary: {
    background: 'var(--color-bg-tertiary)',
    color: 'var(--color-text-primary)'
  },
  outline: {
    background: 'transparent',
    color: 'var(--color-text-primary)',
    border: '1px solid var(--color-border-primary)'
  }
}

/**
 * Badge Component
 * @param {Object} props
 * @param {React.ReactNode} props.children - Badge content
 * @param {'primary'|'success'|'danger'|'warning'|'info'|'secondary'|'outline'} props.variant - Badge style
 * @param {'sm'|'md'|'lg'} props.size - Badge size
 * @param {React.ReactNode} props.icon - Optional icon
 * @param {string} props.className - Additional CSS classes
 */
export function Badge({
  children,
  variant = 'primary',
  size = 'md',
  icon,
  className = '',
  ...props
}) {
  const variantStyle = badgeVariants[variant] || badgeVariants.primary

  const sizeStyles = {
    sm: { padding: '0.125rem 0.375rem', fontSize: '0.6875rem' },
    md: { padding: '0.25rem 0.5rem', fontSize: '0.75rem' },
    lg: { padding: '0.375rem 0.75rem', fontSize: '0.875rem' }
  }

  const sizeStyle = sizeStyles[size] || sizeStyles.md

  return (
    <div
      className={`badge ${className}`}
      role="status"
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.25rem',
        ...sizeStyle,
        ...variantStyle,
        borderRadius: 'var(--radius-full)',
        fontWeight: 600,
        whiteSpace: 'nowrap',
        ...props.style
      }}
      {...props}
    >
      {icon && <span aria-hidden="true">{icon}</span>}
      <span>{children}</span>
    </div>
  )
}
