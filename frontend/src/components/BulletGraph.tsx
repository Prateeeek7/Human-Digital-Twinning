import React from 'react';

interface BulletGraphProps {
    value: number;
    min: number;
    max: number;
    normalLow: number;
    normalHigh: number;
    unit?: string;
    width?: string | number;
}

const BulletGraph: React.FC<BulletGraphProps> = ({
    value,
    min,
    max,
    normalLow,
    normalHigh,
    width = 120
}) => {
    const range = max - min;

    // Calculate percentages for positioning
    const normalStartPct = Math.max(0, ((normalLow - min) / range) * 100);
    const normalWidthPct = Math.min(100, ((normalHigh - normalLow) / range) * 100);

    // Clamp value marker between 0 and 100%
    const valuePct = Math.min(100, Math.max(0, ((value - min) / range) * 100));

    const isAbnormal = value < normalLow || value > normalHigh;
    const markerColor = isAbnormal ? 'var(--color-accent-red)' : 'var(--color-text-primary)';

    return (
        <div style={{
            width,
            height: '12px',
            position: 'relative',
            display: 'inline-block',
            verticalAlign: 'middle',
            backgroundColor: 'var(--color-bg-hover)',
            border: '1px solid var(--color-border-subtle)'
        }}>
            {/* Normal Range Band */}
            <div style={{
                position: 'absolute',
                left: `${normalStartPct}%`,
                width: `${normalWidthPct}%`,
                height: '100%',
                backgroundColor: 'rgba(13, 148, 136, 0.15)', /* Faint teal for safe zone */
                borderLeft: '1px solid rgba(13, 148, 136, 0.3)',
                borderRight: '1px solid rgba(13, 148, 136, 0.3)'
            }} />

            {/* Actual Value Marker */}
            <div style={{
                position: 'absolute',
                left: `${valuePct}%`,
                top: 0,
                bottom: 0,
                width: '3px',
                backgroundColor: markerColor,
                transform: 'translateX(-50%)',
                zIndex: 2
            }} />
        </div>
    );
};

export default BulletGraph;
