"use client";

import { ChangeEvent, FormEvent, useRef, useState } from "react";
import { useRouter } from "next/navigation";

export function CreateAvatar() {
  const router = useRouter();
  const dialogRef = useRef<HTMLDialogElement>(null);
  const [selectedImageName, setSelectedImageName] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  function selectImage(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    setSelectedImageName(file?.name ?? null);
  }

  function closeDialog() {
    dialogRef.current?.close();
    setError("");
  }

  async function createAvatar(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    const form = new FormData(event.currentTarget);

    try {
      const response = await fetch("/api/avatars", {
        method: "POST",
        body: form,
      });
      const body = await response.json();
      if (!response.ok) throw new Error(body.detail ?? "Avatar creation failed.");
      closeDialog();
      router.push(`/dashboard/avatars/${body.id}`);
      router.refresh();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Avatar creation failed.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <>
      <button className="create-avatar-button" type="button" onClick={() => dialogRef.current?.showModal()}>
        <span aria-hidden="true">+</span> Create avatar
      </button>
      <dialog className="avatar-dialog" ref={dialogRef} onCancel={closeDialog}>
        <form className="avatar-create-form" onSubmit={createAvatar}>
          <div className="dialog-heading">
            <div>
              <p className="eyebrow">New profile</p>
              <h2>Create an avatar</h2>
            </div>
            <button className="dialog-close" type="button" aria-label="Close" onClick={closeDialog}>×</button>
          </div>

          <label className={`image-dropzone ${selectedImageName ? "has-selection" : ""}`}>
            <span aria-hidden="true">{selectedImageName ? "✓" : "+"}</span>
            <strong>{selectedImageName ?? "Choose a profile image"}</strong>
            <small>{selectedImageName ? "Click to choose a different image" : "PNG, JPG, or WebP · 10 MB maximum"}</small>
            <input accept="image/png,image/jpeg,image/webp" name="image" onChange={selectImage} required type="file" />
          </label>

          <label htmlFor="avatar-name">Name</label>
          <input id="avatar-name" maxLength={80} name="name" placeholder="Luna Vale" required />

          <label htmlFor="avatar-bio">Bio and dossier</label>
          <textarea id="avatar-bio" maxLength={20000} name="bio" placeholder="Describe their personality, history, style, interests, and voice…" required rows={8} />
          <small className="field-hint">Up to 20,000 characters</small>

          <label htmlFor="avatar-visibility">Visibility</label>
          <select defaultValue="private" id="avatar-visibility" name="visibility">
            <option value="private">Private — only you</option>
            <option value="unlisted">Unlisted — anyone with the link</option>
            <option value="public">Public — visible to everyone</option>
          </select>

          {error && <p className="error-message" role="alert">{error}</p>}
          <div className="dialog-actions">
            <button className="secondary-button" type="button" onClick={closeDialog}>Cancel</button>
            <button className="primary-button" disabled={submitting} type="submit">{submitting ? "Creating…" : "Create avatar"}</button>
          </div>
        </form>
      </dialog>
    </>
  );
}
