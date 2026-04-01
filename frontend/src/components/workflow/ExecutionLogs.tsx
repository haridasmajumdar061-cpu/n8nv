import { useEffect, useState } from "react";

import { api } from "../../api/client";

type LogEntry = {
  level: string;
  message: string;
};

type Props = {
  executionId: number | null;
};

export function ExecutionLogs({ executionId }: Props) {
  const [logs, setLogs] = useState<LogEntry[]>([]);

  useEffect(() => {
    if (!executionId) return;

    api.get(`/executions/${executionId}/logs`).then((res) => setLogs(res.data));

    const base = (import.meta.env.VITE_API_URL || "http://localhost:8000/api").replace("http", "ws").replace("/api", "");
    const socket = new WebSocket(`${base}/api/logs/stream/${executionId}`);
    socket.onmessage = (event) => {
      const payload = JSON.parse(event.data);
      setLogs((prev) => [...prev, payload]);
    };

    return () => socket.close();
  }, [executionId]);

  return (
    <div className="card p-4 h-[460px] overflow-auto">
      <h3 className="font-heading text-lg">Real-time Logs</h3>
      <div className="mt-3 space-y-2 text-sm">
        {logs.map((log, idx) => (
          <div key={`${idx}-${log.message}`} className="rounded bg-slate-50 p-2 border border-slate-100">
            <span className="uppercase text-xs text-slate-500">{log.level}</span>
            <p>{log.message}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
