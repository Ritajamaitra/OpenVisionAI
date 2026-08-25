import { useEffect, useMemo, useState } from "react";
import {
  FolderKanban,
  Plus,
  RefreshCw,
  Search,
  Pencil,
  Trash2,
  X,
  FolderOpen,
  Activity,
  Archive,
} from "lucide-react";

import type { Project } from "../api/projects";
import {
  
  getProjects,
  createProject,
  updateProject,
  deleteProject,
} from "../api/projects";

export default function Projects() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] =
    useState<Project | null>(null);

  const [search, setSearch] = useState("");

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const [error, setError] = useState("");

  const [showModal, setShowModal] = useState(false);
  const [editingProject, setEditingProject] =
    useState<Project | null>(null);

  const [formName, setFormName] = useState("");
  const [formDescription, setFormDescription] =
    useState("");

  const [saving, setSaving] = useState(false);

  const loadProjects = async () => {
    try {
      setError("");

      const data = await getProjects();

      setProjects(data);

      if (data.length > 0) {
        setSelectedProject((current) => {
          if (!current) {
            return data[0];
          }

          return (
            data.find(
              (project) => project.id === current.id
            ) || data[0]
          );
        });
      } else {
        setSelectedProject(null);
      }
    } catch (err: any) {
      console.error(err);

      setError(
        err?.response?.data?.detail ||
          "Unable to load projects."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadProjects();
  };

  const filteredProjects = useMemo(() => {
    const value = search.trim().toLowerCase();

    if (!value) {
      return projects;
    }

    return projects.filter(
      (project) =>
        project.name.toLowerCase().includes(value) ||
        (project.description || "")
          .toLowerCase()
          .includes(value)
    );
  }, [projects, search]);

  const totalProjects = projects.length;

  const activeProjects = projects.filter(
    (project) => project.status === "ACTIVE"
  ).length;

  const archivedProjects = projects.filter(
    (project) => project.status === "ARCHIVED"
  ).length;

  const deletedProjects = projects.filter(
    (project) => project.status === "DELETED"
  ).length;

  const openCreateModal = () => {
    setEditingProject(null);
    setFormName("");
    setFormDescription("");
    setShowModal(true);
  };

  const openEditModal = (project: Project) => {
    setEditingProject(project);
    setFormName(project.name);
    setFormDescription(project.description || "");
    setShowModal(true);
  };

  const closeModal = () => {
    if (saving) return;

    setShowModal(false);
    setEditingProject(null);
    setFormName("");
    setFormDescription("");
  };

  const handleSave = async () => {
    if (!formName.trim()) {
      setError("Project name is required.");
      return;
    }

    try {
      setSaving(true);
      setError("");

      if (editingProject) {
        const updated = await updateProject(
          editingProject.id,
          {
            name: formName.trim(),
            description:
              formDescription.trim() || null,
          }
        );

        setProjects((current) =>
          current.map((project) =>
            project.id === updated.id
              ? updated
              : project
          )
        );

        setSelectedProject(updated);
      } else {
        const created = await createProject({
          name: formName.trim(),
          description:
            formDescription.trim() || null,
        });

        setProjects((current) => [
          created,
          ...current,
        ]);

        setSelectedProject(created);
      }

      closeModal();
    } catch (err: any) {
      console.error(err);

      setError(
        err?.response?.data?.detail ||
          "Unable to save project."
      );
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (
    project: Project
  ) => {
    const confirmed = window.confirm(
      `Delete project "${project.name}"?`
    );

    if (!confirmed) {
      return;
    }

    try {
      setError("");

      await deleteProject(project.id);

      setProjects((current) =>
        current.filter(
          (item) => item.id !== project.id
        )
      );

      if (selectedProject?.id === project.id) {
        const remaining = projects.filter(
          (item) => item.id !== project.id
        );

        setSelectedProject(
          remaining.length > 0
            ? remaining[0]
            : null
        );
      }
    } catch (err: any) {
      console.error(err);

      setError(
        err?.response?.data?.detail ||
          "Unable to delete project."
      );
    }
  };

  const formatDate = (value: string) => {
    if (!value) return "—";

    return new Date(value).toLocaleDateString(
      "en-IN",
      {
        day: "2-digit",
        month: "short",
        year: "numeric",
      }
    );
  };

  return (
    <div className="projects-page">

      {/* ======================================================
          PAGE HEADER
          ====================================================== */}

      <div className="projects-page-header">
        <div>
          <div className="projects-eyebrow">
            OPENVISIONAI PLATFORM
          </div>

          <h1>Projects</h1>

          <p>
            Organize your vision AI workflows,
            datasets, models and training runs.
          </p>
        </div>

        <div className="projects-header-actions">
          <button
            className="projects-secondary-button"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <RefreshCw
              size={16}
              className={
                refreshing ? "spin" : ""
              }
            />

            Refresh
          </button>

          <button
            className="projects-primary-button"
            onClick={openCreateModal}
          >
            <Plus size={17} />

            New Project
          </button>
        </div>
      </div>


      {/* ======================================================
          ERROR
          ====================================================== */}

      {error && (
        <div className="projects-error">
          <div>
            <strong>
              Something went wrong
            </strong>

            <span>{error}</span>
          </div>

          <button
            onClick={() => setError("")}
          >
            <X size={16} />
          </button>
        </div>
      )}


      {/* ======================================================
          TOOLBAR
          ====================================================== */}

      <div className="projects-toolbar">

        <div className="projects-search">
          <Search size={17} />

          <input
            type="text"
            placeholder="Search projects..."
            value={search}
            onChange={(event) =>
              setSearch(event.target.value)
            }
          />
        </div>

      </div>


      {/* ======================================================
          SUMMARY
          ====================================================== */}

      <div className="projects-summary-grid">

        <div className="projects-summary-card">
          <div className="projects-summary-icon">
            <FolderKanban size={20} />
          </div>

          <div>
            <span>Total projects</span>
            <strong>
              {loading ? "—" : totalProjects}
            </strong>
          </div>
        </div>


        <div className="projects-summary-card">
          <div className="projects-summary-icon">
            <Activity size={20} />
          </div>

          <div>
            <span>Active projects</span>
            <strong>
              {loading ? "—" : activeProjects}
            </strong>
          </div>
        </div>


        <div className="projects-summary-card">
          <div className="projects-summary-icon">
            <Archive size={20} />
          </div>

          <div>
            <span>Archived projects</span>
            <strong>
              {loading ? "—" : archivedProjects}
            </strong>
          </div>
        </div>


        <div className="projects-summary-card">
          <div className="projects-summary-icon">
            <FolderOpen size={20} />
          </div>

          <div>
            <span>Deleted projects</span>
            <strong>
              {loading ? "—" : deletedProjects}
            </strong>
          </div>
        </div>

      </div>


      {/* ======================================================
          MAIN CONTENT
          ====================================================== */}

      <div className="projects-content-grid">

        {/* ====================================================
            PROJECT LIBRARY
            ==================================================== */}

        <section className="projects-list-card">

          <div className="projects-list-header">
            <div>
              <h2>Project Library</h2>

              <p>
                Projects belonging to your workspace
              </p>
            </div>

            <span className="projects-count">
              {filteredProjects.length}
            </span>
          </div>


          <div className="projects-table-wrapper">

            <table className="projects-table">

              <thead>
                <tr>
                  <th>PROJECT</th>
                  <th>STATUS</th>
                  <th>CREATED</th>
                  <th>UPDATED</th>
                  <th></th>
                </tr>
              </thead>

              <tbody>

                {loading ? (
                  <tr>
                    <td
                      colSpan={5}
                      className="projects-empty"
                    >
                      Loading projects...
                    </td>
                  </tr>
                ) : filteredProjects.length === 0 ? (
                  <tr>
                    <td
                      colSpan={5}
                      className="projects-empty"
                    >
                      <FolderOpen
                        size={28}
                      />

                      <strong>
                        No projects found
                      </strong>

                      <span>
                        Create your first project
                        to get started.
                      </span>
                    </td>
                  </tr>
                ) : (
                  filteredProjects.map(
                    (project) => (
                      <tr
                        key={project.id}
                        className={
                          selectedProject?.id ===
                          project.id
                            ? "project-row-selected"
                            : ""
                        }
                        onClick={() =>
                          setSelectedProject(
                            project
                          )
                        }
                      >

                        <td>
                          <div className="project-name-cell">

                            <div className="project-row-icon">
                              <FolderKanban
                                size={17}
                              />
                            </div>

                            <div>
                              <strong>
                                {project.name}
                              </strong>

                              <span>
                                {project.description ||
                                  "No description"}
                              </span>
                            </div>

                          </div>
                        </td>


                        <td>
                          <span
                            className={`project-status project-status-${project.status.toLowerCase()}`}
                          >
                            {project.status}
                          </span>
                        </td>


                        <td>
                          {formatDate(
                            project.created_at
                          )}
                        </td>


                        <td>
                          {formatDate(
                            project.updated_at
                          )}
                        </td>


                        <td>
                          <div className="project-row-actions">

                            <button
                              type="button"
                              title="Edit project"
                              onClick={(event) => {
                                event.stopPropagation();

                                openEditModal(
                                  project
                                );
                              }}
                            >
                              <Pencil size={15} />
                            </button>

                            <button
                              type="button"
                              title="Delete project"
                              onClick={(event) => {
                                event.stopPropagation();

                                handleDelete(
                                  project
                                );
                              }}
                            >
                              <Trash2 size={15} />
                            </button>

                          </div>
                        </td>

                      </tr>
                    )
                  )
                )}

              </tbody>

            </table>

          </div>

        </section>


        {/* ====================================================
            DETAILS
            ==================================================== */}

        <aside className="projects-details-card">

          {selectedProject ? (
            <>
              <div className="project-details-header">

                <div className="project-details-title">

                  <div className="project-details-icon">
                    <FolderKanban
                      size={22}
                    />
                  </div>

                  <div>
                    <h2>
                      {selectedProject.name}
                    </h2>

                    <span>
                      Project #{selectedProject.id}
                    </span>
                  </div>

                </div>

                <button
                  className="project-details-edit"
                  onClick={() =>
                    openEditModal(
                      selectedProject
                    )
                  }
                >
                  <Pencil size={15} />
                </button>

              </div>


              <div className="project-details-status">

                <span
                  className={`project-status project-status-${selectedProject.status.toLowerCase()}`}
                >
                  {selectedProject.status}
                </span>

              </div>


              <div className="project-details-description">

                <span>
                  DESCRIPTION
                </span>

                <p>
                  {selectedProject.description ||
                    "No project description has been provided."}
                </p>

              </div>


              <div className="project-details-section">

                <span>
                  PROJECT INFORMATION
                </span>

                <div className="project-info-grid">

                  <div>
                    <small>
                      Project ID
                    </small>

                    <strong>
                      #{selectedProject.id}
                    </strong>
                  </div>

                  <div>
                    <small>
                      Owner ID
                    </small>

                    <strong>
                      #{selectedProject.owner_id}
                    </strong>
                  </div>

                  <div>
                    <small>
                      Created
                    </small>

                    <strong>
                      {formatDate(
                        selectedProject.created_at
                      )}
                    </strong>
                  </div>

                  <div>
                    <small>
                      Updated
                    </small>

                    <strong>
                      {formatDate(
                        selectedProject.updated_at
                      )}
                    </strong>
                  </div>

                </div>

              </div>


              <div className="project-details-footer">

                <button
                  className="projects-secondary-button"
                  onClick={() =>
                    openEditModal(
                      selectedProject
                    )
                  }
                >
                  <Pencil size={15} />

                  Edit Project
                </button>

                <button
                  className="project-delete-button"
                  onClick={() =>
                    handleDelete(
                      selectedProject
                    )
                  }
                >
                  <Trash2 size={15} />

                  Delete
                </button>

              </div>

            </>
          ) : (
            <div className="project-details-empty">

              <div className="project-details-empty-icon">
                <FolderOpen size={28} />
              </div>

              <h3>
                Select a project
              </h3>

              <p>
                Select a project from the
                library to view its details.
              </p>

            </div>
          )}

        </aside>

      </div>


      {/* ======================================================
          CREATE / EDIT MODAL
          ====================================================== */}

      {showModal && (
        <div
          className="projects-modal-overlay"
          onMouseDown={closeModal}
        >

          <div
            className="projects-modal"
            onMouseDown={(event) =>
              event.stopPropagation()
            }
          >

            <div className="projects-modal-header">

              <div>
                <span>
                  {editingProject
                    ? "PROJECT SETTINGS"
                    : "NEW PROJECT"}
                </span>

                <h2>
                  {editingProject
                    ? "Edit Project"
                    : "Create Project"}
                </h2>

                <p>
                  {editingProject
                    ? "Update your project information."
                    : "Create a workspace for your vision AI workflow."}
                </p>
              </div>

              <button
                onClick={closeModal}
                disabled={saving}
              >
                <X size={18} />
              </button>

            </div>


            <div className="projects-modal-body">

              <div className="projects-form-field">

                <label>
                  Project name
                </label>

                <input
                  type="text"
                  placeholder="e.g. PPE Compliance"
                  value={formName}
                  onChange={(event) =>
                    setFormName(
                      event.target.value
                    )
                  }
                  autoFocus
                />

              </div>


              <div className="projects-form-field">

                <label>
                  Description
                </label>

                <textarea
                  placeholder="Describe what this project is used for..."
                  value={formDescription}
                  onChange={(event) =>
                    setFormDescription(
                      event.target.value
                    )
                  }
                  rows={5}
                />

              </div>

            </div>


            <div className="projects-modal-footer">

              <button
                className="projects-secondary-button"
                onClick={closeModal}
                disabled={saving}
              >
                Cancel
              </button>

              <button
                className="projects-primary-button"
                onClick={handleSave}
                disabled={
                  saving ||
                  !formName.trim()
                }
              >
                {saving
                  ? "Saving..."
                  : editingProject
                  ? "Save Changes"
                  : "Create Project"}
              </button>

            </div>

          </div>

        </div>
      )}

    </div>
  );
}