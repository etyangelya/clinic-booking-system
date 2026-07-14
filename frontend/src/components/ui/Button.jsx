const VARIANTS = {
  primary: 'bg-linear-to-r from-brand-start to-brand-end text-white hover:opacity-90',
  secondary: 'bg-card text-ink border border-line hover:bg-line/30',
}

export default function Button({ children, variant = 'primary', className = '', ...props }) {
  return (
    <button
      className={`inline-flex items-center justify-center rounded-full px-6 py-3 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-40 ${VARIANTS[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  )
}
