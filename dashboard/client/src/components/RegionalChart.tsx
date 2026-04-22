import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from "recharts";

interface RegionalChartProps {
  data: Array<{ region: string; democratic: number; conservative: number }>;
  title: string;
}

export default function RegionalChart({ data, title }: RegionalChartProps) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={400}>
        <BarChart
          data={data}
          margin={{ top: 20, right: 30, left: 0, bottom: 80 }}
          layout="vertical"
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis type="number" stroke="#6b7280" />
          <YAxis
            dataKey="region"
            type="category"
            stroke="#6b7280"
            width={120}
            tick={{ fontSize: 12 }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#fff",
              border: "1px solid #e5e7eb",
              borderRadius: "0.5rem"
            }}
            formatter={(value) => {
              if (typeof value === "number") {
                return `${value.toFixed(1)}%`;
              }
              return value;
            }}
          />
          <Legend />
          <Bar dataKey="democratic" fill="#3b82f6" name="Democratic" />
          <Bar dataKey="conservative" fill="#f97316" name="Conservative" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
