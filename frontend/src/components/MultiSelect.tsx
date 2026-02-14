import type { Option } from "../api/types";

type Props = {
  label: string;
  values: string[];
  options: Option[];
  onChange: (values: string[]) => void;
  disabled?: boolean;
};

export function MultiSelect({
  label,
  values,
  options,
  onChange,
  disabled,
}: Props) {
  function toggle(iri: string) {
    if (values.includes(iri)) onChange(values.filter((v) => v !== iri));
    else onChange([...values, iri]);
  }

  return (
    <div style={{ display: "grid", gap: 6 }}>
      <div style={{ fontSize: 14, fontWeight: 600 }}>{label}</div>
      <div
        style={{
          border: "1px solid #ccc",
          borderRadius: 8,
          padding: 10,
          maxHeight: 180,
          overflow: "auto",
          opacity: disabled ? 0.6 : 1,
          pointerEvents: disabled ? "none" : "auto",
        }}
      >
        {options.length === 0 ? (
          <div style={{ fontSize: 13, color: "#666" }}>No options</div>
        ) : (
          options.map((o) => (
            <label
              key={o.iri}
              style={{
                display: "flex",
                gap: 8,
                alignItems: "center",
                padding: "4px 0",
              }}
            >
              <input
                type="checkbox"
                checked={values.includes(o.iri)}
                onChange={() => toggle(o.iri)}
              />
              <span style={{ fontSize: 13 }}>{o.label}</span>
            </label>
          ))
        )}
      </div>
    </div>
  );
}
