import { useEffect, useMemo, useState } from 'react'
import Section from './Section'
import Button from '../ui/Button'
import { bucketSlots, formatTime, TIME_PERIODS, toDateInputValue } from '../../utils/slots'

export default function SlotSection({
  title,
  subtitle,
  fetchSlots,
  selectedSlot,
  onSelectSlot,
  onContinue,
}) {
  const [date, setDate] = useState(() => toDateInputValue(new Date()))
  const [slots, setSlots] = useState([])
  const [status, setStatus] = useState('loading')
  const [period, setPeriod] = useState('morning')

  useEffect(() => {
    let cancelled = false
    fetchSlots(date)
      .then((normalized) => {
        if (cancelled) return
        const upcoming = normalized.filter((slot) => slot.time > new Date())
        setSlots(upcoming)
        setStatus('ready')
        const buckets = bucketSlots(upcoming)
        const firstNonEmpty = TIME_PERIODS.find((p) => buckets[p.key].length > 0)
        setPeriod(firstNonEmpty ? firstNonEmpty.key : 'morning')
      })
      .catch(() => {
        if (!cancelled) setStatus('error')
      })
    return () => {
      cancelled = true
    }
  }, [date, fetchSlots])

  const buckets = useMemo(() => bucketSlots(slots), [slots])
  const visibleSlots = buckets[period] || []
  const minDate = toDateInputValue(new Date())

  return (
    <Section title={title} subtitle={subtitle}>
      <div className="space-y-5">
        <div className="grid grid-cols-1 gap-4 @sm:grid-cols-2 @sm:items-start">
          <label className="block">
            <span className="mb-1 block text-xs font-medium uppercase tracking-wide text-label">Select date</span>
            <input
              type="date"
              value={date}
              min={minDate}
              onChange={(event) => {
                setDate(event.target.value)
                setStatus('loading')
                onSelectSlot(null)
              }}
              className="w-full rounded-xl border border-line bg-page px-4 py-3 text-sm text-ink focus:border-brand-start focus:outline-none focus:ring-2 focus:ring-brand-start/20"
            />
          </label>

          <div>
            <span className="mb-1 block text-xs font-medium uppercase tracking-wide text-label">Select time</span>
            <div className="grid grid-cols-3 gap-2">
              {TIME_PERIODS.map((p) => (
                <button
                  key={p.key}
                  type="button"
                  onClick={() => setPeriod(p.key)}
                  disabled={buckets[p.key].length === 0}
                  className={`rounded-full px-3 py-2 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-30 ${
                    period === p.key
                      ? 'bg-linear-to-r from-brand-start to-brand-end text-white'
                      : 'border border-line bg-page text-label hover:border-brand-start/40'
                  }`}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {status === 'loading' && <p className="text-sm text-label">Loading available times…</p>}
        {status === 'error' && <p className="text-sm text-red-500">Couldn't load availability. Please try again.</p>}
        {status === 'ready' && visibleSlots.length === 0 && (
          <p className="text-sm text-label">No slots in this window — try another date or time of day.</p>
        )}

        {status === 'ready' && visibleSlots.length > 0 && (
          <div className="grid grid-cols-3 gap-2 @sm:grid-cols-4 @lg:grid-cols-5">
            {visibleSlots.map((slot) => {
              const key = slot.time.toISOString()
              const isSelected = selectedSlot && selectedSlot.time.toISOString() === key
              return (
                <button
                  key={key}
                  type="button"
                  onClick={() => onSelectSlot(slot)}
                  className={`rounded-full border px-2 py-2 text-sm font-medium transition ${
                    isSelected
                      ? 'border-transparent bg-linear-to-r from-brand-start to-brand-end text-white'
                      : 'border-line text-ink hover:border-brand-start/40'
                  }`}
                >
                  {formatTime(slot.time)}
                </button>
              )
            })}
          </div>
        )}

        {selectedSlot && onContinue ? (
          <div className="flex flex-col items-start gap-2">
            <div className="flex items-start gap-3">
            </div>
            <Button type="button" onClick={onContinue} className="mt-4 w-full">
              Proceed to book
            </Button>
          </div>
        ) : (
          selectedSlot?.doctorName && (
            <p className="text-sm text-label">
              You&apos;ll see <span className="font-medium text-ink">{selectedSlot.doctorName}</span>.
            </p>
          )
        )}
      </div>
    </Section>
  )
}
