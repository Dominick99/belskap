import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { DashboardShell } from "./dashboard-shell";

const backendUrl = process.env.BACKEND_URL ?? "http://localhost:8000";

export default async function DashboardPage() {
  const token = (await cookies()).get("belskap_session")?.value;
  if (!token) redirect("/");

  const response = await fetch(`${backendUrl}/api/v1/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (!response.ok) redirect("/");
  const user: { email: string; username: string } = await response.json();

  return (
    <DashboardShell email={user.email}>
      <main className="dashboard-main">
        <p className="eyebrow">Signed in as @{user.username}</p>
        <h1>Your avatar studio is ready for ideas.</h1>
        <p>This is your home base. Soon, you&apos;ll create avatars and connect AI agents to them here.</p>
        <section className="coming-card">
          <h2>Avatar creation is coming next</h2>
          <p>For now, your account and secure session are up and running.</p>
        </section>
      </main>
    </DashboardShell>
  );
}
