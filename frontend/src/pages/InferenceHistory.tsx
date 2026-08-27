import {
  useEffect,
  useMemo,
  useState,
} from "react";
import {
  AlertCircle,
  CheckCircle2,
  Clock3,
  RefreshCw,
  Search,
  XCircle,
} from "lucide-react";

import {
  listInferenceRuns,
  type InferenceRun,
} from "../api/inference";

const pageStyle: React.CSSProperties = {
  padding: 28,
  maxWidth: 1400,
  margin: "0 auto",
};

function formatDate(value?: string | null) {
  if (!value) return "—";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";

  return date.toLocaleString(undefined, {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function StatusBadge({ status }: { status: string }) {
  const normalized = status.toUpperCase();

  const completed = normalized === "COMPLETED";
  const failed = normalized === "FAILED";

  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 6,
        borderRadius: 999,
        padding: "5px 9px",
        fontSize: 11,
        fontWeight: 800,
        background: completed
          ? "#ecfdf3"
          : failed
            ? "#fff1f0"
            : "#f2f4f7",
        color: completed
          ? "#087443"
          : failed
            ? "#b42318"
            : "#475467",
      }}
    >
      {completed ? (
        <CheckCircle2 size={13} />
      ) : failed ? (
        <XCircle size={13} />
      ) : (
        <Clock3 size={13} />
      )}
      {normalized}
    </span>
  );
}

export default function InferenceHistory() {
  const [runs, setRuns] = useState<InferenceRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [selectedRun, setSelectedRun] =
    useState<InferenceRun | null>(null);

  async function loadRuns(showSpinner = true) {
    if (showSpinner) setLoading(true);
    setError(null);

    try {
      const result = await listInferenceRuns();
      setRuns(result);
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ??
          "Could not load inference history."
      );
    } finally {
      if (showSpinner) setLoading(false);
    }
  }

  useEffect(() => {
    loadRuns();
  }, []);

  async function refresh() {
    setRefreshing(true);
    try {
      await loadRuns(false);
    } finally {
      setRefreshing(false);
    }
  }

  const filteredRuns = useMemo(() => {
    const query = search.trim().toLowerCase();

    return runs.filter((run) => {
      const status = run.status.toUpperCase();

      if (
        statusFilter !== "ALL" &&
        status !== statusFilter
      ) {
        return false;
      }

      if (!query) return true;

      return (
        String(run.id).includes(query) ||
        run.model_name.toLowerCase().includes(query) ||
        run.model_version.toLowerCase().includes(query) ||
        run.input_filename
          ?.toLowerCase()
          .includes(query)
      );
    });
  }, [runs, search, statusFilter]);

  const completed = runs.filter(
    (run) => run.status.toUpperCase() === "COMPLETED"
  ).length;

  const failed = runs.filter(
    (run) => run.status.toUpperCase() === "FAILED"
  ).length;

  const totalDetections = runs.reduce(
    (sum, run) => sum + (run.prediction_count ?? 0),
    0
  );

  return (
    <div style={pageStyle}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          gap: 20,
          marginBottom: 24,
        }}
      >
        <div>
          <div
            style={{
              fontSize: 12,
              fontWeight: 800,
              letterSpacing: ".08em",
              color: "#2f63e8",
              marginBottom: 8,
            }}
          >
            INFERENCE MONITORING
          </div>

          <h1
            style={{
              margin: 0,
              fontSize: 32,
              color: "#101828",
            }}
          >
            Inference History
          </h1>

          <p
            style={{
              margin: "8px 0 0",
              color: "#667085",
            }}
          >
            Review previous inference executions, models, detections,
            latency and failures.
          </p>
        </div>

        <button
          onClick={refresh}
          disabled={refreshing}
          style={{
            border: "1px solid #d0d5dd",
            background: "#fff",
            borderRadius: 10,
            padding: "10px 14px",
            display: "flex",
            alignItems: "center",
            gap: 8,
            cursor: "pointer",
          }}
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {error && (
        <div
          style={{
            padding: 14,
            marginBottom: 18,
            border: "1px solid #fecdca",
            borderRadius: 12,
            background: "#fff5f4",
            color: "#b42318",
            display: "flex",
            alignItems: "center",
            gap: 9,
          }}
        >
          <AlertCircle size={18} />
          {error}
        </div>
      )}

      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(3, minmax(0, 1fr))",
          gap: 14,
          marginBottom: 18,
        }}
      >
        {[
          ["Total runs", runs.length],
          ["Completed", completed],
          ["Detections", totalDetections],
        ].map(([label, value]) => (
          <div
            key={String(label)}
            style={{
              background: "#fff",
              border: "1px solid #e4e7ec",
              borderRadius: 14,
              padding: 18,
            }}
          >
            <div
              style={{
                color: "#667085",
                fontSize: 13,
                marginBottom: 5,
              }}
            >
              {label}
            </div>
            <strong
              style={{
                fontSize: 25,
                color: "#101828",
              }}
            >
              {value}
            </strong>
          </div>
        ))}
      </div>

      <div
        style={{
          background: "#fff",
          border: "1px solid #e4e7ec",
          borderRadius: 16,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            padding: 16,
            borderBottom: "1px solid #eaecf0",
            display: "flex",
            gap: 10,
            flexWrap: "wrap",
          }}
        >
          <div
            style={{
              flex: "1 1 280px",
              position: "relative",
            }}
          >
            <Search
              size={16}
              style={{
                position: "absolute",
                left: 11,
                top: 11,
                color: "#98a2b3",
              }}
            />

            <input
              value={search}
              onChange={(event) =>
                setSearch(event.target.value)
              }
              placeholder="Search inference ID, model or file..."
              style={{
                width: "100%",
                boxSizing: "border-box",
                padding: "10px 12px 10px 34px",
                border: "1px solid #d0d5dd",
                borderRadius: 9,
              }}
            />
          </div>

          <select
            value={statusFilter}
            onChange={(event) =>
              setStatusFilter(event.target.value)
            }
            style={{
              border: "1px solid #d0d5dd",
              borderRadius: 9,
              padding: "10px 12px",
              background: "#fff",
            }}
          >
            <option value="ALL">All statuses</option>
            <option value="COMPLETED">Completed</option>
            <option value="FAILED">Failed</option>
            <option value="RUNNING">Running</option>
          </select>
        </div>

        {loading ? (
          <div
            style={{
              padding: 50,
              textAlign: "center",
              color: "#667085",
            }}
          >
            Loading inference history…
          </div>
        ) : filteredRuns.length === 0 ? (
          <div
            style={{
              padding: 60,
              textAlign: "center",
              color: "#667085",
            }}
          >
            No inference runs found.
          </div>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                minWidth: 920,
              }}
            >
              <thead>
                <tr
                  style={{
                    background: "#f9fafb",
                    textAlign: "left",
                  }}
                >
                  {[
                    "Inference",
                    "Model",
                    "Status",
                    "Detections",
                    "Confidence",
                    "Latency",
                    "Created",
                  ].map((heading) => (
                    <th
                      key={heading}
                      style={{
                        padding: "12px 16px",
                        color: "#667085",
                        fontSize: 11,
                        textTransform: "uppercase",
                        letterSpacing: ".05em",
                      }}
                    >
                      {heading}
                    </th>
                  ))}
                </tr>
              </thead>

              <tbody>
                {filteredRuns.map((run) => (
                  <tr
                    key={run.id}
                    onClick={() => setSelectedRun(run)}
                    style={{
                      borderTop: "1px solid #eaecf0",
                      cursor: "pointer",
                    }}
                  >
                    <td
                      style={{
                        padding: "14px 16px",
                        fontWeight: 800,
                        color: "#101828",
                      }}
                    >
                      #{run.id}
                    </td>

                    <td style={{ padding: "14px 16px" }}>
                      <strong style={{ color: "#101828" }}>
                        {run.model_name}
                      </strong>
                      <div
                        style={{
                          color: "#667085",
                          fontSize: 12,
                          marginTop: 2,
                        }}
                      >
                        v{run.model_version}
                      </div>
                    </td>

                    <td style={{ padding: "14px 16px" }}>
                      <StatusBadge status={run.status} />
                    </td>

                    <td style={{ padding: "14px 16px" }}>
                      {run.prediction_count}
                    </td>

                    <td style={{ padding: "14px 16px" }}>
                      {(run.confidence_threshold * 100).toFixed(0)}%
                    </td>

                    <td style={{ padding: "14px 16px" }}>
                      {run.inference_latency_ms == null
                        ? "—"
                        : `${run.inference_latency_ms.toFixed(0)} ms`}
                    </td>

                    <td
                      style={{
                        padding: "14px 16px",
                        color: "#667085",
                        fontSize: 12,
                      }}
                    >
                      {formatDate(run.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {failed > 0 && (
        <div
          style={{
            marginTop: 12,
            color: "#b42318",
            fontSize: 12,
          }}
        >
          {failed} failed inference run{failed === 1 ? "" : "s"}.
        </div>
      )}

      {selectedRun && (
        <div
          onClick={() => setSelectedRun(null)}
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(16,24,40,.38)",
            display: "flex",
            justifyContent: "flex-end",
            zIndex: 1000,
          }}
        >
          <aside
            onClick={(event) => event.stopPropagation()}
            style={{
              width: "min(520px, 92vw)",
              height: "100%",
              background: "#fff",
              padding: 24,
              boxSizing: "border-box",
              overflow: "auto",
              boxShadow: "-10px 0 30px rgba(16,24,40,.12)",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: 22,
              }}
            >
              <div>
                <div
                  style={{
                    color: "#667085",
                    fontSize: 12,
                  }}
                >
                  INFERENCE RUN
                </div>
                <h2
                  style={{
                    margin: "4px 0 0",
                    color: "#101828",
                  }}
                >
                  #{selectedRun.id}
                </h2>
              </div>

              <button
                onClick={() => setSelectedRun(null)}
                style={{
                  border: 0,
                  background: "#f2f4f7",
                  borderRadius: 8,
                  padding: 8,
                  cursor: "pointer",
                }}
              >
                ×
              </button>
            </div>

            <StatusBadge status={selectedRun.status} />

            <div
              style={{
                marginTop: 20,
                display: "grid",
                gap: 10,
              }}
            >
              {[
                ["Model", `${selectedRun.model_name} v${selectedRun.model_version}`],
                ["Input", selectedRun.input_filename ?? "Uploaded image"],
                ["Confidence", `${(selectedRun.confidence_threshold * 100).toFixed(1)}%`],
                ["Detections", String(selectedRun.prediction_count)],
                ["Latency", selectedRun.inference_latency_ms == null ? "—" : `${selectedRun.inference_latency_ms.toFixed(2)} ms`],
                ["Created", formatDate(selectedRun.created_at)],
              ].map(([label, value]) => (
                <div
                  key={label}
                  style={{
                    padding: 13,
                    border: "1px solid #eaecf0",
                    borderRadius: 10,
                  }}
                >
                  <div
                    style={{
                      color: "#667085",
                      fontSize: 11,
                      marginBottom: 4,
                    }}
                  >
                    {label}
                  </div>
                  <strong style={{ color: "#101828" }}>
                    {value}
                  </strong>
                </div>
              ))}
            </div>

            {selectedRun.error_message && (
              <div
                style={{
                  marginTop: 16,
                  padding: 13,
                  borderRadius: 10,
                  background: "#fff5f4",
                  color: "#b42318",
                  border: "1px solid #fecdca",
                  fontSize: 13,
                }}
              >
                {selectedRun.error_message}
              </div>
            )}

            <h3
              style={{
                margin: "22px 0 10px",
                color: "#101828",
              }}
            >
              Predictions
            </h3>

            {selectedRun.predictions.length === 0 ? (
              <div
                style={{
                  color: "#667085",
                  fontSize: 13,
                }}
              >
                No predictions stored for this run.
              </div>
            ) : (
              <pre
                style={{
                  margin: 0,
                  padding: 14,
                  borderRadius: 10,
                  background: "#101828",
                  color: "#e4e7ec",
                  overflow: "auto",
                  fontSize: 12,
                  lineHeight: 1.5,
                }}
              >
                {JSON.stringify(
                  selectedRun.predictions,
                  null,
                  2
                )}
              </pre>
            )}
          </aside>
        </div>
      )}
    </div>
  );
}
