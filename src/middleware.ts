import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { SESSION_FLAG_COOKIE } from "@/lib/constants";

const PROTECTED_PREFIXES = ["/dashboard"];
const AUTH_PAGES = ["/login", "/register"];

const DEV_AUTH_BYPASS = process.env.NEXT_PUBLIC_DEV_AUTH_BYPASS === "true";

export function middleware(request: NextRequest) {
  if (DEV_AUTH_BYPASS) {
    return NextResponse.next();
  }

  const { pathname } = request.nextUrl;
  const hasSession = request.cookies.has(SESSION_FLAG_COOKIE);

  const isProtected = PROTECTED_PREFIXES.some((prefix) => pathname.startsWith(prefix));
  const isAuthPage = AUTH_PAGES.some((page) => pathname.startsWith(page));

  if (isProtected && !hasSession) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirectTo", pathname);
    return NextResponse.redirect(loginUrl);
  }

  if (isAuthPage && hasSession) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/login", "/register"],
};
