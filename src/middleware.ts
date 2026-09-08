import { NextResponse } from "next/server";

const DEV_AUTH_BYPASS = process.env.NEXT_PUBLIC_DEV_AUTH_BYPASS === "true";

export function middleware() {
  if (DEV_AUTH_BYPASS) {
    return NextResponse.next();
  }

  // Auth is validated client-side because the refresh cookie belongs to the
  // separate API domain and is not visible to this frontend middleware.
  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/login", "/register"],
};
