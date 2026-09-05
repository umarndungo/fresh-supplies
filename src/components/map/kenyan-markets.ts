export interface Market {
  id: string;
  name: string;
  region: string;
  latitude: number;
  longitude: number;
}

export const KENYAN_MARKETS: Market[] = [
  { id: "nairobi-gikomba", name: "Gikomba Market", region: "Nairobi", latitude: -1.2833, longitude: 36.8167 },
  { id: "nakuru-wakulima", name: "Wakulima Market", region: "Nakuru", latitude: -0.3031, longitude: 36.0800 },
  { id: "mombasa-kongowea", name: "Kongowea Market", region: "Mombasa", latitude: -4.0435, longitude: 39.6682 },
  { id: "kisumu", name: "Kisumu Market", region: "Kisumu", latitude: -0.0917, longitude: 34.7680 },
  { id: "eldoret", name: "Eldoret Market", region: "Eldoret", latitude: 0.5143, longitude: 35.2698 },
  { id: "thika", name: "Thika Market", region: "Thika", latitude: -1.0333, longitude: 37.0667 },
  { id: "kakamega", name: "Kakamega Market", region: "Kakamega", latitude: 0.2819, longitude: 34.7519 },
  { id: "meru", name: "Meru Market", region: "Meru", latitude: 0.0471, longitude: 37.6558 },
  { id: "naivasha", name: "Naivasha Market", region: "Naivasha", latitude: -0.7167, longitude: 36.4333 },
  { id: "bomet", name: "Bomet Market", region: "Bomet", latitude: -0.7900, longitude: 35.3400 },
];

export function getMarketById(id: string): Market | undefined {
  return KENYAN_MARKETS.find((m) => m.id === id);
}

export function getMarketByName(name: string): Market | undefined {
  return KENYAN_MARKETS.find((m) => m.name.toLowerCase() === name.toLowerCase());
}