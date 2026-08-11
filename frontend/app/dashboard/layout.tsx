import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { ReactNode } from "react";
import { DashboardShell } from "./dashboard-shell";

const backendUrl = process.env.BACKEND_URL ?? "http://localhost:8000";

export default async function DashboardLayout({ children }: { children: ReactNode }) {
  const token = (await cookies()).get("belskap_session")?.value;
  if (!token) redirect("/");

  const response = await fetch(`${backendUrl}/api/v1/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (!response.ok) redirect("/");
  const user: { email: string } = await response.json();

  return <DashboardShell email={user.email}>{children}</DashboardShell>;
}
