"use client"

import { Github, Twitter, Heart } from "lucide-react"

export function Footer() {
  return (
    <footer className="py-12 px-4 bg-card border-t border-border">
      <div className="max-w-6xl mx-auto">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          {/* Logo & Description */}
          <div className="text-center md:text-left">
            <div className="flex items-center justify-center md:justify-start gap-2 mb-2">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-md">
                <span className="text-primary-foreground font-bold text-lg">த</span>
              </div>
              <span className="font-semibold text-foreground text-lg">Tamil Font Generator</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Preserving Tamil handwriting, one font at a time
            </p>
          </div>

          {/* Links */}
          <div className="flex items-center gap-8">
            <a
              href="#"
              className="text-muted-foreground hover:text-primary transition-colors text-sm font-medium"
            >
              About
            </a>
            <a
              href="#"
              className="text-muted-foreground hover:text-primary transition-colors text-sm font-medium"
            >
              Privacy
            </a>
            <a
              href="#"
              className="text-muted-foreground hover:text-primary transition-colors text-sm font-medium"
            >
              Terms
            </a>
          </div>

          {/* Social Links */}
          <div className="flex items-center gap-3">
            <a
              href="#"
              className="w-10 h-10 rounded-xl bg-secondary flex items-center justify-center text-muted-foreground hover:text-primary hover:bg-primary/10 transition-all"
              aria-label="GitHub"
            >
              <Github className="w-5 h-5" />
            </a>
            <a
              href="#"
              className="w-10 h-10 rounded-xl bg-secondary flex items-center justify-center text-muted-foreground hover:text-primary hover:bg-primary/10 transition-all"
              aria-label="Twitter"
            >
              <Twitter className="w-5 h-5" />
            </a>
          </div>
        </div>

        <div className="mt-10 pt-8 border-t border-border text-center">
          <p className="text-sm text-muted-foreground flex items-center justify-center gap-1.5">
            Made with <Heart className="w-4 h-4 text-primary fill-primary" /> for the Tamil community
          </p>
        </div>
      </div>
    </footer>
  )
}
