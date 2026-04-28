"use client"

import { useState, useRef } from "react"
import { Download, Grid, FileImage, Check, Printer } from "lucide-react"
import { Button } from "@/components/ui/button"

interface TemplateDownloadProps {
  onContinue: () => void
}

// Full 247-character Tamil alphabet (must match server.py order exactly)
const TAMIL_CHARS = [
  // Section 1: Pure Vowels (12)
  'அ','ஆ','இ','ஈ','உ','ஊ','எ','ஏ','ஐ','ஒ','ஓ','ஔ',
  // Section 2: Aytham (1)
  'ஃ',
  // Section 3: Pure Consonants (18)
  'க','ங','ச','ஞ','ட','ண','த','ந','ப','ம',
  'ய','ர','ல','வ','ழ','ள','ற','ன',
  // Section 4: Uyirmei — க row
  'க','கா','கி','கீ','கு','கூ','கெ','கே','கை','கொ','கோ','கௌ',
  // ங row
  'ங','ஙா','ஙி','ஙீ','ஙு','ஙூ','ஙெ','ஙே','ஙை','ஙொ','ஙோ','ஙௌ',
  // ச row
  'ச','சா','சி','சீ','சு','சூ','செ','சே','சை','சொ','சோ','சௌ',
  // ஞ row
  'ஞ','ஞா','ஞி','ஞீ','ஞு','ஞூ','ஞெ','ஞே','ஞை','ஞொ','ஞோ','ஞௌ',
  // ட row
  'ட','டா','டி','டீ','டு','டூ','டெ','டே','டை','டொ','டோ','டௌ',
  // ண row
  'ண','ணா','ணி','ணீ','ணு','ணூ','ணெ','ணே','ணை','ணொ','ணோ','ணௌ',
  // த row
  'த','தா','தி','தீ','து','தூ','தெ','தே','தை','தொ','தோ','தௌ',
  // ந row
  'ந','நா','நி','நீ','நு','நூ','நெ','நே','நை','நொ','நோ','நௌ',
  // ப row
  'ப','பா','பி','பீ','பு','பூ','பெ','பே','பை','பொ','போ','பௌ',
  // ம row
  'ம','மா','மி','மீ','மு','மூ','மெ','மே','மை','மொ','மோ','மௌ',
  // ய row
  'ய','யா','யி','யீ','யு','யூ','யெ','யே','யை','யொ','யோ','யௌ',
  // ர row
  'ர','ரா','ரி','ரீ','ரு','ரூ','ரெ','ரே','ரை','ரொ','ரோ','ரௌ',
  // ல row
  'ல','லா','லி','லீ','லு','லூ','லெ','லே','லை','லொ','லோ','லௌ',
  // வ row
  'வ','வா','வி','வீ','வு','வூ','வெ','வே','வை','வொ','வோ','வௌ',
  // ழ row
  'ழ','ழா','ழி','ழீ','ழு','ழூ','ழெ','ழே','ழை','ழொ','ழோ','ழௌ',
  // ள row
  'ள','ளா','ளி','ளீ','ளு','ளூ','ளெ','ளே','ளை','ளொ','ளோ','ளௌ',
  // ற row
  'ற','றா','றி','றீ','று','றூ','றெ','றே','றை','றொ','றோ','றௌ',
  // ன row
  'ன','னா','னி','னீ','னு','னூ','னெ','னே','னை','னொ','னோ','னௌ',
]

// Layout constants — must match server.py create_template_image exactly
const COLS = 6
const IMG_WIDTH = 1000
const X_START = 50
const Y_START = 50
const BOX_SIZE = 100
const SPACING = 50    // horizontal gap between boxes
const ROW_GAP = 50    // extra vertical gap (on top of BOX_SIZE)
const FONT_SIZE = 36
const SMALL_FONT_SIZE = 16

function buildPositions() {
  const positions: { char: string; x: number; y: number }[] = []
  let x = X_START
  let y = Y_START
  for (const char of TAMIL_CHARS) {
    positions.push({ char, x, y })
    x += BOX_SIZE + SPACING
    if (x > IMG_WIDTH - BOX_SIZE - SPACING) {
      x = X_START
      y += BOX_SIZE + SPACING + ROW_GAP
    }
  }
  return positions
}

function generateTemplateCanvas(): HTMLCanvasElement {
  const positions = buildPositions()
  const rows = Math.ceil(TAMIL_CHARS.length / COLS)
  const imgHeight = rows * (BOX_SIZE + SPACING + ROW_GAP) + Y_START + BOX_SIZE

  const canvas = document.createElement("canvas")
  canvas.width = IMG_WIDTH
  canvas.height = imgHeight
  const ctx = canvas.getContext("2d")!

  // White background
  ctx.fillStyle = "#ffffff"
  ctx.fillRect(0, 0, IMG_WIDTH, imgHeight)

  positions.forEach(({ char, x, y }, idx) => {
    // Draw box (light grey border — matches server.py #e0e0e0)
    ctx.strokeStyle = "#e0e0e0"
    ctx.lineWidth = 1
    ctx.strokeRect(x, y, BOX_SIZE, BOX_SIZE)

    // Draw box number inside top-left (grey)
    ctx.fillStyle = "#aaaaaa"
    ctx.font = `${SMALL_FONT_SIZE}px sans-serif`
    ctx.textAlign = "left"
    ctx.textBaseline = "top"
    ctx.fillText(String(idx + 1), x + 4, y + 4)

    // Draw Tamil character label above the box
    // Browser Canvas uses HarfBuzz → perfect Tamil shaping including split vowels
    ctx.fillStyle = "#000000"
    ctx.font = `${FONT_SIZE}px 'Nirmala UI', 'Latha', 'Vijaya', serif`
    ctx.textAlign = "center"
    ctx.textBaseline = "alphabetic"
    ctx.fillText(char, x + BOX_SIZE / 2, y - 8)
  })

  return canvas
}

export function TemplateDownload({ onContinue }: TemplateDownloadProps) {
  const [downloaded, setDownloaded] = useState(false)
  const [isHovering, setIsHovering] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)

  const handleDownload = () => {
    setIsGenerating(true)
    // Use setTimeout so the UI updates before the heavy canvas work
    setTimeout(() => {
      try {
        const canvas = generateTemplateCanvas()
        canvas.toBlob((blob) => {
          if (!blob) { setIsGenerating(false); return }
          const url = URL.createObjectURL(blob)
          const link = document.createElement("a")
          link.href = url
          link.download = "tamil-font-template.png"
          link.click()
          URL.revokeObjectURL(url)
          setDownloaded(true)
          setIsGenerating(false)
        }, "image/png")
      } catch (e) {
        console.error("Template generation failed", e)
        setIsGenerating(false)
      }
    }, 50)
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-foreground mb-2">Download Your Template</h2>
        <p className="text-muted-foreground">
          Print this template and fill each box with your beautiful handwriting
        </p>
      </div>

      {/* Template Preview Card */}
      <div
        className={`relative bg-secondary/50 border-2 border-dashed rounded-3xl p-8 transition-all duration-300 ${
          isHovering ? "border-primary bg-primary/5" : "border-border"
        }`}
        onMouseEnter={() => setIsHovering(true)}
        onMouseLeave={() => setIsHovering(false)}
      >
        <div className="flex flex-col lg:flex-row items-center gap-8">
          {/* Template visualization */}
          <div className="relative w-full lg:w-1/2 aspect-[2/5] max-h-[400px] bg-card rounded-2xl border border-border overflow-hidden shadow-sm">
            <div className="absolute inset-4">
              <div className="grid grid-cols-6 gap-1.5 h-full">
                {Array.from({ length: TAMIL_CHARS.length }).map((_, i) => (
                  <div
                    key={i}
                    className="bg-secondary/70 border border-border/50 rounded flex items-center justify-center text-muted-foreground/40 text-xs font-mono hover:bg-primary/10 hover:border-primary/30 transition-colors"
                  >
                    {i + 1}
                  </div>
                ))}
              </div>
            </div>

            {/* Overlay label */}
            <div className="absolute bottom-4 left-4 right-4 bg-card/90 backdrop-blur-sm rounded-xl p-4 border border-border">
              <div className="flex items-center gap-2 text-sm">
                <Grid className="w-4 h-4 text-primary" />
                <span className="font-semibold text-foreground">{TAMIL_CHARS.length} Tamil Characters</span>
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                12 vowels + 1 Aytham + 18 consonants + 216 Uyirmei combinations
              </p>
            </div>
          </div>

          {/* Info section */}
          <div className="flex-1 space-y-6">
            <div className="space-y-4">
              <div className="flex items-start gap-4 p-4 bg-secondary/50 rounded-xl">
                <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center shrink-0">
                  <FileImage className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground">High Resolution PNG</h3>
                  <p className="text-sm text-muted-foreground">1000 × auto pixels — perfect for printing</p>
                </div>
              </div>
              <div className="flex items-start gap-4 p-4 bg-secondary/50 rounded-xl">
                <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center shrink-0">
                  <Printer className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground">Print Ready</h3>
                  <p className="text-sm text-muted-foreground">All 247 Tamil characters correctly rendered</p>
                </div>
              </div>
            </div>

            {/* Download Button */}
            <Button
              onClick={handleDownload}
              disabled={isGenerating}
              size="lg"
              className={`w-full py-6 text-lg rounded-2xl transition-all duration-300 shadow-lg ${
                downloaded
                  ? "bg-primary text-primary-foreground shadow-primary/25"
                  : "bg-primary text-primary-foreground hover:bg-primary/90 shadow-primary/25 hover:shadow-xl"
              }`}
            >
              {isGenerating ? (
                <>Generating template…</>
              ) : downloaded ? (
                <>
                  <Check className="w-5 h-5 mr-2" />
                  Template Downloaded!
                </>
              ) : (
                <>
                  <Download className="w-5 h-5 mr-2" />
                  Download Template
                </>
              )}
            </Button>

            {downloaded && (
              <Button
                onClick={onContinue}
                variant="outline"
                size="lg"
                className="w-full py-6 text-lg rounded-2xl border-2 border-border hover:border-primary/30 hover:bg-primary/5"
              >
                Continue to Upload
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Instructions */}
      <div className="bg-secondary/50 rounded-2xl p-6 border border-border">
        <h3 className="font-semibold text-foreground mb-4">How to fill your template</h3>
        <ol className="space-y-3 text-sm text-muted-foreground">
          <li className="flex items-start gap-3">
            <span className="w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center shrink-0 text-xs font-bold">1</span>
            <span>Print the template on clean white A4 paper (may be multiple pages)</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center shrink-0 text-xs font-bold">2</span>
            <span>Use a black pen (0.5mm or thicker works best)</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center shrink-0 text-xs font-bold">3</span>
            <span>Write each character centered in its box with consistent size</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center shrink-0 text-xs font-bold">4</span>
            <span>Scan or photograph with good lighting when done</span>
          </li>
        </ol>
      </div>
    </div>
  )
}
