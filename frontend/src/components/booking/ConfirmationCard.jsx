import Button from '../ui/Button'
import { formatTime } from '../../utils/slots'

export default function ConfirmationCard({ appointment, onBookAnother }) {
  const slotDate = new Date(appointment.slot_time)
  return (
    <div className="rounded-2xl bg-card p-6 shadow-card sm:p-8">
      <h1 className="text-xl font-semibold text-ink">You're booked!</h1>
      <p className="mt-1 text-sm text-label">We've sent a confirmation to your email.</p>

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
      </div>

      <Button type="button" onClick={onBookAnother} className="mt-6 w-full">
        Book another appointment
      </Button>
    </div>
  )
}
