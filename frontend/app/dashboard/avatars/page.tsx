/* Dynamic avatar media can come from user-configured storage hosts. */
/* eslint-disable @next/next/no-img-element */
import Link from "next/link";
import { Avatar, AvatarMedia, getAvatarMedia, getAvatars, mediaUrl } from "./avatar-data";
import { CreateAvatar } from "./create-avatar";

type AvatarPreview = { avatar: Avatar; profileMedia: AvatarMedia | null; mediaCount: number };

export default async function AvatarsPage() {
  const avatars = await getAvatars();
  const previews: AvatarPreview[] = await Promise.all(
    avatars.map(async (avatar) => {
      const media = await getAvatarMedia(avatar.id);
      return {
        avatar,
        profileMedia: media.find((item) => item.id === avatar.profile_media_id) ?? null,
        mediaCount: media.length,
      };
    }),
  );

  return (
    <main className="avatars-page">
      <header className="page-heading">
        <div>
          <p className="eyebrow">Your cast</p>
          <h1>Avatars</h1>
          <p>Step into each profile to explore its identity and media library.</p>
        </div>
        <div className="avatar-heading-actions">
          <span className="avatar-total">{avatars.length} {avatars.length === 1 ? "avatar" : "avatars"}</span>
          <CreateAvatar />
        </div>
      </header>

      {previews.length ? (
        <section className="avatar-card-grid" aria-label="Your avatars">
          {previews.map(({ avatar, profileMedia, mediaCount }) => {
            const src = mediaUrl(profileMedia?.thumbnail_key ?? profileMedia?.storage_key ?? null);
            return (
              <Link className="avatar-preview-card" href={`/dashboard/avatars/${avatar.id}`} key={avatar.id}>
                <div className="avatar-preview-visual">
                  {src ? <img alt={`${avatar.name} profile`} src={src} /> : <span>{avatar.name.slice(0, 1).toUpperCase()}</span>}
                  <span className={`visibility-badge ${avatar.visibility}`}>{avatar.visibility}</span>
                </div>
                <div className="avatar-preview-copy">
                  <div>
                    <h2>{avatar.name}</h2>
                    <p className="avatar-handle">@{avatar.slug}</p>
                  </div>
                  <p className="avatar-card-bio">{avatar.bio || "This avatar’s story is still being written."}</p>
                  <div className="avatar-card-meta">
                    <span>{mediaCount} {mediaCount === 1 ? "media item" : "media items"}</span>
                    <span aria-hidden="true">View profile →</span>
                  </div>
                </div>
              </Link>
            );
          })}
        </section>
      ) : (
        <section className="avatars-empty">
          <div className="empty-avatar-mark" aria-hidden="true">A</div>
          <p className="eyebrow">Your cast is waiting</p>
          <h2>No avatars yet</h2>
          <p>Once you create an avatar, its profile will appear here.</p>
          <CreateAvatar />
        </section>
      )}
    </main>
  );
}
