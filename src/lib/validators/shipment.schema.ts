import { z } from "zod";

export const createShipmentSchema = z.object({
  origin: z.string().min(2, "Enter an origin location"),
  destination: z.string().min(2, "Enter a destination location"),
  produceType: z.string().min(2, "Enter the produce type"),
  scheduledDate: z.string().min(1, "Select a scheduled date"),
  latitude: z.number().optional(),
  longitude: z.number().optional(),
  temperatureC: z.number().optional(),
  transitDurationHr: z.number().optional(),
  pressurePsi: z.number().optional(),
  baselineLossPct: z.number().optional(),
  quantityKg: z.number().optional(),
});

export type CreateShipmentFormValues = z.infer<typeof createShipmentSchema>;
