"use client"

import { useEffect, useState } from "react"
import { ArrowRight, Heart } from "lucide-react"
import { Button } from "@/components/ui/button"

interface HeroProps {
  onStartCreating: () => void
}

export function Hero({ onStartCreating }: HeroProps) {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center px-4 overflow-hidden">
      {/* Soft gradient background */}
      <div className="absolute inset-0 bg-background">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/10 via-background to-background" />
        <div 
          className={`absolute top-1/4 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-primary/5 rounded-full blur-3xl transition-opacity duration-1000 ${
            mounted ? "opacity-100" : "opacity-0"
          }`}
        />
        <div 
          className={`absolute bottom-1/4 right-1/4 w-[400px] h-[400px] bg-accent/5 rounded-full blur-3xl transition-opacity duration-1000 delay-300 ${
            mounted ? "opacity-100" : "opacity-0"
          }`}
        />
      </div>

      {/* Soft dotted pattern */}
      <div 
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `radial-gradient(circle at center, currentColor 1px, transparent 1px)`,
          backgroundSize: '24px 24px'
        }}
      />

      <div className="relative z-10 max-w-4xl mx-auto text-center">
        {/* Badge */}
        <div 
          className={`inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 mb-8 transition-all duration-700 ${
            mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
          }`}
        >
          <Heart className="w-4 h-4 text-primary fill-primary/30" />
          <span className="text-sm text-foreground/80 font-medium">Made with love for Tamil</span>
        </div>

        {/* Main headline */}
        <h1 
          className={`text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight mb-6 text-balance transition-all duration-700 delay-100 ${
            mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
          }`}
        >
          <span className="text-foreground">Turn Your </span>
          <span className="relative inline-block">
            <span className="bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent">
              Beautiful Handwriting
            </span>
            <svg 
              className="absolute -bottom-1 left-0 w-full h-2 text-primary/30"
              viewBox="0 0 100 8"
              preserveAspectRatio="none"
            >
              <path 
                d="M0,4 Q25,0 50,4 T100,4" 
                fill="none" 
                stroke="currentColor" 
                strokeWidth="3"
                strokeLinecap="round"
              />
            </svg>
          </span>
          <br />
          <span className="text-foreground">Into a Font</span>
        </h1>

        {/* Subheadline */}
        <p 
          className={`text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto mb-10 text-pretty leading-relaxed transition-all duration-700 delay-200 ${
            mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
          }`}
        >
          Your Tamil handwriting is unique and special. Let&apos;s preserve it forever 
          as a digital font you can use anywhere, anytime.
        </p>

        {/* CTA Buttons */}
        <div 
          className={`flex flex-col sm:flex-row items-center justify-center gap-4 transition-all duration-700 delay-300 ${
            mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
          }`}
        >
          <Button
            onClick={onStartCreating}
            size="lg"
            className="group relative px-8 py-6 text-lg bg-primary text-primary-foreground hover:bg-primary/90 rounded-2xl transition-all duration-300 hover:scale-105 shadow-lg shadow-primary/25 hover:shadow-xl hover:shadow-primary/30"
          >
            Start Creating Your Font
            <ArrowRight className="ml-2 w-5 h-5 transition-transform group-hover:translate-x-1" />
          </Button>
          <Button
            variant="outline"
            size="lg"
            className="px-8 py-6 text-lg border-2 border-border hover:border-primary/30 hover:bg-primary/5 rounded-2xl transition-all duration-300"
            asChild
          >
            <a href="#how-it-works">
              See How It Works
            </a>
          </Button>
        </div>

        {/* Stats */}
        <div 
          className={`grid grid-cols-3 gap-8 mt-20 pt-12 border-t border-border/50 transition-all duration-700 delay-500 ${
            mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
          }`}
        >
          {[
            { value: "67", label: "Tamil Characters", icon: "அ" },
            { value: "3", label: "Easy Steps", icon: "✓" },
            { value: "Free", label: "Forever", icon: "♡" },
          ].map((stat) => (
            <div key={stat.label} className="text-center group">
              <div className="text-3xl sm:text-4xl font-bold text-foreground group-hover:text-primary transition-colors">
                {stat.value}
              </div>
              <div className="text-sm text-muted-foreground mt-1">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Scroll indicator */}
      <div 
        className={`absolute bottom-8 left-1/2 -translate-x-1/2 transition-all duration-700 delay-700 ${
          mounted ? "opacity-100" : "opacity-0"
        }`}
      >
        <div className="w-6 h-10 rounded-full border-2 border-primary/30 flex justify-center p-2">
          <div className="w-1.5 h-2.5 bg-primary/50 rounded-full animate-bounce" />
        </div>
      </div>
    </section>
  )
}
