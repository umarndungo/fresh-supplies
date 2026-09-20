import { z } from "zod";

const envSchema = z.object({
  NEXT_PUBLIC_APP_NAME: z.string().min(1).default("Fresh Supplies"),
  NEXT_PUBLIC_APP_URL: z.string().url().default("http://localhost:3000"),
  // Either a full URL (local dev, where frontend/backend are on different
  // ports) or a root-relative path (deployed, where Caddy serves both under
  // one origin — see Caddyfile/docker-compose.yml's cloudflared refactor).
  // Axios resolves a relative baseURL against window.location in-browser.
  NEXT_PUBLIC_API_URL: z
    .string()
    .refine((v) => /^https?:\/\//.test(v) || v.startsWith("/"), {
      message: "must be a full http(s) URL or a root-relative path starting with /",
    })
    .default("/api/v1"),
  NEXT_PUBLIC_DEV_AUTH_BYPASS: z
    .union([z.literal("true"), z.literal("false"), z.boolean()])
    .default("false")
    .transform((val) => val === "true" || val === true),
});

const parsed = envSchema.safeParse({
  NEXT_PUBLIC_APP_NAME: process.env.NEXT_PUBLIC_APP_NAME,
  NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL,
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  NEXT_PUBLIC_DEV_AUTH_BYPASS: process.env.NEXT_PUBLIC_DEV_AUTH_BYPASS,
});

if (!parsed.success) {
  throw new Error(
    `Invalid environment configuration:\n${parsed.error.issues
      .map((issue) => `- ${issue.path.join(".")}: ${issue.message}`)
      .join("\n")}`
  );
}

export const env = parsed.data;
