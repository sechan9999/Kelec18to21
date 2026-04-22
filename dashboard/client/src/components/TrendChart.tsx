import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from "recharts";

interface TrendChartProps {
  data: Array<{ election: string; [key: string]: string | number }>;
  title: string;
  lines: Array<{ key: string; name: string; color: string }>;
  yAxisLabel?: string;
}

export default function TrendChart({
  data,
  title,
  lines,
  yAxisLabel = "Percentage (%)"
}: TrendChartProps) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="election" stroke="#6b7280" />
          <YAxis stroke="#6b7280" label={{ value: yAxisLabel, angle: -90, position: "insideLeft" }} />
          <Tooltip
            contentStyle={{
              backgroundColor: "#fff",
              border: "1px solid #e5e7eb",
              borderRadius: "0.5rem"
            }}
            formatter={(value) => {
              if (typeof value === "number") {
                return value.toFixed(2);
              }
              return value;
            }}
          />
          <Legend />
          {lines.map((line) => (
            <Line
              key={line.key}
              type="monotone"
              dataKey={line.key}
              stroke={line.color}
              name={line.name}
              strokeWidth={2}
              dot={{ fill: line.color, r: 5 }}
              activeDot={{ r: 7 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
