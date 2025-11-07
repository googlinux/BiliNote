import { create } from 'zustand'
import { subscriptionApi } from '@/lib/api/subscription'
import type { Subscription, UsageStats, PricingPlan, PlanType, BillingCycle } from '@/types/auth'

interface SubscriptionState {
  subscription: Subscription | null
  usage: UsageStats | null
  plans: PricingPlan[]
  isLoading: boolean
  error: string | null

  // Actions
  fetchPlans: () => Promise<void>
  fetchSubscription: () => Promise<void>
  fetchUsage: () => Promise<void>
  subscribe: (planType: PlanType, billingCycle: BillingCycle) => Promise<void>
  cancelSubscription: (immediately?: boolean) => Promise<void>
  clearError: () => void
}

export const useSubscriptionStore = create<SubscriptionState>((set) => ({
  subscription: null,
  usage: null,
  plans: [],
  isLoading: false,
  error: null,

  fetchPlans: async () => {
    set({ isLoading: true, error: null })

    try {
      const plans = await subscriptionApi.getPlans()
      set({
        plans,
        isLoading: false,
      })
    } catch (error: any) {
      const errorMessage = error.response?.data?.msg || 'Failed to fetch plans'
      set({
        error: errorMessage,
        isLoading: false,
      })
    }
  },

  fetchSubscription: async () => {
    set({ isLoading: true, error: null })

    try {
      const subscription = await subscriptionApi.getCurrentSubscription()
      set({
        subscription,
        isLoading: false,
      })
    } catch (error: any) {
      const errorMessage = error.response?.data?.msg || 'Failed to fetch subscription'
      set({
        error: errorMessage,
        isLoading: false,
      })
    }
  },

  fetchUsage: async () => {
    set({ isLoading: true, error: null })

    try {
      const usage = await subscriptionApi.getUsage()
      set({
        usage,
        isLoading: false,
      })
    } catch (error: any) {
      const errorMessage = error.response?.data?.msg || 'Failed to fetch usage'
      set({
        error: errorMessage,
        isLoading: false,
      })
    }
  },

  subscribe: async (planType: PlanType, billingCycle: BillingCycle) => {
    set({ isLoading: true, error: null })

    try {
      await subscriptionApi.subscribe(planType, billingCycle)

      // Refresh subscription data
      const subscription = await subscriptionApi.getCurrentSubscription()
      set({
        subscription,
        isLoading: false,
      })
    } catch (error: any) {
      const errorMessage = error.response?.data?.msg || 'Subscription failed'
      set({
        error: errorMessage,
        isLoading: false,
      })
      throw error
    }
  },

  cancelSubscription: async (immediately = false) => {
    set({ isLoading: true, error: null })

    try {
      await subscriptionApi.cancel(immediately)

      // Refresh subscription data
      const subscription = await subscriptionApi.getCurrentSubscription()
      set({
        subscription,
        isLoading: false,
      })
    } catch (error: any) {
      const errorMessage = error.response?.data?.msg || 'Cancellation failed'
      set({
        error: errorMessage,
        isLoading: false,
      })
      throw error
    }
  },

  clearError: () => set({ error: null }),
}))
