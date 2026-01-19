import { ReactNode } from 'react'
import './Card.css'

interface CardProps {
  children: ReactNode
  title?: string | ReactNode
  className?: string
}

export default function Card({ children, title, className = '' }: CardProps) {
  return (
    <div className={`card ${className}`}>
      {title && (
        <h3 className="card-title">
          {typeof title === 'string' ? title : title}
        </h3>
      )}
      <div className="card-content">{children}</div>
    </div>
  )
}

