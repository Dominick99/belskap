import { cookies } from "next/headers";
import { NextResponse } from "next/server";

const backendUrl = process.env.BACKEND_URL ?? "http://localhost:8000";

function slugify(name: string) {
  return name
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 70) || "avatar";
}

export async function POST(request: Request) {
  const token = (await cookies()).get("belskap_session")?.value;
  if (!token) return NextResponse.json({ detail: "Authentication required." }, { status: 401 });

  const body = await request.json();
  const baseSlug = slugify(body.name ?? "");
  let response: Response | null = null;

  for (let attempt = 0; attempt < 2; attempt += 1) {
    const slug = attempt === 0 ? baseSlug : `${baseSlug}-${crypto.randomUUID().slice(0, 6)}`;
    response = await fetch(`${backendUrl}/api/v1/avatars`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        name: body.name,
        bio: body.bio,
        visibility: body.visibility,
        slug,
      }),
    });
    if (response.status !== 409) break;
  }

  if (!response) return NextResponse.json({ detail: "Unable to create avatar." }, { status: 500 });
  const result = await response.json();
  return NextResponse.json(result, { status: response.status });
}
