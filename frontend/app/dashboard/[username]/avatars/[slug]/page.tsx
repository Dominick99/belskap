import { notFound } from "next/navigation";
import { AvatarProfile } from "../../../avatars/avatar-profile";
import { getAvatarBySlug, getAvatarMedia } from "../../../avatars/avatar-data";

export default async function AvatarProfilePage({
  params,
}: {
  params: Promise<{ username: string; slug: string }>;
}) {
  const { username, slug } = await params;
  const avatar = await getAvatarBySlug(username, slug);
  if (!avatar) notFound();

  const media = await getAvatarMedia(avatar.id);
  return <AvatarProfile avatar={avatar} media={media} />;
}
