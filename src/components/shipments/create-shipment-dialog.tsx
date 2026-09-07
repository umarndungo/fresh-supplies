"use client";

import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, Plus, ChevronDown, ChevronUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogBody, DialogTrigger } from "@/components/ui/dialog";
import { createShipmentSchema } from "@/lib/validators/shipment.schema";
import type { CreateShipmentPayload } from "@/types/shipment.types";
import { useCreateShipment } from "@/hooks/use-shipments";
import { LocationPicker } from "@/components/map/location-picker";

type CreateShipmentFormInput = {
  origin: string;
  destination: string;
  produceType: string;
  scheduledDate: string;
  originLatitude?: number;
  originLongitude?: number;
  destinationLatitude?: number;
  destinationLongitude?: number;
  temperatureC?: string;
  transitDurationHr?: string;
  pressurePsi?: string;
  quantityKg?: string;
};

export function CreateShipmentDialog() {
  const [open, setOpen] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const searchParams = useSearchParams();
  const createShipment = useCreateShipment();
  const form = useForm<CreateShipmentFormInput>({
    resolver: zodResolver(createShipmentSchema),
    defaultValues: {
      origin: "",
      destination: "",
      produceType: "",
      scheduledDate: "",
      originLatitude: undefined,
      originLongitude: undefined,
      destinationLatitude: undefined,
      destinationLongitude: undefined,
      temperatureC: "",
      transitDurationHr: "",
      pressurePsi: "",
      quantityKg: "",
    },
  });

  // Auto-open dialog when ?create=true is in URL
  useEffect(() => {
    const shouldOpen = searchParams.get("create") === "true";
    if (shouldOpen) {
      setOpen(true);
      // Clean up URL without reloading
      const url = new URL(window.location.href);
      url.searchParams.delete("create");
      window.history.replaceState({}, "", url);
    }
  }, [searchParams]);

  async function onSubmit(values: CreateShipmentFormInput) {
    const payload: CreateShipmentPayload = {
      origin: values.origin,
      destination: values.destination,
      produceType: values.produceType,
      scheduledDate: values.scheduledDate,
      originLatitude: values.originLatitude,
      originLongitude: values.originLongitude,
      destinationLatitude: values.destinationLatitude,
      destinationLongitude: values.destinationLongitude,
      temperatureC: values.temperatureC ? Number(values.temperatureC) : undefined,
      transitDurationHr: values.transitDurationHr ? Number(values.transitDurationHr) : undefined,
      pressurePsi: values.pressurePsi ? Number(values.pressurePsi) : undefined,
      quantityKg: values.quantityKg ? Number(values.quantityKg) : undefined,
    };
    try {
      await createShipment.mutateAsync(payload);
      form.reset();
      setOpen(false);
    } catch {
      // Surfaced via toast in useCreateShipment's onError handler.
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm">
          <Plus className="size-4" />
          New shipment
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Schedule a shipment</DialogTitle>
          <DialogDescription>
            Plan a delivery and capture optional ML prediction data to estimate spoilage risk.
          </DialogDescription>
        </DialogHeader>
        <DialogBody>
          <Form {...form}>
            <form
              id="create-shipment-form"
              onSubmit={form.handleSubmit(onSubmit)}
              className="space-y-4"
              noValidate
            >
            <FormField
              control={form.control}
              name="origin"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Origin</FormLabel>
                  <FormControl>
                    <Input placeholder="Green Valley Cooperative, Nakuru" {...field} />
                  </FormControl>
                  <FormDescription>Farm or cooperative where the produce is loaded.</FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="destination"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Destination</FormLabel>
                  <FormControl>
                    <Input placeholder="Wakulima Market, Nairobi" {...field} />
                  </FormControl>
                  <FormDescription>Market or delivery point for the shipment.</FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <div className="grid gap-4 sm:grid-cols-2">
              <FormField
                control={form.control}
                name="produceType"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Produce type</FormLabel>
                    <FormControl>
                      <Input placeholder="Tomatoes" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="scheduledDate"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Scheduled date</FormLabel>
                    <FormControl>
                      <Input type="date" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <LocationPicker
              latitude={form.watch("originLatitude")}
              longitude={form.watch("originLongitude")}
              onLocationChange={(lat, lng) => {
                form.setValue("originLatitude", lat);
                form.setValue("originLongitude", lng);
              }}
              label="Origin Location (source for ML predictions)"
            />
            <Button
              type="button"
              variant="outline"
              size="sm"
              className="w-full justify-between gap-2 text-muted-foreground hover:text-foreground hover:bg-muted/50"
              onClick={() => setShowAdvanced(!showAdvanced)}
            >
              <span className="flex items-center gap-1.5 font-medium">
                {showAdvanced ? <ChevronUp className="size-4" /> : <ChevronDown className="size-4" />}
                Advanced (ML prediction data)
              </span>
              <span className="text-xs text-muted-foreground">{showAdvanced ? "Hide" : "Show"}</span>
            </Button>
            {showAdvanced && (
              <div className="grid gap-4 rounded-lg border border-border/60 bg-muted/30 p-4 sm:grid-cols-2">
                <FormField
                  control={form.control}
                  name="temperatureC"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Temperature (°C)</FormLabel>
                      <FormControl>
                        <Input type="number" step="any" placeholder="25" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="transitDurationHr"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Transit duration (hours)</FormLabel>
                      <FormControl>
                        <Input type="number" step="any" placeholder="4" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="pressurePsi"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Pressure (PSI)</FormLabel>
                      <FormControl>
                        <Input type="number" step="any" placeholder="30" {...field} />
                      </FormControl>
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
                        <Input type="number" step="any" placeholder="100" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            )}
          </form>
        </Form>
          </DialogBody>
            <DialogFooter>
              <Button type="submit" form="create-shipment-form" disabled={createShipment.isPending}>
                {createShipment.isPending ? <Loader2 className="size-4 animate-spin" /> : null}
                Create shipment
              </Button>
            </DialogFooter>
        </DialogContent>
    </Dialog>
  );
}
