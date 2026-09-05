import { z } from "zod";

export const createProduceSchema = z.object({
  name: z.string().min(2, "Enter produce name"),
  variety: z.string().min(2, "Enter variety"),
  quantityKg: z.coerce.number().positive("Quantity must be positive"),
  unitPrice: z.coerce.number().positive("Price must be positive"),
  qualityGrade: z.string().min(1, "Enter quality grade"),
  harvestDate: z.string().min(1, "Select harvest date"),
  storageLocation: z.string().min(2, "Enter storage location"),
  commodityClass: z.enum(["PERISHABLE", "STAPLE"]),
});

export type CreateProduceFormValues = z.infer<typeof createProduceSchema>;