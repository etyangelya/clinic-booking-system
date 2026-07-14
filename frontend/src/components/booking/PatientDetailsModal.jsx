import { useState } from 'react'
import Button from '../ui/Button'

const inputClass =
  'w-full rounded-xl border border-line bg-page px-4 py-3 text-sm text-ink focus:border-brand-start focus:outline-none focus:ring-2 focus:ring-brand-start/20'

export default function PatientDetailsModal({ open, onClose, onSubmit, submitting, error }) {
  const [name, setName] = useState('')
  const [phone, setPhone] = useState('')
  const [email, setEmail] = useState('')

  if (!open) return null

  const canSubmit = name.trim().length > 0 && email.trim().length > 0

  const handleSubmit = (event) => {
    event.preventDefault()
    if (!canSubmit) return
    onSubmit({ name: name.trim(), phone: phone.trim(), email: email.trim() })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-ink/40 p-4 sm:items-center">
      <div className="@container w-full max-w-md rounded-2xl bg-card p-6 shadow-card sm:max-w-lg sm:p-8">
        <div className="mb-4 flex items-start justify-between">
          <div>
            <h2 className="text-lg font-semibold text-ink">Your details</h2>
            <p className="mt-1 text-sm text-label">We&apos;ll use this to confirm your appointment.</p>
          </div>
          <button type="button" onClick={onClose} aria-label="Close" className="text-label hover:text-ink">
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="grid grid-cols-1 gap-3 @sm:grid-cols-2">
          <input
            type="text"
            required
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="Full name"
            className={`${inputClass} @sm:col-span-2`}
          />
          <input
            type="tel"
            value={phone}
            onChange={(event) => setPhone(event.target.value)}
            placeholder="+254712345678"
            className={inputClass}
          />
          <input
            type="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="Email address"
            className={inputClass}
          />

          {error && <p className="text-sm text-red-500 @sm:col-span-2">{error}</p>}

          <Button type="submit" disabled={!canSubmit || submitting} className="w-full @sm:col-span-2">
            {submitting ? 'Booking…' : 'Confirm booking'}
          </Button>
        </form>
      </div>
    </div>
  )
}
