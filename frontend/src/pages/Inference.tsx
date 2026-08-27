import {
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  AlertCircle,
  CheckCircle2,
  Image as ImageIcon,
  Loader2,
  RefreshCw,
  Upload,
  X,
} from "lucide-react";

import {
  listManagedModels,
  type ModelManagementRecord,
} from "../api/model";

import {
  runInference,
  type InferencePrediction,
  type InferenceResponse,
} from "../api/inference";

const pageStyle: React.CSSProperties = {
  padding: 28,
  maxWidth: 1400,
  margin: "0 auto",
};

const cardStyle: React.CSSProperties = {
  background: "#fff",
  border: "1px solid #e4e7ec",
  borderRadius: 16,
  boxShadow: "0 1px 2px rgba(16,24,40,.04)",
};

function getApiErrorMessage(
  err: any,
  fallback: string
): string {
  const detail = err?.response?.data?.detail;

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === "string") {
          return item;
        }

        if (item?.msg) {
          const location = Array.isArray(item.loc)
            ? ` (${item.loc.join(" → ")})`
            : "";

          return `${item.msg}${location}`;
        }

        return JSON.stringify(item);
      })
      .join("; ");
  }

  if (detail && typeof detail === "object") {
    return JSON.stringify(detail);
  }

  return fallback;
}

function formatConfidence(value?: number) {
  if (value === undefined || value === null) return "—";
  return `${(value * 100).toFixed(1)}%`;
}

function normaliseBox(prediction: InferencePrediction) {
  const bbox = prediction.bbox;
  if (!bbox || bbox.length !== 4) return null;

  const [x, y, w, h] = bbox;
  if (![x, y, w, h].every(Number.isFinite)) return null;

  return { x, y, w, h };
}

export default function Inference() {
  const [models, setModels] = useState<ModelManagementRecord[]>([]);
  const [selectedModelId, setSelectedModelId] = useState("");
  const [confidence, setConfidence] = useState(0.25);

  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const [result, setResult] = useState<InferenceResponse | null>(null);
  const [loadingModels, setLoadingModels] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const completedModels = useMemo(
    () =>
      models.filter((model) =>
        ["ACTIVE", "REGISTERED"].includes(
          model.status.toUpperCase()
        )
      ),
    [models]
  );

  async function loadModels() {
    setLoadingModels(true);
    setError(null);

    try {
      const data = await listManagedModels();
      setModels(data);

      if (!selectedModelId && data.length > 0) {
        const preferred =
          data.find(
            (model) =>
              model.dataset_id === 2 &&
              ["ACTIVE", "REGISTERED"].includes(
                model.status.toUpperCase()
              )
          ) ?? data[0];

        setSelectedModelId(String(preferred.id));
      }
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ??
          "Could not load registered models."
      );
    } finally {
      setLoadingModels(false);
    }
  }

  useEffect(() => {
    loadModels();

    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleFile(fileValue: File | null) {
    if (!fileValue) return;

    if (!fileValue.type.startsWith("image/")) {
      setError("Please select an image file.");
      return;
    }

    setError(null);
    setFile(fileValue);
    setResult(null);

    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    setPreviewUrl(URL.createObjectURL(fileValue));
  }

  async function handleRunInference() {
    if (!file) {
      setError("Upload an image first.");
      return;
    }

    if (!selectedModelId) {
      setError("Select a registered model.");
      return;
    }

    setRunning(true);
    setError(null);
    setResult(null);

    try {
      const response = await runInference(
        Number(selectedModelId),
        file,
        confidence
      );

      setResult(response);
    } catch (err: any) {
      console.error("Inference error:", err);

      setError(
        getApiErrorMessage(
          err,
          "Inference failed. Check that the inference service is running."
        )
      );
    } finally {
      setRunning(false);
    }
  }

  const selectedModel = models.find(
    (model) => String(model.id) === selectedModelId
  );

  const detections = result?.predictions ?? [];

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
            MODEL INFERENCE
          </div>

          <h1
            style={{
              margin: 0,
              fontSize: 32,
              color: "#101828",
            }}
          >
            Inference
          </h1>

          <p
            style={{
              margin: "8px 0 0",
              color: "#667085",
            }}
          >
            Run registered vision models against an image and inspect
            their detections.
          </p>
        </div>

        <button
          onClick={loadModels}
          disabled={loadingModels}
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
          Refresh models
        </button>
      </div>

      {error && (
        <div
          style={{
            ...cardStyle,
            padding: 14,
            marginBottom: 18,
            display: "flex",
            alignItems: "center",
            gap: 10,
            color: "#b42318",
            background: "#fff5f4",
            borderColor: "#fecdca",
          }}
        >
          <AlertCircle size={18} />
          <span style={{ flex: 1 }}>{error}</span>
          <button
            onClick={() => setError(null)}
            style={{
              border: 0,
              background: "transparent",
              cursor: "pointer",
            }}
          >
            <X size={16} />
          </button>
        </div>
      )}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "360px minmax(0, 1fr)",
          gap: 20,
          alignItems: "start",
        }}
      >
        <section style={{ ...cardStyle, padding: 22 }}>
          <h2
            style={{
              margin: "0 0 18px",
              fontSize: 18,
              color: "#101828",
            }}
          >
            Inference configuration
          </h2>

          <label
            style={{
              display: "block",
              fontSize: 13,
              fontWeight: 700,
              color: "#344054",
              marginBottom: 8,
            }}
          >
            Registered model
          </label>

          <select
            value={selectedModelId}
            onChange={(event) =>
              setSelectedModelId(event.target.value)
            }
            disabled={loadingModels}
            style={{
              width: "100%",
              boxSizing: "border-box",
              padding: "11px 12px",
              border: "1px solid #d0d5dd",
              borderRadius: 10,
              background: "#fff",
              marginBottom: 18,
            }}
          >
            {completedModels.length === 0 && (
              <option value="">
                {loadingModels
                  ? "Loading models..."
                  : "No registered models"}
              </option>
            )}

            {completedModels.map((model) => (
              <option key={model.id} value={model.id}>
                {model.name} v{model.version} · Dataset #{model.dataset_id}
              </option>
            ))}
          </select>

          {selectedModel && (
            <div
              style={{
                padding: 13,
                borderRadius: 10,
                background: "#f8f9fc",
                border: "1px solid #eaecf0",
                marginBottom: 20,
                fontSize: 13,
                lineHeight: 1.7,
                color: "#475467",
              }}
            >
              <strong style={{ color: "#101828" }}>
                {selectedModel.name} v{selectedModel.version}
              </strong>
              <br />
              Dataset: #{selectedModel.dataset_id}
              <br />
              Framework: Ultralytics YOLO
            </div>
          )}

          <div style={{ marginBottom: 22 }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                marginBottom: 8,
              }}
            >
              <label
                style={{
                  fontSize: 13,
                  fontWeight: 700,
                  color: "#344054",
                }}
              >
                Confidence threshold
              </label>

              <strong style={{ fontSize: 13 }}>
                {confidence.toFixed(2)}
              </strong>
            </div>

            <input
              type="range"
              min="0.05"
              max="0.95"
              step="0.05"
              value={confidence}
              onChange={(event) =>
                setConfidence(Number(event.target.value))
              }
              style={{ width: "100%" }}
            />
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            hidden
            onChange={(event) =>
              handleFile(event.target.files?.[0] ?? null)
            }
          />

          <button
            onClick={() => fileInputRef.current?.click()}
            style={{
              width: "100%",
              border: "1px dashed #98a2b3",
              background: "#f9fafb",
              borderRadius: 12,
              padding: "18px 12px",
              cursor: "pointer",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              gap: 8,
              color: "#344054",
              marginBottom: 12,
            }}
          >
            <Upload size={17} />
            {file ? "Replace image" : "Upload image"}
          </button>

          {file && (
            <div
              style={{
                fontSize: 12,
                color: "#667085",
                marginBottom: 16,
                wordBreak: "break-word",
              }}
            >
              {file.name}
            </div>
          )}

          <button
            onClick={handleRunInference}
            disabled={running || !file || !selectedModelId}
            style={{
              width: "100%",
              border: 0,
              background:
                running || !file || !selectedModelId
                  ? "#98a2b3"
                  : "#2f63e8",
              color: "#fff",
              borderRadius: 10,
              padding: "12px 14px",
              fontWeight: 800,
              cursor:
                running || !file || !selectedModelId
                  ? "not-allowed"
                  : "pointer",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              gap: 8,
            }}
          >
            {running ? (
              <>
                <Loader2 size={17} className="spin" />
                Running inference…
              </>
            ) : (
              <>
                <ImageIcon size={17} />
                Run inference
              </>
            )}
          </button>
        </section>

        <section style={{ ...cardStyle, padding: 22, minHeight: 520 }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: 16,
            }}
          >
            <div>
              <h2
                style={{
                  margin: 0,
                  fontSize: 18,
                  color: "#101828",
                }}
              >
                Results
              </h2>

              <p
                style={{
                  margin: "5px 0 0",
                  color: "#667085",
                  fontSize: 13,
                }}
              >
                {result
                  ? `${detections.length} detection${
                      detections.length === 1 ? "" : "s"
                    }`
                  : "Upload an image and run inference."}
              </p>
            </div>

            {result && (
              <span
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 6,
                  color: "#087443",
                  background: "#ecfdf3",
                  padding: "6px 10px",
                  borderRadius: 999,
                  fontSize: 12,
                  fontWeight: 800,
                }}
              >
                <CheckCircle2 size={14} />
                Completed
              </span>
            )}
          </div>

          {!previewUrl ? (
            <div
              style={{
                height: 420,
                borderRadius: 14,
                border: "1px dashed #d0d5dd",
                background: "#f9fafb",
                display: "grid",
                placeItems: "center",
                color: "#98a2b3",
              }}
            >
              <div style={{ textAlign: "center" }}>
                <ImageIcon size={40} />
                <div style={{ marginTop: 10 }}>
                  No image selected
                </div>
              </div>
            </div>
          ) : (
            <div
              style={{
                display: "grid",
                gridTemplateColumns:
                  "minmax(0, 1fr) 280px",
                gap: 18,
              }}
            >
              <div
                style={{
                  borderRadius: 14,
                  background: "#101828",
                  minHeight: 420,
                  display: "grid",
                  placeItems: "center",
                  overflow: "hidden",
                }}
              >
                <img
                  src={previewUrl}
                  alt="Inference input"
                  style={{
                    maxWidth: "100%",
                    maxHeight: 620,
                    display: "block",
                  }}
                />
              </div>

              <div>
                <div
                  style={{
                    border: "1px solid #eaecf0",
                    borderRadius: 12,
                    padding: 14,
                    marginBottom: 12,
                  }}
                >
                  <div
                    style={{
                      fontSize: 12,
                      color: "#667085",
                      marginBottom: 4,
                    }}
                  >
                    Model
                  </div>
                  <strong style={{ color: "#101828" }}>
                    {result?.model_name ?? selectedModel?.name ?? "—"} v
                    {result?.model_version ??
                      selectedModel?.version ??
                      "—"}
                  </strong>
                </div>

                <div
                  style={{
                    border: "1px solid #eaecf0",
                    borderRadius: 12,
                    padding: 14,
                    marginBottom: 12,
                  }}
                >
                  <div
                    style={{
                      fontSize: 12,
                      color: "#667085",
                      marginBottom: 4,
                    }}
                  >
                    Inference ID
                  </div>
                  <strong>#{result?.inference_id ?? "—"}</strong>
                </div>

                <h3
                  style={{
                    margin: "18px 0 10px",
                    fontSize: 14,
                    color: "#101828",
                  }}
                >
                  Detections
                </h3>

                {detections.length === 0 ? (
                  <div
                    style={{
                      padding: 14,
                      background: "#f9fafb",
                      borderRadius: 10,
                      color: "#667085",
                      fontSize: 13,
                    }}
                  >
                    No detections above the selected confidence.
                  </div>
                ) : (
                  <div
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      gap: 8,
                      maxHeight: 330,
                      overflow: "auto",
                    }}
                  >
                    {detections.map((prediction, index) => (
                      <div
                        key={index}
                        style={{
                          border: "1px solid #eaecf0",
                          borderRadius: 10,
                          padding: "10px 12px",
                        }}
                      >
                        <div
                          style={{
                            display: "flex",
                            justifyContent: "space-between",
                            gap: 10,
                          }}
                        >
                          <strong style={{ color: "#101828" }}>
                            {prediction.label ??
                              `Detection ${index + 1}`}
                          </strong>
                          <span
                            style={{
                              color: "#2f63e8",
                              fontWeight: 800,
                            }}
                          >
                            {formatConfidence(
                              prediction.confidence
                            )}
                          </span>
                        </div>

                        {normaliseBox(prediction) && (
                          <div
                            style={{
                              marginTop: 4,
                              color: "#667085",
                              fontSize: 11,
                            }}
                          >
                            bbox:{" "}
                            {normaliseBox(prediction)!.x.toFixed(0)},{" "}
                            {normaliseBox(prediction)!.y.toFixed(0)},{" "}
                            {normaliseBox(prediction)!.w.toFixed(0)},{" "}
                            {normaliseBox(prediction)!.h.toFixed(0)}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
