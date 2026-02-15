import React, { useState } from 'react'
import { Upload, X, Image } from 'lucide-react'

interface PhotosProps {
  formData: {
    message: {
      title: string
      content: string
      recipient: string
    }
  }
  setFormData: React.Dispatch<React.SetStateAction<{
    password: string
    confirmPassword: string
    accounts: unknown[]
    trustedPerson: { name: string; email: string; phone: string; relationship: string }
    message: { title: string; content: string; recipient: string }
  }>>
  onNext: () => void
}

export const Photos: React.FC<PhotosProps> = ({ formData, setFormData }) => {
  const [photos, setPhotos] = useState<string[]>([])
  const [dragActive, setDragActive] = useState(false)

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragActive(false)
    const files = Array.from(e.dataTransfer.files)
    processFiles(files)
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    processFiles(files)
  }

  const processFiles = (files: File[]) => {
    files.forEach(file => {
      if (file.type.startsWith('image/')) {
        const reader = new FileReader()
        reader.onload = (event) => {
          if (event.target?.result) {
            setPhotos(prev => [...prev, event.target?.result as string])
          }
        }
        reader.readAsDataURL(file)
      }
    })
  }

  const removePhoto = (index: number) => {
    setPhotos(prev => prev.filter((_, i) => i !== index))
  }

  return (
    <div>
      <h2 className="text-2xl font-semibold text-warmGray-900 dark:text-warmGray-100 mb-2">
        Attach a meaningful photo (optional)
      </h2>
      <p className="text-warmGray-600 dark:text-warmGray-400 mb-6">
        Add one photo to include with your message. It will be stored securely on your device.
      </p>

      <div className="space-y-4">
        {photos.length > 0 ? (
          <div className="grid grid-cols-3 gap-4">
            {photos.map((photo, index) => (
              <div key={index} className="relative aspect-square rounded-lg overflow-hidden">
                <img
                  src={photo}
                  alt={`Photo ${index + 1}`}
                  className="w-full h-full object-cover"
                />
                <button
                  onClick={() => removePhoto(index)}
                  className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full hover:bg-red-600"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div
            onDrop={handleDrop}
            onDragOver={(e) => { e.preventDefault(); setDragActive(true) }}
            onDragLeave={() => setDragActive(false)}
            className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
              dragActive
                ? 'border-sage bg-sage/5'
                : 'border-warmGray-300 dark:border-warmGray-600'
            }`}
          >
            <Image className="w-12 h-12 mx-auto text-warmGray-400 mb-4" />
            <p className="text-warmGray-600 dark:text-warmGray-400 mb-2">
              Drag and drop a photo here, or
            </p>
            <label className="inline-flex items-center gap-2 px-4 py-2 bg-sage text-white rounded-lg hover:bg-sage-dark cursor-pointer transition-colors">
              <Upload className="w-4 h-4" />
              Browse Files
              <input
                type="file"
                accept="image/*"
                onChange={handleChange}
                className="hidden"
              />
            </label>
          </div>
        )}

        <div className="bg-warmGray-50 dark:bg-warmGray-700 rounded-lg p-4">
          <p className="text-sm text-warmGray-600 dark:text-warmGray-300">
            🔒 <strong>Privacy note:</strong> Photos are stored locally on your device and encrypted
            with your master password. They never leave your device.
          </p>
        </div>
      </div>
    </div>
  )
}
