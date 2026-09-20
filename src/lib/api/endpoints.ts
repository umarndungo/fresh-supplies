export const API_ENDPOINTS = {
  auth: {
    login: "/auth/login",
    otpRequest: "/auth/otp/request",
    otpVerify: "/auth/otp/verify",
    setPassword: "/auth/set-password",
    refresh: "/auth/refresh",
    logout: "/auth/logout",
    me: "/auth/me",
  },
  shipments: {
    base: "/shipments",
    byId: (id: string) => `/shipments/${id}`,
  },
  produce: {
    base: "/produce",
    byId: (id: string) => `/produce/${id}`,
  },
  ml: {
    predictSpoilage: "/ml/predict-spoilage",
    predictStorageSpoilage: "/ml/predict-storage-spoilage",
    recommendMarket: "/ml/recommend-market",
    evaluationSummary: "/ml/evaluation-summary",
  },
  locations: {
    search: "/locations/search",
  },
  admin: {
    users: {
      base: "/admin/users",
      byId: (id: string) => `/admin/users/${id}`,
    },
    tenants: {
      base: "/admin/tenants",
      byId: (id: string) => `/admin/tenants/${id}`,
      usage: "/admin/tenants/usage",
      usageById: (id: string) => `/admin/tenants/${id}/usage`,
      grants: (id: string) => `/admin/tenants/${id}/grants`,
    },
    grants: {
      base: "/admin/grants",
      byId: (id: string) => `/admin/grants/${id}`,
    },
  },
  cooperative: {
    members: {
      base: "/cooperative/members",
    },
  },
  mobile: {
    auth: {
      otpRequest: "/mobile/auth/otp/request",
      otpVerify: "/mobile/auth/otp/verify",
      refresh: "/mobile/auth/refresh",
      completeProfile: "/mobile/auth/complete-profile",
    },
    shipments: {
      sync: "/mobile/shipments/sync",
      photoUpload: "/mobile/shipments/photo-upload",
      syncStatus: "/mobile/shipments/sync-status",
      recommendation: "/mobile/shipments/{id}/recommendation",
    },
    driver: {
      manifest: "/mobile/driver/manifest",
      confirmStop: "/mobile/driver/stops/{id}/confirm",
    },
    devices: {
      register: "/mobile/devices/register",
    },
  },
} as const;
