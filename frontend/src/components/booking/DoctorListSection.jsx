import { useEffect, useState } from 'react'
import Section from './Section'
import { getSpecialists } from '../../api/doctors'

export default function DoctorListSection({ selectedDoctor, onSelect }) {
  const [doctors, setDoctors] = useState([])
  const [status, setStatus] = useState('loading')

  useEffect(() => {
    let cancelled = false
    getSpecialists()
      .then((data) => {
        if (cancelled) return
        setDoctors(data)
        setStatus('ready')
      })
      .catch(() => {
        if (!cancelled) setStatus('error')
      })
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <Section title="Choose a specialist">
      {status === 'loading' && <p className="text-sm text-label">Loading specialists…</p>}
      {status === 'error' && <p className="text-sm text-red-500">Couldn't load specialists. Please try again.</p>}
      {status === 'ready' && doctors.length === 0 && (
        <p className="text-sm text-label">No specialists are available right now.</p>
      )}
      <div className="grid grid-cols-1 gap-2 @sm:grid-cols-2 @lg:grid-cols-3">
        {doctors.map((doctor) => {
          const isSelected = selectedDoctor?.id === doctor.id
          return (
            <button
              key={doctor.id}
              type="button"
              onClick={() => onSelect(doctor)}
              className={`flex w-full items-center justify-between rounded-2xl border px-4 py-3 text-left transition ${
                isSelected
                  ? 'border-transparent bg-linear-to-r from-brand-start to-brand-end'
                  : 'border-line bg-page hover:border-brand-start/40'
              }`}
            >
              <span>
                <span className={`block text-sm font-semibold ${isSelected ? 'text-white' : 'text-ink'}`}>
                  {doctor.name}
                </span>
                <span className={`block text-xs ${isSelected ? 'text-white/80' : 'text-label'}`}>{doctor.specialty}</span>
              </span>
              {isSelected && (
                <span aria-hidden className="text-white">
                  ✓
                </span>
              )}
            </button>
          )
        })}
      </div>
    </Section>
  )
}
