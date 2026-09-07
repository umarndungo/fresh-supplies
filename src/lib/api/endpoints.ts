export const API_ENDPOINTS = {
  auth: {
    login: "/auth/login",
    register: "/auth/register",
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
    recommendMarket: "/ml/recommend-market",
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
