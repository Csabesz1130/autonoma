import React from "react"

interface LabelProps extends React.LabelHTMLAttributes<HTMLLabelElement> {
  htmlFor?: string
  children?: React.ReactNode
}

export const Label: React.FC<LabelProps> = ({ 
  htmlFor, 
  children, 
  className = "", 
  ...props 
}) => {
  return (
    <label 
      htmlFor={htmlFor}
      className={`text-sm font-medium leading-none ${className}`}
      {...props}
    >
      {children}
    </label>
  )
}