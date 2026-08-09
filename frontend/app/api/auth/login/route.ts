import { NextResponse } from "next/server";

const backendUrl = process.env.BACKEND_URL ?? "http://localhost:8000";

export async function POST(request: Request) {
  const response = await fetch(`${backendUrl}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(await request.json()),
  });
  const body = await response.json();

  if (!response.ok) return NextResponse.json(body, { status: response.status });

  const result = NextResponse.json({ ok: true });
  result.cookies.set("belskap_session", body.access_token, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.COOKIE_SECURE === "true",
    maxAge: 60 * 60 * 24,
    path: "/",
  });
  return result;
}
