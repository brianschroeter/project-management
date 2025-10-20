/**
 * Reusable Button Component
 * Consistent styling and behavior across the app
 */

/**
 * Button variants
 */
const buttonVariants = {
  primary: {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    hover: 'brightness(1.1)'
  },
  success: {
    background: 'linear-gradient(135deg, #4ade80 0%, #22c55e 100%)',
    color: 'white',
    hover: 'brightness(1.1)'
  },
  danger: {
    background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
    color: 'white',
    hover: 'brightness(1.1)'
  },
  warning: {
    background: 'linear-gradient(135deg, #f59e0b 0%, #f97316 100%)',
    color: 'white',
    hover: 'brightness(1.1)'
  },
  secondary: {
    background: 'var(--color-bg-tertiary)',
    color: 'var(--color-text-primary)',
    hover: 'brightness(0.95)'
  },
  ghost: {
    background: 'transparent',
    color: 'var(--color-text-primary)',
    hover: 'brightness(0.9)'
  }
}

/**
 * Button sizes
 */
const buttonSizes = {
  xs: { padding: '0.25rem 0.5rem', fontSize: '0.75rem' },
  sm: { padding: '0.5rem 1rem', fontSize: '0.875rem' },
  md: { padding: '0.75rem 1.5rem', fontSize: '1rem' },
  lg: { padding: '1rem 2rem', fontSize: '1.125rem' }
}

/**
 * Button Component
 * @param {Object} props
 * @param {React.ReactNode} props.children - Button content
 * @param {'primary'|'success'|'danger'|'warning'|'secondary'|'ghost'} props.variant - Button style variant
 * @param {'xs'|'sm'|'md'|'lg'} props.size - Button size
 * @param {boolean} props.disabled - Whether button is disabled
 * @param {boolean} props.loading - Whether button is in loading state
 * @param {boolean} props.fullWidth - Whether button should take full width
 * @param {string} props.className - Additional CSS classes
 * @param {Function} props.onClick - Click handler
 * @param {string} props.type - Button type (button, submit, reset)
 */
export function Button({
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  fullWidth = false,
  className = '',
  onClick,
  type = 'button',
  ...props
}) {
  const variantStyle = buttonVariants[variant] || buttonVariants.primary
  const sizeStyle = buttonSizes[size] || buttonSizes.md

  return (
    <button
      type={type}
      disabled={disabled || loading}
      onClick={onClick}
      className={`hover-scale smooth-transition ${className}`}
      aria-busy={loading}
      style={{
        ...sizeStyle,
        background: variantStyle.background,
        color: variantStyle.color,
        border: 'none',
        borderRadius: 'var(--radius-md)',
        cursor: disabled || loading ? 'not-allowed' : 'pointer',
        opacity: disabled || loading ? 0.5 : 1,
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '0.5rem',
        fontWeight: 600,
        fontFamily: 'inherit',
        transition: 'all 0.2s ease',
        width: fullWidth ? '100%' : 'auto',
        ...props.style
      }}
      onMouseEnter={(e) => {
        if (!disabled && !loading) {
          e.currentTarget.style.filter = variantStyle.hover
          e.currentTarget.style.transform = 'translateY(-2px)'
        }
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.filter = 'none'
        e.currentTarget.style.transform = 'translateY(0)'
      }}
      {...props}
    >
      {loading && (
        <div
          className="spinner"
          style={{
            width: '1em',
            height: '1em',
            border: '2px solid currentColor',
            borderTopColor: 'transparent',
            borderRadius: '50%',
            animation: 'spin 0.8s linear infinite'
          }}
          aria-hidden="true"
        />
      )}
      {children}
    </button>
  )
}

/**
 * Icon Button - Button with just an icon
 */
export function IconButton({
  icon,
  label,
  size = 'md',
  variant = 'ghost',
  ...props
}) {
  return (
    <Button
      variant={variant}
      size={size}
      aria-label={label}
      title={label}
      style={{
        padding: size === 'sm' ? '0.5rem' : '0.75rem',
        ...props.style
      }}
      {...props}
    >
      {icon}
    </Button>
  )
}
