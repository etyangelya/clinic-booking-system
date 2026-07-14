import Section from './Section'
import OptionGroup from '../ui/OptionGroup'

const OPTIONS = [
  { value: 'general', label: 'General doctor', description: 'Next available doctor for a routine visit.' },
  { value: 'specialist', label: 'Specialist', description: 'Get matched, or pick one directly.' },
]

export default function CareTypeSection({ value, onChange }) {
  return (
    <Section title="What kind of care do you need?">
      <OptionGroup options={OPTIONS} value={value} onChange={onChange} />
    </Section>
  )
}
