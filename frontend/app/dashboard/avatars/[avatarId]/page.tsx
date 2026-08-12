import { notFound, redirect } from "next/navigation";
import { getAvatar, getCurrentUser } from "../avatar-data";

export default async function LegacyAvatarProfilePage({ params }: { params: Promise<{ avatarId: string }> }) {
  const { avatarId } = await params;
  const [avatar, user] = await Promise.all([getAvatar(avatarId), getCurrentUser()]);
  if (!avatar) notFound();
  redirect(`/dashboard/${user.username}/avatars/${avatar.slug}`);
}
