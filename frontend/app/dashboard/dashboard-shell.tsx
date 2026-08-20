"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { ReactNode, useState } from "react";
import { LogoutButton } from "./logout-button";

type DashboardShellProps = {
  children: ReactNode;
  email: string;
};

export function DashboardShell({ children, email }: DashboardShellProps) {
  const [open, setOpen] = useState(true);
  const pathname = usePathname();

  return (
    <div className={`dashboard ${open ? "sidebar-open" : "sidebar-closed"}`}>
      <aside className="sidebar" aria-label="Main navigation">
        <Link className="sidebar-brand" href="/dashboard" aria-label="Belskap home">
          <span className="sidebar-wordmark">
            <Image className="wordmark-glyph" src="/belskap-wordmark-mark.png" alt="" width={900} height={1065} priority />
            <span className="wordmark-letters">ELSKAP</span>
          </span>
          <Image className="sidebar-mark" src="/belskap-mark.png" alt="" width={320} height={320} priority />
        </Link>
        <nav className="sidebar-nav">
          <Link className={`sidebar-item ${pathname === "/dashboard" ? "active" : ""}`} href="/dashboard">
            <svg aria-hidden="true" viewBox="0 0 24 24"><path d="m3 11 9-8 9 8v9a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1Z" /></svg>
            <span>Home</span>
          </Link>
          <Link className={`sidebar-item ${pathname.startsWith("/dashboard/avatars") ? "active" : ""}`} href="/dashboard/avatars">
            <svg aria-hidden="true" viewBox="0 0 24 24"><circle cx="12" cy="8" r="4" /><path d="M4.5 21a7.5 7.5 0 0 1 15 0M19 5v6M16 8h6" /></svg>
            <span>Avatars</span>
          </Link>
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-item settings" title={email}>
            <svg aria-hidden="true" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3" /><path d="M19 12a7 7 0 0 0-.1-1l2-1.5-2-3.4-2.4 1A8 8 0 0 0 15 6l-.3-2.6h-4L10.4 6a8 8 0 0 0-1.5.9l-2.4-1-2 3.4 2 1.6a7 7 0 0 0 0 2.2l-2 1.6 2 3.4 2.4-1a8 8 0 0 0 1.5.9l.3 2.6h4L15 18a8 8 0 0 0 1.5-.9l2.4 1 2-3.4-2-1.6a7 7 0 0 0 .1-1Z" /></svg>
            <span>Settings</span>
          </div>
          {open && <small className="account-email">{email}</small>}
          <LogoutButton />
        </div>
      </aside>

      <button className="sidebar-edge-toggle" type="button" onClick={() => setOpen((value) => !value)} aria-expanded={open} aria-label={open ? "Collapse sidebar" : "Expand sidebar"}>
        <span aria-hidden="true">{open ? "‹" : "›"}</span>
      </button>
      {open && <button className="sidebar-scrim" onClick={() => setOpen(false)} aria-label="Close sidebar" />}
      <div className="dashboard-content">{children}</div>
    </div>
  );
}
