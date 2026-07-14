import Section from './Section'
import OptionGroup from '../ui/OptionGroup'

const OPTIONS = [
  { value: 'doctor', label: 'Pick a doctor', description: 'Choose the specialist you want to see.' },
  { value: 'symptoms', label: 'Describe symptoms', description: "Tell us what's wrong and we'll match you." },
]

export default function SpecialistModeSection({ value, onChange }) {
  return (
    <Section title="How would you like to proceed?">
      <OptionGroup options={OPTIONS} value={value} onChange={onChange} />
    </Section>
  )
}
