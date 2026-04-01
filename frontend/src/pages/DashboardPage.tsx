import { useState } from "react";

import { api } from "../api/client";
import { LifeOSPanel } from "../components/lifeos/LifeOSPanel";
import { AIGenerator } from "../components/workflow/AIGenerator";
import { ExecutionLogs } from "../components/workflow/ExecutionLogs";
import { WorkflowCanvas } from "../components/workflow/WorkflowCanvas";
import { useAuthStore } from "../hooks/useAuthStore";

export function DashboardPage() {
  const setToken = useAuthStore((s) => s.setToken);
  const [executionId, setExecutionId] = useState<number | null>(null);

  const onRun = async (workflowId: number) => {
    const res = await api.post("/executions/run", { workflow_id: workflowId });
    setExecutionId(res.data.id);
  };

  return (
    <div className="min-h-screen p-6">
      <header className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-heading text-3xl text-ink">AI Life OS Platform</h1>
          <p className="text-slate-600">Workflow automation + personal operating intelligence.</p>
        </div>
        <button className="rounded-md bg-slate-900 text-white px-3 py-2" onClick={() => setToken(null)}>Logout</button>
      </header>

      <section className="grid grid-cols-1 xl:grid-cols-3 gap-4 mb-4">
        <div className="xl:col-span-2">
          <WorkflowCanvas onRun={onRun} />
        </div>
        <ExecutionLogs executionId={executionId} />
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <AIGenerator onApply={(wf) => console.log("AI workflow", wf)} />
        <LifeOSPanel />
      </section>
    </div>
  );
}
