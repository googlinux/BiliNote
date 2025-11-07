import { Brain, Globe, Image, Zap, FileText, Network } from "lucide-react"

const features = [
  {
    icon: Brain,
    title: "AI-Powered Summarization",
    description: "Advanced AI models extract key insights and generate structured notes automatically.",
  },
  {
    icon: Globe,
    title: "Multi-Platform Support",
    description: "Works with YouTube, Bilibili, TikTok, Kuaishou, and local video files.",
  },
  {
    icon: Image,
    title: "Smart Screenshots",
    description: "Automatically capture key moments with timestamped screenshots.",
  },
  {
    icon: Zap,
    title: "Lightning Fast",
    description: "Generate comprehensive notes in minutes, not hours.",
  },
  {
    icon: FileText,
    title: "Markdown Export",
    description: "Export to clean markdown format compatible with Notion, Obsidian, and more.",
  },
  {
    icon: Network,
    title: "Mind Map Generation",
    description: "Visualize video content with automatically generated mind maps.",
  },
]

export function FeaturesSection() {
  return (
    <section id="features" className="bg-muted/50 py-20 sm:py-32">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="mb-4 text-3xl font-bold tracking-tight sm:text-4xl">
            Everything you need for video notes
          </h2>
          <p className="text-lg text-muted-foreground">
            Powerful features to help you learn faster and retain more from video content.
          </p>
        </div>

        <div className="mx-auto mt-16 max-w-6xl">
          <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((feature, index) => (
              <div
                key={index}
                className="group relative rounded-lg border bg-card p-6 shadow-sm transition-all hover:shadow-md"
              >
                <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                  <feature.icon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="mb-2 text-xl font-semibold">{feature.title}</h3>
                <p className="text-muted-foreground">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
