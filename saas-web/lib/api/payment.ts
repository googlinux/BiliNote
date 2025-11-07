import apiClient from '../api-client'
import type { ApiResponse, PlanType, BillingCycle } from '@/types/auth'

export interface CheckoutSessionRequest {
  plan_type: PlanType
  billing_cycle: BillingCycle
}

export interface CheckoutSessionResponse {
  session_id: string
  url: string
}

export interface CustomerPortalResponse {
  url: string
}

export const paymentApi = {
  // Create Stripe checkout session
  async createCheckoutSession(
    planType: PlanType,
    billingCycle: BillingCycle
  ): Promise<CheckoutSessionResponse> {
    const response = await apiClient.post<ApiResponse<CheckoutSessionResponse>>(
      '/api/payment/create-checkout-session',
      {
        plan_type: planType,
        billing_cycle: billingCycle,
      }
    )
    return response.data.data
  },

  // Get customer portal URL
  async getCustomerPortal(): Promise<CustomerPortalResponse> {
    const response = await apiClient.get<ApiResponse<CustomerPortalResponse>>(
      '/api/payment/customer-portal'
    )
    return response.data.data
  },
}
