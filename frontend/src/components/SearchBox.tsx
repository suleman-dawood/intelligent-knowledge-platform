import { MagnifyingGlassIcon } from '@heroicons/react/24/outline'
import React, { ChangeEvent, FormEvent } from 'react'

interface SearchBoxProps {
  value: string
  onChange: (e: ChangeEvent<HTMLInputElement>) => void
  onSubmit: (e: FormEvent) => void
  placeholder?: string
  fullWidth?: boolean
  className?: string
}

export default function SearchBox({
  value,
  onChange,
  onSubmit,
  placeholder = 'Search...',
  fullWidth = false,
  className = '',
}: SearchBoxProps) {
  return (
    <form onSubmit={onSubmit} className={`${fullWidth ? 'w-full' : 'max-w-lg'} ${className}`}>
      <div className="relative">
        <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
          <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
        </div>
        <input
          type="text"
          value={value}
          onChange={onChange}
          className="block w-full rounded-md border-0 bg-white py-3 pl-10 pr-3 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-600 sm:text-sm sm:leading-6"
          placeholder={placeholder}
        />
        <button
          type="submit"
          className="absolute inset-y-0 right-0 flex items-center pr-3"
        >
          <span className="sr-only">Search</span>
          <div className="rounded-md bg-primary-600 p-1 text-white hover:bg-primary-700">
            <MagnifyingGlassIcon className="h-5 w-5" aria-hidden="true" />
          </div>
        </button>
      </div>
    </form>
  )
} 