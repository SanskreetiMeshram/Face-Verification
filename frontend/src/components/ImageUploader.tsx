import React, { useState, useRef } from 'react';
import { UploadCloud, Image as ImageIcon, Sparkles, AlertCircle, RefreshCw, Camera } from 'lucide-react';

interface ImageUploaderProps {
  onImageSelected: (file: File, previewUrl: string) => void;
  onRunPipeline: () => void;
  isLoading: boolean;
  selectedFile: File | null;
  previewUrl: string | null;
  onReset: () => void;
}

// Generate offline fallback canvas face image so sample images ALWAYS work even without internet
function generateSyntheticFaceDataUrl(variant: number): string {
  const canvas = document.createElement('canvas');
  canvas.width = 400;
  canvas.height = 400;
  const ctx = canvas.getContext('2d')!;

  // Background gradient
  const bgGrad = ctx.createLinearGradient(0, 0, 400, 400);
  if (variant === 1) {
    bgGrad.addColorStop(0, '#1E293B');
    bgGrad.addColorStop(1, '#0F172A');
  } else if (variant === 2) {
    bgGrad.addColorStop(0, '#1E1B4B');
    bgGrad.addColorStop(1, '#0F172A');
  } else if (variant === 3) {
    bgGrad.addColorStop(0, '#134E4A');
    bgGrad.addColorStop(1, '#0F172A');
  } else {
    // Landscape no face
    bgGrad.addColorStop(0, '#0284C7');
    bgGrad.addColorStop(1, '#059669');
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, 400, 400);
    // Mountains
    ctx.fillStyle = '#064E3B';
    ctx.beginPath();
    ctx.moveTo(0, 400);
    ctx.lineTo(150, 200);
    ctx.lineTo(300, 400);
    ctx.fill();
    return canvas.toDataURL('image/jpeg', 0.9);
  }

  ctx.fillStyle = bgGrad;
  ctx.fillRect(0, 0, 400, 400);

  // Face Oval
  ctx.fillStyle = variant === 1 ? '#FBCFE8' : variant === 2 ? '#FDE68A' : '#E2E8F0';
  ctx.beginPath();
  ctx.ellipse(200, 200, 90, 115, 0, 0, 2 * Math.PI);
  ctx.fill();

  // Eyes
  ctx.fillStyle = '#1E293B';
  ctx.beginPath();
  ctx.arc(165, 175, 12, 0, 2 * Math.PI);
  ctx.arc(235, 175, 12, 0, 2 * Math.PI);
  ctx.fill();

  // Eyeballs pupil highlight
  ctx.fillStyle = '#FFFFFF';
  ctx.beginPath();
  ctx.arc(168, 172, 4, 0, 2 * Math.PI);
  ctx.arc(238, 172, 4, 0, 2 * Math.PI);
  ctx.fill();

  // Nose
  ctx.strokeStyle = '#94A3B8';
  ctx.lineWidth = 4;
  ctx.beginPath();
  ctx.moveTo(200, 185);
  ctx.lineTo(195, 215);
  ctx.lineTo(205, 215);
  ctx.stroke();

  // Smile / Mouth
  ctx.strokeStyle = '#E11D48';
  ctx.lineWidth = 5;
  ctx.beginPath();
  ctx.arc(200, 240, 30, 0.2 * Math.PI, 0.8 * Math.PI);
  ctx.stroke();

  // Hair
  ctx.fillStyle = variant === 1 ? '#4C0519' : variant === 2 ? '#78350F' : '#0F172A';
  ctx.beginPath();
  ctx.arc(200, 130, 95, Math.PI, 2 * Math.PI);
  ctx.fill();

  return canvas.toDataURL('image/jpeg', 0.9);
}

const SAMPLE_IMAGES = [
  {
    name: "Portrait 1 (Female)",
    url: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=600&q=80",
    variant: 1,
    description: "High-contrast studio portrait"
  },
  {
    name: "Portrait 2 (Male)",
    url: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=600&q=80",
    variant: 2,
    description: "Natural lighting speaker photo"
  },
  {
    name: "Portrait 3 (Profile)",
    url: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=600&q=80",
    variant: 3,
    description: "Social media headshot"
  },
  {
    name: "Landscape (No Face)",
    url: "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=600&q=80",
    variant: 4,
    description: "Test edge-case: No face"
  }
];

export const ImageUploader: React.FC<ImageUploaderProps> = ({
  onImageSelected,
  onRunPipeline,
  isLoading,
  selectedFile,
  previewUrl,
  onReset,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [loadingSample, setLoadingSample] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleFile = (file: File) => {
    setErrorMessage(null);
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      setErrorMessage('Only JPG, PNG, or WebP images are supported.');
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setErrorMessage('Image size exceeds 10MB limit.');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const url = e.target?.result as string;
      onImageSelected(file, url);
    };
    reader.readAsDataURL(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const dataUrlToFile = async (dataUrl: string, filename: string): Promise<File> => {
    const res = await fetch(dataUrl);
    const blob = await res.blob();
    return new File([blob], filename, { type: 'image/jpeg' });
  };

  const loadSample = async (sample: typeof SAMPLE_IMAGES[0]) => {
    try {
      setLoadingSample(sample.name);
      setErrorMessage(null);
      
      // Try loading external high-res photo, or seamlessly fall back to embedded synthetic face
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 2500);
        const res = await fetch(sample.url, { signal: controller.signal });
        clearTimeout(timeoutId);
        if (res.ok) {
          const blob = await res.blob();
          const file = new File([blob], `${sample.name.toLowerCase().replace(/[^a-z0-9]/g, '_')}.jpg`, { type: 'image/jpeg' });
          const objectUrl = URL.createObjectURL(blob);
          onImageSelected(file, objectUrl);
          return;
        }
      } catch (networkErr) {
        // Fallback to local instant generator
      }

      // Generate local fallback
      const fallbackDataUrl = generateSyntheticFaceDataUrl(sample.variant);
      const file = await dataUrlToFile(fallbackDataUrl, `${sample.name.toLowerCase().replace(/[^a-z0-9]/g, '_')}.jpg`);
      onImageSelected(file, fallbackDataUrl);
    } catch (err) {
      setErrorMessage('Could not load sample image. Please upload a local file.');
    } finally {
      setLoadingSample(null);
    }
  };

  return (
    <div className="glass-panel p-5 sm:p-8 rounded-2xl relative overflow-hidden border border-slate-800/80 shadow-2xl">
      {/* Background glow decoration */}
      <div className="absolute top-0 right-0 w-80 h-80 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20"></div>

      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center space-x-2">
            <UploadCloud className="w-5 h-5 text-cyan-400" />
            <span>Upload Image for Verification</span>
          </h2>
          <p className="text-xs text-slate-400">
            JPG, PNG or WebP up to 10MB. Face will be detected and verified on-chain.
          </p>
        </div>

        {previewUrl && (
          <button
            onClick={onReset}
            disabled={isLoading}
            className="text-xs text-slate-400 hover:text-white flex items-center space-x-1.5 bg-slate-800/60 hover:bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-700 transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Reset</span>
          </button>
        )}
      </div>

      {errorMessage && (
        <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Drag & Drop Area */}
      {!previewUrl ? (
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-2xl p-6 sm:p-8 text-center cursor-pointer transition-all duration-300 ${
            isDragging
              ? 'border-cyan-400 bg-cyan-500/10 scale-[1.01]'
              : 'border-slate-700/80 hover:border-cyan-500/50 bg-slate-900/40 hover:bg-slate-900/70'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            className="hidden"
            onChange={(e) => {
              if (e.target.files && e.target.files.length > 0) {
                handleFile(e.target.files[0]);
              }
            }}
          />

          <div className="w-14 h-14 mx-auto rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 mb-3 group-hover:scale-110 transition">
            <UploadCloud className="w-7 h-7" />
          </div>

          <p className="text-sm font-semibold text-slate-200 mb-1">
            Drop your image here, or <span className="text-cyan-400 hover:underline">browse files</span>
          </p>
          <p className="text-xs text-slate-500 font-mono">
            Zero Biometric Exposure • Deterministic Hashing
          </p>
        </div>
      ) : (
        <div className="flex flex-col sm:flex-row items-center gap-6 p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <div className="w-32 h-32 shrink-0 rounded-xl overflow-hidden border border-slate-700 bg-black flex items-center justify-center">
            <img src={previewUrl} alt="Upload preview" className="w-full h-full object-cover" />
          </div>
          <div className="flex-1 w-full space-y-2 text-center sm:text-left">
            <div className="flex items-center justify-center sm:justify-start space-x-2">
              <span className="text-sm font-semibold text-white truncate max-w-[200px]">
                {selectedFile?.name || 'Selected Photograph'}
              </span>
              <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-slate-800 text-slate-300 border border-slate-700">
                {selectedFile ? `${(selectedFile.size / 1024).toFixed(1)} KB` : 'Image'}
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Ready to execute full detection, reverse search, and blockchain registration pipeline.
            </p>
            <div className="pt-2">
              <button
                onClick={onRunPipeline}
                disabled={isLoading}
                className="w-full sm:w-auto px-6 py-2.5 rounded-xl font-semibold text-sm text-black bg-gradient-to-r from-cyan-400 via-teal-300 to-cyan-400 hover:opacity-95 active:scale-95 transition shadow-lg shadow-cyan-500/20 flex items-center justify-center space-x-2 disabled:opacity-50 disabled:pointer-events-none"
              >
                {isLoading ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin text-black" />
                    <span>Running Verification Pipeline...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 text-black" />
                    <span>Run Verification</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Quick Sample Image Picker */}
      <div className="mt-6 pt-5 border-t border-slate-800/80">
        <p className="text-xs font-semibold text-slate-400 mb-3 flex items-center space-x-1.5">
          <ImageIcon className="w-3.5 h-3.5 text-indigo-400" />
          <span>Or test with instant benchmark sample images:</span>
        </p>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
          {SAMPLE_IMAGES.map((sample) => (
            <button
              key={sample.name}
              disabled={isLoading || loadingSample !== null}
              onClick={() => loadSample(sample)}
              className="p-2 rounded-xl bg-slate-900/50 hover:bg-slate-800/80 border border-slate-800 hover:border-slate-700 text-left transition flex items-center space-x-2.5 group disabled:opacity-50"
            >
              <img
                src={sample.url}
                alt={sample.name}
                onError={(e) => {
                  (e.target as HTMLElement).style.display = 'none';
                }}
                className="w-8 h-8 rounded-lg object-cover border border-slate-700 group-hover:border-cyan-400 transition"
              />
              <div className="min-w-0 flex-1">
                <p className="text-xs font-semibold text-slate-200 truncate group-hover:text-cyan-300">
                  {sample.name}
                </p>
                <p className="text-[10px] text-slate-500 truncate">
                  {sample.description}
                </p>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
