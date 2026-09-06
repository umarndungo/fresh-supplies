"use client";

import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2, Plus, ChevronDown, ChevronUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogBody, DialogTrigger } from "@/components/ui/dialog";
import { createShipmentSchema, type CreateShipmentFormValues } from "@/lib/validators/shipment.schema";
import { useCreateShipment } from "@/hooks/use-shipments";
import { LocationPicker } from "@/components/map/location-picker";

export function CreateShipmentDialog() {
  const [open, setOpen] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const searchParams = useSearchParams();
  const createShipment = useCreateShipment();
  const form = useForm<CreateShipmentFormValues>({
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
      temperatureC: undefined,
      transitDurationHr: undefined,
      pressurePsi: undefined,
      quantityKg: undefined,
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

  async function onSubmit(values: CreateShipmentFormValues) {
    try {
      await createShipment.mutateAsync(values);
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
        </DialogHeader>
        <DialogBody>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4" noValidate>
            <FormField
              control={form.control}
              name="origin"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Origin</FormLabel>
                  <FormControl>
                    <Input placeholder="Green Valley Cooperative, Nakuru" {...field} />
                  </FormControl>
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
                  <FormMessage />
                </FormItem>
              )}
            />
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
              variant="ghost"
              size="sm"
              className="w-full justify-start text-muted-foreground hover:text-foreground"
              onClick={() => setShowAdvanced(!showAdvanced)}
            >
              {showAdvanced ? <ChevronUp className="size-4 mr-1" /> : <ChevronDown className="size-4 mr-1" />}
              Advanced (ML prediction data)
            </Button>
            {showAdvanced && (
              <div className="space-y-4 border-t pt-4">
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
              <Button type="submit" disabled={createShipment.isPending}>
                {createShipment.isPending ? <Loader2 className="size-4 animate-spin" /> : null}
                Create shipment
              </Button>
            </DialogFooter>
        </DialogContent>
    </Dialog>
  );
}
