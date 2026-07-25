import { type NextRequest, NextResponse } from "next/server";

// Middleware placeholder prepared for Supabase authentication/session refresh rules.
export function middleware(_request: NextRequest) {
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
