"use client"

import { useState, useCallback } from "react"
import { Upload, FileImage, X, Check, AlertCircle, Loader2, Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"

interface TemplateUploadProps {
  onUpload: (file: File) => Promise<void>
  isGenerating: boolean
}

export function TemplateUpload({ onUpload, isGenerating }: TemplateUploadProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const validateFile = (file: File): boolean => {
    setError(null)
    
    // Check file type
    if (!file.type.startsWith('image/')) {
      setError('Please upload an image file (PNG, JPG, etc.)')
      return false
    }
    
    // Check file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB')
      return false
    }
    
    return true
  }

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile && validateFile(droppedFile)) {
      setFile(droppedFile)
      setPreview(URL.createObjectURL(droppedFile))
    }
  }, [])

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile && validateFile(selectedFile)) {
      setFile(selectedFile)
      setPreview(URL.createObjectURL(selectedFile))
    }
  }, [])

  const handleRemove = useCallback(() => {
    setFile(null)
    setPreview(null)
    setError(null)
  }, [])

  const handleUpload = async () => {
    if (!file) return
    await onUpload(file)
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-foreground mb-2">Upload Your Template</h2>
        <p className="text-muted-foreground">
          Share your completed template and watch the magic happen
        </p>
      </div>

      {/* Upload Zone */}
      {!file ? (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`relative border-2 border-dashed rounded-3xl p-12 text-center transition-all duration-300 ${
            isDragging
              ? "border-primary bg-primary/10 scale-[1.02]"
              : error
              ? "border-destructive bg-destructive/5"
              : "border-border hover:border-primary/50 bg-secondary/30"
          }`}
        >
          <input
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
          
          <div className="space-y-4">
            <div className={`w-20 h-20 mx-auto rounded-2xl flex items-center justify-center transition-all duration-300 ${
              isDragging ? "bg-primary/20" : "bg-secondary"
            }`}>
              <Upload className={`w-10 h-10 transition-colors ${
                isDragging ? "text-primary" : "text-muted-foreground"
              }`} />
            </div>
            
            <div>
              <p className="text-xl font-semibold text-foreground">
                {isDragging ? "Drop it here!" : "Drag & drop your template"}
              </p>
              <p className="text-sm text-muted-foreground mt-2">
                or click to browse - PNG, JPG up to 10MB
              </p>
            </div>
          </div>
        </div>
      ) : (
        /* File Preview */
        <div className="relative bg-secondary/30 rounded-3xl border border-border overflow-hidden">
          <div className="flex flex-col md:flex-row">
            {/* Image Preview */}
            <div className="relative w-full md:w-1/2 aspect-[2/5] max-h-[400px] bg-card">
              {preview && (
                <img
                  src={preview}
                  alt="Template preview"
                  className="w-full h-full object-contain p-4"
                />
              )}
              <div className="absolute top-3 right-3">
                <Button
                  variant="secondary"
                  size="icon"
                  onClick={handleRemove}
                  className="w-8 h-8 rounded-full bg-card/90 backdrop-blur-sm hover:bg-destructive hover:text-destructive-foreground shadow-md"
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </div>

            {/* File Info & Actions */}
            <div className="flex-1 p-6 space-y-6">
              <div className="flex items-start gap-4 p-4 bg-card rounded-2xl border border-border">
                <div className="w-12 h-12 rounded-xl bg-primary/20 flex items-center justify-center">
                  <FileImage className="w-6 h-6 text-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-foreground truncate">{file.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
                <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center">
                  <Check className="w-4 h-4 text-primary" />
                </div>
              </div>

              <div className="space-y-3 p-4 bg-card rounded-2xl border border-border">
                <div className="flex items-center gap-2 text-sm">
                  <Check className="w-4 h-4 text-primary" />
                  <span className="text-foreground">Valid image format</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Check className="w-4 h-4 text-primary" />
                  <span className="text-foreground">File size within limits</span>
                </div>
              </div>

              <Button
                onClick={handleUpload}
                disabled={isGenerating}
                size="lg"
                className="w-full py-6 text-lg rounded-2xl bg-primary text-primary-foreground hover:bg-primary/90 transition-all duration-300 shadow-lg shadow-primary/25"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Creating Your Font...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5 mr-2" />
                    Generate My Font
                  </>
                )}
              </Button>

              {isGenerating && (
                <div className="space-y-3">
                  <div className="h-2 bg-secondary rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-primary to-accent rounded-full animate-pulse w-2/3" />
                  </div>
                  <p className="text-sm text-muted-foreground text-center">
                    Extracting characters and building your unique font...
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="flex items-center gap-3 p-4 bg-destructive/10 border border-destructive/30 rounded-2xl">
          <AlertCircle className="w-5 h-5 text-destructive shrink-0" />
          <p className="text-sm text-destructive">{error}</p>
        </div>
      )}

      {/* Tips */}
      <div className="bg-secondary/50 rounded-2xl p-6 border border-border">
        <h3 className="font-semibold text-foreground mb-3">Tips for best results</h3>
        <ul className="space-y-2.5 text-sm text-muted-foreground">
          <li className="flex items-start gap-2">
            <span className="text-primary font-bold">1.</span>
            <span>Ensure good, even lighting when scanning or photographing</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-primary font-bold">2.</span>
            <span>Keep the template flat and avoid shadows or creases</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-primary font-bold">3.</span>
            <span>Higher resolution images produce better font quality</span>
          </li>
        </ul>
      </div>
    </div>
  )
}
