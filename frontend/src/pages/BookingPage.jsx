import { useCallback, useState } from 'react'
import BrandPanel from '../components/booking/BrandPanel'
import CareTypeSection from '../components/booking/CareTypeSection'
import SpecialistModeSection from '../components/booking/SpecialistModeSection'
import SymptomSection from '../components/booking/SymptomSection'
import DoctorListSection from '../components/booking/DoctorListSection'
import SlotSection from '../components/booking/SlotSection'
import ConfirmationCard from '../components/booking/ConfirmationCard'
import PatientDetailsModal from '../components/booking/PatientDetailsModal'
import { getGeneralAvailability, getDoctorAvailability, matchSpeciality } from '../api/doctors'
import { createAppointment } from '../api/appointments'
import { normalizeMergedSlots, normalizeDoctorSlots, toLocalIsoString } from '../utils/slots'

export default function BookingPage() {
  const [careType, setCareType] = useState('general')
  const [specialistMode, setSpecialistMode] = useState(null)
  const [selectedDoctor, setSelectedDoctor] = useState(null)
  const [symptoms, setSymptoms] = useState(null)
  const [matchInfo, setMatchInfo] = useState(null)
  const [selectedSlot, setSelectedSlot] = useState(null)
  const [consent, setConsent] = useState(false)

  const [modalOpen, setModalOpen] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState(null)
  const [appointment, setAppointment] = useState(null)

  const handleCareTypeChange = (value) => {
    setCareType(value)
    setSpecialistMode(null)
    setSelectedDoctor(null)
    setSymptoms(null)
    setMatchInfo(null)
    setSelectedSlot(null)
    setConsent(false)
  }

  const handleModeChange = (mode) => {
    setSpecialistMode(mode)
    setSelectedDoctor(null)
    setSymptoms(null)
    setMatchInfo(null)
    setSelectedSlot(null)
    setConsent(false)
  }

  const handleDoctorSelect = (doctor) => {
    setSelectedDoctor(doctor)
    setSelectedSlot(null)
    setConsent(false)
  }

  const handleSymptomsCommit = (text) => {
    setSymptoms(text)
    setSelectedSlot(null)
    setConsent(false)
  }

  const handleSlotSelect = (slot) => {
    setSelectedSlot(slot)
    setConsent(false)
  }

  const handleConsentChange = (checked) => {
    setConsent(checked)
    if (checked && selectedSlot) {
      setSubmitError(null)
      setModalOpen(true)
    }
  }

  const handleModalClose = () => {
    setModalOpen(false)
    setConsent(false)
  }

  const fetchGeneralSlots = useCallback(
    (date) => getGeneralAvailability(date).then((res) => normalizeMergedSlots(res.available_slots)),
    [],
  )

  const fetchDoctorSlots = useCallback(
    (date) => getDoctorAvailability(selectedDoctor.id, date).then((res) => normalizeDoctorSlots(res.available_slots, selectedDoctor)),
    [selectedDoctor],
  )

  const fetchSymptomSlots = useCallback(
    (date) =>
      matchSpeciality(symptoms, date).then((res) => {
        setMatchInfo({ speciality: res.matched_speciality, fallback: res.fallback })
        return normalizeMergedSlots(res.available_slots)
      }),
    [symptoms],
  )

  const handleConfirmBooking = async ({ name, phone, email }) => {
    setSubmitting(true)
    setSubmitError(null)
    try {
      const created = await createAppointment({
        doctorId: selectedSlot.doctorId,
        patientName: name,
        patientEmail: email,
        patientPhone: phone,
        slotTime: toLocalIsoString(selectedSlot.time),
      })
      setAppointment(created)
      setModalOpen(false)
    } catch (err) {
      setSubmitError(err?.response?.data?.detail ?? 'Something went wrong. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  const resetFlow = () => {
    setCareType(null)
    setSpecialistMode(null)
    setSelectedDoctor(null)
    setSymptoms(null)
    setMatchInfo(null)
    setSelectedSlot(null)
    setConsent(false)
    setAppointment(null)
    setSubmitError(null)
  }

  const readyForSlots =
    careType === 'general' || (specialistMode === 'doctor' && selectedDoctor) || (specialistMode === 'symptoms' && symptoms)

  const slotFetcher = careType === 'general' ? fetchGeneralSlots : selectedDoctor ? fetchDoctorSlots : fetchSymptomSlots

  return (
    <div className="flex min-h-svh bg-page">
      <BrandPanel />

      <div className="flex flex-1 justify-center px-4 py-6 sm:px-6 sm:py-12 lg:py-16">
        <div className="@container mx-auto w-full max-w-md self-center sm:max-w-lg lg:max-w-xl">
          {appointment ? (
            <ConfirmationCard appointment={appointment} onBookAnother={resetFlow} />
          ) : (
            <div className="rounded-2xl bg-card p-5 shadow-card sm:p-8 lg:p-10">
              <h1 className="text-xl font-semibold text-ink lg:text-2xl">Book an appointment</h1>
              <p className="mt-1 text-sm text-label">Everything you need is on this one page.</p>

              <div className="mt-6 space-y-6">
                <CareTypeSection value={careType} onChange={handleCareTypeChange} />

                {careType === 'specialist' && <SpecialistModeSection value={specialistMode} onChange={handleModeChange} />}

                {specialistMode === 'doctor' && (
                  <DoctorListSection selectedDoctor={selectedDoctor} onSelect={handleDoctorSelect} />
                )}

                {specialistMode === 'symptoms' && <SymptomSection committed={symptoms} onCommit={handleSymptomsCommit} />}

                {readyForSlots && (
                  <SlotSection
                    title={selectedDoctor ? `Book with ${selectedDoctor.name}` : 'Pick a time'}
                    subtitle={
                      matchInfo?.speciality
                        ? `Matched to ${matchInfo.speciality}${matchInfo.fallback ? ' (closest match)' : ''}`
                        : undefined
                    }
                    fetchSlots={slotFetcher}
                    selectedSlot={selectedSlot}
                    onSelectSlot={handleSlotSelect}
                    consent={consent}
                    onConsentChange={handleConsentChange}
                  />
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      <PatientDetailsModal
        open={modalOpen}
        onClose={handleModalClose}
        onSubmit={handleConfirmBooking}
        submitting={submitting}
        error={submitError}
      />
    </div>
  )
}
