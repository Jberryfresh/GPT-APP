
import React, { useState, createContext, useContext } from 'react'

const DialogContext = createContext()

export const Dialog = ({ children, open, onOpenChange }) => {
  const [isOpen, setIsOpen] = useState(open || false)
  
  const handleOpenChange = (newOpen) => {
    setIsOpen(newOpen)
    if (onOpenChange) onOpenChange(newOpen)
  }

  return (
    <DialogContext.Provider value={{ isOpen, setIsOpen: handleOpenChange }}>
      {children}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="fixed inset-0 bg-black/50" onClick={() => handleOpenChange(false)} />
          <div className="relative z-50 bg-white rounded-lg shadow-lg max-w-md w-full mx-4">
            {React.Children.map(children, child => 
              React.isValidElement(child) && child.type === DialogContent ? child : null
            )}
          </div>
        </div>
      )}
    </DialogContext.Provider>
  )
}

export const DialogTrigger = ({ children, asChild, ...props }) => {
  const { setIsOpen } = useContext(DialogContext)
  
  return (
    <div onClick={() => setIsOpen(true)} {...props}>
      {children}
    </div>
  )
}

export const DialogContent = ({ children, className, ...props }) => {
  return (
    <div className={`p-6 ${className}`} {...props}>
      {children}
    </div>
  )
}

export const DialogHeader = ({ children, className, ...props }) => {
  return (
    <div className={`mb-4 ${className}`} {...props}>
      {children}
    </div>
  )
}

export const DialogTitle = ({ children, className, ...props }) => {
  return (
    <h2 className={`text-lg font-semibold ${className}`} {...props}>
      {children}
    </h2>
  )
}

export const DialogDescription = ({ children, className, ...props }) => {
  return (
    <p className={`text-sm text-gray-600 ${className}`} {...props}>
      {children}
    </p>
  )
}
