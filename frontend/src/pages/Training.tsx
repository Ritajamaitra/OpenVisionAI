import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  Activity,
  AlertCircle,
  BarChart3,
  CheckCircle2,
  ChevronRight,
  Clock3,
  Cpu,
  Database,
  Eye,
  Loader2,
  Play,
  RefreshCw,
  Search,
  Trash2,
  X,
  XCircle,
} from "lucide-react";

import {
  cancelTrainingRun,
  createTrainingJob,
  deleteTrainingRun,
  getTrainingRun,
  listTrainingRuns,
  syncTrainingRun,
  type TrainingRun,
  type TrainingRunSummary,
} from "../api/training";

import {
  getProjects,
  type Project,
} from "../api/projects";

import {
  getProjectDatasets,
  type Dataset,
} from "../api/datasets";


const MODEL_OPTIONS = [
  {
    value: "yolov8n.pt",
    label: "YOLOv8 Nano",
    description: "Fastest · CPU-friendly",
  },
  {
    value: "yolov8s.pt",
    label: "YOLOv8 Small",
    description: "Balanced speed and accuracy",
  },
  {
    value: "yolov8m.pt",
    label: "YOLOv8 Medium",
    description: "Higher accuracy · heavier",
  },
];


const ACTIVE_STATUSES = [
  "QUEUED",
  "RUNNING",
  "STARTING",
  "PREPARING",
  "SUBMITTED",
];

type TrainingConfig = {
  epochs: number;
  imgsz: number;
  batch: number;
  modelName: string;
};

const TRAINING_CONFIG_STORAGE_KEY =
  "openvisionai.training.config.v1";

const MODEL_COST_MULTIPLIER: Record<string, number> = {
  "yolov8n.pt": 1,
  "yolov8s.pt": 1.35,
  "yolov8m.pt": 2,
};

function readTrainingConfigs(): Record<string, TrainingConfig> {
  try {
    return JSON.parse(
      localStorage.getItem(TRAINING_CONFIG_STORAGE_KEY) ?? "{}"
    );
  } catch {
    return {};
  }
}

function saveTrainingConfig(
  azureRunId: string,
  config: TrainingConfig
) {
  try {
    const configs = readTrainingConfigs();
    configs[azureRunId] = config;
    localStorage.setItem(
      TRAINING_CONFIG_STORAGE_KEY,
      JSON.stringify(configs)
    );
  } catch {
    // Training must still work if browser storage is unavailable.
  }
}

function formatDuration(seconds: number) {
  if (!Number.isFinite(seconds) || seconds < 0) {
    return "—";
  }

  const rounded = Math.floor(seconds);

  if (rounded < 60) {
    return `${rounded}s`;
  }

  const minutes = Math.floor(rounded / 60);
  const remainingSeconds = rounded % 60;

  if (minutes < 60) {
    return `${minutes}m ${remainingSeconds}s`;
  }

  const hours = Math.floor(minutes / 60);
  return `${hours}h ${minutes % 60}m`;
}

function estimateTrainingSeconds(
  config: TrainingConfig,
  referenceRuns: TrainingRunSummary[],
  configs: Record<string, TrainingConfig>
) {
  const samples = referenceRuns
    .filter(
      (run) =>
        normaliseStatus(run.status) === "COMPLETED" &&
        typeof run.training_time === "number" &&
        run.training_time > 0 &&
        configs[run.azure_run_id]
    )
    .map((run) => {
      const reference = configs[run.azure_run_id];
      const modelMultiplier =
        MODEL_COST_MULTIPLIER[reference.modelName] ?? 1.5;

      const work =
        reference.epochs *
        Math.pow(reference.imgsz / 640, 2) *
        (4 / Math.max(reference.batch, 1)) *
        modelMultiplier;

      return (run.training_time ?? 0) / Math.max(work, 1);
    })
    .filter((value) => Number.isFinite(value));

  if (samples.length === 0) {
    return null;
  }

  const sorted = [...samples].sort((a, b) => a - b);
  const median = sorted[Math.floor(sorted.length / 2)];

  const modelMultiplier =
    MODEL_COST_MULTIPLIER[config.modelName] ?? 1.5;

  const work =
    config.epochs *
    Math.pow(config.imgsz / 640, 2) *
    (4 / Math.max(config.batch, 1)) *
    modelMultiplier;

  return median * work;
}


function normaliseStatus(status?: string) {
  return (
    status ??
    "UNKNOWN"
  ).toUpperCase();
}


function formatMetric(
  value?: number | null
) {
  if (
    value === null ||
    value === undefined
  ) {
    return "—";
  }

  return `${(
    value * 100
  ).toFixed(1)}%`;
}


function formatTrainingTime(
  seconds?: number | null
) {
  if (
    seconds === null ||
    seconds === undefined
  ) {
    return "—";
  }

  if (seconds < 60) {
    return `${seconds.toFixed(0)} sec`;
  }

  const minutes =
    Math.floor(seconds / 60);

  const remainingSeconds =
    Math.floor(seconds % 60);

  if (minutes < 60) {
    return `${minutes}m ${remainingSeconds}s`;
  }

  const hours =
    Math.floor(minutes / 60);

  return `${hours}h ${
    minutes % 60
  }m`;
}


function formatDate(
  value?: string | null
) {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return "—";
  }

  return date.toLocaleString(
    undefined,
    {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }
  );
}


function StatusBadge({
  status,
}: {
  status: string;
}) {
  const normalized =
    normaliseStatus(status);

  const isRunning =
    ACTIVE_STATUSES.includes(
      normalized
    );

  let className =
    "training-status";

  if (isRunning) {
    className +=
      " training-status-running";
  } else if (
    normalized === "COMPLETED"
  ) {
    className +=
      " training-status-completed";
  } else if (
    normalized === "FAILED"
  ) {
    className +=
      " training-status-failed";
  } else if (
    normalized === "CANCELED" ||
    normalized === "CANCELLED"
  ) {
    className +=
      " training-status-cancelled";
  } else {
    className +=
      " training-status-default";
  }

  return (
    <span className={className}>
      {isRunning && (
        <span className="status-pulse" />
      )}

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
  icon: React.ReactNode;
}) {
  return (
    <div className="training-metric-card">
      <div className="training-metric-icon">
        {icon}
      </div>

      <div>
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
    </div>
  );
}


export default function Training() {

  // ------------------------------------------------------------
  // Data
  // ------------------------------------------------------------

  const [
    trainingRuns,
    setTrainingRuns,
  ] = useState<TrainingRunSummary[]>(
    []
  );

  const [
    projects,
    setProjects,
  ] = useState<Project[]>(
    []
  );

  const [
    datasets,
    setDatasets,
  ] = useState<Dataset[]>(
    []
  );


  // ------------------------------------------------------------
  // UI state
  // ------------------------------------------------------------

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    refreshing,
    setRefreshing,
  ] = useState(false);

  const [
    submitting,
    setSubmitting,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState<string | null>(
    null
  );

  const [
    search,
    setSearch,
  ] = useState("");

  const [
    statusFilter,
    setStatusFilter,
  ] = useState("ALL");

  const [
    selectedRun,
    setSelectedRun,
  ] = useState<TrainingRun | null>(
    null
  );

  const [
    detailsLoading,
    setDetailsLoading,
  ] = useState(false);

  const [
    actionLoading,
    setActionLoading,
  ] = useState(false);

  const [
    showNewTraining,
    setShowNewTraining,
  ] = useState(false);

  const [now, setNow] = useState(() => Date.now());

  const [trainingConfigs, setTrainingConfigs] =
    useState<Record<string, TrainingConfig>>(() =>
      readTrainingConfigs()
    );


  // ------------------------------------------------------------
  // New training form
  // ------------------------------------------------------------

  const [
    projectId,
    setProjectId,
  ] = useState("");

  const [
    datasetId,
    setDatasetId,
  ] = useState("");

  const [
    modelName,
    setModelName,
  ] = useState(
    "yolov8n.pt"
  );

  const [
    epochs,
    setEpochs,
  ] = useState(5);

  const [
    imageSize,
    setImageSize,
  ] = useState(640);

  const [
    batchSize,
    setBatchSize,
  ] = useState(4);


  // ------------------------------------------------------------
  // Load projects
  // ------------------------------------------------------------

  const loadProjects =
    useCallback(
      async () => {
        const result =
          await getProjects();

        setProjects(result);

        if (
          result.length > 0 &&
          !projectId
        ) {
          setProjectId(
            String(result[0].id)
          );
        }
      },
      [projectId]
    );


  // ------------------------------------------------------------
  // Load datasets
  // ------------------------------------------------------------

  const loadDatasets =
    useCallback(
      async (
        selectedProjectId: string
      ) => {

        if (
          !selectedProjectId
        ) {
          setDatasets([]);
          setDatasetId("");
          return;
        }

        const result =
          await getProjectDatasets(
            Number(
              selectedProjectId
            )
          );

        setDatasets(result);

        setDatasetId(
          result.length > 0
            ? String(result[0].id)
            : ""
        );
      },
      []
    );


  // ------------------------------------------------------------
  // Load training runs
  // ------------------------------------------------------------

  const loadTrainingRuns =
    useCallback(
      async (
        showSpinner = true
      ) => {

        if (showSpinner) {
          setLoading(true);
        }

        setError(null);

        try {
          const result =
            await listTrainingRuns();

          setTrainingRuns(result);

        } catch (err: any) {

          setError(
            err?.response?.data
              ?.detail ??
              "Could not load training runs."
          );

        } finally {

          if (showSpinner) {
            setLoading(false);
          }
        }
      },
      []
    );


  // ------------------------------------------------------------
  // Initial load
  // ------------------------------------------------------------

  useEffect(() => {

    async function initialise() {

      try {

        await Promise.all([
          loadProjects(),
          loadTrainingRuns(),
        ]);

      } catch (err: any) {

        setError(
          err?.response?.data
            ?.detail ??
            "Could not load training data."
        );

      } finally {

        setLoading(false);
      }
    }

    initialise();

  }, [
    loadProjects,
    loadTrainingRuns,
  ]);


  // ------------------------------------------------------------
  // Load datasets whenever project changes
  // ------------------------------------------------------------

  useEffect(() => {

    if (!projectId) {
      return;
    }

    loadDatasets(
      projectId
    );

  }, [
    projectId,
    loadDatasets,
  ]);


  // ------------------------------------------------------------
  // Refresh
  // ------------------------------------------------------------

  async function refresh() {

    setRefreshing(true);

    try {

      await loadTrainingRuns(
        false
      );

    } finally {

      setRefreshing(false);
    }
  }


  // ------------------------------------------------------------
  // Live elapsed-time clock
  // ------------------------------------------------------------

  useEffect(() => {
    const timer = window.setInterval(
      () => setNow(Date.now()),
      1000
    );

    return () => window.clearInterval(timer);
  }, []);

  // ------------------------------------------------------------
  // Sync active jobs
  // ------------------------------------------------------------

  const syncActiveRuns =
    useCallback(
      async () => {

        const activeRuns =
          trainingRuns.filter(
            (run) =>
              ACTIVE_STATUSES.includes(
                normaliseStatus(
                  run.status
                )
              )
          );

        if (
          activeRuns.length === 0
        ) {
          return;
        }

        await Promise.allSettled(
          activeRuns.map(
            (run) =>
              syncTrainingRun(
                run.azure_run_id
              )
          )
        );

        await loadTrainingRuns(
          false
        );

        if (
          selectedRun &&
          ACTIVE_STATUSES.includes(
            normaliseStatus(
              selectedRun.status
            )
          )
        ) {

          try {

            const updated =
              await getTrainingRun(
                selectedRun.azure_run_id
              );

            setSelectedRun(
              updated
            );

          } catch {
            // Keep existing details.
          }
        }

      },
      [
        trainingRuns,
        selectedRun,
        loadTrainingRuns,
      ]
    );


  // ------------------------------------------------------------
  // Poll active jobs
  // ------------------------------------------------------------

  useEffect(() => {

    const hasActive =
      trainingRuns.some(
        (run) =>
          ACTIVE_STATUSES.includes(
            normaliseStatus(
              run.status
            )
          )
      );

    if (!hasActive) {
      return;
    }

    const timer =
      window.setInterval(
        () => {
          syncActiveRuns();
        },
        5000
      );

    return () =>
      window.clearInterval(
        timer
      );

  }, [
    trainingRuns,
    syncActiveRuns,
  ]);


  // ------------------------------------------------------------
  // Open run details
  // ------------------------------------------------------------

  async function openRun(
    azureRunId: string
  ) {

    setDetailsLoading(true);
    setError(null);

    try {

      const result =
        await getTrainingRun(
          azureRunId
        );

      setSelectedRun(
        result
      );

    } catch (err: any) {

      setError(
        err?.response?.data
          ?.detail ??
          "Could not load training run."
      );

    } finally {

      setDetailsLoading(false);
    }
  }


  // ------------------------------------------------------------
  // Start training
  // ------------------------------------------------------------

  async function submitTraining(
    event: React.FormEvent
  ) {

    event.preventDefault();

    if (
      !projectId ||
      !datasetId
    ) {
      setError(
        "Select a project and dataset."
      );
      return;
    }

    setSubmitting(true);
    setError(null);

    try {

      const result =
        await createTrainingJob({
          project_id:
            Number(projectId),

          dataset_id:
            Number(datasetId),

          model_name:
            modelName,

          epochs:
            Number(epochs),

          imgsz:
            Number(imageSize),

          batch:
            Number(batchSize),
        });

      const submittedConfig: TrainingConfig = {
        modelName,
        epochs: Number(epochs),
        imgsz: Number(imageSize),
        batch: Number(batchSize),
      };

      saveTrainingConfig(
        result.azure_run_id,
        submittedConfig
      );

      setTrainingConfigs(
        readTrainingConfigs()
      );

      setShowNewTraining(
        false
      );

      await loadTrainingRuns(
        false
      );

      await openRun(
        result.azure_run_id
      );

    } catch (err: any) {

      setError(
        err?.response?.data
          ?.detail ??
          "Could not submit training job."
      );

    } finally {

      setSubmitting(false);
    }
  }


  // ------------------------------------------------------------
  // Cancel training
  // ------------------------------------------------------------

  async function cancelSelectedRun() {

    if (!selectedRun) {
      return;
    }

    const confirmed =
      window.confirm(
        "Cancel this Azure ML training run?"
      );

    if (!confirmed) {
      return;
    }

    setActionLoading(true);
    setError(null);

    try {

      const result =
        await cancelTrainingRun(
          selectedRun.azure_run_id
        );

      setSelectedRun(
        result
      );

      await loadTrainingRuns(
        false
      );

    } catch (err: any) {

      setError(
        err?.response?.data
          ?.detail ??
          "Could not cancel training run."
      );

    } finally {

      setActionLoading(false);
    }
  }


  // ------------------------------------------------------------
  // Delete training run
  // ------------------------------------------------------------

  async function deleteSelectedRun() {

    if (!selectedRun) {
      return;
    }

    const confirmed =
      window.confirm(
        "Delete this training run record? This does not delete the Azure ML artifacts."
      );

    if (!confirmed) {
      return;
    }

    setActionLoading(true);
    setError(null);

    try {

      await deleteTrainingRun(
        selectedRun.azure_run_id
      );

      setSelectedRun(null);

      await loadTrainingRuns(
        false
      );

    } catch (err: any) {

      setError(
        err?.response?.data
          ?.detail ??
          "Could not delete training run."
      );

    } finally {

      setActionLoading(false);
    }
  }


  // ------------------------------------------------------------
  // Filtered runs
  // ------------------------------------------------------------

  const filteredRuns =
    useMemo(() => {

      const query =
        search
          .trim()
          .toLowerCase();

      return trainingRuns.filter(
        (run) => {

          const status =
            normaliseStatus(
              run.status
            );

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
            run.azure_run_id
              ?.toLowerCase()
              .includes(query) ||
            run.model_name
              ?.toLowerCase()
              .includes(query) ||
            run.experiment_name
              ?.toLowerCase()
              .includes(query)
          );
        }
      );

    }, [
      trainingRuns,
      search,
      statusFilter,
    ]);


  // ------------------------------------------------------------
  // KPI counts
  // ------------------------------------------------------------

  const totalJobs =
    trainingRuns.length;

  const runningJobs =
    trainingRuns.filter(
      (run) =>
        ACTIVE_STATUSES.includes(
          normaliseStatus(
            run.status
          )
        )
    ).length;

  const completedJobs =
    trainingRuns.filter(
      (run) =>
        normaliseStatus(
          run.status
        ) === "COMPLETED"
    ).length;

  const failedJobs =
    trainingRuns.filter(
      (run) =>
        normaliseStatus(
          run.status
        ) === "FAILED"
    ).length;


  // ------------------------------------------------------------
  // Project / dataset labels
  // ------------------------------------------------------------

  function projectName(
    id: number
  ) {

    return (
      projects.find(
        (project) =>
          project.id === id
      )?.name ??
      `Project #${id}`
    );
  }


  const selectedProject =
    projects.find(
      (project) =>
        String(project.id) ===
        projectId
    );


  // ------------------------------------------------------------
  // Render
  // ------------------------------------------------------------

  return (
    <div className="training-page">

      {/* ========================================================
          PAGE HEADER
          ======================================================== */}

      <div className="training-page-heading">

        <div>

          <span className="training-eyebrow">
            MODEL DEVELOPMENT
          </span>

          <h1>
            Training
          </h1>

          <p>
            Train computer vision models
            on reviewed datasets using
            Azure Machine Learning.
          </p>

        </div>

        <div className="training-header-actions">

          <button
            className="training-secondary-button"
            onClick={refresh}
            disabled={
              refreshing ||
              loading
            }
          >

            {refreshing ? (
              <Loader2
                size={16}
                className="training-spin"
              />
            ) : (
              <RefreshCw size={16} />
            )}

            Refresh

          </button>

          <button
            className="training-primary-button"
            onClick={() =>
              setShowNewTraining(true)
            }
          >

            <Play size={15} />

            New Training Job

          </button>

        </div>

      </div>


      {/* ========================================================
          ERROR
          ======================================================== */}

      {error && (

        <div className="training-error">

          <AlertCircle
            size={17}
          />

          <span>
            {error}
          </span>

          <button
            onClick={() =>
              setError(null)
            }
          >
            <X size={15} />
          </button>

        </div>

      )}


      {/* ========================================================
          KPI CARDS
          ======================================================== */}

      <div className="training-kpi-grid">

        <MetricCard
          label="Total Jobs"
          value={String(
            totalJobs
          )}
          icon={
            <BarChart3
              size={18}
            />
          }
        />

        <MetricCard
          label="Running"
          value={String(
            runningJobs
          )}
          icon={
            <Activity
              size={18}
            />
          }
        />

        <MetricCard
          label="Completed"
          value={String(
            completedJobs
          )}
          icon={
            <CheckCircle2
              size={18}
            />
          }
        />

        <MetricCard
          label="Failed"
          value={String(
            failedJobs
          )}
          icon={
            <XCircle
              size={18}
            />
          }
        />

      </div>


      {/* ========================================================
          JOB TABLE
          ======================================================== */}

      <section className="training-card">

        <div className="training-card-header">

          <div>

            <span className="training-card-eyebrow">
              EXPERIMENT HISTORY
            </span>

            <h2>
              Training Jobs
            </h2>

            <p>
              Track Azure ML training
              runs and evaluation metrics.
            </p>

          </div>

          <div className="training-table-count">
            {filteredRuns.length} jobs
          </div>

        </div>


        {/* Filters */}

        <div className="training-filters">

          <div className="training-search">

            <Search
              size={15}
            />

            <input
              value={search}
              onChange={(event) =>
                setSearch(
                  event.target.value
                )
              }
              placeholder="Search runs, models or experiments"
            />

          </div>


          <select
            value={statusFilter}
            onChange={(event) =>
              setStatusFilter(
                event.target.value
              )
            }
            className="training-filter-select"
          >

            <option value="ALL">
              All statuses
            </option>

            <option value="QUEUED">
              Queued
            </option>

            <option value="RUNNING">
              Running
            </option>

            <option value="COMPLETED">
              Completed
            </option>

            <option value="FAILED">
              Failed
            </option>

            <option value="CANCELED">
              Canceled
            </option>

          </select>

        </div>


        {/* Table */}

        {loading ? (

          <div className="training-empty-state">

            <Loader2
              size={22}
              className="training-spin"
            />

            <strong>
              Loading training jobs…
            </strong>

            <span>
              Fetching your training history.
            </span>

          </div>

        ) : filteredRuns.length === 0 ? (

          <div className="training-empty-state">

            <div className="training-empty-icon">
              <Cpu size={22} />
            </div>

            <strong>
              No training jobs found
            </strong>

            <span>
              Start your first Azure ML
              training run to see it here.
            </span>

            <button
              className="training-primary-button"
              onClick={() =>
                setShowNewTraining(true)
              }
            >
              <Play size={15} />
              Start Training
            </button>

          </div>

        ) : (

          <div className="training-table-wrapper">

            <table className="training-table">

              <thead>

                <tr>

                  <th>
                    Training Run
                  </th>

                  <th>
                    Project
                  </th>

                  <th>
                    Model
                  </th>

                  <th>
                    Status
                  </th>

                  <th>
                    Time
                  </th>

                  <th>
                    Estimate
                  </th>

                  <th>
                    Precision
                  </th>

                  <th>
                    mAP@50
                  </th>

                  <th>
                    mAP@50:95
                  </th>

                  <th />

                </tr>

              </thead>

              <tbody>

                {filteredRuns.map(
                  (run) => (

                    <tr
                      key={
                        run.azure_run_id
                      }
                      onClick={() =>
                        openRun(
                          run.azure_run_id
                        )
                      }
                      className="training-table-row"
                    >

                      <td>

                        <div className="training-run-cell">

                          <div className="training-run-icon">
                            <Cpu
                              size={16}
                            />
                          </div>

                          <div>

                            <strong>
                              {run.experiment_name ||
                                "OpenVisionAI Training"}
                            </strong>

                            <span>
                              {run.azure_run_id}
                            </span>

                          </div>

                        </div>

                      </td>


                      <td>

                        <span className="training-project-text">
                          {projectName(
                            run.project_id
                          )}
                        </span>

                      </td>


                      <td>

                        <span className="training-model-pill">
                          {run.model_name ||
                            "—"}
                        </span>

                      </td>


                      <td>
                        <StatusBadge
                          status={
                            run.status
                          }
                        />
                      </td>

                      <td>
                        <div className="training-time-cell">
                          <Clock3 size={14} />
                          <span>
                            {(() => {
                              const status =
                                normaliseStatus(
                                  run.status
                                );

                              if (
                                status === "COMPLETED"
                              ) {
                                return formatTrainingTime(
                                  run.training_time
                                );
                              }

                              if (
                                ACTIVE_STATUSES.includes(
                                  status
                                )
                              ) {
                                if (!run.started_at) {
                                  return "Starting…";
                                }

                                const started =
                                  new Date(
                                    run.started_at
                                  ).getTime();

                                return formatDuration(
                                  Math.max(
                                    0,
                                    (now - started) /
                                      1000
                                  )
                                );
                              }

                              return "—";
                            })()}
                          </span>
                        </div>
                      </td>

                      <td>
                        {(() => {
                          const status =
                            normaliseStatus(
                              run.status
                            );
                          const config =
                            trainingConfigs[
                              run.azure_run_id
                            ];

                          if (
                            status === "COMPLETED"
                          ) {
                            return formatTrainingTime(
                              run.training_time
                            );
                          }

                          if (
                            !ACTIVE_STATUSES.includes(
                              status
                            )
                          ) {
                            return "—";
                          }

                          if (!config) {
                            return (
                              <span className="training-estimate-text">
                                Learning…
                              </span>
                            );
                          }

                          const estimate =
                            estimateTrainingSeconds(
                              config,
                              trainingRuns,
                              trainingConfigs
                            );

                          if (estimate == null) {
                            return (
                              <span className="training-estimate-text">
                                Learning…
                              </span>
                            );
                          }

                          const started =
                            run.started_at
                              ? new Date(
                                  run.started_at
                                ).getTime()
                              : now;

                          const elapsed =
                            Math.max(
                              0,
                              (now - started) /
                                1000
                            );

                          const remaining =
                            Math.max(
                              0,
                              estimate - elapsed
                            );

                          return (
                            <span className="training-estimate-text">
                              {remaining > 0
                                ? `~${formatDuration(
                                    remaining
                                  )} left`
                                : "Finishing…"}
                            </span>
                          );
                        })()}
                      </td>


                      <td>
                        {formatMetric(
                          run.precision
                        )}
                      </td>


                      <td>
                        {formatMetric(
                          run.map50
                        )}
                      </td>


                      <td>
                        {formatMetric(
                          run.map50_95
                        )}
                      </td>


                      <td>

                        <button
                          className="training-row-action"
                          onClick={(
                            event
                          ) => {
                            event.stopPropagation();

                            openRun(
                              run.azure_run_id
                            );
                          }}
                        >
                          <ChevronRight
                            size={17}
                          />
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


      {/* ========================================================
          NEW TRAINING MODAL
          ======================================================== */}

      {showNewTraining && (

        <div
          className="training-modal-backdrop"
          onMouseDown={() =>
            !submitting &&
            setShowNewTraining(false)
          }
        >

          <div
            className="training-modal"
            onMouseDown={(event) =>
              event.stopPropagation()
            }
          >

            <div className="training-modal-header">

              <div>

                <span className="training-card-eyebrow">
                  AZURE ML TRAINING
                </span>

                <h2>
                  New Training Job
                </h2>

                <p>
                  Configure a YOLO training
                  run using a reviewed dataset.
                </p>

              </div>

              <button
                className="training-modal-close"
                onClick={() =>
                  !submitting &&
                  setShowNewTraining(false)
                }
                disabled={
                  submitting
                }
              >
                <X size={18} />
              </button>

            </div>


            <form
              className="training-form"
              onSubmit={
                submitTraining
              }
            >

              {/* Project */}

              <div className="training-field">

                <label>
                  Project
                </label>

                <select
                  value={projectId}
                  onChange={(event) =>
                    setProjectId(
                      event.target.value
                    )
                  }
                  required
                >

                  <option value="">
                    Select project
                  </option>

                  {projects.map(
                    (project) => (

                      <option
                        key={
                          project.id
                        }
                        value={
                          project.id
                        }
                      >
                        {project.name}
                      </option>

                    )
                  )}

                </select>

              </div>


              {/* Dataset */}

              <div className="training-field">

                <label>
                  Dataset
                </label>

                <select
                  value={datasetId}
                  onChange={(event) =>
                    setDatasetId(
                      event.target.value
                    )
                  }
                  disabled={
                    !projectId
                  }
                  required
                >

                  <option value="">
                    {projectId
                      ? "Select dataset"
                      : "Select project first"}
                  </option>

                  {datasets.map(
                    (dataset) => (

                      <option
                        key={
                          dataset.id
                        }
                        value={
                          dataset.id
                        }
                      >
                        {dataset.name}
                      </option>

                    )
                  )}

                </select>

                {selectedProject && (
                  <span className="training-field-hint">
                    Datasets belonging to{" "}
                    {selectedProject.name}
                  </span>
                )}

              </div>


              {/* Model */}

              <div className="training-field">

                <label>
                  Base Model
                </label>

                <select
                  value={modelName}
                  onChange={(event) =>
                    setModelName(
                      event.target.value
                    )
                  }
                >

                  {MODEL_OPTIONS.map(
                    (model) => (

                      <option
                        key={
                          model.value
                        }
                        value={
                          model.value
                        }
                      >
                        {model.label} ·{" "}
                        {model.value}
                      </option>

                    )
                  )}

                </select>

                <span className="training-field-hint">
                  {
                    MODEL_OPTIONS.find(
                      (model) =>
                        model.value ===
                        modelName
                    )?.description
                  }
                </span>

              </div>


              {/* Parameters */}

              <div className="training-form-grid">

                <div className="training-field">

                  <label>
                    Epochs
                  </label>

                  <input
                    type="number"
                    min={1}
                    max={1000}
                    value={epochs}
                    onChange={(event) =>
                      setEpochs(
                        Number(
                          event.target.value
                        )
                      )
                    }
                  />

                  <span className="training-field-hint">
                    5 for smoke testing;
                    50+ for actual training.
                  </span>

                </div>


                <div className="training-field">

                  <label>
                    Image Size
                  </label>

                  <select
                    value={imageSize}
                    onChange={(event) =>
                      setImageSize(
                        Number(
                          event.target.value
                        )
                      )
                    }
                  >

                    <option value={320}>
                      320 × 320
                    </option>

                    <option value={416}>
                      416 × 416
                    </option>

                    <option value={640}>
                      640 × 640
                    </option>

                    <option value={832}>
                      832 × 832
                    </option>

                  </select>

                </div>


                <div className="training-field">

                  <label>
                    Batch Size
                  </label>

                  <select
                    value={batchSize}
                    onChange={(event) =>
                      setBatchSize(
                        Number(
                          event.target.value
                        )
                      )
                    }
                  >

                    <option value={1}>
                      1
                    </option>

                    <option value={2}>
                      2
                    </option>

                    <option value={4}>
                      4
                    </option>

                    <option value={8}>
                      8
                    </option>

                    <option value={16}>
                      16
                    </option>

                  </select>

                </div>

              </div>


              {/* Estimated time */}

              <div className="training-info-box">
                <Clock3
                  size={17}
                />

                <div>
                  <strong>
                    Estimated training time
                  </strong>

                  <span>
                    {(() => {
                      const estimate =
                        estimateTrainingSeconds(
                          {
                            modelName,
                            epochs: Number(epochs),
                            imgsz: Number(imageSize),
                            batch: Number(batchSize),
                          },
                          trainingRuns,
                          trainingConfigs
                        );

                      return estimate != null
                        ? `~${formatDuration(
                            estimate
                          )} based on completed runs.`
                        : "Complete one run to enable data-driven estimates.";
                    })()}
                  </span>
                </div>
              </div>

              {/* Info */}

              <div className="training-info-box">

                <Database
                  size={17}
                />

                <div>

                  <strong>
                    Dataset preparation
                  </strong>

                  <span>
                    OpenVisionAI will export
                    the selected dataset to
                    YOLO format before submitting
                    the Azure ML job.
                  </span>

                </div>

              </div>


              {/* Actions */}

              <div className="training-form-actions">

                <button
                  type="button"
                  className="training-secondary-button"
                  onClick={() =>
                    setShowNewTraining(
                      false
                    )
                  }
                  disabled={
                    submitting
                  }
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="training-primary-button"
                  disabled={
                    submitting ||
                    !projectId ||
                    !datasetId
                  }
                >

                  {submitting ? (
                    <>
                      <Loader2
                        size={16}
                        className="training-spin"
                      />
                      Submitting…
                    </>
                  ) : (
                    <>
                      <Play size={15} />
                      Start Training
                    </>
                  )}

                </button>

              </div>

            </form>

          </div>

        </div>

      )}


      {/* ========================================================
          RUN DETAILS DRAWER
          ======================================================== */}

      {(selectedRun ||
        detailsLoading) && (

        <div
          className="training-drawer-backdrop"
          onMouseDown={() =>
            setSelectedRun(null)
          }
        >

          <aside
            className="training-drawer"
            onMouseDown={(event) =>
              event.stopPropagation()
            }
          >

            {detailsLoading &&
            !selectedRun ? (

              <div className="training-drawer-loading">

                <Loader2
                  size={24}
                  className="training-spin"
                />

                <span>
                  Loading training run…
                </span>

              </div>

            ) : selectedRun ? (

              <>

                <div className="training-drawer-header">

                  <div>

                    <span className="training-card-eyebrow">
                      TRAINING RUN
                    </span>

                    <h2>
                      {selectedRun
                        .experiment_name ||
                        "OpenVisionAI Training"}
                    </h2>

                    <code>
                      {
                        selectedRun.azure_run_id
                      }
                    </code>

                  </div>

                  <button
                    className="training-modal-close"
                    onClick={() =>
                      setSelectedRun(
                        null
                      )
                    }
                  >
                    <X size={18} />
                  </button>

                </div>


                {/* Status */}

                <div className="training-detail-status">

                  <div>

                    <span>
                      Current status
                    </span>

                    <StatusBadge
                      status={
                        selectedRun.status
                      }
                    />

                  </div>

                  {(
                    ACTIVE_STATUSES.includes(
                      normaliseStatus(
                        selectedRun.status
                      )
                    ) ||
                    (
                      normaliseStatus(
                        selectedRun.status
                      ) === "COMPLETED" &&
                      !selectedRun.registered_model_name
                    )
                  ) && (

                    <button
                      className="training-secondary-button"
                      onClick={() =>
                        syncTrainingRun(
                          selectedRun.azure_run_id
                        ).then(
                          (updated) => {
                            setSelectedRun(
                              updated
                            );
                            loadTrainingRuns(
                              false
                            );
                          }
                        )
                      }
                    >
                      <RefreshCw
                        size={14}
                      />
                      {normaliseStatus(
                        selectedRun.status
                      ) === "COMPLETED"
                        ? "Register Model"
                        : "Sync"}
                    </button>

                  )}

                </div>


                {/* Run information */}

                <section className="training-detail-section">

                  <div className="training-detail-section-title">
                    Run Configuration
                  </div>

                  <div className="training-detail-grid">

                    <div>
                      <span>
                        Project
                      </span>

                      <strong>
                        {projectName(
                          selectedRun.project_id
                        )}
                      </strong>
                    </div>

                    <div>
                      <span>
                        Dataset
                      </span>

                      <strong>
                        Dataset #
                        {
                          selectedRun.dataset_id
                        }
                      </strong>
                    </div>

                    <div>
                      <span>
                        Model
                      </span>

                      <strong>
                        {
                          selectedRun.model_name ||
                          "—"
                        }
                      </strong>
                    </div>

                    <div>
                      <span>
                        Experiment
                      </span>

                      <strong>
                        {
                          selectedRun.experiment_name ||
                          "—"
                        }
                      </strong>
                    </div>

                  </div>

                </section>


                {/* Metrics */}

                <section className="training-detail-section">

                  <div className="training-detail-section-title">
                    Evaluation Metrics
                  </div>

                  <div className="training-detail-metrics">

                    <div>

                      <span>
                        Precision
                      </span>

                      <strong>
                        {formatMetric(
                          selectedRun.precision
                        )}
                      </strong>

                    </div>

                    <div>

                      <span>
                        Recall
                      </span>

                      <strong>
                        {formatMetric(
                          selectedRun.recall
                        )}
                      </strong>

                    </div>

                    <div>

                      <span>
                        mAP@50
                      </span>

                      <strong>
                        {formatMetric(
                          selectedRun.map50
                        )}
                      </strong>

                    </div>

                    <div>

                      <span>
                        mAP@50:95
                      </span>

                      <strong>
                        {formatMetric(
                          selectedRun.map50_95
                        )}
                      </strong>

                    </div>

                  </div>

                </section>


                {/* Timing */}

                <section className="training-detail-section">

                  <div className="training-detail-section-title">
                    Execution
                  </div>

                  <div className="training-timeline">

                    <div>

                      <Clock3
                        size={16}
                      />

                      <span>
                        Created
                      </span>

                      <strong>
                        {formatDate(
                          selectedRun.created_at
                        )}
                      </strong>

                    </div>

                    <div>

                      <Activity
                        size={16}
                      />

                      <span>
                        Started
                      </span>

                      <strong>
                        {formatDate(
                          selectedRun.started_at
                        )}
                      </strong>

                    </div>

                    <div>

                      <CheckCircle2
                        size={16}
                      />

                      <span>
                        Completed
                      </span>

                      <strong>
                        {formatDate(
                          selectedRun.completed_at
                        )}
                      </strong>

                    </div>

                    <div>

                      <Clock3
                        size={16}
                      />

                      <span>
                        Training Time
                      </span>

                      <strong>
                        {formatTrainingTime(
                          selectedRun.training_time
                        )}
                      </strong>

                    </div>

                  </div>

                </section>


                {ACTIVE_STATUSES.includes(
                  normaliseStatus(
                    selectedRun.status
                  )
                ) && (
                  <section className="training-detail-section">
                    <div className="training-detail-section-title">
                      Live Progress
                    </div>

                    <div className="training-detail-metrics">
                      <div>
                        <span>
                          Elapsed
                        </span>

                        <strong>
                          {selectedRun.started_at
                            ? formatDuration(
                                Math.max(
                                  0,
                                  (now -
                                    new Date(
                                      selectedRun.started_at
                                    ).getTime()) /
                                    1000
                                )
                              )
                            : "Starting…"}
                        </strong>
                      </div>

                      <div>
                        <span>
                          Estimated remaining
                        </span>

                        <strong>
                          {(() => {
                            const config =
                              trainingConfigs[
                                selectedRun.azure_run_id
                              ];

                            if (!config) {
                              return "Learning…";
                            }

                            const estimate =
                              estimateTrainingSeconds(
                                config,
                                trainingRuns,
                                trainingConfigs
                              );

                            if (
                              estimate == null ||
                              !selectedRun.started_at
                            ) {
                              return "Learning…";
                            }

                            const elapsed =
                              Math.max(
                                0,
                                (now -
                                  new Date(
                                    selectedRun.started_at
                                  ).getTime()) /
                                  1000
                              );

                            return elapsed < estimate
                              ? `~${formatDuration(
                                  estimate - elapsed
                                )}`
                              : "Finishing…";
                          })()}
                        </strong>
                      </div>
                    </div>
                  </section>
                )}

                {/* Registered model */}

                <section className="training-detail-section">

                  <div className="training-detail-section-title">
                    Model Registry
                  </div>

                  {selectedRun
                    .registered_model_name ? (

                    <div className="training-registered-model">

                      <CheckCircle2
                        size={17}
                      />

                      <div>

                        <strong>
                          {
                            selectedRun.registered_model_name
                          }
                        </strong>

                        <span>
                          Version{" "}
                          {
                            selectedRun
                              .registered_model_version ||
                            "—"
                          }
                        </span>

                      </div>

                    </div>

                  ) : (

                    <div className="training-registry-placeholder">

                      <Eye size={17} />

                      <div>

                        <strong>
                          Not registered yet
                        </strong>

                        <span>
                          Model registration
                          will be connected in
                          the Model Registry
                          workflow.
                        </span>

                      </div>

                    </div>

                  )}

                </section>


                {/* Actions */}

                <div className="training-drawer-actions">

                  {ACTIVE_STATUSES.includes(
                    normaliseStatus(
                      selectedRun.status
                    )
                  ) && (

                    <button
                      className="training-danger-outline"
                      onClick={
                        cancelSelectedRun
                      }
                      disabled={
                        actionLoading
                      }
                    >

                      <XCircle
                        size={15}
                      />

                      Cancel Job

                    </button>

                  )}

                  <button
                    className="training-delete-button"
                    onClick={
                      deleteSelectedRun
                    }
                    disabled={
                      actionLoading
                    }
                  >

                    {actionLoading ? (
                      <Loader2
                        size={15}
                        className="training-spin"
                      />
                    ) : (
                      <Trash2
                        size={15}
                      />
                    )}

                    Delete Record

                  </button>

                </div>

              </>

            ) : null}

          </aside>

        </div>

      )}

    </div>
  );
}