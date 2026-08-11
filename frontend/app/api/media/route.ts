import { cookies } from "next/headers";
import { NextResponse } from "next/server";

const backendUrl = process.env.BACKEND_URL ?? "http://localhost:8000";

export async function GET(request: Request) {
  const token = (await cookies()).get("belskap_session")?.value;
  if (!token) return NextResponse.json({ detail: "Authentication required." }, { status: 401 });
  const key = new URL(request.url).searchParams.get("key");
  if (!key) return NextResponse.json({ detail: "Media key is required." }, { status: 400 });

  const response = await fetch(`${backendUrl}/api/v1/media/content?key=${encodeURIComponent(key)}`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "force-cache",
  });
  if (!response.ok) return NextResponse.json({ detail: "Media not found." }, { status: response.status });
  return new NextResponse(response.body, {
    status: 200,
    headers: {
      "Content-Type": response.headers.get("Content-Type") ?? "application/octet-stream",
      "Cache-Control": response.headers.get("Cache-Control") ?? "private, max-age=3600",
    },
  });
}
