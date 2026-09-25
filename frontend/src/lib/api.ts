import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const API_BASE_URL = `${BASE_URL}/api/v1`;

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const processArtifact = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  
  // Artificial 10s delay to simulate heavy extraction and integrity checking
  await new Promise(resolve => setTimeout(resolve, 10000));
  
  const res = await api.post("/artifacts/process", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return res.data;
};

export const createSession = async (
  signer_id: string, 
  verifier_id: string, 
  message_digest: string,
  artifact_name?: string,
  artifact_size?: number,
  artifact_type?: string
) => {
  const res = await api.post("/sessions/", { 
    signer_id, 
    verifier_id, 
    message_digest,
    artifact_name,
    artifact_size,
    artifact_type
  });
  return res.data;
};

export const createExperiment = async (session_id: string, shots: number, noise_enabled: boolean, attack_type: string, attack_strength: number) => {
  const res = await api.post("/experiments/", { session_id, shots, noise_enabled, attack_type, attack_strength });
  return res.data;
};

export const runExperiment = async (experiment_id: string) => {
  const res = await api.post(`/experiments/${experiment_id}/run`);
  return res.data;
};

export const getExperimentResult = async (experiment_id: string) => {
  const res = await api.get(`/experiments/${experiment_id}`);
  return res.data;
};

export const getLatestExperiment = async () => {
  const res = await api.get(`/experiments/latest`);
  return res.data;
};

export const getHealth = async () => {
  const [api_health, quantum, database, redis, worker] = await Promise.all([
    axios.get(`${BASE_URL}/health/`).catch(() => ({ data: { status: "OFFLINE" } })),
    axios.get(`${BASE_URL}/health/quantum`).catch(() => ({ data: { status: "OFFLINE" } })),
    axios.get(`${BASE_URL}/health/database`).catch(() => ({ data: { status: "OFFLINE" } })),
    axios.get(`${BASE_URL}/health/redis`).catch(() => ({ data: { status: "OFFLINE" } })),
    axios.get(`${BASE_URL}/health/worker`).catch(() => ({ data: { status: "OFFLINE" } }))
  ]);

  return {
    api: api_health.data,
    quantum: quantum.data,
    database: database.data,
    redis: redis.data,
    worker: worker.data
  };
};
