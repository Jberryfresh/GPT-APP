
import React from 'react'

export const Progress = ({ value, className, ...props }) => {
  return (
    <div className={`w-full bg-gray-200 rounded-full h-2.5 ${className}`} {...props}>
      <div
        className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
        style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
      ></div>
    </div>
  )
}
