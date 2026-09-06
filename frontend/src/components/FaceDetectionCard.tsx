import React from 'react';
import { ScanFace, CheckCircle2, AlertCircle, ShieldAlert, Cpu, Hash } from 'lucide-react';
import { FaceDetectionResult } from '../types';
import { CanvasBoundingBox } from './CanvasBoundingBox';

interface FaceDetectionCardProps {
  faceData: FaceDetectionResult | null;
  imageSrc: string | null;
}

export const FaceDetectionCard: React.FC<FaceDetectionCardProps> = ({ faceData, imageSrc }) => {
  if (!faceData) {
    return (
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-col items-center justify-center min-h-[300px] text-center text-slate-500">
        <ScanFace className="w-12 h-12 text-slate-700 mb-3 animate-pulse" />
        <p className="text-sm font-semibold text-slate-400">Awaiting Image Analysis</p>
        <p className="text-xs text-slate-600 mt-1">Upload an image to trigger face detection & encoding</p>
      </div>
    );
  }

  const primaryFace = faceData.faces && faceData.faces.length > 0 ? faceData.faces[0] : null;

  return (
    <div className="glass-panel p-6 rounded-2xl border border-slate-800 shadow-xl relative overflow-hidden">
      {/* Glow highlight */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none"></div>

      <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-800/80">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
            <ScanFace className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">Face Analysis</h3>
            <p className="text-xs text-slate-400">Neural Detection & Local Embedding Extraction</p>
          </div>
        </div>

        <div>
          {faceData.face_detected ? (
            <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Face Detected</span>
            </span>
          ) : (
            <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
              <AlertCircle className="w-3.5 h-3.5" />
              <span>No Face Detected</span>
            </span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Visual bounding box canvas */}
        <div>
          {imageSrc && (
            <CanvasBoundingBox
              imageSrc={imageSrc}
              faces={faceData.faces}
              className="w-full shadow-inner"
            />
          )}
          <p className="text-[11px] text-slate-500 text-center mt-2 font-mono">
            {faceData.image_width} × {faceData.image_height} px • {faceData.detector_model}
          </p>
        </div>

        {/* Face metrics & embedding summary */}
        <div className="space-y-4 flex flex-col justify-between">
          <div className="space-y-3">
            {/* Faces Count & Confidence */}
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                <span className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold">
                  Faces Found
                </span>
                <p className="text-xl font-bold text-white mt-0.5">
                  {faceData.face_count}
                </p>
              </div>

              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                <span className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold">
                  Detection Confidence
                </span>
                <p className="text-xl font-bold text-cyan-400 mt-0.5">
                  {(faceData.primary_confidence * 100).toFixed(1)}%
                </p>
              </div>
            </div>

            {/* Embedding Fingerprint */}
            <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800">
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-semibold text-slate-300 flex items-center space-x-1.5">
                  <Hash className="w-3.5 h-3.5 text-purple-400" />
                  <span>Embedding Fingerprint</span>
                </span>
                <span className="text-[10px] font-mono text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20">
                  128-D Vector SHA-256
                </span>
              </div>
              <div className="p-2 rounded-lg bg-black/50 font-mono text-xs text-slate-300 break-all select-all border border-slate-800/80">
                {primaryFace ? primaryFace.embedding_fingerprint : 'None (No face detected)'}
              </div>
              <p className="text-[10px] text-slate-500 mt-1.5">
                Generated locally via normalized gradient moments. Biometric vector remains private.
              </p>
            </div>

            {/* Bounding Box Metrics */}
            {primaryFace && (
              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-xs">
                <span className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold block mb-1">
                  Bounding Box Coordinates
                </span>
                <div className="grid grid-cols-4 gap-2 font-mono text-[11px] text-slate-300">
                  <div>X: <span className="text-cyan-400">{primaryFace.bounding_box.x}</span></div>
                  <div>Y: <span className="text-cyan-400">{primaryFace.bounding_box.y}</span></div>
                  <div>W: <span className="text-cyan-400">{primaryFace.bounding_box.width}</span></div>
                  <div>H: <span className="text-cyan-400">{primaryFace.bounding_box.height}</span></div>
                </div>
              </div>
            )}
          </div>

          {/* Privacy Note */}
          <div className="p-3 rounded-xl bg-indigo-950/20 border border-indigo-500/20 flex items-start space-x-2.5">
            <ShieldAlert className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
            <p className="text-[11px] text-indigo-200/80 leading-relaxed">
              <strong className="text-indigo-200">Zero Biometric Storage:</strong> Raw embeddings and user photos are processed in temporary memory and are never uploaded to the public blockchain ledger.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
