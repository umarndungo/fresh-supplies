"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, Plus, X, ChevronDown, ChevronUp, Edit2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { createProduceSchema, type CreateProduceFormValues } from "@/lib/validators/produce.schema";
import { useCreateProduce, useUpdateProduce } from "@/hooks/use-produce";
import type { Produce, UpdateProducePayload } from "@/types/produce.types";

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
        await createProduce.mutateAsync(values);
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
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4" noValidate>
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
                  <FormMessage />
                </FormItem>
              )}
            />
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
            <FormField
              control={form.control}
              name="storageLocation"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Storage Location</FormLabel>
                  <FormControl>
                    <Input placeholder="Warehouse A, Nairobi" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
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
          </DialogHeader>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4" noValidate>
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
                    <FormMessage />
                  </FormItem>
                )}
              />
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
              <FormField
                control={form.control}
                name="storageLocation"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Storage Location</FormLabel>
                    <FormControl>
                      <Input placeholder="Warehouse A, Nairobi" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
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