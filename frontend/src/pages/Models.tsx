import {
  useEffect,
  useMemo,
  useState,
  type CSSProperties,
  type ReactNode,
} from "react";

import {
  CheckCircle2,
  Clock3,
  Database,
  ExternalLink,
  Loader2,
  RefreshCw,
  Rocket,
  Search,
  ShieldCheck,
  X,
  XCircle,
} from "lucide-react";

import {
  listManagedModels,
  type ModelManagementRecord,
} from "../api/model";

import {
  deployModel,
} from "../api/deployments";


function formatMetric(value?: number | null) {
  if (value === null || value === undefined) {
    return "—";
  }

  return `${(value * 100).toFixed(1)}%`;
}


function formatDuration(seconds?: number | null) {
  if (seconds === null || seconds === undefined) {
    return "—";
  }

  if (seconds < 60) {
    return `${Math.round(seconds)}s`;
  }

  const minutes = Math.floor(seconds / 60);
  const remaining = Math.floor(seconds % 60);

  if (minutes < 60) {
    return `${minutes}m ${remaining}s`;
  }

  const hours = Math.floor(minutes / 60);

  return `${hours}h ${minutes % 60}m`;
}


function formatDate(value?: string | null) {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "—";
  }

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

  const isActive =
    normalized === "ACTIVE" ||
    normalized === "REGISTERED";

  const isFailed =
    normalized === "FAILED" ||
    normalized === "ERROR";

  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 6,
        padding: "5px 10px",
        borderRadius: 999,
        fontSize: 12,
        fontWeight: 700,
        background: isActive
          ? "#e9f9f0"
          : isFailed
            ? "#fff0f0"
            : "#f2f4f7",
        color: isActive
          ? "#087443"
          : isFailed
            ? "#b42318"
            : "#475467",
      }}
    >
      {isActive ? (
        <CheckCircle2 size={13} />
      ) : isFailed ? (
        <XCircle size={13} />
      ) : null}
      {normalized}
    </span>
  );
}


function MetricCard({
  label,
  value,
  icon,
}: {
  label: string;
  value: string;
  icon: ReactNode;
}) {
  return (
    <div
      style={{
        flex: "1 1 210px",
        minWidth: 190,
        padding: 20,
        border: "1px solid #e4e7ec",
        borderRadius: 14,
        background: "#fff",
        display: "flex",
        alignItems: "center",
        gap: 14,
      }}
    >
      <div
        style={{
          width: 38,
          height: 38,
          borderRadius: 10,
          background: "#eef4ff",
          color: "#2f63e8",
          display: "grid",
          placeItems: "center",
        }}
      >
        {icon}
      </div>

      <div>
        <div
          style={{
            color: "#667085",
            fontSize: 13,
            marginBottom: 3,
          }}
        >
          {label}
        </div>

        <strong
          style={{
            color: "#101828",
            fontSize: 24,
          }}
        >
          {value}
        </strong>
      </div>
    </div>
  );
}


export default function Models() {
  const [models, setModels] = useState<ModelManagementRecord[]>(
    []
  );

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");

  const [selectedModel, setSelectedModel] =
    useState<ModelManagementRecord | null>(null);

  const [deployingModelId, setDeployingModelId] =
    useState<number | null>(null);


  async function loadModels(showSpinner = true) {
    if (showSpinner) {
      setLoading(true);
    }

    setError(null);

    try {
      const result = await listManagedModels();
      setModels(result);
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ??
          "Could not load registered models."
      );
    } finally {
      if (showSpinner) {
        setLoading(false);
      }
    }
  }


  useEffect(() => {
    loadModels();
  }, []);


  async function refresh() {
    setRefreshing(true);

    try {
      await loadModels(false);
    } finally {
      setRefreshing(false);
    }
  }


  const filteredModels = useMemo(() => {
    const query = search.trim().toLowerCase();

    return models.filter((model) => {
      const status = model.status.toUpperCase();

      if (
        statusFilter !== "ALL" &&
        status !== statusFilter
      ) {
        return false;
      }

      if (!query) {
        return true;
      }

      return (
        model.name.toLowerCase().includes(query) ||
        model.version.toLowerCase().includes(query) ||
        model.dataset_name
          .toLowerCase()
          .includes(query) ||
        (model.training_run_id ?? "")
          .toLowerCase()
          .includes(query) ||
        model.azure_model_reference
          .toLowerCase()
          .includes(query)
      );
    });
  }, [models, search, statusFilter]);


  const activeModels = models.filter(
    (model) =>
      model.status.toUpperCase() === "ACTIVE"
  ).length;

  async function handleDeploy(
    model: ModelManagementRecord
  ) {
    const confirmed =
      window.confirm(
        `Deploy ${model.name} v${model.version} to an Azure ML Managed Online Endpoint?`
      );

    if (!confirmed) {
      return;
    }

    setDeployingModelId(model.id);
    setError(null);

    try {
      const deployment =
        await deployModel(model.id);

      setSelectedModel(null);

      window.location.assign(
        `/deployments?endpoint=${encodeURIComponent(
          deployment.endpoint_name
        )}`
      );
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ??
          "Could not deploy model."
      );
    } finally {
      setDeployingModelId(null);
    }
  }


  const averageMap50 =
    models.filter(
      (model) => model.map50 !== null
    ).length > 0
      ? models
          .filter(
            (model) => model.map50 !== null
          )
          .reduce(
            (sum, model) =>
              sum + (model.map50 ?? 0),
            0
          ) /
        models.filter(
          (model) => model.map50 !== null
        ).length
      : null;


  return (
    <div
      style={{
        minHeight: "100%",
        padding: "28px 34px 40px",
        background: "#f8fafc",
      }}
    >
      {/* Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          gap: 20,
          marginBottom: 28,
        }}
      >
        <div>
          <div
            style={{
              color: "#667085",
              fontSize: 12,
              fontWeight: 800,
              letterSpacing: "0.08em",
              marginBottom: 6,
            }}
          >
            MODEL LIFECYCLE
          </div>

          <h1
            style={{
              margin: 0,
              color: "#101828",
              fontSize: 30,
              lineHeight: 1.2,
            }}
          >
            Models
          </h1>

          <p
            style={{
              margin: "8px 0 0",
              color: "#667085",
              fontSize: 14,
            }}
          >
            Automatically registered models and evaluation
            metrics from completed Azure ML training runs.
          </p>
        </div>

        <button
          onClick={refresh}
          disabled={refreshing || loading}
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
            padding: "10px 15px",
            borderRadius: 9,
            border: "1px solid #d0d5dd",
            background: "#fff",
            color: "#344054",
            fontWeight: 700,
            cursor:
              refreshing || loading
                ? "default"
                : "pointer",
          }}
        >
          {refreshing ? (
            <Loader2 size={16} />
          ) : (
            <RefreshCw size={16} />
          )}
          Refresh
        </button>
      </div>


      {error && (
        <div
          style={{
            marginBottom: 20,
            padding: "12px 14px",
            borderRadius: 10,
            border: "1px solid #fecdca",
            background: "#fff4f2",
            color: "#b42318",
            display: "flex",
            alignItems: "center",
            gap: 9,
          }}
        >
          <XCircle size={17} />
          <span style={{ flex: 1 }}>{error}</span>
          <button
            onClick={() => setError(null)}
            style={{
              border: 0,
              background: "transparent",
              cursor: "pointer",
            }}
          >
            <X size={15} />
          </button>
        </div>
      )}


      {/* KPIs */}
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: 16,
          marginBottom: 24,
        }}
      >
        <MetricCard
          label="Registered Models"
          value={String(models.length)}
          icon={<ShieldCheck size={18} />}
        />

        <MetricCard
          label="Active"
          value={String(activeModels)}
          icon={<CheckCircle2 size={18} />}
        />

        <MetricCard
          label="Datasets Represented"
          value={String(
            new Set(
              models.map(
                (model) => model.dataset_id
              )
            ).size
          )}
          icon={<Database size={18} />}
        />

        <MetricCard
          label="Average mAP@50"
          value={
            averageMap50 === null
              ? "—"
              : `${(
                  averageMap50 * 100
                ).toFixed(1)}%`
          }
          icon={<ShieldCheck size={18} />}
        />
      </div>


      {/* Registry table */}
      <section
        style={{
          background: "#fff",
          border: "1px solid #e4e7ec",
          borderRadius: 14,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            padding: "20px 22px 16px",
            borderBottom: "1px solid #eaecf0",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-end",
            gap: 16,
          }}
        >
          <div>
            <div
              style={{
                color: "#667085",
                fontSize: 11,
                fontWeight: 800,
                letterSpacing: "0.08em",
              }}
            >
              MODEL REGISTRY
            </div>

            <h2
              style={{
                margin: "5px 0 3px",
                fontSize: 20,
                color: "#101828",
              }}
            >
              Registered Models
            </h2>

            <p
              style={{
                margin: 0,
                color: "#667085",
                fontSize: 13,
              }}
            >
              Metrics are sourced automatically from training
              runs. Nothing is entered manually.
            </p>
          </div>

          <div
            style={{
              padding: "7px 11px",
              borderRadius: 999,
              background: "#f2f4f7",
              color: "#475467",
              fontSize: 12,
              fontWeight: 700,
            }}
          >
            {filteredModels.length} models
          </div>
        </div>


        {/* Filters */}
        <div
          style={{
            padding: "14px 22px",
            display: "flex",
            gap: 10,
            borderBottom: "1px solid #eaecf0",
          }}
        >
          <div
            style={{
              flex: 1,
              maxWidth: 520,
              display: "flex",
              alignItems: "center",
              gap: 8,
              border: "1px solid #d0d5dd",
              borderRadius: 9,
              padding: "0 11px",
              background: "#fff",
            }}
          >
            <Search
              size={15}
              color="#98a2b3"
            />

            <input
              value={search}
              onChange={(event) =>
                setSearch(event.target.value)
              }
              placeholder="Search models, datasets or training runs"
              style={{
                width: "100%",
                height: 38,
                border: 0,
                outline: 0,
                fontSize: 13,
              }}
            />
          </div>

          <select
            value={statusFilter}
            onChange={(event) =>
              setStatusFilter(event.target.value)
            }
            style={{
              minWidth: 140,
              border: "1px solid #d0d5dd",
              borderRadius: 9,
              padding: "0 10px",
              background: "#fff",
              color: "#344054",
            }}
          >
            <option value="ALL">
              All statuses
            </option>
            <option value="ACTIVE">
              Active
            </option>
          </select>
        </div>


        {loading ? (
          <div
            style={{
              minHeight: 280,
              display: "grid",
              placeItems: "center",
              color: "#667085",
              gap: 10,
            }}
          >
            <Loader2 size={24} />
            <span>
              Loading registered models…
            </span>
          </div>
        ) : filteredModels.length === 0 ? (
          <div
            style={{
              minHeight: 280,
              display: "grid",
              placeItems: "center",
              color: "#667085",
              padding: 30,
              textAlign: "center",
            }}
          >
            <div>
              <Database
                size={30}
                style={{ marginBottom: 10 }}
              />

              <h3
                style={{
                  margin: 0,
                  color: "#344054",
                }}
              >
                No registered models found
              </h3>

              <p style={{ margin: "7px 0 0" }}>
                Complete an Azure ML training run and
                register the resulting model to populate
                this registry.
              </p>
            </div>
          </div>
        ) : (
          <div
            style={{
              overflowX: "auto",
            }}
          >
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                minWidth: 1250,
              }}
            >
              <thead>
                <tr>
                  {[
                    "MODEL",
                    "VERSION",
                    "DATASET",
                    "TRAINING RUN",
                    "PRECISION",
                    "RECALL",
                    "MAP@50",
                    "MAP@50:95",
                    "TRAINING TIME",
                    "AZURE ML REFERENCE",
                    "STATUS",
                    "CREATED",
                    "ACTIONS",
                  ].map((heading) => (
                    <th
                      key={heading}
                      style={{
                        textAlign: "left",
                        padding: "12px 14px",
                        background: "#f9fafb",
                        color: "#667085",
                        fontSize: 10,
                        fontWeight: 800,
                        letterSpacing: "0.04em",
                        borderBottom:
                          "1px solid #eaecf0",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {heading}
                    </th>
                  ))}
                </tr>
              </thead>

              <tbody>
                {filteredModels.map((model) => (
                  <tr
                    key={model.id}
                    onClick={() =>
                      setSelectedModel(model)
                    }
                    style={{
                      cursor: "pointer",
                      borderBottom:
                        "1px solid #f0f2f5",
                    }}
                  >
                    <td style={cellStyle}>
                      <strong
                        style={{
                          color: "#101828",
                        }}
                      >
                        {model.name}
                      </strong>
                    </td>

                    <td style={cellStyle}>
                      <span
                        style={{
                          padding: "4px 8px",
                          borderRadius: 7,
                          background: "#f2f4f7",
                          fontWeight: 700,
                        }}
                      >
                        v{model.version}
                      </span>
                    </td>

                    <td style={cellStyle}>
                      {model.dataset_name}
                    </td>

                    <td style={cellStyle}>
                      <code
                        style={{
                          fontSize: 11,
                          color: "#475467",
                        }}
                      >
                        {model.training_run_id ?? "—"}
                      </code>
                    </td>

                    <td style={cellStyle}>
                      {formatMetric(
                        model.precision
                      )}
                    </td>

                    <td style={cellStyle}>
                      {formatMetric(
                        model.recall
                      )}
                    </td>

                    <td style={cellStyle}>
                      {formatMetric(model.map50)}
                    </td>

                    <td style={cellStyle}>
                      {formatMetric(
                        model.map50_95
                      )}
                    </td>

                    <td style={cellStyle}>
                      <span
                        style={{
                          display: "inline-flex",
                          alignItems: "center",
                          gap: 5,
                        }}
                      >
                        <Clock3 size={13} />
                        {formatDuration(
                          model.training_time
                        )}
                      </span>
                    </td>

                    <td style={cellStyle}>
                      <code
                        style={{
                          fontSize: 11,
                          color: "#475467",
                        }}
                      >
                        {model.azure_model_reference}
                      </code>
                    </td>

                    <td style={cellStyle}>
                      <StatusBadge
                        status={model.status}
                      />
                    </td>

                    <td
                      style={{
                        ...cellStyle,
                        whiteSpace: "nowrap",
                      }}
                    >
                      {formatDate(model.created_at)}
                    </td>

                    <td
                      style={cellStyle}
                      onClick={(event) =>
                        event.stopPropagation()
                      }
                    >
                      <button
                        onClick={() =>
                          handleDeploy(model)
                        }
                        disabled={
                          deployingModelId ===
                          model.id
                        }
                        style={{
                          display:
                            "inline-flex",
                          alignItems:
                            "center",
                          gap: 6,
                          padding:
                            "7px 10px",
                          borderRadius: 8,
                          border:
                            "1px solid #b8cdfb",
                          background:
                            "#eef4ff",
                          color:
                            "#2456c5",
                          fontWeight: 700,
                          cursor:
                            deployingModelId ===
                            model.id
                              ? "default"
                              : "pointer",
                          opacity:
                            deployingModelId ===
                            model.id
                              ? 0.65
                              : 1,
                        }}
                      >
                        {deployingModelId ===
                        model.id ? (
                          <Loader2
                            size={14}
                          />
                        ) : (
                          <Rocket
                            size={14}
                          />
                        )}
                        Deploy
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>


      {/* Details drawer */}
      {selectedModel && (
        <div
          onMouseDown={() =>
            setSelectedModel(null)
          }
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(16, 24, 40, 0.35)",
            zIndex: 50,
          }}
        >
          <aside
            onMouseDown={(event) =>
              event.stopPropagation()
            }
            style={{
              position: "absolute",
              right: 0,
              top: 0,
              bottom: 0,
              width: "min(520px, 92vw)",
              background: "#fff",
              padding: 28,
              overflowY: "auto",
              boxShadow:
                "-12px 0 40px rgba(16,24,40,.14)",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "flex-start",
                marginBottom: 24,
              }}
            >
              <div>
                <div
                  style={{
                    color: "#667085",
                    fontSize: 11,
                    fontWeight: 800,
                    letterSpacing: "0.08em",
                  }}
                >
                  REGISTERED MODEL
                </div>

                <h2
                  style={{
                    margin: "5px 0",
                    color: "#101828",
                  }}
                >
                  {selectedModel.name}
                </h2>

                <span
                  style={{
                    color: "#667085",
                    fontSize: 13,
                  }}
                >
                  Version {selectedModel.version}
                </span>
              </div>

              <button
                onClick={() =>
                  setSelectedModel(null)
                }
                style={{
                  border: 0,
                  background: "#f2f4f7",
                  borderRadius: 8,
                  width: 34,
                  height: 34,
                  display: "grid",
                  placeItems: "center",
                  cursor: "pointer",
                }}
              >
                <X size={17} />
              </button>
            </div>


            <section style={sectionStyle}>
              <h3 style={sectionTitleStyle}>
                Provenance
              </h3>

              <DetailRow
                label="Dataset"
                value={selectedModel.dataset_name}
              />

              <DetailRow
                label="Training run"
                value={
                  selectedModel.training_run_id ??
                  "—"
                }
                mono
              />

              <DetailRow
                label="Azure ML model"
                value={
                  selectedModel.azure_model_reference
                }
                mono
              />

              <DetailRow
                label="Created"
                value={formatDate(
                  selectedModel.created_at
                )}
              />

              <DetailRow
                label="Status"
                value={
                  <StatusBadge
                    status={selectedModel.status}
                  />
                }
              />
            </section>


            <section style={sectionStyle}>
              <h3 style={sectionTitleStyle}>
                Evaluation Metrics
              </h3>

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns:
                    "1fr 1fr",
                  gap: 10,
                }}
              >
                {[
                  [
                    "Precision",
                    formatMetric(
                      selectedModel.precision
                    ),
                  ],
                  [
                    "Recall",
                    formatMetric(
                      selectedModel.recall
                    ),
                  ],
                  [
                    "mAP@50",
                    formatMetric(
                      selectedModel.map50
                    ),
                  ],
                  [
                    "mAP@50:95",
                    formatMetric(
                      selectedModel.map50_95
                    ),
                  ],
                  [
                    "Training time",
                    formatDuration(
                      selectedModel.training_time
                    ),
                  ],
                ].map(([label, value]) => (
                  <div
                    key={label}
                    style={{
                      padding: 14,
                      borderRadius: 10,
                      background: "#f9fafb",
                    }}
                  >
                    <div
                      style={{
                        color: "#667085",
                        fontSize: 12,
                        marginBottom: 5,
                      }}
                    >
                      {label}
                    </div>

                    <strong
                      style={{
                        color: "#101828",
                        fontSize: 18,
                      }}
                    >
                      {value}
                    </strong>
                  </div>
                ))}
              </div>
            </section>


            {selectedModel.artifact_uri && (
              <section style={sectionStyle}>
                <h3 style={sectionTitleStyle}>
                  Artifact
                </h3>

                <div
                  style={{
                    padding: 14,
                    borderRadius: 10,
                    background: "#f9fafb",
                    wordBreak: "break-all",
                  }}
                >
                  <code
                    style={{
                      color: "#475467",
                      fontSize: 12,
                    }}
                  >
                    {selectedModel.artifact_uri}
                  </code>
                </div>
              </section>
            )}

            <button
              onClick={() =>
                handleDeploy(selectedModel)
              }
              disabled={
                deployingModelId ===
                selectedModel.id
              }
              style={{
                width: "100%",
                marginBottom: 12,
                display: "inline-flex",
                alignItems: "center",
                justifyContent: "center",
                gap: 8,
                padding: "12px 16px",
                border: 0,
                borderRadius: 9,
                background: "#2f63e8",
                color: "#fff",
                fontWeight: 700,
                cursor:
                  deployingModelId ===
                  selectedModel.id
                    ? "default"
                    : "pointer",
                opacity:
                  deployingModelId ===
                  selectedModel.id
                    ? 0.65
                    : 1,
              }}
            >
              {deployingModelId ===
              selectedModel.id ? (
                <Loader2 size={16} />
              ) : (
                <Rocket size={16} />
              )}
              {deployingModelId ===
              selectedModel.id
                ? "Deploying…"
                : "Deploy Model"}
            </button>

            <div
              style={{
                padding: 14,
                borderRadius: 10,
                background: "#ecfdf3",
                color: "#067647",
                display: "flex",
                gap: 9,
                alignItems: "flex-start",
                fontSize: 13,
              }}
            >
              <ShieldCheck
                size={17}
                style={{
                  flex: "0 0 auto",
                  marginTop: 1,
                }}
              />

              <span>
                Metrics and provenance are automatically
                sourced from the completed Azure ML
                training run. This page has no manual
                metric-entry workflow.
              </span>
            </div>
          </aside>
        </div>
      )}
    </div>
  );
}


const cellStyle: CSSProperties = {
  padding: "13px 14px",
  color: "#475467",
  fontSize: 12,
  whiteSpace: "nowrap",
};


const sectionStyle: CSSProperties = {
  padding: "18px 0",
  borderTop: "1px solid #eaecf0",
};


const sectionTitleStyle: CSSProperties = {
  margin: "0 0 14px",
  color: "#344054",
  fontSize: 13,
};


function DetailRow({
  label,
  value,
  mono = false,
}: {
  label: string;
  value: ReactNode;
  mono?: boolean;
}) {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "130px 1fr",
        gap: 12,
        padding: "9px 0",
        alignItems: "center",
      }}
    >
      <span
        style={{
          color: "#667085",
          fontSize: 12,
        }}
      >
        {label}
      </span>

      <span
        style={{
          color: "#101828",
          fontSize: 12,
          fontFamily: mono
            ? "ui-monospace, SFMono-Regular, Menlo, monospace"
            : "inherit",
          wordBreak: "break-word",
        }}
      >
        {value}
      </span>
    </div>
  );
}
