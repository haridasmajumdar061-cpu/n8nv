import { useEffect, useMemo, useState } from "react";
import ReactFlow, { Background, Controls, Edge, Node, addEdge, Connection, useEdgesState, useNodesState } from "reactflow";
import "reactflow/dist/style.css";

import { api } from "../../api/client";

type WorkflowCanvasProps = {
  onRun: (workflowId: number) => void;
};

const starterNodes: Node[] = [
  { id: "1", position: { x: 80, y: 60 }, data: { label: "Manual Trigger" }, type: "input" },
  { id: "2", position: { x: 360, y: 60 }, data: { label: "AI Summarize" } },
  { id: "3", position: { x: 620, y: 60 }, data: { label: "Telegram Action" }, type: "output" }
];

const starterEdges: Edge[] = [
  { id: "e1-2", source: "1", target: "2" },
  { id: "e2-3", source: "2", target: "3" }
];

export function WorkflowCanvas({ onRun }: WorkflowCanvasProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState(starterNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(starterEdges);
  const [workflowId, setWorkflowId] = useState<number | null>(null);

  const definition = useMemo(
    () => ({
      nodes: nodes.map((n) => ({ id: n.id, type: n.type === "input" ? "trigger" : n.type === "output" ? "action" : "ai", config: { label: n.data.label } })),
      edges: edges.map((e) => ({ source: e.source, target: e.target }))
    }),
    [nodes, edges]
  );

  const onConnect = (params: Connection) => setEdges((eds) => addEdge(params, eds));

  const saveWorkflow = async () => {
    const response = await api.post("/workflows", {
      name: "Generated Flow",
      description: "Built from drag and drop canvas",
      definition,
      is_active: true
    });
    setWorkflowId(response.data.id);
  };

  useEffect(() => {
    saveWorkflow().catch(() => undefined);
  }, []);

  return (
    <div className="card p-4 h-[460px]">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-heading text-lg">Workflow Builder</h3>
        <div className="space-x-2">
          <button className="px-3 py-1.5 rounded-md bg-slate-200" onClick={saveWorkflow}>Save</button>
          <button disabled={!workflowId} className="px-3 py-1.5 rounded-md bg-brand text-white disabled:opacity-60" onClick={() => workflowId && onRun(workflowId)}>Run</button>
        </div>
      </div>
      <ReactFlow nodes={nodes} edges={edges} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} onConnect={onConnect} fitView>
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}
