"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { useAuthStore } from "@/store/auth-store"
import { AlertCircle, CheckCircle } from "lucide-react"

export default function RegisterPage() {
  const router = useRouter()
  const { register, isLoading, error, clearError } = useAuthStore()

  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [fullName, setFullName] = useState("")
  const [agreed, setAgreed] = useState(false)
  const [localError, setLocalError] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    clearError()
    setLocalError("")

    // Validate
    if (password !== confirmPassword) {
      setLocalError("Passwords do not match")
      return
    }

    if (password.length < 8) {
      setLocalError("Password must be at least 8 characters")
      return
    }

    if (!agreed) {
      setLocalError("Please agree to the Terms of Service")
      return
    }

    try {
      await register({ email, password, full_name: fullName })
      // Redirect to dashboard on success
      router.push("/dashboard")
    } catch (err) {
      console.error("Registration failed:", err)
    }
  }

  const displayError = error || localError

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/50 py-12">
      <div className="w-full max-w-md rounded-lg border bg-card p-8 shadow-lg">
        <div className="mb-8 text-center">
          <Link href="/" className="inline-flex items-center space-x-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <span className="text-lg font-bold">B</span>
            </div>
            <span className="text-xl font-bold">BiliNote</span>
          </Link>
          <h1 className="mt-6 text-2xl font-bold">Create an account</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Start your free trial today. No credit card required.
          </p>
        </div>

        {displayError && (
          <div className="mb-4 flex items-center gap-2 rounded-md bg-destructive/10 p-3 text-sm text-destructive">
            <AlertCircle className="h-4 w-4" />
            <span>{displayError}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="fullName" className="block text-sm font-medium mb-2">
              Full Name
            </label>
            <input
              id="fullName"
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="John Doe"
              disabled={isLoading}
            />
          </div>

          <div>
            <label htmlFor="email" className="block text-sm font-medium mb-2">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="you@example.com"
              required
              disabled={isLoading}
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium mb-2">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="At least 8 characters"
              required
              disabled={isLoading}
            />
          </div>

          <div>
            <label htmlFor="confirm-password" className="block text-sm font-medium mb-2">
              Confirm Password
            </label>
            <input
              id="confirm-password"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="••••••••"
              required
              disabled={isLoading}
            />
          </div>

          <div className="flex items-start">
            <input
              type="checkbox"
              className="mt-1 mr-2"
              id="terms"
              checked={agreed}
              onChange={(e) => setAgreed(e.target.checked)}
              disabled={isLoading}
            />
            <label htmlFor="terms" className="text-sm text-muted-foreground">
              I agree to the{" "}
              <Link href="/terms" className="text-primary hover:underline">
                Terms of Service
              </Link>{" "}
              and{" "}
              <Link href="/privacy" className="text-primary hover:underline">
                Privacy Policy
              </Link>
            </label>
          </div>

          <Button className="w-full" type="submit" disabled={isLoading}>
            {isLoading ? "Creating account..." : "Create Account"}
          </Button>
        </form>

        <div className="mt-6 text-center text-sm text-muted-foreground">
          Already have an account?{" "}
          <Link href="/auth/login" className="text-primary hover:underline">
            Sign in
          </Link>
        </div>

        <div className="mt-6">
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t"></div>
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-card px-2 text-muted-foreground">Or continue with</span>
            </div>
          </div>

          <div className="mt-6 grid grid-cols-2 gap-4">
            <Button variant="outline" type="button" disabled>
              Google
            </Button>
            <Button variant="outline" type="button" disabled>
              GitHub
            </Button>
          </div>
        </div>

        <div className="mt-6 flex items-center gap-2 rounded-md bg-primary/10 p-3 text-sm">
          <CheckCircle className="h-4 w-4 text-primary" />
          <span>Free tier includes 5 videos per month</span>
        </div>
      </div>
    </div>
  )
}
