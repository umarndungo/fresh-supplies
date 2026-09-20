"use client";

import { useState } from "react";
import { toast } from "sonner";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, Plus, X, Edit2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Dialog, DialogBody, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { createProduceSchema, type CreateProduceFormValues } from "@/lib/validators/produce.schema";
import { useCreateProduce, useUpdateProduce } from "@/hooks/use-produce";
import type { Produce, UpdateProducePayload } from "@/types/produce.types";
import { predictStorageSpoilageRequest } from "@/lib/api/storage-ml.api";

interface CreateProduceDialogProps {
  initialData?: Produce | null;
  onSuccess?: () => void;
}

export function CreateProduceDialog({ initialData, onSuccess }: CreateProduceDialogProps) {
  const [open, setOpen] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const isEditing = !!initialData;
  const createProduce = useCreateProduce();
  const updateProduce = useUpdateProduce();
  const isPending = isEditing ? updateProduce.isPending : createProduce.isPending;

  const form = useForm<CreateProduceFormValues>({
    resolver: zodResolver(createProduceSchema),
    defaultValues: {
      name: "",
      variety: "",
      quantityKg: 0,
      unitPrice: 0,
      qualityGrade: "",
      harvestDate: "",
      storageLocation: "",
      commodityClass: "PERISHABLE",
      ...initialData,
    },
  });

  async function onSubmit(values: CreateProduceFormValues) {
    try {
      if (isEditing && initialData) {
        await updateProduce.mutateAsync({ id: initialData.id, payload: values as UpdateProducePayload });
      } else {
        const created = await createProduce.mutateAsync(values);
        try {
          const storageRisk = await predictStorageSpoilageRequest(created);
          await updateProduce.mutateAsync({
            id: created.id,
            payload: {
              storageSpoilageProbability: storageRisk.storage_spoilage_probability,
              storageRiskTier: storageRisk.storage_risk_tier,
              storageSpoilPrediction: storageRisk.storage_spoil_prediction,
              estimatedShelfLifeDays: storageRisk.estimated_shelf_life_days,
            },
          });
        } catch (error) {
          // The lot remains saved even if the optional ML assessment is
          // unavailable — but silently, "Pending" would look identical to
          // "not attempted yet," so tell the user it actually failed.
          console.error("Storage risk assessment failed for produce", created.id, error);
          toast.warning("Produce saved — storage risk assessment unavailable right now.");
        }
      }
      form.reset();
      setOpen(false);
      onSuccess?.();
    } catch {
      // Error handled by hook
    }
  }

  function handleOpenChange(newOpen: boolean) {
    if (!newOpen && isEditing) {
      form.reset();
    }
    setOpen(newOpen);
  }

  const triggerLabel = isEditing ? "Edit produce" : "New produce";

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      {initialData ? null : (
        <DialogTrigger asChild>
          <Button size="sm">
            <Plus className="size-4" />
            {triggerLabel}
          </Button>
        </DialogTrigger>
      )}
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>{isEditing ? "Edit produce" : "Add produce"}</DialogTitle>
          <DialogDescription>
            Record a produce lot to track inventory and freshness across the supply chain.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="flex flex-1 flex-col overflow-hidden" noValidate>
          <DialogBody className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Name</FormLabel>
                    <FormControl>
                      <Input placeholder="Tomatoes" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="variety"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Variety</FormLabel>
                    <FormControl>
                      <Input placeholder="Roma VF" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <FormField
              control={form.control}
              name="commodityClass"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Commodity Class</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger {...field}>
                        <SelectValue placeholder="Select class" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="PERISHABLE">Perishable</SelectItem>
                      <SelectItem value="STAPLE">Staple</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormDescription>Perishable lots get priority tracking for spoilage risk.</FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <div className="grid gap-4 sm:grid-cols-2">
              <FormField
                control={form.control}
                name="quantityKg"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Quantity (kg)</FormLabel>
                    <FormControl>
                      <Input type="number" step="0.1" min="0" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="unitPrice"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Unit Price (KES/kg)</FormLabel>
                    <FormControl>
                      <Input type="number" step="0.1" min="0" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <FormField
                control={form.control}
                name="qualityGrade"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Quality Grade</FormLabel>
                    <FormControl>
                      <Input placeholder="Grade 1" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="harvestDate"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Harvest Date</FormLabel>
                    <FormControl>
                      <Input type="date" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <FormField
              control={form.control}
              name="storageLocation"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Storage Location</FormLabel>
                  <FormControl>
                    <Input placeholder="Warehouse A, Nairobi" {...field} />
                  </FormControl>
                  <FormDescription>Where the lot is stored while waiting to be shipped.</FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <div className="grid gap-4 sm:grid-cols-2">
              <FormField
                control={form.control}
                name="storageTemperatureC"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Storage temperature (°C)</FormLabel>
                    <FormControl><Input type="number" step="any" placeholder="22" {...field} value={field.value ?? ""} /></FormControl>
                    <FormDescription>Used to estimate storage spoilage risk.</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="storagePressurePsi"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Storage pressure (PSI)</FormLabel>
                    <FormControl><Input type="number" step="any" placeholder="30" {...field} value={field.value ?? ""} /></FormControl>
                    <FormDescription>Packaging or stacking pressure.</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
          </DialogBody>
            <DialogFooter>
              {isEditing && (
                <Button type="button" variant="outline" onClick={() => handleOpenChange(false)}>
                  <X className="size-4 mr-2" />
                  Cancel
                </Button>
              )}
              <Button type="submit" disabled={isPending}>
                {isPending ? <Loader2 className="size-4 animate-spin" /> : null}
                {isEditing ? "Save changes" : "Create produce"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}

export function EditProduceTrigger({ produce, onSuccess }: { produce: Produce; onSuccess?: () => void }) {
  const [open, setOpen] = useState(false);
  const updateProduce = useUpdateProduce();

  const form = useForm<CreateProduceFormValues>({
    resolver: zodResolver(createProduceSchema),
    defaultValues: {
      name: produce.name,
      variety: produce.variety,
      quantityKg: produce.quantityKg,
      unitPrice: produce.unitPrice,
      qualityGrade: produce.qualityGrade,
      harvestDate: produce.harvestDate.split("T")[0],
      storageLocation: produce.storageLocation,
      commodityClass: produce.commodityClass,
      storageTemperatureC: produce.storageTemperatureC,
      storagePressurePsi: produce.storagePressurePsi,
    },
  });

  async function onSubmit(values: CreateProduceFormValues) {
    try {
      await updateProduce.mutateAsync({ id: produce.id, payload: values as UpdateProducePayload });
      form.reset();
      setOpen(false);
      onSuccess?.();
    } catch {
      // Error handled by hook
    }
  }

  return (
    <>
      <Button variant="ghost" size="icon" onClick={() => setOpen(true)} aria-label="Edit produce">
        <Edit2 className="size-4" />
      </Button>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Edit produce</DialogTitle>
            <DialogDescription>
              Update the details for this produce lot.
            </DialogDescription>
          </DialogHeader>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="flex flex-1 flex-col overflow-hidden" noValidate>
            <DialogBody className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Name</FormLabel>
                      <FormControl>
                        <Input placeholder="Tomatoes" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="variety"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Variety</FormLabel>
                      <FormControl>
                        <Input placeholder="Roma VF" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
              <FormField
                control={form.control}
                name="commodityClass"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Commodity Class</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger {...field}>
                          <SelectValue placeholder="Select class" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="PERISHABLE">Perishable</SelectItem>
                        <SelectItem value="STAPLE">Staple</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormDescription>Perishable lots get priority tracking for spoilage risk.</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <div className="grid gap-4 sm:grid-cols-2">
                <FormField
                  control={form.control}
                  name="quantityKg"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Quantity (kg)</FormLabel>
                      <FormControl>
                        <Input type="number" step="0.1" min="0" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="unitPrice"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Unit Price (KES/kg)</FormLabel>
                      <FormControl>
                        <Input type="number" step="0.1" min="0" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <FormField
                  control={form.control}
                  name="qualityGrade"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Quality Grade</FormLabel>
                      <FormControl>
                        <Input placeholder="Grade 1" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="harvestDate"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Harvest Date</FormLabel>
                      <FormControl>
                        <Input type="date" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
              <FormField
                control={form.control}
                name="storageLocation"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Storage Location</FormLabel>
                    <FormControl>
                      <Input placeholder="Warehouse A, Nairobi" {...field} />
                    </FormControl>
                    <FormDescription>Where the lot is stored while waiting to be shipped.</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </DialogBody>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={updateProduce.isPending}>
                  {updateProduce.isPending ? <Loader2 className="size-4 animate-spin" /> : null}
                  Save changes
                </Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>
    </>
  );
}