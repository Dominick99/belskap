"use client";

import { ReactNode, useState } from "react";
import { LogoutButton } from "./logout-button";

type DashboardShellProps = {
  children: ReactNode;
  email: string;
};

function ChevronIcon({ open }: { open: boolean }) {
  return <svg aria-hidden="true" viewBox="0 0 24 24"><path d={open ? "m15 18-6-6 6-6" : "m9 18 6-6-6-6"} /></svg>;
}

function HomeIcon() {
  return <svg aria-hidden="true" viewBox="0 0 24 24"><path d="m3 11 9-8 9 8v9a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1Z" /></svg>;
}

function SettingsIcon() {
  return <svg aria-hidden="true" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06-2.83 2.83-.06-.06a1.7 1.7 0 0 0-1.88-.34 1.7 1.7 0 0 0-1.03 1.56V21h-4v-.08A1.7 1.7 0 0 0 8.96 19.4a1.7 1.7 0 0 0-1.88.34l-.06.06-2.83-2.83.06-.06A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-1.56-1.03H3v-4h.08A1.7 1.7 0 0 0 4.6 8.94a1.7 1.7 0 0 0-.34-1.88L4.2 7l2.83-2.83.06.06a1.7 1.7 0 0 0 1.88.34H9A1.7 1.7 0 0 0 10 3.08V3h4v.08a1.7 1.7 0 0 0 1.03 1.56 1.7 1.7 0 0 0 1.88-.34l.06-.06L19.8 7l-.06.06a1.7 1.7 0 0 0-.34 1.88v.03A1.7 1.7 0 0 0 20.92 10H21v4h-.08A1.7 1.7 0 0 0 19.4 15Z" /></svg>;
}

export function DashboardShell({ children, email }: DashboardShellProps) {
  const [open, setOpen] = useState(true);
  const [settingsOpen, setSettingsOpen] = useState(false);

  return (
    <div className={`dashboard ${open ? "sidebar-open" : "sidebar-closed"}`}>
      <aside className="sidebar" aria-label="Main navigation">
        <nav className="sidebar-nav">
          <a className="sidebar-item active" href="/dashboard"><HomeIcon /><span>Home</span></a>
        </nav>

        <div className="sidebar-footer">
          <button className="sidebar-item" type="button" onClick={() => setSettingsOpen((value) => !value)} aria-expanded={settingsOpen}>
            <SettingsIcon /><span>Settings</span>
          </button>
          {settingsOpen && open && (
            <section className="settings-card" aria-label="Account settings">
              <strong>Account</strong>
              <span>{email}</span>
            </section>
          )}
          <LogoutButton compact={!open} />
        </div>
      </aside>

      <button className="sidebar-edge-toggle" type="button" onClick={() => setOpen((value) => !value)} aria-expanded={open} aria-label={open ? "Collapse sidebar" : "Expand sidebar"}>
        <ChevronIcon open={open} />
      </button>
      {open && <button className="sidebar-scrim" onClick={() => setOpen(false)} aria-label="Close sidebar" />}
      <div className="dashboard-content">{children}</div>
    </div>
  );
}
