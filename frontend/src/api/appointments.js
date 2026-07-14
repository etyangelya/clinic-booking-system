import { apiClient } from './client'

export async function createAppointment({ doctorId, patientName, patientEmail, patientPhone, slotTime }) {
  const { data } = await apiClient.post('/appointments', {
    doctor_id: doctorId,
    patient_name: patientName,
    patient_email: patientEmail,
    patient_phone: patientPhone || null,
    slot_time: slotTime,
  })
  return data
}

export async function getAppointmentByLink(appointmentId, token) {
  const { data } = await apiClient.get(`/appointments/${appointmentId}/view`, {
    params: { token },
  })
  return data
}

export async function cancelAppointmentByLink(appointmentId, token, phone, reason) {
  const { data } = await apiClient.patch(`/appointments/${appointmentId}/link-cancel`, null, {
    params: { token, phone, reason: reason || undefined },
  })
  return data
}

export async function rescheduleAppointmentByLink(appointmentId, token, phone, newSlotTime) {
  const { data } = await apiClient.patch(
    `/appointments/${appointmentId}/link-reschedule`,
    { new_slot_time: newSlotTime },
    { params: { token, phone } },
  )
  return data
}
