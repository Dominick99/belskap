"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

type Mode = "login" | "signup";

function errorMessage(detail: unknown): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && typeof detail[0]?.msg === "string") {
    return detail[0].msg.replace(/^Value error, /, "");
  }
  return "Something went wrong. Please try again.";
}

export default function AuthPage() {
  const router = useRouter();
  const [mode, setMode] = useState<Mode>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch(`/api/auth/${mode}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const body = await response.json();

      if (!response.ok) {
        setError(errorMessage(body.detail));
        return;
      }

      router.push("/dashboard");
      router.refresh();
    } catch {
      setError("We couldn't reach the server. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  function changeMode(nextMode: Mode) {
    setMode(nextMode);
    setError("");
  }

  return (
    <main className="auth-shell">
      <section className="form-panel" aria-labelledby="auth-title">
        <div className="auth-card">
          <h1 id="auth-title">{mode === "login" ? "Welcome back" : "Create your account"}</h1>
          <p className="form-intro">
            {mode === "login"
              ? "Sign in to continue building your avatar."
              : "Start creating your first AI avatar today."}
          </p>

          <div className="mode-switch" aria-label="Choose authentication mode">
            <button className={mode === "login" ? "active" : ""} onClick={() => changeMode("login")} type="button">Log in</button>
            <button className={mode === "signup" ? "active" : ""} onClick={() => changeMode("signup")} type="button">Sign up</button>
          </div>

          <form onSubmit={submit}>
            <label htmlFor="email">Email</label>
            <input id="email" type="email" autoComplete="email" placeholder="you@example.com" value={email} onChange={(event) => setEmail(event.target.value)} required />

            <label htmlFor="password">Password</label>
            <input id="password" type="password" autoComplete={mode === "login" ? "current-password" : "new-password"} placeholder={mode === "signup" ? "At least 8 characters" : "Your password"} minLength={mode === "signup" ? 8 : 1} maxLength={128} value={password} onChange={(event) => setPassword(event.target.value)} required />

            {error && <p className="error-message" role="alert">{error}</p>}

            <button className="primary-button" disabled={loading} type="submit">
              {loading ? "Please wait..." : mode === "login" ? "Log in" : "Create account"}
            </button>
          </form>
          <p className="terms">By continuing, you agree to keep things creative and kind.</p>
        </div>
      </section>
    </main>
  );
}
