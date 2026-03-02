import React from 'react';
import { LineChart, Line, YAxis, ResponsiveContainer } from 'recharts';

interface SparklineProps {
    data: number[];
    color?: string;
    width?: number | string;
    height?: number;
    min?: number;
    max?: number;
}

const Sparkline: React.FC<SparklineProps> = ({
    data,
    color = "var(--color-text-secondary)",
    width = 80,
    height = 24,
    min,
    max
}) => {
    // Convert flat array to Recharts format
    const chartData = data.map((val, i) => ({ value: val, index: i }));

    const dataMin = min !== undefined ? min : Math.min(...data);
    const dataMax = max !== undefined ? max : Math.max(...data);

    // Add padding to domain so lines don't clip at the very edge
    const padding = (dataMax - dataMin) * 0.1;

    return (
        <div style={{ width, height, display: 'inline-block', verticalAlign: 'middle' }}>
            <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                    <YAxis
                        domain={[dataMin - padding, dataMax + padding]}
                        hide
                    />
                    <Line
                        type="monotone"
                        dataKey="value"
                        stroke={color}
                        strokeWidth={1.5}
                        dot={false}
                        isAnimationActive={false} // Mechanical feel, no animation
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

export default Sparkline;
