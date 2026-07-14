import { useState } from 'react'
import Section from './Section'
import Button from '../ui/Button'

const MAX_SYMPTOMS = 3

export default function SymptomSection({ committed, onCommit }) {
  const [symptoms, setSymptoms] = useState(Array(MAX_SYMPTOMS).fill(''))

  const updateSymptom = (index, value) => {
    setSymptoms((prev) => prev.map((s, i) => (i === index ? value : s)))
  }

  const canContinue = symptoms[0].trim().length > 0

  const handleSubmit = (event) => {
    event.preventDefault()
    if (!canContinue) return
    onCommit(symptoms.map((s) => s.trim()).filter(Boolean).join(', '))
  }

  return (
    <Section title="Describe your symptoms" subtitle="Add up to 3 symptoms and we'll match you to the right specialist.">
      <form onSubmit={handleSubmit} className="grid grid-cols-1 gap-3 @sm:grid-cols-3">
        {symptoms.map((value, index) => (
          <input
            key={index}
            type="text"
            value={value}
            onChange={(event) => updateSymptom(index, event.target.value)}
            placeholder={`Symptom ${index + 1}${index === 0 ? '' : ' (optional)'}`}
            maxLength={60}
            className="w-full rounded-xl border border-line bg-page px-4 py-3 text-sm text-ink focus:border-brand-start focus:outline-none focus:ring-2 focus:ring-brand-start/20"
          />
        ))}
        <Button type="submit" disabled={!canContinue} className="w-full @sm:col-span-3">
          {committed ? 'Update matches' : 'Find specialist'}
        </Button>
      </form>
    </Section>
  )
}
