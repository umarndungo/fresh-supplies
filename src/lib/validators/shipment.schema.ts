import { z } from "zod";

export const createShipmentSchema = z.object({
  origin: z.string().min(2, "Enter an origin location"),
  destination: z.string().min(2, "Enter a destination location"),
  produceType: z.string().min(2, "Enter the produce type"),
  scheduledDate: z.string().min(1, "Select a scheduled date"),
});

export type CreateShipmentFormValues = z.infer<typeof createShipmentSchema>;
