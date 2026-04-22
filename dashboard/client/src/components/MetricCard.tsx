import { ReactNode } from "react";

interface MetricCardProps {
  icon: ReactNode;
  label: string;
  value: string | number;
  subtitle?: string;
  color?: "blue" | "purple" | "green" | "orange";
}

export default function MetricCard({
  icon,
  label,
  value,
  subtitle,
  color = "blue"
}: MetricCardProps) {
  const colorClasses = {
    blue: "bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200",
    purple: "bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200",
    green: "bg-gradient-to-br from-green-50 to-green-100 border-green-200",
    orange: "bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200"
  };

  const iconColors = {
    blue: "text-blue-600",
    purple: "text-purple-600",
    green: "text-green-600",
    orange: "text-orange-600"
  };

  return (
    <div className={`${colorClasses[color]} border rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 mb-1">{label}</p>
          <p className="text-3xl font-bold text-gray-900">{value}</p>
          {subtitle && <p className="text-xs text-gray-500 mt-2">{subtitle}</p>}
        </div>
        <div className={`${iconColors[color]} text-2xl`}>{icon}</div>
      </div>
    </div>
  );
}
