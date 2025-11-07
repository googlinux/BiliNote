"use client"

import { useState } from "react"
import { ChevronDown } from "lucide-react"
import { cn } from "@/lib/utils"

const faqs = [
  {
    question: "What video platforms are supported?",
    answer:
      "BiliNote supports YouTube, Bilibili, TikTok, Kuaishou, Xiaoyuzhoufm, and local video files. We're constantly adding support for more platforms.",
  },
  {
    question: "How does the AI generate notes?",
    answer:
      "We use advanced AI models like GPT-4 and Claude to transcribe and analyze video content. The AI extracts key insights, generates summaries, and creates structured notes with timestamps and screenshots.",
  },
  {
    question: "Can I export my notes?",
    answer:
      "Yes! You can export your notes in Markdown format, which is compatible with Notion, Obsidian, Roam Research, and most note-taking apps. Pro and Enterprise plans also support PDF export.",
  },
  {
    question: "Is there a free trial?",
    answer:
      "Absolutely! All paid plans come with a 14-day free trial. No credit card required. You can also use our Free plan indefinitely with limited features.",
  },
  {
    question: "What languages are supported for transcription?",
    answer:
      "We support transcription in 50+ languages including English, Chinese, Spanish, French, German, Japanese, Korean, and more. The AI can generate notes in your preferred language.",
  },
  {
    question: "Can I cancel my subscription anytime?",
    answer:
      "Yes, you can cancel your subscription at any time from your account settings. There are no cancellation fees, and you'll retain access until the end of your billing period.",
  },
  {
    question: "Do you offer refunds?",
    answer:
      "We offer a 30-day money-back guarantee. If you're not satisfied with BiliNote, contact our support team within 30 days of your purchase for a full refund.",
  },
  {
    question: "Is my data secure?",
    answer:
      "Yes, we take security seriously. All data is encrypted in transit and at rest. We use industry-standard security practices and never share your data with third parties. Enterprise plans include additional security features like SSO and SOC 2 compliance.",
  },
]

function FAQItem({ faq, index }: { faq: typeof faqs[0]; index: number }) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="border-b border-border">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex w-full items-center justify-between py-5 text-left"
      >
        <span className="text-lg font-semibold">{faq.question}</span>
        <ChevronDown
          className={cn(
            "h-5 w-5 shrink-0 transition-transform",
            isOpen && "rotate-180"
          )}
        />
      </button>
      {isOpen && (
        <div className="pb-5 text-muted-foreground">
          <p>{faq.answer}</p>
        </div>
      )}
    </div>
  )
}

export function FAQSection() {
  return (
    <section id="faq" className="bg-muted/50 py-20 sm:py-32">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="mb-4 text-3xl font-bold tracking-tight sm:text-4xl">
            Frequently asked questions
          </h2>
          <p className="text-lg text-muted-foreground">
            Have a different question? Contact our support team.
          </p>
        </div>

        <div className="mx-auto mt-16 max-w-3xl">
          {faqs.map((faq, index) => (
            <FAQItem key={index} faq={faq} index={index} />
          ))}
        </div>

        <div className="mt-10 text-center">
          <p className="text-sm text-muted-foreground">
            Still have questions?{" "}
            <a href="mailto:support@bilinote.com" className="text-primary hover:underline">
              Contact our support team
            </a>
          </p>
        </div>
      </div>
    </section>
  )
}
