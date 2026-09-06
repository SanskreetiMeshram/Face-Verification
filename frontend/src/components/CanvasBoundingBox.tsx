import React, { useEffect, useRef } from 'react';
import { FaceDetail } from '../types';

interface CanvasBoundingBoxProps {
  imageSrc: string;
  faces: FaceDetail[];
  className?: string;
}

export const CanvasBoundingBox: React.FC<CanvasBoundingBoxProps> = ({
  imageSrc,
  faces,
  className = '',
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !imageSrc) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const img = new Image();
    if (imageSrc.startsWith('http://') || imageSrc.startsWith('https://')) {
      img.crossOrigin = 'anonymous';
    }
    img.src = imageSrc;

    img.onload = () => {
      // Set canvas display size
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;

      // Draw base image
      ctx.drawImage(img, 0, 0);

      // If no faces detected, return base image
      if (!faces || faces.length === 0) return;

      faces.forEach((face, i) => {
        const { x, y, width: w, height: h } = face.bounding_box;

        // Bounding Box Glow & Style
        ctx.save();
        ctx.strokeStyle = '#06B6D4'; // Cyan
        ctx.lineWidth = Math.max(2, Math.floor(canvas.width / 300));
        ctx.shadowColor = 'rgba(6, 182, 212, 0.8)';
        ctx.shadowBlur = 10;
        ctx.strokeRect(x, y, w, h);
        ctx.restore();

        // Corner Brackets (Violet Accent)
        const cornerLen = Math.max(10, Math.floor(Math.min(w, h) / 6));
        ctx.save();
        ctx.strokeStyle = '#A855F7'; // Purple/Violet
        ctx.lineWidth = Math.max(3, Math.floor(canvas.width / 200));
        ctx.shadowColor = 'rgba(168, 85, 247, 0.9)';
        ctx.shadowBlur = 12;

        // Top-Left
        ctx.beginPath();
        ctx.moveTo(x, y + cornerLen);
        ctx.lineTo(x, y);
        ctx.lineTo(x + cornerLen, y);
        ctx.stroke();

        // Top-Right
        ctx.beginPath();
        ctx.moveTo(x + w - cornerLen, y);
        ctx.lineTo(x + w, y);
        ctx.lineTo(x + w, y + cornerLen);
        ctx.stroke();

        // Bottom-Left
        ctx.beginPath();
        ctx.moveTo(x, y + h - cornerLen);
        ctx.lineTo(x, y + h);
        ctx.lineTo(x + cornerLen, y + h);
        ctx.stroke();

        // Bottom-Right
        ctx.beginPath();
        ctx.moveTo(x + w - cornerLen, y + h);
        ctx.lineTo(x + w, y + h);
        ctx.lineTo(x + w, y + h - cornerLen);
        ctx.stroke();
        ctx.restore();

        // Draw Landmarks if present
        if (face.landmarks) {
          ctx.save();
          ctx.fillStyle = '#10B981';
          ctx.shadowColor = '#10B981';
          ctx.shadowBlur = 8;
          Object.values(face.landmarks).forEach(([lx, ly]) => {
            ctx.beginPath();
            ctx.arc(lx, ly, Math.max(3, Math.floor(canvas.width / 250)), 0, 2 * Math.PI);
            ctx.fill();
          });
          ctx.restore();
        }

        // Tag label
        const labelText = `FACE #${face.index} • ${(face.confidence * 100).toFixed(0)}%`;
        const fontSize = Math.max(12, Math.floor(canvas.width / 40));
        ctx.font = `600 ${fontSize}px 'JetBrains Mono', monospace`;
        const textWidth = ctx.measureText(labelText).width;
        const tagHeight = fontSize + 8;
        const tagY = Math.max(tagHeight, y - 6);

        // Tag background
        ctx.fillStyle = 'rgba(11, 17, 32, 0.9)';
        ctx.fillRect(x, tagY - tagHeight, textWidth + 12, tagHeight);
        ctx.strokeStyle = '#06B6D4';
        ctx.lineWidth = 1;
        ctx.strokeRect(x, tagY - tagHeight, textWidth + 12, tagHeight);

        // Tag text
        ctx.fillStyle = '#06B6D4';
        ctx.fillText(labelText, x + 6, tagY - 6);
      });
    };
  }, [imageSrc, faces]);

  return (
    <div className={`relative overflow-hidden rounded-xl border border-slate-800 bg-slate-950 flex items-center justify-center ${className}`}>
      <canvas ref={canvasRef} className="max-h-[380px] w-auto max-w-full object-contain rounded-lg" />
    </div>
  );
};
