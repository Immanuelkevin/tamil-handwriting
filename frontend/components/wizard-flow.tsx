"use client"

import { useState, useCallback, useEffect } from "react"
import { Download, Upload, Check, Cloud, ChevronLeft, ChevronRight, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { TemplateDownload } from "@/components/steps/template-download"
import { TemplateUpload } from "@/components/steps/template-upload"
import { FontPreview } from "@/components/steps/font-preview"

type Step = 1 | 2 | 3

interface WizardFlowProps {
  onBack: () => void
}

const STEPS = [
  { id: 1 as const, title: "Download Template", icon: Download, description: "Get your character grid" },
  { id: 2 as const, title: "Upload Your Work", icon: Upload, description: "Share your handwriting" },
  { id: 3 as const, title: "Preview & Save", icon: Cloud, description: "See the magic happen" },
]

export function WizardFlow({ onBack }: WizardFlowProps) {
  const [currentStep, setCurrentStep] = useState<Step>(1)
  const [fontData, setFontData] = useState<{ url: string; name: string } | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const handleTemplateUploaded = useCallback(async (file: File) => {
    setIsGenerating(true)
    
    try {
      const formData = new FormData()
      formData.append('template', file)
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/generate-font`, {
        method: 'POST',
        body: formData,
      })
      
      if (!response.ok) {
        throw new Error("Failed to generate font")
      }
      
      const data = await response.json()
      setFontData({ url: data.fontUrl, name: data.fontName })
    } catch (e) {
      console.error(e)
      alert("Error generating font! Check your backend server.")
    }
    
    setIsGenerating(false)
    setCurrentStep(3)
  }, [])

  const goToStep = (step: Step) => {
    if (step === 3 && !fontData) return // Can't go to preview without font data
    setCurrentStep(step)
  }

  const canGoNext = () => {
    if (currentStep === 1) return true
    if (currentStep === 2) return !!fontData
    return false
  }

  return (
    <section className="min-h-screen bg-background py-12 px-4">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div 
          className={`mb-12 transition-all duration-500 ${
            mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
          }`}
        >
          <Button
            variant="ghost"
            onClick={onBack}
            className="mb-6 text-muted-foreground hover:text-foreground hover:bg-primary/5"
          >
            <ChevronLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Button>
          <h1 className="text-3xl sm:text-4xl font-bold text-foreground">
            Let&apos;s Create Your Font
          </h1>
          <p className="text-muted-foreground mt-2">
            Just three simple steps to turn your handwriting into something beautiful
          </p>
        </div>

        {/* Step Indicator */}
        <div 
          className={`mb-12 transition-all duration-500 delay-100 ${
            mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
          }`}
        >
          <div className="flex items-center justify-between">
            {STEPS.map((step, index) => (
              <div key={step.id} className="flex items-center flex-1">
                {/* Step circle */}
                <button
                  onClick={() => goToStep(step.id)}
                  disabled={step.id === 3 && !fontData}
                  className={`relative flex flex-col items-center group ${
                    step.id === 3 && !fontData ? 'cursor-not-allowed' : 'cursor-pointer'
                  }`}
                >
                  <div
                    className={`w-14 h-14 rounded-2xl flex items-center justify-center transition-all duration-300 ${
                      currentStep === step.id
                        ? "bg-primary text-primary-foreground scale-110 shadow-lg shadow-primary/30"
                        : currentStep > step.id
                        ? "bg-primary/20 text-primary"
                        : "bg-secondary text-muted-foreground"
                    }`}
                  >
                    {currentStep > step.id ? (
                      <Check className="w-6 h-6" />
                    ) : isGenerating && step.id === 2 ? (
                      <Loader2 className="w-6 h-6 animate-spin" />
                    ) : (
                      <step.icon className="w-6 h-6" />
                    )}
                  </div>
                  <div className="mt-3 text-center hidden sm:block">
                    <div className={`text-sm font-semibold transition-colors ${
                      currentStep === step.id ? "text-primary" : "text-foreground"
                    }`}>
                      {step.title}
                    </div>
                    <div className="text-xs text-muted-foreground mt-0.5">
                      {step.description}
                    </div>
                  </div>
                </button>

                {/* Connector line */}
                {index < STEPS.length - 1 && (
                  <div className="flex-1 h-1 mx-4 bg-secondary rounded-full relative overflow-hidden">
                    <div
                      className={`absolute inset-y-0 left-0 bg-primary rounded-full transition-all duration-500 ${
                        currentStep > step.id ? "w-full" : "w-0"
                      }`}
                    />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Step Content */}
        <div 
          className={`transition-all duration-500 delay-200 ${
            mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
          }`}
        >
          <div className="bg-card border border-border rounded-3xl p-6 sm:p-8 shadow-sm">
            {currentStep === 1 && (
              <TemplateDownload onContinue={() => setCurrentStep(2)} />
            )}
            {currentStep === 2 && (
              <TemplateUpload 
                onUpload={handleTemplateUploaded} 
                isGenerating={isGenerating}
              />
            )}
            {currentStep === 3 && fontData && (
              <FontPreview fontUrl={fontData.url} onNext={() => {}} />
            )}
          </div>
        </div>

        {/* Navigation Buttons */}
        <div 
          className={`flex justify-between mt-8 transition-all duration-500 delay-300 ${
            mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
          }`}
        >
          <Button
            variant="outline"
            onClick={() => setCurrentStep((prev) => (prev > 1 ? (prev - 1) as Step : prev))}
            disabled={currentStep === 1}
            className="border-2 border-border hover:border-primary/30 hover:bg-primary/5 rounded-xl"
          >
            <ChevronLeft className="w-4 h-4 mr-2" />
            Previous
          </Button>
          {currentStep < 3 && (
            <Button
              onClick={() => setCurrentStep((prev) => (prev < 3 ? (prev + 1) as Step : prev))}
              disabled={!canGoNext()}
              className="bg-primary text-primary-foreground hover:bg-primary/90 rounded-xl shadow-md shadow-primary/20"
            >
              Next Step
              <ChevronRight className="w-4 h-4 ml-2" />
            </Button>
          )}
        </div>
      </div>
    </section>
  )
}
