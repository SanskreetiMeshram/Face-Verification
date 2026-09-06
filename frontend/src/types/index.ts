export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
  normalized_x: number;
  normalized_y: number;
  normalized_width: number;
  normalized_height: number;
}

export interface FaceDetail {
  index: number;
  confidence: number;
  bounding_box: BoundingBox;
  landmarks?: Record<string, number[]>;
  embedding_fingerprint: string;
}

export interface FaceDetectionResult {
  face_detected: boolean;
  face_count: number;
  faces: FaceDetail[];
  primary_confidence: number;
  embedding_generated: boolean;
  source_image_sha256: string;
  image_width: number;
  image_height: number;
  annotated_image_url?: string;
  detector_model: string;
  message: string;
}

export interface SearchResultItem {
  title: string;
  url: string;
  domain: string;
  thumbnail?: string;
  source: string;
  platform?: string;
  is_social_media: boolean;
  similarity?: string;
  published_at?: string;
  raw_metadata?: Record<string, any>;
}

export interface ReverseSearchResponse {
  success: boolean;
  provider: string;
  results_count: number;
  social_match_found: boolean;
  primary_match?: SearchResultItem;
  all_results: SearchResultItem[];
  is_demo_mode: boolean;
  demo_badge_message?: string;
  error_message?: string;
}

export interface CanonicalEvidence {
  source_image_sha256: string;
  reverse_search_provider: string;
  matched_url: string;
  platform: string;
  search_timestamp: string;
  match_metadata: Record<string, any>;
}

export interface EvidenceHashResult {
  evidence: CanonicalEvidence;
  canonical_json: string;
  sha256_hash: string;
  bytes32_hash: string;
}

export interface BlockchainRegisterResponse {
  success: boolean;
  record_id: number;
  evidence_hash: string;
  transaction_hash: string;
  block_number: number;
  gas_used?: number;
  contract_address: string;
  explorer_tx_url: string;
  submitter: string;
  timestamp: string;
  chain_id: number;
  chain_name: string;
  is_simulated: boolean;
  error_message?: string;
}

export interface BlockchainRecordData {
  record_id: number;
  evidence_hash: string;
  result_url: string;
  platform: string;
  timestamp: number;
  timestamp_iso: string;
  submitter: string;
  transaction_hash?: string;
  block_number?: number;
  explorer_tx_url?: string;
  explorer_contract_url?: string;
  chain_name: string;
  chain_id: number;
}

export interface VerificationResult {
  record_id: number;
  is_verified: boolean;
  status: 'VERIFIED' | 'RECORD_MISMATCH' | 'NOT_FOUND';
  calculated_hash: string;
  blockchain_hash: string;
  hashes_match: boolean;
  blockchain_record?: BlockchainRecordData;
  verification_message: string;
  tamper_detected: boolean;
  verified_at: string;
}

export interface PipelineStepStatus {
  step_number: number;
  name: string;
  status: 'pending' | 'processing' | 'success' | 'failed' | 'skipped';
  message: string;
  timestamp?: string;
}

export interface PipelineRunResponse {
  success: boolean;
  pipeline_id: string;
  steps: PipelineStepStatus[];
  face_analysis?: FaceDetectionResult;
  reverse_search?: ReverseSearchResponse;
  evidence_hash?: EvidenceHashResult;
  blockchain_record?: BlockchainRegisterResponse;
  verification?: VerificationResult;
  is_demo_mode: boolean;
  error_details?: string;
}

export interface SystemStatusResponse {
  app_name: string;
  app_version: string;
  face_ai_status: string;
  face_detector_model: string;
  reverse_image_provider: string;
  reverse_image_api_configured: boolean;
  blockchain_network: string;
  blockchain_chain_id: number;
  blockchain_rpc_connected: boolean;
  smart_contract_configured: boolean;
  smart_contract_address: string;
  is_demo_mode_active: boolean;
}
