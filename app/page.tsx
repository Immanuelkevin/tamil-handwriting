"use client"

import { useState } from "react"
import { Hero } from "@/components/hero"
import { WizardFlow } from "@/components/wizard-flow"
import { HowItWorks } from "@/components/how-it-works"
import { Footer } from "@/components/footer"

export default function Home() {
  const [showWizard, setShowWizard] = useState(false)

  if (showWizard) {
    return <WizardFlow onBack={() => setShowWizard(false)} />
  }

  return (
    <main className="min-h-screen bg-background">
      <Hero onStartCreating={() => setShowWizard(true)} />
      <HowItWorks />
      <Footer />
    </main>
  )
}
