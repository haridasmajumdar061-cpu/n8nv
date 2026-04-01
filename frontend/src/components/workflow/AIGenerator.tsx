import { useState } from "react";

import { api } from "../../api/client";

type Props = {
  onApply: (definition: Record<string, unknown>) => void;
};

export function AIGenerator({ onApply }: Props) {
  const [prompt, setPrompt] = useState("When new Gmail arrives summarize with AI then send to Telegram");
  const [busy, setBusy] = useState(false);

  const generate = async () => {
    setBusy(true);
    try {
      const res = await api.post("/ai/prompt-to-workflow", { prompt });
      onApply(res.data.result);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="card p-4">
      <h3 className="font-heading text-lg">AI Workflow Generator</h3>
      <textarea className="mt-3 w-full rounded-lg border p-3 h-24" value={prompt} onChange={(e) => setPrompt(e.target.value)} />
      <button className="mt-3 rounded-md bg-accent text-white px-3 py-2" onClick={generate} disabled={busy}>
        {busy ? "Generating..." : "Generate JSON"}
      </button>
    </div>
  );
}
