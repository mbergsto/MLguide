import type { Option } from "../api/types";

type Props = {
  label: string;
  value: string;
  options: Option[];
  placeholder?: string;
  onChange: (iri: string) => void;
  disabled?: boolean;
};

export function Select({
  label,
  value,
  options,
  placeholder,
  onChange,
  disabled,
}: Props) {
  return (
    <label style={{ display: "grid", gap: 6 }}>
      <div style={{ fontSize: 14, fontWeight: 600 }}>{label}</div>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        style={{ padding: 10, borderRadius: 8, border: "1px solid #ccc" }}
      >
        <option value="">{placeholder ?? "Select..."}</option>
        {options.map((o) => (
          <option key={o.iri} value={o.iri}>
            {o.label}
          </option>
        ))}
      </select>
    </label>
  );
}
