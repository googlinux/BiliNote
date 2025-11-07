"use client"

import { useEffect } from "react"
import { useAuthStore } from "@/store/auth-store"

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const initialize = useAuthStore((state) => state.initialize)

  useEffect(() => {
    // Initialize auth state from localStorage on mount
    initialize()
  }, [initialize])

  return <>{children}</>
}
