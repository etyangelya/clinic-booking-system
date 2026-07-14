export default function Section({ title, subtitle, children }) {
  return (
    <div className="border-t border-line pt-6 first:border-t-0 first:pt-0">
      {title && <h2 className="text-base font-semibold text-ink">{title}</h2>}
      {subtitle && <p className="mt-1 text-sm text-label">{subtitle}</p>}
      <div className="mt-4">{children}</div>
    </div>
  )
}
