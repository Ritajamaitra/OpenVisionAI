import { useEffect, useMemo, useRef, useState } from "react";
import {
  AlertCircle,
  CheckCircle2,
  Database,
  Edit3,
  ExternalLink,
  FileText,
  FolderOpen,
  Image,
  Image as ImageIcon,
  Loader2,
  Plus,
  RefreshCw,
  Search,
  Trash2,
  Upload,
  X,
} from "lucide-react";

import {
  createDataset,
  deleteDataset,
  getDatasetStatistics,
  getProjectDatasets,
  listDatasetImages,
  updateDataset,
  uploadDatasetImages,
  type Dataset,
  type DatasetStatistics,
} from "../api/datasets";

import {
  getProjects,
  type Project,
} from "../api/projects";

import { useNavigate } from "react-router-dom";

interface DatasetImageCardProps {
  datasetId: number;
  imageName: string;
  onAnnotate: () => void;
}

function DatasetImageCard({
  datasetId,
  imageName,
  onAnnotate,
}: DatasetImageCardProps) {
  return (
    <article className="dataset-image-card" data-dataset-id={datasetId}>
      <div className="dataset-image-preview">
        <ImageIcon size={28} />
      </div>

      <div className="dataset-image-card-body">
        <div className="dataset-image-name">
          <strong title={imageName}>{imageName}</strong>
        </div>

        <div className="dataset-image-status">
          <CheckCircle2 size={14} />
          Ready to annotate
        </div>

        <button
          type="button"
          className="dataset-secondary-button dataset-annotate-button"
          onClick={onAnnotate}
        >
          <ExternalLink size={15} />
          Annotate
        </button>
      </div>
    </article>
  );
}

export default function Datasets() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] =
    useState<number | null>(null);

  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDataset, setSelectedDataset] =
    useState<Dataset | null>(null);

  const navigate = useNavigate();

  const [selectedDatasetId, setSelectedDatasetId] =
    useState<number | null>(null);

  const [datasetImages, setDatasetImages] =
    useState<string[]>([]);

  const [imageSearch, setImageSearch] = useState("");

  const [loadingImages, setLoadingImages] = useState(false);
  const [uploadingImages, setUploadingImages] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const [statistics, setStatistics] =
    useState<DatasetStatistics | null>(null);

  const [search, setSearch] = useState("");

  const [loadingProjects, setLoadingProjects] = useState(true);
  const [loadingDatasets, setLoadingDatasets] = useState(false);
  const [loadingStatistics, setLoadingStatistics] =
    useState(false);

  const [error, setError] = useState("");

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const [form, setForm] = useState({
    name: "",
    description: "",
    storage_path: "",
    dataset_version: "1.0",
  });

  // ---------------------------------------------------------
  // Load Projects
  // ---------------------------------------------------------

  const loadProjects = async () => {
    try {
      setLoadingProjects(true);
      setError("");

      const data = await getProjects();

      setProjects(data);

      if (data.length > 0 && selectedProjectId === null) {
        setSelectedProjectId(data[0].id);
      }
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ??
          "Unable to load projects."
      );
    } finally {
      setLoadingProjects(false);
    }
  };

  // ---------------------------------------------------------
  // Load Datasets
  // ---------------------------------------------------------

  const loadDatasets = async (projectId: number) => {
    try {
      setLoadingDatasets(true);
      setError("");

      const data = await getProjectDatasets(projectId);

      setDatasets(data);

      if (
        selectedDataset &&
        !data.some(
          (dataset) => dataset.id === selectedDataset.id
        )
      ) {
        setSelectedDataset(null);
        setSelectedDatasetId(null);
        setStatistics(null);
      }
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ??
          "Unable to load datasets."
      );
    } finally {
      setLoadingDatasets(false);
    }
  };

  // ---------------------------------------------------------
  // Load Statistics
  // ---------------------------------------------------------

  const loadStatistics = async (datasetId: number) => {
    try {
      setLoadingStatistics(true);

      const data = await getDatasetStatistics(datasetId);

      setStatistics(data);
    } catch (err: any) {
      console.error("Failed to load dataset statistics", err);
      setStatistics(null);
    } finally {
      setLoadingStatistics(false);
    }
  };

  // ---------------------------------------------------------
  // Initial Load
  // ---------------------------------------------------------

  useEffect(() => {
    loadProjects();
  }, []);

  // ---------------------------------------------------------
  // Project Changed
  // ---------------------------------------------------------

  useEffect(() => {
    if (selectedProjectId !== null) {
      setSelectedDataset(null);
      setSelectedDatasetId(null);
      setStatistics(null);

      loadDatasets(selectedProjectId);
    }
  }, [selectedProjectId]);

  const loadDatasetImages = async (datasetId: number) => {
    setLoadingImages(true);
    setUploadError(null);

    try {
      const images = await listDatasetImages(datasetId);
      setDatasetImages(images);
    } catch (error: any) {
      setUploadError(
        error?.message ?? "Could not load dataset images."
      );
    } finally {
      setLoadingImages(false);
    }
  };

  useEffect(() => {
    if (selectedDatasetId === null) {
      setDatasetImages([]);
      return;
    }

    void loadDatasetImages(selectedDatasetId);
  }, [selectedDatasetId]);

  // ---------------------------------------------------------
  // Filtered datasets
  // ---------------------------------------------------------

  const filteredDatasets = useMemo(() => {
    const value = search.trim().toLowerCase();

    if (!value) {
      return datasets;
    }

    return datasets.filter((dataset) =>
      [
        dataset.name,
        dataset.description,
        dataset.dataset_version,
        dataset.status,
      ]
        .filter(Boolean)
        .some((field) =>
          String(field).toLowerCase().includes(value)
        )
    );
  }, [datasets, search]);

  // ---------------------------------------------------------
  // Open Dataset
  // ---------------------------------------------------------

  const handleSelectDataset = async (
    dataset: Dataset
  ) => {
    setSelectedDataset(dataset);
    setSelectedDatasetId(dataset.id);
    setImageSearch("");
    setUploadError(null);
    setUploadSuccess(null);
    await loadStatistics(dataset.id);
  };

  const handleUploadImages = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const files = Array.from(event.target.files ?? []);

    if (selectedDatasetId === null || files.length === 0) {
      return;
    }

    setUploadingImages(true);
    setUploadProgress(0);
    setUploadError(null);
    setUploadSuccess(null);

    try {
      await uploadDatasetImages(
        selectedDatasetId,
        files,
        setUploadProgress
      );
      setUploadSuccess(`${files.length} image${files.length === 1 ? "" : "s"} uploaded.`);
      await loadDatasetImages(selectedDatasetId);
      await loadStatistics(selectedDatasetId);
    } catch (error: any) {
      setUploadError(
        error?.response?.data?.detail ??
          error?.message ??
          "Could not upload dataset images."
      );
    } finally {
      setUploadingImages(false);
      event.target.value = "";
    }
  };

  const filteredDatasetImages = datasetImages.filter(
    (imageName) =>
      imageName
        .toLowerCase()
        .includes(imageSearch.trim().toLowerCase())
  );

  // ---------------------------------------------------------
  // Create
  // ---------------------------------------------------------

  const openCreateModal = () => {
    if (selectedProjectId === null) {
      setError("Please select a project first.");
      return;
    }

    setForm({
      name: "",
      description: "",
      storage_path: `datasets/project_${selectedProjectId}`,
      dataset_version: "1.0",
    });

    setShowCreateModal(true);
    setError("");
  };

  const handleCreate = async (
    event: React.FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    if (selectedProjectId === null) {
      return;
    }

    try {
      setSaving(true);
      setError("");

      await createDataset(selectedProjectId, {
        name: form.name.trim(),
        description: form.description.trim(),
        storage_path: form.storage_path.trim(),
        dataset_version: form.dataset_version.trim(),
      });

      setShowCreateModal(false);

      await loadDatasets(selectedProjectId);
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ??
          "Unable to create dataset."
      );
    } finally {
      setSaving(false);
    }
  };

  // ---------------------------------------------------------
  // Edit
  // ---------------------------------------------------------

  const openEditModal = (dataset: Dataset) => {
    setSelectedDataset(dataset);

    setForm({
      name: dataset.name,
      description: dataset.description ?? "",
      storage_path: dataset.storage_path,
      dataset_version: dataset.dataset_version,
    });

    setShowEditModal(true);
    setError("");
  };

  const handleUpdate = async (
    event: React.FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    if (!selectedDataset || selectedProjectId === null) {
      return;
    }

    try {
      setSaving(true);
      setError("");

      const updated = await updateDataset(
        selectedDataset.id,
        {
          name: form.name.trim(),
          description: form.description.trim(),
          storage_path: form.storage_path.trim(),
          dataset_version: form.dataset_version.trim(),
        }
      );

      setSelectedDataset(updated);
      setShowEditModal(false);

      await loadDatasets(selectedProjectId);
      await loadStatistics(updated.id);
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ??
          "Unable to update dataset."
      );
    } finally {
      setSaving(false);
    }
  };

  // ---------------------------------------------------------
  // Delete
  // ---------------------------------------------------------

  const openDeleteModal = (dataset: Dataset) => {
    setSelectedDataset(dataset);
    setShowDeleteModal(true);
    setError("");
  };

  const handleDelete = async () => {
    if (!selectedDataset || selectedProjectId === null) {
      return;
    }

    try {
      setDeleting(true);
      setError("");

      await deleteDataset(selectedDataset.id);

      setShowDeleteModal(false);
      setSelectedDataset(null);
      setStatistics(null);

      await loadDatasets(selectedProjectId);
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ??
          "Unable to delete dataset."
      );
    } finally {
      setDeleting(false);
    }
  };

  // ---------------------------------------------------------
  // Helpers
  // ---------------------------------------------------------

  const formatDate = (
    value?: string | null
  ) => {
    if (!value) {
      return "—";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return "—";
    }

    return date.toLocaleDateString(
      undefined,
      {
        day: "2-digit",
        month: "short",
        year: "numeric",
      }
    );
  };

  const selectedProject = projects.find(
    (project) =>
      project.id === selectedProjectId
  );

  // ---------------------------------------------------------
  // UI
  // ---------------------------------------------------------

  return (
    <div className="dataset-page">

      {/* ---------------------------------------------------
          HEADER
      --------------------------------------------------- */}

      <div className="dataset-page-header">

        <div>
          <div className="dataset-eyebrow">
            OPENVISIONAI PLATFORM
          </div>

          <h1>Datasets</h1>

          <p>
            Manage your vision datasets, versions,
            storage and annotation readiness.
          </p>
        </div>

        <div className="dataset-header-actions">

          <button
            className="dataset-secondary-button"
            onClick={() => {
              if (selectedProjectId !== null) {
                loadDatasets(selectedProjectId);
              }
            }}
            disabled={
              loadingDatasets ||
              selectedProjectId === null
            }
          >
            <RefreshCw
              size={16}
              className={
                loadingDatasets
                  ? "dataset-spin"
                  : ""
              }
            />

            Refresh
          </button>

          <button
            className="dataset-primary-button"
            onClick={openCreateModal}
          >
            <Plus size={17} />

            New Dataset
          </button>

        </div>
      </div>

      {/* ---------------------------------------------------
          ERROR
      --------------------------------------------------- */}

      {error && (
        <div className="dataset-error">
          <span>{error}</span>

          <button
            onClick={() => setError("")}
            aria-label="Dismiss"
          >
            <X size={16} />
          </button>
        </div>
      )}

      {/* ---------------------------------------------------
          PROJECT BAR
      --------------------------------------------------- */}

      <div className="dataset-toolbar">

        <div className="dataset-project-selector">

          <label>Project</label>

          <select
            value={selectedProjectId ?? ""}
            onChange={(event) => {
              const value = event.target.value;

              setSelectedProjectId(
                value ? Number(value) : null
              );
            }}
            disabled={loadingProjects}
          >
            <option value="">
              Select project
            </option>

            {projects.map((project) => (
              <option
                key={project.id}
                value={project.id}
              >
                {project.name}
              </option>
            ))}
          </select>

        </div>

        <div className="dataset-search">

          <Search size={17} />

          <input
            value={search}
            onChange={(event) =>
              setSearch(event.target.value)
            }
            placeholder="Search datasets..."
          />

        </div>

      </div>

      {/* ---------------------------------------------------
          SUMMARY
      --------------------------------------------------- */}

      <div className="dataset-summary-grid">

        <div className="dataset-summary-card">

          <div className="dataset-summary-icon">
            <Database size={19} />
          </div>

          <div>
            <span>Total datasets</span>
            <strong>{datasets.length}</strong>
          </div>

        </div>

        <div className="dataset-summary-card">

          <div className="dataset-summary-icon">
            <Image size={19} />
          </div>

          <div>
            <span>Total images</span>

            <strong>
              {datasets.reduce(
                (total, dataset) =>
                  total + (dataset.total_images || 0),
                0
              )}
            </strong>
          </div>

        </div>

        <div className="dataset-summary-card">

          <div className="dataset-summary-icon">
            <FileText size={19} />
          </div>

          <div>
            <span>Annotations</span>

            <strong>
              {datasets.reduce(
                (total, dataset) =>
                  total +
                  (dataset.total_annotations || 0),
                0
              )}
            </strong>
          </div>

        </div>

        <div className="dataset-summary-card">

          <div className="dataset-summary-icon">
            <FolderOpen size={19} />
          </div>

          <div>
            <span>Active datasets</span>

            <strong>
              {
                datasets.filter(
                  (dataset) =>
                    dataset.status === "ACTIVE"
                ).length
              }
            </strong>
          </div>

        </div>

      </div>

      {/* ---------------------------------------------------
          MAIN CONTENT
      --------------------------------------------------- */}

      <div className="dataset-content-grid">

        {/* DATASET LIST */}

        <div className="dataset-list-card">

          <div className="dataset-list-header">

            <div>
              <h2>Dataset Library</h2>

              <p>
                {selectedProject
                  ? `Datasets in ${selectedProject.name}`
                  : "Select a project to view datasets"}
              </p>
            </div>

            <span className="dataset-count">
              {filteredDatasets.length}
            </span>

          </div>

          {loadingDatasets ? (
            <div className="dataset-loading">
              <RefreshCw
                size={20}
                className="dataset-spin"
              />

              Loading datasets...
            </div>
          ) : filteredDatasets.length === 0 ? (
            <div className="dataset-empty">

              <div className="dataset-empty-icon">
                <Database size={25} />
              </div>

              <h3>
                {search
                  ? "No datasets found"
                  : "No datasets yet"}
              </h3>

              <p>
                {search
                  ? "Try changing your search."
                  : "Create your first dataset to get started."}
              </p>

              {!search && selectedProjectId !== null && (
                <button
                  className="dataset-primary-button"
                  onClick={openCreateModal}
                >
                  <Plus size={16} />
                  Create Dataset
                </button>
              )}

            </div>
          ) : (
            <div className="dataset-table-wrapper">

              <table className="dataset-table">

                <thead>
                  <tr>
                    <th>Dataset</th>
                    <th>Version</th>
                    <th>Images</th>
                    <th>Annotations</th>
                    <th>Status</th>
                    <th>Updated</th>
                    <th></th>
                  </tr>
                </thead>

                <tbody>

                  {filteredDatasets.map(
                    (dataset) => (
                      <tr
                        key={dataset.id}
                        className={
                          selectedDataset?.id ===
                          dataset.id
                            ? "dataset-row-selected"
                            : ""
                        }
                        onClick={() =>
                          handleSelectDataset(dataset)
                        }
                      >

                        <td>
                          <div className="dataset-name-cell">

                            <div className="dataset-row-icon">
                              <Database size={17} />
                            </div>

                            <div>
                              <strong>
                                {dataset.name}
                              </strong>

                              <span>
                                {dataset.description ||
                                  "No description"}
                              </span>
                            </div>

                          </div>
                        </td>

                        <td>
                          <span className="dataset-version">
                            v{dataset.dataset_version}
                          </span>
                        </td>

                        <td>
                          {dataset.total_images ?? 0}
                        </td>

                        <td>
                          {dataset.total_annotations ?? 0}
                        </td>

                        <td>
                          <span
                            className={`dataset-status dataset-status-${String(
                              dataset.status
                            ).toLowerCase()}`}
                          >
                            {dataset.status}
                          </span>
                        </td>

                        <td>
                          {formatDate(
                            dataset.last_updated
                          )}
                        </td>

                        <td>
                          <div
                            className="dataset-row-actions"
                            onClick={(event) =>
                              event.stopPropagation()
                            }
                          >

                            <button
                              title="Edit dataset"
                              onClick={() =>
                                openEditModal(dataset)
                              }
                            >
                              <Edit3 size={16} />
                            </button>

                            <button
                              title="Delete dataset"
                              className="dataset-delete-action"
                              onClick={() =>
                                openDeleteModal(dataset)
                              }
                            >
                              <Trash2 size={16} />
                            </button>

                          </div>
                        </td>

                      </tr>
                    )
                  )}

                </tbody>

              </table>

            </div>
          )}

        </div>

        {/* DATASET DETAILS */}

        <div className="dataset-details-card">

          {!selectedDataset ? (
            <div className="dataset-details-empty">

              <div className="dataset-details-empty-icon">
                <Database size={25} />
              </div>

              <h3>Select a dataset</h3>

              <p>
                Select a dataset from the library
                to view its details and statistics.
              </p>

            </div>
          ) : (
            <>
              <div className="dataset-details-header">

                <div>

                  <div className="dataset-details-title-row">

                    <div className="dataset-details-icon">
                      <Database size={20} />
                    </div>

                    <div>
                      <h2>
                        {selectedDataset.name}
                      </h2>

                      <span>
                        Dataset #{selectedDataset.id}
                      </span>
                    </div>

                  </div>

                </div>

                <button
                  className="dataset-icon-button"
                  onClick={() =>
                    openEditModal(selectedDataset)
                  }
                >
                  <Edit3 size={16} />
                </button>

                <button
                  className="dataset-secondary-button"
                  onClick={() =>
                    navigate(
                      `/datasets/${selectedDataset.id}/annotations`
                    )
                  }
                >
                  <ExternalLink size={16} />
                  Open annotations
                </button>

              </div>

              <div className="dataset-details-status-row">

                <span
                  className={`dataset-status dataset-status-${String(
                    selectedDataset.status
                  ).toLowerCase()}`}
                >
                  {selectedDataset.status}
                </span>

                <span className="dataset-version">
                  v{selectedDataset.dataset_version}
                </span>

              </div>

              <p className="dataset-details-description">
                {selectedDataset.description ||
                  "No description provided."}
              </p>

              <div className="dataset-details-section">

                <div className="dataset-section-label">
                  Dataset Statistics
                </div>

                <div className="dataset-detail-stats">

                  <div>
                    <span>Images</span>
                    <strong>
                      {loadingStatistics
                        ? "..."
                        : statistics?.total_images ??
                          selectedDataset.total_images ??
                          0}
                    </strong>
                  </div>

                  <div>
                    <span>Annotated</span>
                    <strong>
                      {loadingStatistics
                        ? "..."
                        : statistics?.annotated_images ??
                          selectedDataset.annotated_images ??
                          0}
                    </strong>
                  </div>

                  <div>
                    <span>Annotations</span>
                    <strong>
                      {loadingStatistics
                        ? "..."
                        : statistics?.total_annotations ??
                          selectedDataset.total_annotations ??
                          0}
                    </strong>
                  </div>

                  <div>
                    <span>Classes</span>
                    <strong>
                      {loadingStatistics
                        ? "..."
                        : statistics?.total_classes ??
                          selectedDataset.total_classes ??
                          0}
                    </strong>
                  </div>

                </div>

              </div>

              <section className="dataset-images-section">
                <div className="dataset-images-header">
                  <div>
                    <div className="section-eyebrow">DATASET ASSETS</div>
                    <h2>Images</h2>
                    <p>
                      Upload, review and annotate images belonging to this dataset.
                    </p>
                  </div>

                  <div className="dataset-image-count">
                    <ImageIcon size={16} />
                    {datasetImages.length} images
                  </div>
                </div>

                <div className="dataset-image-toolbar">
                  <div className="dataset-image-search">
                    <Search size={16} />
                    <input
                      type="text"
                      placeholder="Search images..."
                      value={imageSearch}
                      onChange={(event) => setImageSearch(event.target.value)}
                    />
                  </div>

                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/jpeg,image/png,image/webp"
                    multiple
                    hidden
                    onChange={handleUploadImages}
                  />

                  <button
                    type="button"
                    className="primary-button"
                    disabled={selectedDatasetId === null || uploadingImages}
                    onClick={() => fileInputRef.current?.click()}
                  >
                    {uploadingImages ? (
                      <>
                        <Loader2 size={16} className="dataset-spin" />
                        Uploading {uploadProgress}%
                      </>
                    ) : (
                      <>
                        <Upload size={16} />
                        Upload Images
                      </>
                    )}
                  </button>
                </div>

                {uploadSuccess && (
                  <div className="dataset-upload-success">
                    <CheckCircle2 size={17} />
                    {uploadSuccess}
                    <button type="button" onClick={() => setUploadSuccess(null)}>
                      <X size={15} />
                    </button>
                  </div>
                )}

                {uploadError && (
                  <div className="dataset-upload-error">
                    <AlertCircle size={17} />
                    {uploadError}
                    <button type="button" onClick={() => setUploadError(null)}>
                      <X size={15} />
                    </button>
                  </div>
                )}

                {loadingImages ? (
                  <div className="dataset-images-empty">
                    <Loader2 size={24} className="dataset-spin" />
                    Loading images...
                  </div>
                ) : filteredDatasetImages.length === 0 ? (
                  <div className="dataset-images-empty">
                    <ImageIcon size={32} />
                    <strong>No images found</strong>
                    <span>Upload images to start annotating this dataset.</span>
                  </div>
                ) : (
                  <div className="dataset-image-grid">
                    {filteredDatasetImages.map((imageName) => (
                      <DatasetImageCard
                        key={imageName}
                        datasetId={selectedDatasetId!}
                        imageName={imageName}
                        onAnnotate={() =>
                          navigate(
                            `/datasets/${selectedDatasetId}/annotations?image=${encodeURIComponent(imageName)}`
                          )
                        }
                      />
                    ))}
                  </div>
                )}
              </section>

              <div className="dataset-details-section">

                <div className="dataset-section-label">
                  Storage
                </div>

                <div className="dataset-storage-path">
                  <FolderOpen size={16} />

                  <span>
                    {selectedDataset.storage_path}
                  </span>
                </div>

              </div>

              <div className="dataset-details-section">

                <div className="dataset-section-label">
                  Metadata
                </div>

                <div className="dataset-metadata">

                  <div>
                    <span>Project ID</span>
                    <strong>
                      {selectedDataset.project_id}
                    </strong>
                  </div>

                  <div>
                    <span>Dataset ID</span>
                    <strong>
                      {selectedDataset.id}
                    </strong>
                  </div>

                  <div>
                    <span>Created</span>
                    <strong>
                      {formatDate(
                        selectedDataset.created_at
                      )}
                    </strong>
                  </div>

                  <div>
                    <span>Last updated</span>
                    <strong>
                      {formatDate(
                        selectedDataset.updated_at ??
                          selectedDataset.last_updated
                      )}
                    </strong>
                  </div>

                </div>

              </div>

            </>
          )}

        </div>

      </div>

      {/* =====================================================
          CREATE MODAL
      ===================================================== */}

      {showCreateModal && (
        <div className="dataset-modal-overlay">

          <div className="dataset-modal">

            <div className="dataset-modal-header">

              <div>
                <h2>Create Dataset</h2>
                <p>
                  Add a new vision dataset to this project.
                </p>
              </div>

              <button
                className="dataset-modal-close"
                onClick={() =>
                  setShowCreateModal(false)
                }
              >
                <X size={18} />
              </button>

            </div>

            <form onSubmit={handleCreate}>

              <div className="dataset-form-group">

                <label>
                  Dataset name
                </label>

                <input
                  value={form.name}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      name: event.target.value,
                    })
                  }
                  placeholder="e.g. PPE Detection Dataset"
                  required
                />

              </div>

              <div className="dataset-form-group">

                <label>
                  Description
                </label>

                <textarea
                  value={form.description}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      description:
                        event.target.value,
                    })
                  }
                  placeholder="Describe this dataset..."
                  rows={3}
                />

              </div>

              <div className="dataset-form-row">

                <div className="dataset-form-group">

                  <label>
                    Version
                  </label>

                  <input
                    value={form.dataset_version}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        dataset_version:
                          event.target.value,
                      })
                    }
                    placeholder="1.0"
                    required
                  />

                </div>

                <div className="dataset-form-group">

                  <label>
                    Storage path
                  </label>

                  <input
                    value={form.storage_path}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        storage_path:
                          event.target.value,
                      })
                    }
                    required
                  />

                </div>

              </div>

              <div className="dataset-modal-actions">

                <button
                  type="button"
                  className="dataset-secondary-button"
                  onClick={() =>
                    setShowCreateModal(false)
                  }
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="dataset-primary-button"
                  disabled={saving}
                >
                  {saving
                    ? "Creating..."
                    : "Create Dataset"}
                </button>

              </div>

            </form>

          </div>

        </div>
      )}

      {/* =====================================================
          EDIT MODAL
      ===================================================== */}

      {showEditModal && (
        <div className="dataset-modal-overlay">

          <div className="dataset-modal">

            <div className="dataset-modal-header">

              <div>
                <h2>Edit Dataset</h2>
                <p>
                  Update dataset metadata.
                </p>
              </div>

              <button
                className="dataset-modal-close"
                onClick={() =>
                  setShowEditModal(false)
                }
              >
                <X size={18} />
              </button>

            </div>

            <form onSubmit={handleUpdate}>

              <div className="dataset-form-group">

                <label>
                  Dataset name
                </label>

                <input
                  value={form.name}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      name: event.target.value,
                    })
                  }
                  required
                />

              </div>

              <div className="dataset-form-group">

                <label>
                  Description
                </label>

                <textarea
                  value={form.description}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      description:
                        event.target.value,
                    })
                  }
                  rows={3}
                />

              </div>

              <div className="dataset-form-row">

                <div className="dataset-form-group">

                  <label>
                    Version
                  </label>

                  <input
                    value={form.dataset_version}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        dataset_version:
                          event.target.value,
                      })
                    }
                    required
                  />

                </div>

                <div className="dataset-form-group">

                  <label>
                    Storage path
                  </label>

                  <input
                    value={form.storage_path}
                    onChange={(event) =>
                      setForm({
                        ...form,
                        storage_path:
                          event.target.value,
                      })
                    }
                    required
                  />

                </div>

              </div>

              <div className="dataset-modal-actions">

                <button
                  type="button"
                  className="dataset-secondary-button"
                  onClick={() =>
                    setShowEditModal(false)
                  }
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="dataset-primary-button"
                  disabled={saving}
                >
                  {saving
                    ? "Saving..."
                    : "Save Changes"}
                </button>

              </div>

            </form>

          </div>

        </div>
      )}

      {/* =====================================================
          DELETE MODAL
      ===================================================== */}

      {showDeleteModal && selectedDataset && (
        <div className="dataset-modal-overlay">

          <div className="dataset-modal dataset-delete-modal">

            <div className="dataset-delete-icon">
              <Trash2 size={22} />
            </div>

            <h2>Delete dataset?</h2>

            <p>
              You are about to delete{" "}
              <strong>
                {selectedDataset.name}
              </strong>
              . This action cannot be undone.
            </p>

            <div className="dataset-modal-actions">

              <button
                className="dataset-secondary-button"
                onClick={() =>
                  setShowDeleteModal(false)
                }
              >
                Cancel
              </button>

              <button
                className="dataset-danger-button"
                onClick={handleDelete}
                disabled={deleting}
              >
                {deleting
                  ? "Deleting..."
                  : "Delete Dataset"}
              </button>

            </div>

          </div>

        </div>
      )}

    </div>
  );
}