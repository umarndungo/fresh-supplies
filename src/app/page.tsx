import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { ROUTES, SESSION_FLAG_COOKIE } from "@/lib/constants";

export default async function RootPage() {
  const cookieStore = await cookies();
  const hasSession = cookieStore.has(SESSION_FLAG_COOKIE);
  redirect(hasSession ? ROUTES.dashboard : ROUTES.login);
}
