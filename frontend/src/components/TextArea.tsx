type Props = {
  label: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
};

export function TextArea({ label, value, onChange, placeholder }: Props) {
  return (
    <label style={{ display: "grid", gap: 6 }}>
      <div style={{ fontSize: 14, fontWeight: 600 }}>{label}</div>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        rows={4}
        style={{
          padding: 10,
          borderRadius: 8,
          border: "1px solid #ccc",
          resize: "vertical",
        }}
      />
    </label>
  );
}
