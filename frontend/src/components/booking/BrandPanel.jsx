const HIGHLIGHTS = [
  'Real-time availability across every doctor',
  'Instant email confirmation',
  'Reschedule or cancel anytime',
]

export default function BrandPanel() {
  return (
    <div className="relative hidden overflow-hidden bg-linear-to-br from-brand-start to-brand-end px-12 py-16 text-white lg:flex lg:w-2/5 lg:flex-col lg:justify-between xl:w-1/3">
      <div aria-hidden className="pointer-events-none absolute -top-24 -right-24 h-72 w-72 rounded-full bg-white/10" />
      <div aria-hidden className="pointer-events-none absolute -bottom-32 -left-16 h-80 w-80 rounded-full bg-white/10" />

      <div className="relative">
        <p className="text-sm font-medium tracking-widest text-white/70 uppercase">Clinic Booking</p>
        <h2 className="mt-4 text-3xl font-semibold leading-tight xl:text-4xl">Care that fits your schedule.</h2>
        <p className="mt-4 max-w-sm text-white/80">
          Book with a general doctor or get matched to the right specialist in under a minute.
        </p>
      </div>

      <ul className="relative space-y-3 text-sm text-white/80">
        {HIGHLIGHTS.map((item) => (
          <li key={item} className="flex items-center gap-2">
            <span aria-hidden className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-white/15 text-xs">
              ✓
            </span>
            {item}
          </li>
        ))}
      </ul>
    </div>
  )
}
