"use client"

import { Button } from "@/components/ui/button"
import { Check } from "lucide-react"
import Link from "next/link"
import { useState } from "react"

const plans = [
  {
    name: "Free",
    price: { monthly: 0, yearly: 0 },
    description: "Perfect for trying out BiliNote",
    features: [
      "5 videos per month",
      "Up to 10 minutes per video",
      "Basic AI models",
      "Standard transcription",
      "Markdown export",
      "Community support",
    ],
    cta: "Get Started",
    highlighted: false,
  },
  {
    name: "Basic",
    price: { monthly: 9, yearly: 86 }, // ~20% discount on yearly
    description: "For regular video learners",
    features: [
      "100 videos per month",
      "Up to 30 minutes per video",
      "GPT-4 & Claude models",
      "Advanced transcription",
      "Smart screenshots",
      "Timestamp links",
      "Email support",
      "No watermarks",
    ],
    cta: "Start Free Trial",
    highlighted: false,
  },
  {
    name: "Pro",
    price: { monthly: 29, yearly: 278 }, // ~20% discount
    description: "For power users and professionals",
    features: [
      "500 videos per month",
      "Up to 2 hours per video",
      "All AI models including GPT-4o",
      "Multi-modal video understanding",
      "Automatic mind maps",
      "Grid screenshots",
      "Priority processing",
      "Priority support",
      "API access",
      "Custom prompts",
    ],
    cta: "Start Free Trial",
    highlighted: true,
  },
  {
    name: "Enterprise",
    price: { monthly: 99, yearly: 950 },
    description: "For teams and organizations",
    features: [
      "Unlimited videos",
      "Unlimited duration",
      "All Pro features",
      "Custom AI models (BYOK)",
      "Team collaboration",
      "SSO integration",
      "Dedicated support",
      "Custom integration",
      "On-premise deployment option",
      "SLA guarantee",
    ],
    cta: "Contact Sales",
    highlighted: false,
  },
]

export function PricingSection() {
  const [isYearly, setIsYearly] = useState(false)

  return (
    <section id="pricing" className="bg-background py-20 sm:py-32">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="mb-4 text-3xl font-bold tracking-tight sm:text-4xl">
            Simple, transparent pricing
          </h2>
          <p className="mb-8 text-lg text-muted-foreground">
            Choose the plan that fits your needs. Upgrade or downgrade anytime.
          </p>

          {/* Billing toggle */}
          <div className="inline-flex items-center rounded-lg border bg-muted p-1">
            <button
              onClick={() => setIsYearly(false)}
              className={`rounded-md px-4 py-2 text-sm font-medium transition-colors ${
                !isYearly
                  ? "bg-background text-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setIsYearly(true)}
              className={`rounded-md px-4 py-2 text-sm font-medium transition-colors ${
                isYearly
                  ? "bg-background text-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              Yearly
              <span className="ml-2 text-xs text-primary">Save 20%</span>
            </button>
          </div>
        </div>

        <div className="mx-auto mt-16 grid max-w-6xl gap-8 lg:grid-cols-4">
          {plans.map((plan, index) => (
            <div
              key={index}
              className={`relative rounded-2xl border ${
                plan.highlighted
                  ? "border-primary shadow-lg ring-2 ring-primary/20"
                  : "border-border"
              } bg-card p-8`}
            >
              {plan.highlighted && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <span className="rounded-full bg-primary px-3 py-1 text-xs font-semibold text-primary-foreground">
                    Most Popular
                  </span>
                </div>
              )}

              <div className="mb-4">
                <h3 className="text-xl font-bold">{plan.name}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{plan.description}</p>
              </div>

              <div className="mb-6">
                <div className="flex items-baseline">
                  <span className="text-4xl font-bold">
                    ${isYearly ? plan.price.yearly : plan.price.monthly}
                  </span>
                  {plan.price.monthly > 0 && (
                    <span className="ml-2 text-muted-foreground">
                      /{isYearly ? "year" : "month"}
                    </span>
                  )}
                </div>
                {isYearly && plan.price.monthly > 0 && (
                  <p className="mt-1 text-sm text-muted-foreground">
                    ${(plan.price.yearly / 12).toFixed(2)}/month billed yearly
                  </p>
                )}
              </div>

              <Button
                asChild
                variant={plan.highlighted ? "default" : "outline"}
                className="mb-6 w-full"
              >
                <Link href={plan.name === "Enterprise" ? "/contact" : "/auth/register"}>
                  {plan.cta}
                </Link>
              </Button>

              <ul className="space-y-3">
                {plan.features.map((feature, featureIndex) => (
                  <li key={featureIndex} className="flex items-start">
                    <Check className="mr-3 h-5 w-5 shrink-0 text-primary" />
                    <span className="text-sm text-muted-foreground">{feature}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 text-center text-sm text-muted-foreground">
          <p>All plans include a 14-day free trial. No credit card required.</p>
        </div>
      </div>
    </section>
  )
}
