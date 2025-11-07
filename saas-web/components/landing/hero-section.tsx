import { Button } from "@/components/ui/button"
import { ArrowRight, PlayCircle } from "lucide-react"
import Link from "next/link"

export function HeroSection() {
  return (
    <section className="relative overflow-hidden bg-background py-20 sm:py-32">
      {/* Background gradient */}
      <div className="absolute inset-0 -z-10 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]" />
      <div className="absolute left-0 right-0 top-0 -z-10 m-auto h-[310px] w-[310px] rounded-full bg-primary/20 blur-[100px]" />

      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-4xl text-center">
          {/* Badge */}
          <div className="mb-8 inline-flex items-center rounded-full border bg-card px-3 py-1 text-sm">
            <span className="mr-2 text-xs">✨</span>
            <span className="text-muted-foreground">AI-Powered Video Notes</span>
          </div>

          {/* Main heading */}
          <h1 className="mb-6 text-4xl font-bold tracking-tight text-foreground sm:text-6xl lg:text-7xl">
            Transform Videos into
            <span className="block bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
              Structured Notes
            </span>
          </h1>

          {/* Subheading */}
          <p className="mx-auto mb-10 max-w-2xl text-lg text-muted-foreground sm:text-xl">
            Let AI extract key insights from your videos. Supports YouTube, Bilibili, TikTok, and more.
            Generate markdown notes with screenshots, timestamps, and mind maps in minutes.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Button asChild size="lg" className="w-full sm:w-auto">
              <Link href="/auth/register">
                Get Started Free
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg" className="w-full sm:w-auto">
              <Link href="#demo">
                <PlayCircle className="mr-2 h-4 w-4" />
                Watch Demo
              </Link>
            </Button>
          </div>

          {/* Social proof */}
          <div className="mt-12 text-sm text-muted-foreground">
            <p>Trusted by 10,000+ students and professionals worldwide</p>
          </div>
        </div>

        {/* Hero Image / Demo */}
        <div className="relative mx-auto mt-16 max-w-5xl">
          <div className="overflow-hidden rounded-xl border bg-card shadow-2xl">
            <div className="aspect-video bg-muted/50 flex items-center justify-center">
              <PlayCircle className="h-20 w-20 text-muted-foreground/50" />
            </div>
          </div>

          {/* Floating elements */}
          <div className="absolute -left-4 top-1/4 hidden rounded-lg border bg-card p-4 shadow-lg lg:block">
            <div className="mb-2 text-xs font-semibold">✅ Video Downloaded</div>
            <div className="text-xs text-muted-foreground">Processing: 45%</div>
          </div>
          <div className="absolute -right-4 top-1/3 hidden rounded-lg border bg-card p-4 shadow-lg lg:block">
            <div className="mb-2 text-xs font-semibold">🎯 AI Analysis</div>
            <div className="text-xs text-muted-foreground">Generating notes...</div>
          </div>
        </div>
      </div>
    </section>
  )
}
