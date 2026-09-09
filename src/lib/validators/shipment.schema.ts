import { z } from "zod";

export const createShipmentSchema = z.object({
  origin: z.string().min(2, "Enter an origin location"),
  destination: z.string().min(2, "Enter a destination location"),
  produceType: z.string().min(2, "Enter the produce type"),
  scheduledDate: z.string().min(1, "Select a scheduled date"),
  originLatitude: z.coerce.number().min(-90).max(90).optional(),
  originLongitude: z.coerce.number().min(-180).max(180).optional(),
  destinationLatitude: z.coerce.number().min(-90).max(90).optional(),
  destinationLongitude: z.coerce.number().min(-180).max(180).optional(),
  temperatureC: z.coerce.number().optional(),
  transitDurationHr: z.coerce.number().optional(),
  pressurePsi: z.coerce.number().optional(),
  baselineLossPct: z.coerce.number().optional(),
  quantityKg: z.coerce.number().optional(),
});

export type CreateShipmentFormValues = z.infer<typeof createShipmentSchema>;
