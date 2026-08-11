import { cookies } from "next/headers";
import { redirect } from "next/navigation";

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
      <main className="dashboard-main">
        <p className="eyebrow">Signed in as @{user.username}</p>
        <h1>Your avatar studio is ready for ideas.</h1>
        <p>This is your home base. Create and shape the digital personalities in your studio.</p>
        <section className="coming-card">
          <h2>Your characters, all in one place</h2>
          <p>Visit Avatars to browse profiles and their image and video libraries.</p>
        </section>
      </main>
  );
}
