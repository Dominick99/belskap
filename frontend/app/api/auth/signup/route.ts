import { NextResponse } from "next/server";

const backendUrl = process.env.BACKEND_URL ?? "http://localhost:8000";

export async function POST(request: Request) {
  const credentials = await request.json();
  const registration = await fetch(`${backendUrl}/api/v1/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(credentials),
  });
  const registrationBody = await registration.json();

  if (!registration.ok) {
    return NextResponse.json(registrationBody, { status: registration.status });
  }

  const login = await fetch(`${backendUrl}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(credentials),
  });
  const loginBody = await login.json();
  if (!login.ok) return NextResponse.json(loginBody, { status: login.status });

  const result = NextResponse.json({ ok: true }, { status: 201 });
  result.cookies.set("belskap_session", loginBody.access_token, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.COOKIE_SECURE === "true",
    maxAge: 60 * 60 * 24,
    path: "/",
  });
  return result;
}
