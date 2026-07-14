import { apiClient } from './client'

export async function getGeneralAvailability(date) {
  const { data } = await apiClient.get('/doctors/availability/general', { params: { date } })
  return data
}

export async function getSpecialists() {
  const { data } = await apiClient.get('/doctors/specialists')
  return data
}

export async function getDoctorAvailability(doctorId, date) {
  const { data } = await apiClient.get(`/doctors/${doctorId}/availability`, { params: { date } })
  return data
}

export async function matchSpeciality(symptoms, date) {
  const { data } = await apiClient.post('/doctors/match-speciality', { symptoms, date })
  return data
}
