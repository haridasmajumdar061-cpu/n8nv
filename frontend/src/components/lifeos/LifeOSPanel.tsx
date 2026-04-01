import { useState } from "react";

import { api } from "../../api/client";

export function LifeOSPanel() {
  const [skillText, setSkillText] = useState("python, automation, copywriting");
  const [suggestions, setSuggestions] = useState<string[]>([]);

  const fetchIncomeIdeas = async () => {
    const skills = skillText.split(",").map((s) => s.trim()).filter(Boolean);
    const res = await api.post("/life-os/income-suggestions", { skills, available_hours_per_week: 12 });
    const list = (res.data.strategies || []).map((x: { title: string }) => x.title);
    setSuggestions(list);
  };

  return (
    <div className="card p-4">
      <h3 className="font-heading text-lg">AI Life OS</h3>
      <p className="text-sm text-slate-600 mt-1">Adaptive planner, memory, focus and income copilot.</p>
      <input className="mt-3 w-full rounded-lg border p-2" value={skillText} onChange={(e) => setSkillText(e.target.value)} />
      <button className="mt-3 rounded-md bg-brand text-white px-3 py-2" onClick={fetchIncomeIdeas}>Suggest Income Paths</button>
      <ul className="mt-3 space-y-1 text-sm text-slate-700 list-disc pl-5">
        {suggestions.map((s) => (
          <li key={s}>{s}</li>
        ))}
      </ul>
    </div>
  );
}
