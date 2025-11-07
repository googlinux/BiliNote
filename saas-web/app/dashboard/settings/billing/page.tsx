"use client"

import { useEffect, useState } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { useAuthStore } from "@/store/auth-store"
import { useSubscriptionStore } from "@/store/subscription-store"
import { paymentApi } from "@/lib/api/payment"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Loader2, CreditCard, Calendar, CheckCircle, XCircle, AlertCircle } from "lucide-react"
import type { PlanType, BillingCycle } from "@/types/auth"

export default function BillingPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { isAuthenticated, isLoading: authLoading } = useAuthStore()
  const { subscription, plans, fetchSubscription, fetchPlans, isLoading } = useSubscriptionStore()
  const [processingPortal, setProcessingPortal] = useState(false)
  const [processingCheckout, setProcessingCheckout] = useState<string | null>(null)

  // Handle success/cancel from Stripe redirect
  useEffect(() => {
    const success = searchParams.get('success')
    const cancelled = searchParams.get('cancelled')

    if (success === 'true') {
      // Refresh subscription data after successful payment
      fetchSubscription()
    }
  }, [searchParams, fetchSubscription])

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/auth/login")
    }
  }, [isAuthenticated, authLoading, router])

  useEffect(() => {
    if (isAuthenticated) {
      fetchSubscription()
      fetchPlans()
    }
  }, [isAuthenticated, fetchSubscription, fetchPlans])

  const handleManageBilling = async () => {
    setProcessingPortal(true)
    try {
      const { url } = await paymentApi.getCustomerPortal()
      window.location.href = url
    } catch (error: any) {
      console.error("Failed to open customer portal:", error)
      alert(error.response?.data?.detail || "Failed to open customer portal")
    } finally {
      setProcessingPortal(false)
    }
  }

  const handleUpgrade = async (planType: PlanType, billingCycle: BillingCycle) => {
    const key = `${planType}-${billingCycle}`
    setProcessingCheckout(key)
    try {
      const { url } = await paymentApi.createCheckoutSession(planType, billingCycle)
      window.location.href = url
    } catch (error: any) {
      console.error("Failed to create checkout session:", error)
      alert(error.response?.data?.detail || "Failed to start checkout")
      setProcessingCheckout(null)
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge className="bg-green-500"><CheckCircle className="mr-1 h-3 w-3" /> Active</Badge>
      case 'cancelled':
        return <Badge variant="destructive"><XCircle className="mr-1 h-3 w-3" /> Cancelled</Badge>
      case 'past_due':
        return <Badge variant="destructive"><AlertCircle className="mr-1 h-3 w-3" /> Past Due</Badge>
      default:
        return <Badge variant="secondary">{status}</Badge>
    }
  }

  if (authLoading || isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  return (
    <div className="container mx-auto max-w-6xl p-6 space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Billing & Subscription</h1>
        <p className="text-muted-foreground mt-2">
          Manage your subscription and billing information
        </p>
      </div>

      {/* Current Subscription */}
      {subscription && (
        <Card>
          <CardHeader>
            <CardTitle>Current Plan</CardTitle>
            <CardDescription>Your active subscription details</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-2xl font-bold capitalize">{subscription.plan_type}</h3>
                  {getStatusBadge(subscription.status)}
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  {subscription.billing_cycle && (
                    <span className="capitalize">{subscription.billing_cycle} billing</span>
                  )}
                </p>
              </div>
              {subscription.stripe_customer_id && (
                <Button onClick={handleManageBilling} disabled={processingPortal}>
                  {processingPortal ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Loading...
                    </>
                  ) : (
                    <>
                      <CreditCard className="mr-2 h-4 w-4" />
                      Manage Billing
                    </>
                  )}
                </Button>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t">
              <div>
                <p className="text-sm text-muted-foreground">Videos per month</p>
                <p className="text-2xl font-bold">
                  {subscription.max_videos_per_month === -1 ? 'Unlimited' : subscription.max_videos_per_month}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Max video duration</p>
                <p className="text-2xl font-bold">
                  {subscription.max_video_duration_minutes === -1 ? 'Unlimited' : `${subscription.max_video_duration_minutes} min`}
                </p>
              </div>
              {subscription.current_period_end && (
                <div>
                  <p className="text-sm text-muted-foreground">
                    <Calendar className="inline mr-1 h-4 w-4" />
                    {subscription.status === 'cancelled' ? 'Access until' : 'Renews on'}
                  </p>
                  <p className="text-lg font-semibold">
                    {new Date(subscription.current_period_end).toLocaleDateString()}
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Available Plans */}
      <div>
        <h2 className="text-2xl font-bold mb-4">Available Plans</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {plans.filter(plan => plan.plan_type !== 'free').map((plan) => (
            <Card key={plan.plan_type} className={subscription?.plan_type === plan.plan_type ? 'border-primary border-2' : ''}>
              <CardHeader>
                <CardTitle className="capitalize">{plan.plan_type}</CardTitle>
                <CardDescription>{plan.description}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="text-3xl font-bold">
                    ${plan.price_monthly}
                    <span className="text-sm font-normal text-muted-foreground">/month</span>
                  </p>
                  {plan.price_yearly && (
                    <p className="text-sm text-muted-foreground mt-1">
                      or ${plan.price_yearly}/year (save ${(plan.price_monthly * 12 - plan.price_yearly).toFixed(0)})
                    </p>
                  )}
                </div>

                <ul className="space-y-2 text-sm">
                  <li className="flex items-start">
                    <CheckCircle className="mr-2 h-4 w-4 text-green-500 mt-0.5" />
                    <span>
                      {plan.max_videos_per_month === -1 ? 'Unlimited' : plan.max_videos_per_month} videos/month
                    </span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="mr-2 h-4 w-4 text-green-500 mt-0.5" />
                    <span>
                      {plan.max_video_duration_minutes === -1 ? 'Unlimited' : `${plan.max_video_duration_minutes} min`} video duration
                    </span>
                  </li>
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-start">
                      <CheckCircle className="mr-2 h-4 w-4 text-green-500 mt-0.5" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>

                <div className="space-y-2 pt-4">
                  <Button
                    className="w-full"
                    onClick={() => handleUpgrade(plan.plan_type, 'monthly')}
                    disabled={processingCheckout === `${plan.plan_type}-monthly` || subscription?.plan_type === plan.plan_type}
                  >
                    {processingCheckout === `${plan.plan_type}-monthly` ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Processing...
                      </>
                    ) : subscription?.plan_type === plan.plan_type ? (
                      'Current Plan'
                    ) : (
                      'Subscribe Monthly'
                    )}
                  </Button>
                  {plan.price_yearly && (
                    <Button
                      variant="outline"
                      className="w-full"
                      onClick={() => handleUpgrade(plan.plan_type, 'yearly')}
                      disabled={processingCheckout === `${plan.plan_type}-yearly` || subscription?.plan_type === plan.plan_type}
                    >
                      {processingCheckout === `${plan.plan_type}-yearly` ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Processing...
                        </>
                      ) : (
                        'Subscribe Yearly'
                      )}
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Billing Information */}
      <Card>
        <CardHeader>
          <CardTitle>Payment Method</CardTitle>
          <CardDescription>Manage your payment methods in the Stripe customer portal</CardDescription>
        </CardHeader>
        <CardContent>
          {subscription?.stripe_customer_id ? (
            <Button onClick={handleManageBilling} disabled={processingPortal}>
              {processingPortal ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Loading...
                </>
              ) : (
                <>
                  <CreditCard className="mr-2 h-4 w-4" />
                  Manage Payment Methods
                </>
              )}
            </Button>
          ) : (
            <p className="text-sm text-muted-foreground">
              No payment method on file. Subscribe to a paid plan to add a payment method.
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
