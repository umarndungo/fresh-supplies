import type { ApiErrorDetail } from "@/types/api.types";

export class ApiError extends Error {
  readonly statusCode: number;
  readonly errors?: ApiErrorDetail[];

  constructor(message: string, statusCode: number, errors?: ApiErrorDetail[]) {
    super(message);
    this.name = "ApiError";
    this.statusCode = statusCode;
    this.errors = errors;
  }
}
