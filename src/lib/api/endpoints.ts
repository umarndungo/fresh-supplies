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
} as const;
