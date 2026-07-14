export default function OptionGroup({ options, value, onChange }) {
  return (
    <div className="grid grid-cols-1 gap-3 @sm:grid-cols-2">
      {options.map((option) => {
        const isSelected = value === option.value
        return (
          <button
            key={option.value}
            type="button"
            onClick={() => onChange(option.value)}
            className={`rounded-2xl border p-4 text-left transition ${
              isSelected
                ? 'border-transparent bg-linear-to-r from-brand-start to-brand-end'
                : 'border-line bg-page hover:border-brand-start/40 hover:bg-brand-start/5'
            }`}
          >
            <span className={`block text-sm font-semibold ${isSelected ? 'text-white' : 'text-ink'}`}>{option.label}</span>
            {option.description && (
              <span className={`mt-1 block text-xs ${isSelected ? 'text-white/80' : 'text-label'}`}>
                {option.description}
              </span>
            )}
          </button>
        )
      })}
    </div>
  )
}
