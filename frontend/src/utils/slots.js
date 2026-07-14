export function toDateInputValue(date) {
  return date.toISOString().slice(0, 10)
}

// The backend stores appointment times as naive wall-clock values (not real
// UTC instants), so this must send the slot's local clock digits as-is.
// date.toISOString() would convert to UTC using the browser's offset and
// silently shift the booked time (e.g. 2pm booked as 11am in UTC+3).
export function toLocalIsoString(date) {
  const pad = (n) => String(n).padStart(2, '0')
  return (
    `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T` +
    `${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
  )
}

export function normalizeMergedSlots(rawSlots) {
  const seen = new Map()
  for (const slot of rawSlots) {
    const time = new Date(slot.slot_time)
    const key = time.toISOString()
    if (!seen.has(key)) {
      seen.set(key, { time, doctorId: slot.doctor_id, doctorName: slot.doctor_name })
    }
  }
  return Array.from(seen.values()).sort((a, b) => a.time - b.time)
}

export function normalizeDoctorSlots(rawTimes, doctor) {
  return rawTimes
    .map((iso) => ({ time: new Date(iso), doctorId: doctor.id, doctorName: doctor.name }))
    .sort((a, b) => a.time - b.time)
}

export const TIME_PERIODS = [
  { key: 'morning', label: 'Morning', test: (hour) => hour < 12 },
  { key: 'afternoon', label: 'Afternoon', test: (hour) => hour >= 12 && hour < 17 },
  { key: 'evening', label: 'Evening', test: (hour) => hour >= 17 },
]

export function bucketSlots(slots) {
  const buckets = { morning: [], afternoon: [], evening: [] }
  for (const slot of slots) {
    const hour = slot.time.getHours()
    const period = TIME_PERIODS.find((p) => p.test(hour))
    buckets[period.key].push(slot)
  }
  return buckets
}

export function formatTime(date) {
  return new Intl.DateTimeFormat(undefined, { hour: 'numeric', minute: '2-digit', hour12: true }).format(date)
}
