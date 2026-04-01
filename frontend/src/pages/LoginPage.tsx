import { useState } from "react";

import { api } from "../api/client";
import { useAuthStore } from "../hooks/useAuthStore";

export function LoginPage() {
  const setToken = useAuthStore((s) => s.setToken);
  const [email, setEmail] = useState("founder@example.com");
  const [password, setPassword] = useState("password123");
  const [fullName, setFullName] = useState("Product Owner");

  const submit = async (mode: "login" | "signup") => {
    const payload = mode === "signup" ? { email, password, full_name: fullName } : { email, password };
    const response = await api.post(`/auth/${mode}`, payload);
    setToken(response.data.access_token);
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="card p-8 w-full max-w-md">
        <h1 className="font-heading text-2xl text-ink">AI Life OS</h1>
        <p className="text-slate-600 mt-1">Automation meets adaptive personal OS.</p>

        <div className="mt-6 space-y-3">
          <input className="w-full rounded-lg border p-2" value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="Full name" />
          <input className="w-full rounded-lg border p-2" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
          <input className="w-full rounded-lg border p-2" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" />
        </div>

        <div className="mt-6 grid grid-cols-2 gap-3">
          <button className="rounded-lg bg-brand text-white py-2" onClick={() => submit("login")}>Login</button>
          <button className="rounded-lg bg-accent text-white py-2" onClick={() => submit("signup")}>Signup</button>
        </div>
      </div>
    </div>
  );
}
