"use client"

import { useState, useEffect } from "react"
import { Download, Cloud, Check, Loader2, Type, Sparkles, Heart } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { FieldGroup, Field, FieldLabel } from "@/components/ui/field"

interface FontPreviewProps {
  onNext: () => void
  fontUrl: string
}

export function FontPreview({ onNext, fontUrl }: FontPreviewProps) {
  const [previewText, setPreviewText] = useState("அஆஇஈஉஊஎஏஐஒஓஃ")
  const [authorName, setAuthorName] = useState("")
  const [fontName, setFontName] = useState("My Handwritten Font")
  const [isSaving, setIsSaving] = useState(false)
  const [isSaved, setIsSaved] = useState(false)
  const [fontLoaded, setFontLoaded] = useState(false)

  const sampleWords = [
    { label: "Vowels", word: "அஆஇஈஉஊஎஏஐஒஓஃ" },
    { label: "Consonants 1", word: "கஙசஞடணதநபம" },
    { label: "Consonants 2", word: "யரலவழளறன" }
  ]

  useEffect(() => {
    // Dynamically inject @font-face rule
    const styleId = "custom-tamil-font"
    let styleElement = document.getElementById(styleId) as HTMLStyleElement | null
    
    if (!styleElement) {
      styleElement = document.createElement("style")
      styleElement.id = styleId
      document.head.appendChild(styleElement)
    }

    // In production, fontUrl would be a blob URL or base64 from your Python backend
    // For now, we'll use a fallback font for demo purposes
    const fontFaceRule = `
      @font-face {
        font-family: 'CustomTamilFont';
        src: url('/TamilHandWritten.ttf?t=${Date.now()}') format('truetype');
        font-weight: normal;
        font-style: normal;
      }
    `
    
    styleElement.textContent = fontFaceRule
    
    // Simulate font loading
    setTimeout(() => {
      setFontLoaded(true)
    }, 500)

    return () => {
      // Cleanup
      const el = document.getElementById(styleId)
      if (el) el.remove()
    }
  }, [fontUrl])

  const handleSaveToCloud = async () => {
    if (!authorName || !fontName) return
    
    setIsSaving(true)
    
    try {
      const response = await fetch('http://localhost:8000/api/save-font', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          authorName,
          fontName,
          fontUrl: fontUrl,
        }),
      })
      
      if (response.ok) {
        setIsSaved(true)
      } else {
        alert("Failed to save to MongoDB")
      }
    } catch(e) {
      console.error(e)
      alert("Failed to connect to backend")
    }
    setIsSaving(false)
  }

  const handleDownloadFont = async () => {
    try {
      const response = await fetch(fontUrl)
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${fontName || 'TamilHandwritten'}.ttf`
      link.click()
      window.URL.revokeObjectURL(url)
    } catch (e) {
      console.error(e)
    }
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary mb-4">
          <Sparkles className="w-4 h-4" />
          <span className="text-sm font-medium">Your Font is Ready!</span>
        </div>
        <h2 className="text-2xl font-bold text-foreground mb-2">Preview Your Creation</h2>
        <p className="text-muted-foreground">
          See your handwriting come to life as a digital font
        </p>
      </div>

      {/* Live Preview Section */}
      <div className="bg-secondary/30 rounded-3xl border border-border overflow-hidden">
        <div className="p-6 border-b border-border">
          <div className="flex items-center gap-2 mb-2">
            <Type className="w-5 h-5 text-primary" />
            <h3 className="font-semibold text-foreground">Live Preview</h3>
          </div>
          <p className="text-sm text-muted-foreground">
            Type below to see your handwriting in action
          </p>
        </div>
        
        {/* Preview Area */}
        <div className="p-8 bg-card min-h-[200px] flex items-center justify-center">
          {fontLoaded ? (
            <p
              className="text-4xl sm:text-5xl md:text-6xl text-center text-foreground leading-relaxed transition-all duration-300"
              style={{
                fontFamily: "'CustomTamilFont', 'Noto Sans Tamil', sans-serif",
              }}
            >
              {previewText || "Start typing..."}
            </p>
          ) : (
            <div className="flex items-center gap-3 text-muted-foreground">
              <Loader2 className="w-5 h-5 animate-spin text-primary" />
              <span>Loading your font...</span>
            </div>
          )}
        </div>
        
        {/* Input Area */}
        <div className="p-6 border-t border-border bg-secondary/30">
          <Input
            value={previewText}
            onChange={(e) => setPreviewText(e.target.value)}
            placeholder="Type Tamil text here to preview..."
            className="text-lg h-14 bg-card border-border focus:ring-primary rounded-xl"
          />
        </div>
      </div>

      {/* Sample Texts */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-sm text-muted-foreground mr-2">Try these:</span>
        {sampleWords.map((sample) => (
          <button
            key={sample.label}
            onClick={() => setPreviewText(sample.word)}
            className="px-4 py-2 text-sm rounded-xl bg-secondary hover:bg-primary/10 hover:text-primary text-foreground transition-all border border-transparent hover:border-primary/30"
          >
            {sample.label}
          </button>
        ))}
      </div>

      {/* Save to Cloud Section */}
      <div className="bg-secondary/30 rounded-3xl border border-border p-6 space-y-6">
        <div className="flex items-center gap-2">
          <Cloud className="w-5 h-5 text-primary" />
          <h3 className="font-semibold text-foreground">Save to Cloud</h3>
        </div>

        <FieldGroup>
          <Field>
            <FieldLabel htmlFor="authorName">Your Name</FieldLabel>
            <Input
              id="authorName"
              value={authorName}
              onChange={(e) => setAuthorName(e.target.value)}
              placeholder="Enter your name"
              className="bg-card border-border rounded-xl"
              disabled={isSaved}
            />
          </Field>
          <Field>
            <FieldLabel htmlFor="fontName">Font Name</FieldLabel>
            <Input
              id="fontName"
              value={fontName}
              onChange={(e) => setFontName(e.target.value)}
              placeholder="Give your font a name"
              className="bg-card border-border rounded-xl"
              disabled={isSaved}
            />
          </Field>
        </FieldGroup>

        <div className="flex flex-col sm:flex-row gap-4">
          <Button
            onClick={handleSaveToCloud}
            disabled={!authorName || !fontName || isSaving || isSaved}
            size="lg"
            className={`flex-1 py-6 rounded-2xl transition-all duration-300 shadow-lg ${
              isSaved
                ? "bg-primary text-primary-foreground shadow-primary/25"
                : "bg-primary text-primary-foreground hover:bg-primary/90 shadow-primary/25"
            }`}
          >
            {isSaving ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Saving...
              </>
            ) : isSaved ? (
              <>
                <Check className="w-5 h-5 mr-2" />
                Saved to Cloud!
              </>
            ) : (
              <>
                <Cloud className="w-5 h-5 mr-2" />
                Save to Cloud
              </>
            )}
          </Button>
          
          <Button
            onClick={handleDownloadFont}
            variant="outline"
            size="lg"
            className="flex-1 py-6 rounded-2xl border-2 border-border hover:border-primary/30 hover:bg-primary/5"
          >
            <Download className="w-5 h-5 mr-2" />
            Download TTF
          </Button>
        </div>

        {isSaved && (
          <div className="flex items-center gap-3 p-4 bg-primary/10 border border-primary/20 rounded-2xl">
            <Heart className="w-5 h-5 text-primary fill-primary shrink-0" />
            <p className="text-sm text-foreground">
              Your font has been saved! You can access it anytime from your library.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
