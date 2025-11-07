import apiClient from '../api-client'
import type {
  Subscription,
  UsageStats,
  PricingPlan,
  ApiResponse,
  PlanType,
  BillingCycle,
} from '@/types/auth'

export const subscriptionApi = {
  // Get all pricing plans (public)
  async getPlans(): Promise<PricingPlan[]> {
    const response = await apiClient.get<ApiResponse<PricingPlan[]>>('/api/subscription/plans')
    return response.data.data
  },

  // Get current user's subscription
  async getCurrentSubscription(): Promise<Subscription> {
    const response = await apiClient.get<ApiResponse<Subscription>>('/api/subscription/current')
    return response.data.data
  },

  // Get usage statistics
  async getUsage(): Promise<UsageStats> {
    const response = await apiClient.get<ApiResponse<UsageStats>>('/api/subscription/usage')
    return response.data.data
  },

  // Subscribe to a plan
  async subscribe(planType: PlanType, billingCycle: BillingCycle): Promise<void> {
    await apiClient.post<ApiResponse<{ subscription_id: number }>>('/api/subscription/subscribe', {
      plan_type: planType,
      billing_cycle: billingCycle,
    })
  },

  // Cancel subscription
  async cancel(immediately = false): Promise<void> {
    await apiClient.post<ApiResponse<null>>(`/api/subscription/cancel?immediately=${immediately}`)
  },

  // Get invoices
  async getInvoices(): Promise<any[]> {
    const response = await apiClient.get<ApiResponse<any[]>>('/api/subscription/invoices')
    return response.data.data
  },
}
