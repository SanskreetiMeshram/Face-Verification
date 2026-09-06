import React, { useState } from 'react';
import { ImageUploader } from '../components/ImageUploader';
import { PipelineProgress } from '../components/PipelineProgress';
import { FaceDetectionCard } from '../components/FaceDetectionCard';
import { ReverseSearchCard } from '../components/ReverseSearchCard';
import { BlockchainCard } from '../components/BlockchainCard';
import { VerificationBadge } from '../components/VerificationBadge';
import { TechnicalDetails } from '../components/TechnicalDetails';
import { PipelineRunResponse, SystemStatusResponse, SearchResultItem, CanonicalEvidence } from '../types';
import { runPipeline, registerBlockchain, verifyEvidence } from '../services/api';
import { ShieldCheck, Sparkles, ArrowRight, AlertOctagon, Lock, CheckCircle2 } from 'lucide-react';

interface DashboardProps {
  status: SystemStatusResponse | null;
  onNavigateToTamper: (evidence: any, recordId: number) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ status, onNavigateToTamper }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [pipelineData, setPipelineData] = useState<PipelineRunResponse | null>(null);
  const [errorDetails, setErrorDetails] = useState<string | null>(null);
  const [isRegisteringSelected, setIsRegisteringSelected] = useState(false);
  const [registerSuccessMessage, setRegisterSuccessMessage] = useState<string | null>(null);

  const handleImageSelected = (file: File, url: string) => {
    setSelectedFile(file);
    setPreviewUrl(url);
    setPipelineData(null);
    setErrorDetails(null);
    setRegisterSuccessMessage(null);
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setPipelineData(null);
    setErrorDetails(null);
    setRegisterSuccessMessage(null);
  };

  const handleRunPipeline = async () => {
    if (!selectedFile) return;

    try {
      setIsLoading(true);
      setErrorDetails(null);
      setRegisterSuccessMessage(null);
      const res = await runPipeline(selectedFile);
      setPipelineData(res);
      if (!res.success && res.error_details) {
        setErrorDetails(res.error_details);
      }
    } catch (err: any) {
      setErrorDetails(err.message || 'An unexpected error occurred while executing the pipeline.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegisterSelectedResult = async (item: SearchResultItem) => {
    if (!pipelineData?.face_analysis) return;
    try {
      setIsRegisteringSelected(true);
      setErrorDetails(null);
      setRegisterSuccessMessage(null);

      const nowIso = new Date().toISOString();
      const evidence: CanonicalEvidence = {
        source_image_sha256: pipelineData.face_analysis.source_image_sha256,
        reverse_search_provider: pipelineData.reverse_search?.provider || 'Reverse Search',
        matched_url: item.url,
        platform: item.platform || 'Web Discovery',
        search_timestamp: nowIso,
        match_metadata: {
          title: item.title,
          domain: item.domain,
          url: item.url,
          platform: item.platform,
          discoveredAt: nowIso,
          similarity: item.similarity
        }
      };

      const regRes = await registerBlockchain(evidence);
      const verRes = await verifyEvidence(regRes.record_id, evidence);

      setPipelineData(prev => prev ? {
        ...prev,
        blockchain_record: regRes,
        verification: verRes
      } : null);

      setRegisterSuccessMessage(`Record #${regRes.record_id} registered and verified successfully on-chain!`);
    } catch (err: any) {
      setErrorDetails(`Failed to register selected result on-chain: ${err.message}`);
    } finally {
      setIsRegisteringSelected(false);
    }
  };

  return (
    <div className="space-y-8 pb-16">
      
      {/* Hero Section */}
      <div className="text-center space-y-3 pt-4">
        <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 text-xs font-semibold mb-1 shadow-sm">
          <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
          <span>Authorized Image → Web Discovery → Blockchain Verification</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white">
          Verify. Discover. Prove.
        </h1>
        <p className="text-base sm:text-lg text-slate-400 max-w-2xl mx-auto font-medium">
          Trace authorized image content to public web sources and create a tamper-evident blockchain record.
        </p>

        {/* Privacy badge */}
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-lg bg-slate-900/80 border border-slate-800 text-slate-400 text-xs mt-2">
          <Lock className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
          <span>Process only images you are authorized to use. No raw biometrics are stored on-chain.</span>
        </div>
      </div>

      {/* Main Upload Zone */}
      <ImageUploader
        onImageSelected={handleImageSelected}
        onRunPipeline={handleRunPipeline}
        isLoading={isLoading}
        selectedFile={selectedFile}
        previewUrl={previewUrl}
        onReset={handleReset}
      />

      {/* Pipeline Progress Stepper */}
      {(isLoading || pipelineData) && (
        <PipelineProgress
          steps={pipelineData?.steps || []}
          isLoading={isLoading}
        />
      )}

      {/* Success notification banner if any */}
      {registerSuccessMessage && (
        <div className="p-4 rounded-2xl bg-emerald-950/40 border border-emerald-500/40 text-emerald-300 text-xs flex items-center space-x-3 shadow-lg shadow-emerald-950/20">
          <CheckCircle2 className="w-5 h-5 shrink-0 text-emerald-400" />
          <div>
            <strong className="font-bold block text-sm">Blockchain Confirmation:</strong>
            <span>{registerSuccessMessage}</span>
          </div>
        </div>
      )}

      {/* Error notification banner if any */}
      {errorDetails && (
        <div className="p-4 rounded-2xl bg-rose-950/40 border border-rose-500/40 text-rose-300 text-xs flex items-center space-x-3 shadow-lg shadow-rose-950/20">
          <AlertOctagon className="w-5 h-5 shrink-0 text-rose-400" />
          <div>
            <strong className="font-bold block text-sm">Pipeline Notice:</strong>
            <span>{errorDetails}</span>
          </div>
        </div>
      )}

      {/* Verification Badge */}
      {pipelineData?.verification && (
        <VerificationBadge verification={pipelineData.verification} />
      )}

      {/* Analysis & Blockchain Cards Grid */}
      {(pipelineData || previewUrl) && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left: Face AI Card */}
            <FaceDetectionCard
              faceData={pipelineData?.face_analysis || null}
              imageSrc={previewUrl}
            />

            {/* Right: Reverse Search Card */}
            <ReverseSearchCard
              searchData={pipelineData?.reverse_search || null}
              onRegisterOnChain={handleRegisterSelectedResult}
              isRegistering={isRegisteringSelected}
            />
          </div>

          {/* Full-width Blockchain Card */}
          {pipelineData?.blockchain_record && (
            <BlockchainCard
              blockchainData={pipelineData.blockchain_record}
            />
          )}

          {/* Quick link to Tamper Lab */}
          {pipelineData?.blockchain_record && pipelineData?.evidence_hash && (
            <div className="p-4 rounded-2xl bg-gradient-to-r from-purple-950/30 via-slate-900 to-indigo-950/30 border border-purple-500/30 flex flex-col sm:flex-row items-center justify-between gap-4">
              <div>
                <h4 className="text-sm font-bold text-white flex items-center space-x-2">
                  <ShieldCheck className="w-4 h-4 text-purple-400" />
                  <span>Want to test tampering this exact record?</span>
                </h4>
                <p className="text-xs text-slate-400">
                  Open the Tamper Lab with Record #{pipelineData.blockchain_record.record_id} to test how alterations are detected on-chain.
                </p>
              </div>

              <button
                onClick={() =>
                  onNavigateToTamper(
                    pipelineData.evidence_hash?.evidence,
                    pipelineData.blockchain_record!.record_id
                  )
                }
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-purple-600 hover:bg-purple-500 text-white flex items-center space-x-1.5 shadow-md shadow-purple-500/20 transition whitespace-nowrap"
              >
                <span>Open in Tamper Lab</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          )}

          {/* Technical Details Collapsible Drawer */}
          <TechnicalDetails
            pipelineData={pipelineData}
            status={status}
          />
        </div>
      )}

    </div>
  );
};
