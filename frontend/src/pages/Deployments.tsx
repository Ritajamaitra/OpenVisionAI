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
  ExternalLink,
  Loader2,
  RefreshCw,
  Rocket,
  Search,
  Server,
  Square,
  X,
  XCircle,
} from "lucide-react";

import {
  deployModel,
  listDeployments,
  stopDeployment,
  type DeploymentRecord,
} from "../api/deployments";


function statusIsHealthy(
  deployment: DeploymentRecord
) {
  const value = (
    deployment.deployment_status ||
    deployment.endpoint_status ||
    ""
  ).toLowerCase();

  return (
    value.includes("succeed") ||
    value.includes("healthy") ||
    value.includes("ready")
  );
}


function StatusBadge({
  deployment,
}: {
  deployment: DeploymentRecord;
}) {
  const healthy = statusIsHealthy(deployment);

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
        background: healthy
          ? "#e9f9f0"
          : "#fff4e5",
        color: healthy
          ? "#087443"
          : "#b54708",
      }}
    >
      {healthy ? (
        <CheckCircle2 size={13} />
      ) : (
        <Clock3 size={13} />
      )}

      {healthy
        ? "HEALTHY"
        : (
            deployment.deployment_status ||
            deployment.endpoint_status ||
            "PROVISIONING"
          ).toUpperCase()}
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
        flex: "1 1 220px",
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


export default function Deployments() {
  const [deployments, setDeployments] =
    useState<DeploymentRecord[]>([]);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] =
    useState(false);

  const [actionId, setActionId] =
    useState<number | null>(null);

  const [error, setError] =
    useState<string | null>(null);

  const [search, setSearch] = useState("");

  const [selected, setSelected] =
    useState<DeploymentRecord | null>(null);


  async function loadDeployments(
    showSpinner = true
  ) {
    if (showSpinner) {
      setLoading(true);
    }

    setError(null);

    try {
      setDeployments(
        await listDeployments()
      );
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ??
          "Could not load deployments."
      );
    } finally {
      if (showSpinner) {
        setLoading(false);
      }
    }
  }


  useEffect(() => {
    loadDeployments();
  }, []);


  async function refresh() {
    setRefreshing(true);

    try {
      await loadDeployments(false);
    } finally {
      setRefreshing(false);
    }
  }


  async function stop(
    deployment: DeploymentRecord
  ) {
    const confirmed =
      window.confirm(
        `Stop endpoint "${deployment.endpoint_name}"?`
      );

    if (!confirmed) {
      return;
    }

    setActionId(deployment.model_id);
    setError(null);

    try {
      await stopDeployment(
        deployment.endpoint_name
      );

      setSelected(null);

      await loadDeployments(false);
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ??
          "Could not stop endpoint."
      );
    } finally {
      setActionId(null);
    }
  }


  const filtered = useMemo(() => {
    const query =
      search.trim().toLowerCase();

    if (!query) {
      return deployments;
    }

    return deployments.filter(
      (deployment) =>
        deployment.model_name
          .toLowerCase()
          .includes(query) ||
        deployment.endpoint_name
          .toLowerCase()
          .includes(query) ||
        deployment.deployment_name
          .toLowerCase()
          .includes(query) ||
        deployment.azure_model_reference
          .toLowerCase()
          .includes(query)
    );
  }, [deployments, search]);


  const healthyCount =
    deployments.filter(
      statusIsHealthy
    ).length;


  return (
    <div
      style={{
        minHeight: "100%",
        padding: "28px 34px 40px",
        background: "#f8fafc",
      }}
    >
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
            MODEL SERVING
          </div>

          <h1
            style={{
              margin: 0,
              color: "#101828",
              fontSize: 30,
            }}
          >
            Deployments
          </h1>

          <p
            style={{
              margin: "8px 0 0",
              color: "#667085",
              fontSize: 14,
            }}
          >
            Deploy registered models to Azure ML Managed
            Online Endpoints and monitor serving status.
          </p>
        </div>

        <button
          onClick={refresh}
          disabled={refreshing || loading}
          style={buttonStyle}
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
        <div style={errorStyle}>
          <XCircle size={17} />
          <span>{error}</span>
          <button
            onClick={() => setError(null)}
            style={{
              marginLeft: "auto",
              border: 0,
              background: "transparent",
              cursor: "pointer",
            }}
          >
            <X size={15} />
          </button>
        </div>
      )}


      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: 16,
          marginBottom: 24,
        }}
      >
        <MetricCard
          label="Active Endpoints"
          value={String(
            deployments.length
          )}
          icon={<Rocket size={18} />}
        />

        <MetricCard
          label="Healthy"
          value={String(
            healthyCount
          )}
          icon={<CheckCircle2 size={18} />}
        />

        <MetricCard
          label="Instances"
          value={String(
            deployments.reduce(
              (sum, item) =>
                sum +
                (item.instance_count ?? 0),
              0
            )
          )}
          icon={<Server size={18} />}
        />
      </div>


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
            borderBottom:
              "1px solid #eaecf0",
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
              ONLINE ENDPOINTS
            </div>

            <h2
              style={{
                margin: "5px 0 3px",
                fontSize: 20,
                color: "#101828",
              }}
            >
              Managed Deployments
            </h2>

            <p
              style={{
                margin: 0,
                color: "#667085",
                fontSize: 13,
              }}
            >
              Registered models running behind Azure ML
              managed online endpoints.
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
            {filtered.length} deployments
          </div>
        </div>


        <div
          style={{
            padding: "14px 22px",
            borderBottom:
              "1px solid #eaecf0",
          }}
        >
          <div
            style={{
              maxWidth: 560,
              display: "flex",
              alignItems: "center",
              gap: 8,
              border: "1px solid #d0d5dd",
              borderRadius: 9,
              padding: "0 11px",
            }}
          >
            <Search
              size={15}
              color="#98a2b3"
            />

            <input
              value={search}
              onChange={(event) =>
                setSearch(
                  event.target.value
                )
              }
              placeholder="Search models or endpoints"
              style={{
                width: "100%",
                height: 38,
                border: 0,
                outline: 0,
                fontSize: 13,
              }}
            />
          </div>
        </div>


        {loading ? (
          <div style={emptyStyle}>
            <Loader2 size={24} />
            Loading deployments…
          </div>
        ) : filtered.length === 0 ? (
          <div style={emptyStyle}>
            <Rocket size={30} />

            <strong>
              No deployed models yet
            </strong>

            <span>
              Deploy a registered model from the Models
              page to create your first Azure ML endpoint.
            </span>
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
                minWidth: 1180,
                borderCollapse: "collapse",
              }}
            >
              <thead>
                <tr>
                  {[
                    "MODEL",
                    "VERSION",
                    "ENDPOINT",
                    "STATUS",
                    "INSTANCE",
                    "AZURE ML REFERENCE",
                    "ENDPOINT URL",
                    "ACTIONS",
                  ].map((heading) => (
                    <th
                      key={heading}
                      style={thStyle}
                    >
                      {heading}
                    </th>
                  ))}
                </tr>
              </thead>

              <tbody>
                {filtered.map(
                  (deployment) => (
                    <tr
                      key={`${deployment.endpoint_name}:${deployment.deployment_name}`}
                      onClick={() =>
                        setSelected(
                          deployment
                        )
                      }
                      style={{
                        borderBottom:
                          "1px solid #f0f2f5",
                        cursor: "pointer",
                      }}
                    >
                      <td style={tdStyle}>
                        <strong>
                          {deployment.model_name}
                        </strong>
                      </td>

                      <td style={tdStyle}>
                        v
                        {
                          deployment.model_version
                        }
                      </td>

                      <td style={tdStyle}>
                        <code>
                          {
                            deployment.endpoint_name
                          }
                        </code>
                      </td>

                      <td style={tdStyle}>
                        <StatusBadge
                          deployment={
                            deployment
                          }
                        />
                      </td>

                      <td style={tdStyle}>
                        {deployment.instance_count ??
                          1}{" "}
                        ×{" "}
                        {deployment.instance_type ??
                          "—"}
                      </td>

                      <td style={tdStyle}>
                        <code>
                          {
                            deployment.azure_model_reference
                          }
                        </code>
                      </td>

                      <td style={tdStyle}>
                        {deployment.endpoint_url ? (
                          <a
                            href={
                              deployment.endpoint_url
                            }
                            target="_blank"
                            rel="noreferrer"
                            onClick={(event) =>
                              event.stopPropagation()
                            }
                            style={{
                              color:
                                "#2f63e8",
                              textDecoration:
                                "none",
                            }}
                          >
                            Endpoint
                            <ExternalLink
                              size={12}
                              style={{
                                marginLeft: 4,
                                verticalAlign:
                                  "middle",
                              }}
                            />
                          </a>
                        ) : (
                          "—"
                        )}
                      </td>

                      <td
                        style={tdStyle}
                        onClick={(event) =>
                          event.stopPropagation()
                        }
                      >
                        <button
                          onClick={() =>
                            stop(
                              deployment
                            )
                          }
                          disabled={
                            actionId ===
                            deployment.model_id
                          }
                          style={{
                            ...dangerButtonStyle,
                            opacity:
                              actionId ===
                              deployment.model_id
                                ? 0.6
                                : 1,
                          }}
                        >
                          {actionId ===
                          deployment.model_id ? (
                            <Loader2 size={14} />
                          ) : (
                            <Square
                              size={14}
                            />
                          )}
                          Stop
                        </button>
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>
        )}
      </section>


      {selected && (
        <div
          onMouseDown={() =>
            setSelected(null)
          }
          style={{
            position: "fixed",
            inset: 0,
            background:
              "rgba(16,24,40,.35)",
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
              width: "min(500px, 92vw)",
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
                justifyContent:
                  "space-between",
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
                    letterSpacing:
                      "0.08em",
                  }}
                >
                  DEPLOYED MODEL
                </div>

                <h2
                  style={{
                    margin: "5px 0",
                    color: "#101828",
                  }}
                >
                  {selected.model_name}
                </h2>

                <span
                  style={{
                    color: "#667085",
                    fontSize: 13,
                  }}
                >
                  Version{" "}
                  {selected.model_version}
                </span>
              </div>

              <button
                onClick={() =>
                  setSelected(null)
                }
                style={{
                  border: 0,
                  background:
                    "#f2f4f7",
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


            <section
              style={sectionStyle}
            >
              <h3
                style={
                  sectionTitleStyle
                }
              >
                Endpoint
              </h3>

              <Detail
                label="Endpoint"
                value={
                  selected.endpoint_name
                }
                mono
              />

              <Detail
                label="Deployment"
                value={
                  selected.deployment_name
                }
                mono
              />

              <Detail
                label="Status"
                value={
                  <StatusBadge
                    deployment={
                      selected
                    }
                  />
                }
              />

              <Detail
                label="Instance"
                value={`${selected.instance_count ?? 1} × ${selected.instance_type ?? "—"}`}
              />

              <Detail
                label="Model reference"
                value={
                  selected.azure_model_reference
                }
                mono
              />
            </section>


            <section
              style={sectionStyle}
            >
              <h3
                style={
                  sectionTitleStyle
                }
              >
                Endpoint URL
              </h3>

              <div
                style={{
                  padding: 14,
                  background:
                    "#f9fafb",
                  borderRadius: 10,
                  wordBreak:
                    "break-all",
                }}
              >
                <code
                  style={{
                    fontSize: 12,
                    color: "#475467",
                  }}
                >
                  {selected.endpoint_url ??
                    "Provisioning…"}
                </code>
              </div>
            </section>


            <div
              style={{
                display: "flex",
                gap: 10,
                marginTop: 18,
              }}
            >
              <button
                onClick={() =>
                  window.location.assign(
                    `/inference?endpoint=${encodeURIComponent(
                      selected.endpoint_name
                    )}&deployment=${encodeURIComponent(
                      selected.deployment_name
                    )}`
                  )
                }
                style={{
                  ...primaryButtonStyle,
                  flex: 1,
                }}
              >
                Test Endpoint
              </button>

              <button
                onClick={() =>
                  stop(selected)
                }
                style={{
                  ...dangerButtonStyle,
                  flex: 1,
                }}
              >
                <Square size={14} />
                Stop Endpoint
              </button>
            </div>
          </aside>
        </div>
      )}
    </div>
  );
}


function Detail({
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
        gridTemplateColumns:
          "130px 1fr",
        gap: 12,
        padding: "9px 0",
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
          wordBreak:
            "break-word",
        }}
      >
        {value}
      </span>
    </div>
  );
}


const buttonStyle: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  gap: 8,
  padding: "10px 15px",
  borderRadius: 9,
  border: "1px solid #d0d5dd",
  background: "#fff",
  color: "#344054",
  fontWeight: 700,
  cursor: "pointer",
};


const primaryButtonStyle: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  gap: 8,
  padding: "11px 15px",
  borderRadius: 9,
  border: 0,
  background: "#2f63e8",
  color: "#fff",
  fontWeight: 700,
  cursor: "pointer",
};


const dangerButtonStyle: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  justifyContent: "center",
  gap: 6,
  padding: "8px 11px",
  borderRadius: 8,
  border: "1px solid #fecdca",
  background: "#fff",
  color: "#b42318",
  fontWeight: 700,
  cursor: "pointer",
};


const errorStyle: CSSProperties = {
  marginBottom: 20,
  padding: "12px 14px",
  borderRadius: 10,
  border: "1px solid #fecdca",
  background: "#fff4f2",
  color: "#b42318",
  display: "flex",
  alignItems: "center",
  gap: 9,
};


const emptyStyle: CSSProperties = {
  minHeight: 280,
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  gap: 9,
  color: "#667085",
  padding: 30,
  textAlign: "center",
};


const thStyle: CSSProperties = {
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
};


const tdStyle: CSSProperties = {
  padding: "13px 14px",
  color: "#475467",
  fontSize: 12,
  whiteSpace: "nowrap",
};


const sectionStyle: CSSProperties = {
  padding: "18px 0",
  borderTop:
    "1px solid #eaecf0",
};


const sectionTitleStyle: CSSProperties = {
  margin: "0 0 14px",
  color: "#344054",
  fontSize: 13,
};
