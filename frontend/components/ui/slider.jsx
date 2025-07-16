
import React from 'react'

const Slider = React.forwardRef(({ className, value = [0], onValueChange, max = 100, min = 0, step = 1, ...props }, ref) => {
  const handleChange = (e) => {
    const newValue = [Number(e.target.value)]
    onValueChange?.(newValue)
  }

  return (
    <div className={`relative flex w-full touch-none select-none items-center ${className || ''}`}>
      <input
        ref={ref}
        type="range"
        min={min}
        max={max}
        step={step}
        value={value[0]}
        onChange={handleChange}
        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
        {...props}
      />
    </div>
  )
})
Slider.displayName = "Slider"

export { Slider }
