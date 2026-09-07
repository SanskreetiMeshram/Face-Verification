import {
  PipelineRunResponse,
  FaceDetectionResult,
  FaceCompareResult,
  ReverseSearchResponse,
  CanonicalEvidence,
  BlockchainRegisterResponse,
  BlockchainRecordData,
  VerificationResult,
  SystemStatusResponse
} from '../types';

const API_BASE = '/api';

export async function runPipeline(file: File): Promise<PipelineRunResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/pipeline/run`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Pipeline execution failed' }));
    throw new Error(errorData.detail || `Server responded with status ${response.status}`);
  }

  return response.json();
}

export async function detectFace(file: File): Promise<FaceDetectionResult> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/face/detect`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Face detection failed' }));
    throw new Error(err.detail || 'Face detection failed');
  }

  return response.json();
}

export async function compareFaces(file1: File, file2: File): Promise<FaceCompareResult> {
  const formData = new FormData();
  formData.append('file1', file1);
  formData.append('file2', file2);

  const response = await fetch(`${API_BASE}/face/compare`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Face comparison failed' }));
    throw new Error(err.detail || 'Face comparison failed');
  }

  return response.json();
}

export async function reverseSearch(file?: File, imageUrl?: string): Promise<ReverseSearchResponse> {
  const formData = new FormData();
  if (file) formData.append('file', file);
  if (imageUrl) formData.append('image_url', imageUrl);

  const response = await fetch(`${API_BASE}/reverse-search`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Reverse search failed' }));
    throw new Error(err.detail || 'Reverse search failed');
  }

  return response.json();
}

export async function registerBlockchain(evidence: CanonicalEvidence): Promise<BlockchainRegisterResponse> {
  const response = await fetch(`${API_BASE}/blockchain/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ evidence }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Registration failed' }));
    throw new Error(err.detail || 'Registration failed');
  }

  return response.json();
}

export async function getBlockchainRecord(recordId: number): Promise<BlockchainRecordData> {
  const response = await fetch(`${API_BASE}/blockchain/record/${recordId}`);
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Record not found' }));
    throw new Error(err.detail || 'Record not found');
  }
  return response.json();
}

export async function verifyEvidence(recordId: number, evidence: CanonicalEvidence): Promise<VerificationResult> {
  const response = await fetch(`${API_BASE}/blockchain/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ record_id: recordId, evidence }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Verification check failed' }));
    throw new Error(err.detail || 'Verification check failed');
  }

  return response.json();
}

export async function getHistory(): Promise<{ history: any[] }> {
  const response = await fetch(`${API_BASE}/blockchain/history`);
  if (!response.ok) {
    throw new Error('Failed to fetch verification history');
  }
  return response.json();
}

export async function getSystemStatus(): Promise<SystemStatusResponse> {
  const response = await fetch(`${API_BASE}/config/status`);
  if (!response.ok) {
    throw new Error('Failed to fetch system status');
  }
  return response.json();
}
