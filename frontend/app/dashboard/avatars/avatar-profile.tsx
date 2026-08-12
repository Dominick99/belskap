/* Dynamic avatar media can come from user-configured storage hosts. */
/* eslint-disable @next/next/no-img-element */
import Link from "next/link";
import { Avatar, AvatarMedia, mediaUrl } from "./avatar-data";

export function AvatarProfile({ avatar, media }: { avatar: Avatar; media: AvatarMedia[] }) {
  const profileMedia = media.find((item) => item.id === avatar.profile_media_id && item.media_type === "image");
  const profileSrc = mediaUrl(profileMedia?.storage_key ?? null);

  return (
    <main className="avatar-profile-page">
      <Link className="back-link" href="/dashboard/avatars">← All avatars</Link>
      <section className="profile-header">
        <div className="profile-picture">
          {profileSrc ? <img alt={`${avatar.name} profile`} src={profileSrc} /> : <span>{avatar.name.slice(0, 1).toUpperCase()}</span>}
        </div>
        <div className="profile-copy">
          <div className="profile-name-line">
            <div><p className="avatar-handle">@{avatar.slug}</p><h1>{avatar.name}</h1></div>
            <span className={`visibility-badge ${avatar.visibility}`}>{avatar.visibility}</span>
          </div>
          <div className="profile-stats">
            <span><strong>{media.length}</strong> media</span>
            <span><strong>{media.filter((item) => item.media_type === "image").length}</strong> images</span>
            <span><strong>{media.filter((item) => item.media_type === "video").length}</strong> videos</span>
          </div>
          <p className="profile-bio">{avatar.bio || "This avatar’s story is still being written."}</p>
        </div>
      </section>
      <section className="profile-feed">
        <div className="feed-heading"><h2>Media</h2><span>Latest first</span></div>
        {media.length ? (
          <div className="media-grid">
            {media.map((item) => {
              const src = mediaUrl(item.thumbnail_key ?? item.storage_key);
              return (
                <article className="media-tile" key={item.id}>
                  {src ? (item.media_type === "video" ? <video aria-label={`${avatar.name} video`} muted preload="metadata" src={src} /> : <img alt={`${avatar.name} media`} src={src} />) : (
                    <div className="media-placeholder"><span>{item.media_type === "video" ? "▶" : "◇"}</span><small>{item.media_type}</small></div>
                  )}
                  {item.media_type === "video" && <span className="video-badge">Video</span>}
                </article>
              );
            })}
          </div>
        ) : (
          <div className="media-empty"><h3>No media yet</h3><p>Images and videos added to this avatar will build its profile grid.</p></div>
        )}
      </section>
    </main>
  );
}
