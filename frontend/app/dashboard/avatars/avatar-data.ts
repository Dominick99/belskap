import { cookies } from "next/headers";
import { redirect } from "next/navigation";

const backendUrl = process.env.BACKEND_URL ?? "http://localhost:8000";
const mediaBaseUrl = process.env.NEXT_PUBLIC_MEDIA_BASE_URL?.replace(/\/$/, "");

export type Avatar = {
  id: string;
  user_id: string;
  name: string;
  slug: string;
  bio: string | null;
  visibility: "private" | "unlisted" | "public";
  profile_media_id: string | null;
  created_at: string;
  updated_at: string;
};

export type AvatarMedia = {
  id: string;
  avatar_id: string;
  media_type: "image" | "video";
  storage_key: string;
  thumbnail_key: string | null;
  mime_type: string | null;
  width: number | null;
  height: number | null;
  duration_seconds: number | null;
  created_at: string;
  updated_at: string;
};

async function authenticatedFetch(path: string) {
  const token = (await cookies()).get("belskap_session")?.value;
  if (!token) redirect("/");
  const response = await fetch(`${backendUrl}${path}`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (response.status === 401) redirect("/");
  return response;
}

export async function getAvatars(): Promise<Avatar[]> {
  const response = await authenticatedFetch("/api/v1/avatars");
  return response.ok ? response.json() : [];
}

export async function getAvatar(id: string): Promise<Avatar | null> {
  const response = await authenticatedFetch(`/api/v1/avatars/${id}`);
  return response.ok ? response.json() : null;
}

export async function getAvatarMedia(id: string): Promise<AvatarMedia[]> {
  const response = await authenticatedFetch(`/api/v1/avatars/${id}/media`);
  return response.ok ? response.json() : [];
}

export function mediaUrl(key: string | null): string | null {
  if (!key) return null;
  if (/^https?:\/\//.test(key)) return key;
  return mediaBaseUrl ? `${mediaBaseUrl}/${key.replace(/^\//, "")}` : null;
}
