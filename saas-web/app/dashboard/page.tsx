"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/store/auth-store"
import { useSubscriptionStore } from "@/store/subscription-store"
import { Button } from "@/components/ui/button"
import { LogOut, Settings, FileText, BarChart3 } from "lucide-react"

export default function DashboardPage() {
  const router = useRouter()
  const { user, isAuthenticated, logout, isLoading: authLoading } = useAuthStore()
  const { subscription, usage, fetchSubscription, fetchUsage, isLoading: subLoading } = useSubscriptionStore()

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/auth/login")
    }
  }, [isAuthenticated, authLoading, router])

  useEffect(() => {
    if (isAuthenticated) {
      fetchSubscription()
      fetchUsage()
    }
  }, [isAuthenticated, fetchSubscription, fetchUsage])

  const handleLogout = () => {
    logout()
    router.push("/")
  }

  if (authLoading || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="mb-4 h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent mx-auto"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    )
  }

  const usagePercentage = usage
    ? Math.min((usage.videos_used / usage.videos_limit) * 100, 100)
    : 0

  return (
    <div className="min-h-screen bg-muted/50">
      {/* Header */}
      <header className="border-b bg-background">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <div className="flex items-center space-x-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <span className="text-lg font-bold">B</span>
            </div>
            <span className="text-xl font-bold">BiliNote</span>
          </div>

          <div className="flex items-center space-x-4">
            <span className="text-sm text-muted-foreground">
              {user.email}
            </span>
            <Button variant="outline" size="sm" onClick={() => router.push("/dashboard/settings")}>
              <Settings className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Welcome back{user.full_name ? `, ${user.full_name}` : ''}!</h1>
          <p className="text-muted-foreground">Here's your overview</p>
        </div>

        {/* Stats Grid */}
        <div className="grid gap-6 md:grid-cols-3 mb-8">
          {/* Subscription Card */}
          <div className="rounded-lg border bg-card p-6">
            <div className="mb-2 flex items-center justify-between">
              <span className="text-sm font-medium text-muted-foreground">Plan</span>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </div>
            <div className="text-2xl font-bold capitalize">
              {subscription?.plan_type || 'Free'}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {subscription?.status || 'Active'}
            </p>
          </div>

          {/* Usage Card */}
          <div className="rounded-lg border bg-card p-6">
            <div className="mb-2 flex items-center justify-between">
              <span className="text-sm font-medium text-muted-foreground">Videos Used</span>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </div>
            <div className="text-2xl font-bold">
              {usage?.videos_used || 0} / {usage?.videos_limit || 5}
            </div>
            <div className="mt-2 h-2 w-full rounded-full bg-muted">
              <div
                className="h-full rounded-full bg-primary transition-all"
                style={{ width: `${usagePercentage}%` }}
              />
            </div>
          </div>

          {/* Duration Card */}
          <div className="rounded-lg border bg-card p-6">
            <div className="mb-2 flex items-center justify-between">
              <span className="text-sm font-medium text-muted-foreground">Duration</span>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </div>
            <div className="text-2xl font-bold">
              {usage?.duration_used_minutes || 0} min
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              of {usage?.duration_limit_minutes || 10} min limit
            </p>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="rounded-lg border bg-card p-6">
          <h2 className="mb-4 text-xl font-bold">Quick Actions</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            <Button className="h-auto flex-col items-start p-6 text-left" variant="outline">
              <FileText className="mb-2 h-6 w-6" />
              <div className="font-semibold">Generate Note</div>
              <div className="text-xs text-muted-foreground">
                Create a new note from video URL
              </div>
            </Button>

            <Button
              className="h-auto flex-col items-start p-6 text-left"
              variant="outline"
              onClick={() => router.push("/dashboard/settings")}
            >
              <Settings className="mb-2 h-6 w-6" />
              <div className="font-semibold">Settings</div>
              <div className="text-xs text-muted-foreground">
                Manage your account and preferences
              </div>
            </Button>
          </div>
        </div>

        {/* Upgrade Banner (for free users) */}
        {subscription?.plan_type === 'free' && (
          <div className="mt-8 rounded-lg border-2 border-primary/20 bg-primary/5 p-6">
            <h3 className="mb-2 text-lg font-bold">Upgrade to Pro</h3>
            <p className="mb-4 text-sm text-muted-foreground">
              Get 500 videos per month, longer durations, and advanced AI models
            </p>
            <Button onClick={() => router.push("/#pricing")}>
              View Plans
            </Button>
          </div>
        )}
      </main>
    </div>
  )
}
