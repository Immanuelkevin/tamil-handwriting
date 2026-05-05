"use client"

import { useEffect, useState, useRef } from "react"
import { Download, Pencil, Upload, Sparkles, ArrowRight } from "lucide-react"

const STEPS = [
  {
    icon: Download,
    title: "Download Template",
    description: "Get our beautiful 67-character Tamil grid. Print it on white paper and grab your favorite pen.",
    color: "from-pink-400 to-rose-500",
  },
  {
    icon: Pencil,
    title: "Write with Love",
    description: "Fill each box with your handwriting. Take your time - this is your unique style we are capturing.",
    color: "from-rose-400 to-pink-500",
  },
  {
    icon: Upload,
    title: "Upload Your Work",
    description: "Scan or photograph your template. Good lighting helps us capture every beautiful curve and stroke.",
    color: "from-pink-500 to-fuchsia-500",
  },
  {
    icon: Sparkles,
    title: "Get Your Font",
    description: "In seconds, your personal Tamil font is ready. Install it anywhere and type in your own handwriting.",
    color: "from-fuchsia-400 to-pink-400",
  },
]

export function HowItWorks() {
  const [isVisible, setIsVisible] = useState(false)
  const sectionRef = useRef<HTMLElement>(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
        }
      },
      { threshold: 0.1 }
    )

    if (sectionRef.current) {
      observer.observe(sectionRef.current)
    }

    return () => observer.disconnect()
  }, [])

  return (
    <section
      ref={sectionRef}
      id="how-it-works"
      className="py-24 px-4 bg-secondary/30 relative overflow-hidden"
    >
      {/* Soft decorative background */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] bg-primary/5 rounded-full blur-3xl" />

      <div className="max-w-6xl mx-auto relative">
        {/* Header */}
        <div 
          className={`text-center mb-16 transition-all duration-700 ${
            isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"
          }`}
        >
          <span className="inline-block px-4 py-1.5 rounded-full bg-primary/10 text-primary text-sm font-medium mb-4">
            Simple Process
          </span>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-foreground mb-4 text-balance">
            How It Works
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto text-pretty">
            Four simple steps to preserve your handwriting forever
          </p>
        </div>

        {/* Steps Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {STEPS.map((step, index) => (
            <div
              key={step.title}
              className={`group relative transition-all duration-700 ${
                isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"
              }`}
              style={{ transitionDelay: `${index * 100 + 200}ms` }}
            >
              {/* Card */}
              <div className="relative h-full bg-card border border-border rounded-3xl p-6 hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5 transition-all duration-300">
                {/* Step number */}
                <div className="absolute -top-3 -left-3 w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-bold shadow-md">
                  {index + 1}
                </div>

                {/* Icon */}
                <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${step.color} flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300 shadow-lg`}>
                  <step.icon className="w-7 h-7 text-white" />
                </div>

                {/* Content */}
                <h3 className="text-xl font-semibold text-foreground mb-3">{step.title}</h3>
                <p className="text-muted-foreground text-sm leading-relaxed">{step.description}</p>

                {/* Arrow connector (hidden on last item and mobile) */}
                {index < STEPS.length - 1 && (
                  <div className="hidden lg:flex absolute -right-3 top-1/2 -translate-y-1/2 z-10">
                    <div className="w-6 h-6 rounded-full bg-card border-2 border-primary/30 flex items-center justify-center">
                      <ArrowRight className="w-3 h-3 text-primary" />
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Features highlight */}
        <div 
          className={`mt-16 grid sm:grid-cols-3 gap-6 transition-all duration-700 delay-700 ${
            isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"
          }`}
        >
          {[
            { label: "Processing Time", value: "Under 30 seconds" },
            { label: "Font Format", value: "TrueType (.ttf)" },
            { label: "Cloud Storage", value: "Save & access anywhere" },
          ].map((feature) => (
            <div key={feature.label} className="text-center p-6 bg-card rounded-2xl border border-border">
              <div className="text-xl font-bold text-foreground">{feature.value}</div>
              <div className="text-sm text-muted-foreground mt-1">{feature.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
