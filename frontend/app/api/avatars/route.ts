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

  const form = await request.formData();
  const image = form.get("image");
  const name = String(form.get("name") ?? "");
  const bio = String(form.get("bio") ?? "");
  const visibility = String(form.get("visibility") ?? "private");
  if (!(image instanceof File)) {
    return NextResponse.json({ detail: "A profile image is required." }, { status: 422 });
  }

  const baseSlug = slugify(name);
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
        name,
        bio,
        visibility,
        slug,
      }),
    });
    if (response.status !== 409) break;
  }

  if (!response) return NextResponse.json({ detail: "Unable to create avatar." }, { status: 500 });
  const avatar = await response.json();
  if (!response.ok) return NextResponse.json(avatar, { status: response.status });

  const upload = new FormData();
  upload.append("image", image);
  const uploadResponse = await fetch(
    `${backendUrl}/api/v1/avatars/${avatar.id}/media/upload-image?set_as_profile=true`,
    { method: "POST", headers: { Authorization: `Bearer ${token}` }, body: upload },
  );
  const media = await uploadResponse.json();
  if (!uploadResponse.ok) {
    await fetch(`${backendUrl}/api/v1/avatars/${avatar.id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    return NextResponse.json(media, { status: uploadResponse.status });
  }
  return NextResponse.json({ ...avatar, profile_media_id: media.id }, { status: 201 });
}
