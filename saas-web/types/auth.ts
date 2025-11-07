export interface User {
  id: number
  email: string
  username?: string
  full_name?: string
  avatar_url?: string
  is_active: boolean
  is_verified: boolean
  created_at: string
  last_login?: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  full_name?: string
  username?: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface ApiResponse<T> {
  code: number
  data: T
  msg: string
}

export type PlanType = 'free' | 'basic' | 'pro' | 'enterprise'
export type BillingCycle = 'monthly' | 'yearly'

export interface Subscription {
  id: number
  user_id: number
  plan_type: PlanType
  billing_cycle?: BillingCycle
  status: string
  max_videos_per_month: number
  max_video_duration_minutes: number
  current_period_start: string
  current_period_end?: string
  trial_end?: string
  cancel_at?: string
  auto_renew: boolean
  created_at: string
}

export interface UsageStats {
  videos_used: number
  videos_limit: number
  duration_used_minutes: number
  duration_limit_minutes: number
  period_start: string
  period_end?: string
  is_unlimited: boolean
}

export interface PricingPlan {
  plan_type: PlanType
  name: string
  description: string
  price_monthly: number
  price_yearly: number
  features: PlanFeatures
}

export interface PlanFeatures {
  max_videos_per_month: number
  max_video_duration_minutes: number
  ai_models: string[]
  screenshots: boolean
  multi_modal: boolean
  mind_maps: boolean
  api_access: boolean
  priority_support: boolean
  custom_ai_keys: boolean
}
