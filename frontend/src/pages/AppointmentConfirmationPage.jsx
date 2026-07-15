import { useCallback, useEffect, useState } from 'react'
import { useParams, useSearchParams } from 'react-router-dom'
import BrandPanel from '../components/booking/BrandPanel'
import Section from '../components/booking/Section'
import SlotSection from '../components/booking/SlotSection'
import Button from '../components/ui/Button'
import { cancelAppointmentByLink, getAppointmentByLink, rescheduleAppointmentByLink } from '../api/appointments'
import { getDoctorAvailability } from '../api/doctors'
import { formatTime, normalizeDoctorSlots, toLocalIsoString } from '../utils/slots'

const inputClass =
  'w-full rounded-xl border border-line bg-page px-4 py-3 text-sm text-ink focus:border-brand-start focus:outline-none focus:ring-2 focus:ring-brand-start/20'

// International format only (e.g. +254712345678) so verification works the
// same way regardless of which country the patient booked from.
const PHONE_RE = /^\+[1-9]\d{6,14}$/
const normalizePhone = (value) => value.replace(/[^\d+]/g, '')

export default function AppointmentConfirmationPage() {
  const { id } = useParams()
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')

  const [status, setStatus] = useState(() => (token ? 'loading' : 'error'))
  const [appointment, setAppointment] = useState(null)
  const [actionMode, setActionMode] = useState(null)
  const [rescheduled, setRescheduled] = useState(false)

  useEffect(() => {
    if (!token) return
    let cancelled = false
    getAppointmentByLink(id, token)
      .then((data) => {
        if (cancelled) return
        setAppointment(data)
        setStatus('ready')
      })
      .catch(() => {
        if (!cancelled) setStatus('error')
      })
    return () => {
      cancelled = true
    }
  }, [id, token])

  const handleCancelled = (updated) => {
    setAppointment(updated)
    setActionMode(null)
  }

  const handleRescheduled = () => {
    setActionMode(null)
    setRescheduled(true)
  }

  return (
    <div className="flex min-h-svh bg-page">
      <BrandPanel />

      <div className="flex flex-1 justify-center px-4 py-6 sm:px-6 sm:py-12 lg:py-16">
        <div className="@container mx-auto w-full max-w-md self-center sm:max-w-lg lg:max-w-xl">
          <div className="rounded-2xl bg-card p-6 shadow-card sm:p-8">
            {status === 'loading' && <p className="text-sm text-label">Loading your appointment…</p>}

            {status === 'error' && (
              <>
                <h1 className="text-xl font-semibold text-ink">Link not valid</h1>
                <p className="mt-1 text-sm text-label">
                  This confirmation link is invalid or has expired. Please check your email for the most recent link.
                </p>
              </>
            )}

            {status === 'ready' && appointment && rescheduled && (
              <>
                <h1 className="text-xl font-semibold text-ink">You&apos;re all set!</h1>
                <p className="mt-1 text-sm text-label">
                  Your appointment has been rescheduled. We&apos;ve sent an updated confirmation link to your email.
                </p>
              </>
            )}

            {status === 'ready' && appointment && !rescheduled && (
              <>
                <ConfirmationDetails appointment={appointment} />

                {appointment.status === 'CONFIRMED' && (
                  <ManageAppointment
                    appointment={appointment}
                    token={token}
                    actionMode={actionMode}
                    onActionModeChange={setActionMode}
                    onCancelled={handleCancelled}
                    onRescheduled={handleRescheduled}
                  />
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function ConfirmationDetails({ appointment }) {
  const slotDate = new Date(appointment.slot_time)
  const isCancelled = appointment.status === 'CANCELLED'

  return (
    <>
      <h1 className="text-xl font-semibold text-ink">
        {isCancelled ? 'This appointment was cancelled' : "You're booked!"}
      </h1>
      <p className="mt-1 text-sm text-label">
        {isCancelled ? 'This booking is no longer active.' : 'Here are your appointment details.'}
      </p>

      <div className="mt-6 space-y-2 rounded-2xl bg-page p-4 text-sm text-ink">
        <p>
          <span className="font-medium">Date:</span>{' '}
          {slotDate.toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric' })}
        </p>
        <p>
          <span className="font-medium">Time:</span> {formatTime(slotDate)}
        </p>
        <p>
          <span className="font-medium">Reference:</span> #{appointment.id}
        </p>
        <p>
          <span className="font-medium">Status:</span> {isCancelled ? 'Cancelled' : 'Confirmed'}
        </p>
      </div>
    </>
  )
}

function ManageAppointment({ appointment, token, actionMode, onActionModeChange, onCancelled, onRescheduled }) {
  if (actionMode === null) {
    return (
      <div className="mt-6 flex gap-3">
        <Button variant="secondary" className="flex-1" onClick={() => onActionModeChange('reschedule')}>
          Reschedule
        </Button>
        <Button variant="secondary" className="flex-1" onClick={() => onActionModeChange('cancel')}>
          Cancel appointment
        </Button>
      </div>
    )
  }

  if (actionMode === 'cancel') {
    return (
      <CancelForm
        appointment={appointment}
        token={token}
        onCancelled={onCancelled}
        onBack={() => onActionModeChange(null)}
      />
    )
  }

  return (
    <RescheduleForm
      appointment={appointment}
      token={token}
      onRescheduled={onRescheduled}
      onBack={() => onActionModeChange(null)}
    />
  )
}

function CancelForm({ appointment, token, onCancelled, onBack }) {
  const [phone, setPhone] = useState('')
  const [reason, setReason] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)

  const canSubmit = PHONE_RE.test(normalizePhone(phone))

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!canSubmit) return
    setSubmitting(true)
    setError(null)
    try {
      const updated = await cancelAppointmentByLink(appointment.id, token, normalizePhone(phone), reason.trim())
      onCancelled(updated)
    } catch (err) {
      setError(err?.response?.data?.detail ?? 'Something went wrong. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Section title="Cancel appointment" subtitle="Enter the phone number you booked with to confirm.">
      <form onSubmit={handleSubmit} className="space-y-3">
        <div>
          <input
            type="tel"
            value={phone}
            onChange={(event) => setPhone(event.target.value)}
            placeholder="+254712345678"
            className={inputClass}
          />
          <p className={`mt-1 text-xs ${phone && !canSubmit ? 'text-red-500' : 'text-label'}`}>
            Include your country code, e.g. +254712345678
          </p>
        </div>
        <textarea
          value={reason}
          onChange={(event) => setReason(event.target.value)}
          placeholder="Reason (optional)"
          rows={3}
          className={inputClass}
        />

        {error && <p className="text-sm text-red-500">{error}</p>}

        <div className="flex gap-3">
          <Button type="button" variant="secondary" className="flex-1" onClick={onBack} disabled={submitting}>
            Back
          </Button>
          <Button type="submit" className="flex-1" disabled={!canSubmit || submitting}>
            {submitting ? 'Cancelling…' : 'Confirm cancellation'}
          </Button>
        </div>
      </form>
    </Section>
  )
}

function RescheduleForm({ appointment, token, onRescheduled, onBack }) {
  const [phone, setPhone] = useState('')
  const [newSlot, setNewSlot] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)

  const fetchSlots = useCallback(
    (date) =>
      getDoctorAvailability(appointment.doctor_id, date).then((res) =>
        normalizeDoctorSlots(res.available_slots, { id: appointment.doctor_id }),
      ),
    [appointment.doctor_id],
  )

  const phoneValid = PHONE_RE.test(normalizePhone(phone))
  const canSubmit = phoneValid && newSlot

  const handleSubmit = async () => {
    if (!canSubmit) return
    setSubmitting(true)
    setError(null)
    try {
      await rescheduleAppointmentByLink(appointment.id, token, normalizePhone(phone), toLocalIsoString(newSlot.time))
      onRescheduled()
    } catch (err) {
      setError(err?.response?.data?.detail ?? 'Something went wrong. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="mt-6 space-y-3 border-t border-line pt-6">
      <SlotSection
        title="Pick a new time"
        subtitle="Confirm with your phone number once you've chosen a slot."
        fetchSlots={fetchSlots}
        selectedSlot={newSlot}
        onSelectSlot={setNewSlot}
      />

      <div>
        <input
          type="tel"
          value={phone}
          onChange={(event) => setPhone(event.target.value)}
          placeholder="+254712345678"
          className={inputClass}
        />
        <p className={`mt-1 text-xs ${phone && !phoneValid ? 'text-red-500' : 'text-label'}`}>
          Include your country code, e.g. +254712345678
        </p>
      </div>

      {error && <p className="text-sm text-red-500">{error}</p>}

      <div className="flex gap-3">
        <Button type="button" variant="secondary" className="flex-1" onClick={onBack} disabled={submitting}>
          Back
        </Button>
        <Button type="button" className="flex-1" onClick={handleSubmit} disabled={!canSubmit || submitting}>
          {submitting ? 'Rescheduling…' : 'Confirm reschedule'}
        </Button>
      </div>
    </div>
  )
}
