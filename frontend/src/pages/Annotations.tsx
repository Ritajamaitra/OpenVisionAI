import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import {
  Check,
  ChevronLeft,
  ChevronRight,
  Image as ImageIcon,
  Loader2,
  RefreshCw,
  Search,
  Sparkles,
  X,
} from "lucide-react";

import {
  useParams,
  useSearchParams,
} from "react-router-dom";

import {
  autoAnnotateImage,
  getDatasetImage,
  getImageAnnotations,
  listDatasetImages,
  reviewAnnotation,
  type Annotation,
  type AnnotationStatus,
} from "../api/annotations";


/* ============================================================
   DEFAULT AI CONFIGURATION
   ============================================================ */

const DEFAULT_MODEL =
  "grounding_dino";

const DEFAULT_PROMPT =
  "person, helmet, vest, gloves, shoes, mask, goggles";

const DEFAULT_CONFIDENCE = 0.35;


/* ============================================================
   COMPONENT
   ============================================================ */

export default function Annotations() {

  const { datasetId: datasetIdParam } = useParams<{
    datasetId: string;
  }>();

  const [searchParams] = useSearchParams();

  const initialImage = searchParams.get("image");
  const datasetId = Number(datasetIdParam);

  if (!Number.isInteger(datasetId) || datasetId <= 0) {
    return (
      <div className="annotation-workspace">
        <div className="workspace-error">
          Invalid dataset ID.
        </div>
      </div>
    );
  }

  /* ==========================================================
     DATASET
     ========================================================== */

  const [images, setImages] =
    useState<string[]>([]);

  const [selectedImage, setSelectedImage] =
    useState<string | null>(null);

  const [search, setSearch] =
    useState("");


  /* ==========================================================
     IMAGE
     ========================================================== */

  const [imageUrl, setImageUrl] =
    useState<string | null>(null);

  const [imageDimensions, setImageDimensions] =
    useState({
      width: 0,
      height: 0,
    });

  const imageUrlRef =
    useRef<string | null>(null);


  /* ==========================================================
     ANNOTATIONS
     ========================================================== */

  const [annotations, setAnnotations] =
    useState<Annotation[]>([]);


  /* ==========================================================
     LOADING
     ========================================================== */

  const [loadingImages, setLoadingImages] =
    useState(true);

  const [loadingImage, setLoadingImage] =
    useState(false);

  const [runningModel, setRunningModel] =
    useState(false);

  const [reviewingId, setReviewingId] =
    useState<number | null>(null);


  /* ==========================================================
     AI CONFIG
     ========================================================== */

  const [model, setModel] =
    useState(DEFAULT_MODEL);

  const [prompt, setPrompt] =
    useState(DEFAULT_PROMPT);

  const [confidence, setConfidence] =
    useState(DEFAULT_CONFIDENCE);

  const [lastRun, setLastRun] =
    useState<number | null>(null);


  /* ==========================================================
     ERROR
     ========================================================== */

  const [error, setError] =
    useState<string | null>(null);


  /* ==========================================================
     IMAGE URL CLEANUP
     ========================================================== */

  const replaceImageUrl = useCallback(
    (nextUrl: string | null) => {

      if (imageUrlRef.current) {
        URL.revokeObjectURL(
          imageUrlRef.current
        );
      }

      imageUrlRef.current = nextUrl;

      setImageUrl(nextUrl);
    },
    []
  );


  useEffect(() => {

    return () => {

      if (imageUrlRef.current) {
        URL.revokeObjectURL(
          imageUrlRef.current
        );

        imageUrlRef.current = null;
      }

    };

  }, []);


  /* ==========================================================
     LOAD IMAGE LIST
     ========================================================== */

  const loadImages = useCallback(
    async (
      shouldSelectFirst = true
    ) => {

      setLoadingImages(true);
      setError(null);

      try {

        const result =
          await listDatasetImages(
            datasetId
          );

        setImages(result);

        /*
         * If current image no longer exists,
         * select the first available image.
         */

        const currentStillExists =
          selectedImage !== null &&
          result.includes(selectedImage);

        if (
          result.length > 0 &&
          (
            !currentStillExists ||
            shouldSelectFirst &&
            selectedImage === null
          )
        ) {
          const requestedImage =
            initialImage && result.includes(initialImage)
              ? initialImage
              : result[0];

          setSelectedImage(requestedImage);
        }

        if (result.length === 0) {
          setSelectedImage(null);
          setAnnotations([]);
          replaceImageUrl(null);
        }

      } catch (err: any) {

        setError(
          err?.message ??
          "Could not load dataset images."
        );

      } finally {

        setLoadingImages(false);
      }

    },
    [
      datasetId,
      initialImage,
      replaceImageUrl,
      selectedImage,
    ]
  );


  /* ==========================================================
     INITIAL DATASET LOAD
     ========================================================== */

  useEffect(() => {
    let cancelled = false;

    async function initialize() {
      setLoadingImages(true);
      setError(null);

      try {
        const result = await listDatasetImages(datasetId);

        if (cancelled) {
          return;
        }

        setImages(result);

        if (result.length > 0) {
          setSelectedImage((current) => {
            if (current && result.includes(current)) {
              return current;
            }

            return initialImage && result.includes(initialImage)
              ? initialImage
              : result[0];
          });
        } else {
          setSelectedImage(null);
          setAnnotations([]);
          replaceImageUrl(null);
        }
      } catch (err: any) {
        if (!cancelled) {
          setError(
            err?.response?.data?.detail ??
              err?.message ??
              "Could not load dataset images."
          );
        }
      } finally {
        if (!cancelled) {
          setLoadingImages(false);
        }
      }
    }

    void initialize();

    return () => {
      cancelled = true;
    };
  }, [datasetId, initialImage, replaceImageUrl]);


  /* ==========================================================
     LOAD SELECTED IMAGE
     ========================================================== */

  /* ==========================================================
     SELECTED IMAGE EFFECT
     ========================================================== */

  useEffect(() => {
    if (!selectedImage) {
      return;
    }

    const imageName = selectedImage;
    let cancelled = false;

    async function load() {
      setLoadingImage(true);
      setError(null);
      setAnnotations([]);
      setImageDimensions({
        width: 0,
        height: 0,
      });

      try {
        const [imageBlob, annotationResponse] = await Promise.all([
          getDatasetImage(datasetId, imageName),
          getImageAnnotations(datasetId, imageName),
        ]);

        if (cancelled) {
          return;
        }

        const url = URL.createObjectURL(imageBlob);
        replaceImageUrl(url);
        setAnnotations(annotationResponse.annotations);
      } catch (err: any) {
        if (!cancelled) {
          replaceImageUrl(null);
          setError(
            err?.response?.data?.detail ??
              err?.message ??
              "Could not load the selected image."
          );
        }
      } finally {
        if (!cancelled) {
          setLoadingImage(false);
        }
      }
    }

    void load();

    return () => {
      cancelled = true;
    };
  }, [datasetId, replaceImageUrl, selectedImage]);


  /* ==========================================================
     FILTERED IMAGE LIST
     ========================================================== */

  const filteredImages =
    useMemo(() => {

      const normalizedSearch =
        search.trim().toLowerCase();

      if (!normalizedSearch) {
        return images;
      }

      return images.filter(
        (imageName) =>
          imageName
            .toLowerCase()
            .includes(
              normalizedSearch
            )
      );

    }, [
      images,
      search,
    ]);


  /* ==========================================================
     CURRENT IMAGE INDEX
     ========================================================== */

  const currentIndex =
    selectedImage
      ? images.indexOf(
          selectedImage
        )
      : -1;


  /* ==========================================================
     NAVIGATION
     ========================================================== */

  const selectPrevious = () => {

    if (currentIndex <= 0) {
      return;
    }

    setSelectedImage(
      images[currentIndex - 1]
    );
  };


  const selectNext = () => {

    if (
      currentIndex < 0 ||
      currentIndex >=
        images.length - 1
    ) {
      return;
    }

    setSelectedImage(
      images[currentIndex + 1]
    );
  };


  /* ==========================================================
     IMAGE LOADED
     ========================================================== */

  const handleImageLoaded = (
    event: React.SyntheticEvent<
      HTMLImageElement
    >
  ) => {

    const image =
      event.currentTarget;

    setImageDimensions({
      width:
        image.naturalWidth,

      height:
        image.naturalHeight,
    });
  };


  /* ==========================================================
     BOUNDING BOX
     
     Supports:
     
     1. Pixel coordinates:
        x=120, y=50, w=60, h=40

     2. Normalized coordinates:
        x=0.25, y=0.20, w=0.15, h=0.10

     3. Percentage coordinates:
        x=25, y=20, w=15, h=10
     ========================================================== */

  const getBoundingBoxStyle = (
    annotation: Annotation
  ): React.CSSProperties => {

    const x =
      Number(annotation.bbox_x) || 0;

    const y =
      Number(annotation.bbox_y) || 0;

    const width =
      Number(annotation.bbox_width) || 0;

    const height =
      Number(annotation.bbox_height) || 0;


    /*
     * NORMALIZED 0–1
     */

    const isNormalized =
      x >= 0 &&
      x <= 1 &&
      y >= 0 &&
      y <= 1 &&
      width >= 0 &&
      width <= 1 &&
      height >= 0 &&
      height <= 1;


    if (isNormalized) {

      return {
        left: `${x * 100}%`,
        top: `${y * 100}%`,
        width: `${width * 100}%`,
        height: `${height * 100}%`,
      };
    }


    /*
     * PIXEL COORDINATES
     *
     * If image dimensions are known,
     * convert pixels to percentages.
     */

    if (
      imageDimensions.width > 0 &&
      imageDimensions.height > 0
    ) {

      return {
        left:
          `${(x / imageDimensions.width) * 100}%`,

        top:
          `${(y / imageDimensions.height) * 100}%`,

        width:
          `${(width / imageDimensions.width) * 100}%`,

        height:
          `${(height / imageDimensions.height) * 100}%`,
      };
    }


    /*
     * FALLBACK:
     *
     * Assume values are percentages.
     */

    return {
      left: `${x}%`,
      top: `${y}%`,
      width: `${width}%`,
      height: `${height}%`,
    };
  };


  /* ==========================================================
     AUTO ANNOTATION
     ========================================================== */

  const runAutoAnnotation =
    async () => {

      if (!selectedImage) {
        return;
      }

      setRunningModel(true);
      setError(null);

      try {

        const result =
          await autoAnnotateImage(
            datasetId,
            selectedImage,
            {
              model:
                model.trim(),

              prompt:
                prompt.trim(),

              confidence,
            }
          );


        setLastRun(
          result.processing_time_ms
        );


        /*
         * Always reload from backend.
         *
         * This guarantees the UI reflects
         * the database rather than merely
         * trusting the inference response.
         */

        const refreshed =
          await getImageAnnotations(
            datasetId,
            selectedImage
          );

        setAnnotations(
          refreshed.annotations
        );

      } catch (err: any) {

        setError(
          err?.message ??
          "Auto-annotation failed."
        );

      } finally {

        setRunningModel(false);
      }
    };


  /* ==========================================================
     REVIEW ANNOTATION
     ========================================================== */

  const updateStatus =
    async (
      annotation: Annotation,
      status: AnnotationStatus
    ) => {

      setReviewingId(
        annotation.id
      );

      setError(null);

      try {

        const updated =
          await reviewAnnotation(
            annotation.id,
            status
          );

        setAnnotations(
          (current) =>
            current.map(
              (item) =>
                item.id === updated.id
                  ? updated
                  : item
            )
        );

      } catch (err: any) {

        setError(
          err?.message ??
          "Could not update annotation."
        );

      } finally {

        setReviewingId(null);
      }
    };


  /* ==========================================================
     REVIEW COUNTS
     ========================================================== */

  const pendingCount =
    annotations.filter(
      (item) =>
        item.status ===
        "AUTO_GENERATED"
    ).length;

  const approvedCount =
    annotations.filter(
      (item) =>
        item.status ===
        "APPROVED"
    ).length;

  const rejectedCount =
    annotations.filter(
      (item) =>
        item.status ===
        "REJECTED"
    ).length;


  /* ==========================================================
     RENDER
     ========================================================== */

  return (

    <div className="annotation-workspace">

      {/* ======================================================
          HEADER
          ====================================================== */}

      <header className="annotation-toolbar">

        <div>

          <div className="workspace-eyebrow">
            DATASET ANNOTATION
          </div>

          <h1>
            Annotation Workspace
          </h1>

          <p>
            Review model-generated detections
            before they enter your training dataset.
          </p>

        </div>


        <div className="workspace-actions">

          <button
            type="button"
            className="ghost-button"
            onClick={() =>
              void loadImages(false)
            }
            disabled={loadingImages}
          >

            {loadingImages ? (
              <Loader2
                size={16}
                className="spin"
              />
            ) : (
              <RefreshCw size={16} />
            )}

            Refresh

          </button>


          <button
            type="button"
            className="primary-button"
            onClick={() =>
              void runAutoAnnotation()
            }
            disabled={
              !selectedImage ||
              runningModel
            }
          >

            {runningModel ? (
              <Loader2
                size={16}
                className="spin"
              />
            ) : (
              <Sparkles size={16} />
            )}

            {runningModel
              ? "Annotating..."
              : "Auto Annotate"}

          </button>

        </div>

      </header>


      {/* ======================================================
          ERROR
          ====================================================== */}

      {error && (

        <div className="workspace-error">

          {error}

        </div>

      )}


      {/* ======================================================
          MAIN
          ====================================================== */}

      <div className="annotation-layout">


        {/* ====================================================
            LEFT — IMAGE LIBRARY
            ==================================================== */}

        <aside className="image-library">

          <div className="panel-heading">

            <div>

              <strong>
                Images
              </strong>

              <span>
                {images.length} in dataset
              </span>

            </div>

          </div>


          <div className="image-search">

            <Search size={15} />

            <input
              type="text"
              value={search}
              onChange={(event) =>
                setSearch(
                  event.target.value
                )
              }
              placeholder="Search images"
            />

          </div>


          <div className="image-list">

            {loadingImages ? (

              <div className="empty-state">

                <Loader2
                  size={20}
                  className="spin"
                />

                Loading images...

              </div>

            ) : filteredImages.length === 0 ? (

              <div className="empty-state">

                <ImageIcon size={18} />

                No images found.

              </div>

            ) : (

              filteredImages.map(
                (imageName) => (

                  <button
                    type="button"
                    key={imageName}
                    className={
                      `image-row ${
                        selectedImage ===
                        imageName
                          ? "active"
                          : ""
                      }`
                    }
                    onClick={() =>
                      setSelectedImage(
                        imageName
                      )
                    }
                  >

                    <span className="image-file-icon">
                      IMG
                    </span>

                    <span className="image-name">
                      {imageName}
                    </span>

                    {selectedImage ===
                      imageName && (
                      <span className="selected-dot" />
                    )}

                  </button>

                )
              )

            )}

          </div>

        </aside>


        {/* ====================================================
            CENTER — IMAGE VIEWER
            ==================================================== */}

        <main className="annotation-canvas-panel">

          <div className="canvas-header">

            <div className="image-title">

              <strong>
                {selectedImage ??
                  "Select an image"}
              </strong>

              {selectedImage && (
                <span>
                  {currentIndex + 1}
                  {" / "}
                  {images.length}
                </span>
              )}

            </div>


            <div className="canvas-navigation">

              <button
                type="button"
                onClick={
                  selectPrevious
                }
                disabled={
                  currentIndex <= 0
                }
                aria-label="Previous image"
              >

                <ChevronLeft
                  size={17}
                />

              </button>


              <button
                type="button"
                onClick={
                  selectNext
                }
                disabled={
                  currentIndex < 0 ||
                  currentIndex >=
                    images.length - 1
                }
                aria-label="Next image"
              >

                <ChevronRight
                  size={17}
                />

              </button>

            </div>

          </div>


          <div className="canvas-stage">

            {loadingImage ? (

              <div className="canvas-empty">

                <Loader2
                  size={28}
                  className="spin"
                />

                Loading image...

              </div>

            ) : !imageUrl ? (

              <div className="canvas-empty">

                <ImageIcon
                  size={30}
                />

                Select an image
                from the library.

              </div>

            ) : (

              <div className="image-overlay-wrap">

                <img
                  src={imageUrl}
                  alt={
                    selectedImage ??
                    "Dataset image"
                  }
                  onLoad={
                    handleImageLoaded
                  }
                />


                {/* ==============================================
                    BOUNDING BOXES
                    ============================================== */}

                {annotations.map(
                  (annotation) => (

                    <div
                      key={
                        annotation.id
                      }
                      className={
                        `bbox ${
                          annotation.status ===
                          "APPROVED"
                            ? "bbox-approved"
                            : annotation.status ===
                              "REJECTED"
                            ? "bbox-rejected"
                            : ""
                        }`
                      }
                      style={
                        getBoundingBoxStyle(
                          annotation
                        )
                      }
                    >

                      <div className="bbox-label">

                        {annotation.label}

                        {" "}

                        {Math.round(
                          annotation.confidence *
                            100
                        )}
                        %

                      </div>

                    </div>

                  )
                )}

              </div>

            )}

          </div>

        </main>


        {/* ====================================================
            RIGHT — REVIEW PANEL
            ==================================================== */}

        <aside className="review-panel">


          {/* ==================================================
              COUNTS
              ================================================== */}

          <div className="review-stats">

            <div>

              <span>
                Pending
              </span>

              <strong>
                {pendingCount}
              </strong>

            </div>


            <div>

              <span>
                Approved
              </span>

              <strong>
                {approvedCount}
              </strong>

            </div>


            <div>

              <span>
                Rejected
              </span>

              <strong>
                {rejectedCount}
              </strong>

            </div>

          </div>


          {/* ==================================================
              AI CONFIGURATION
              ================================================== */}

          <div className="model-config">

            <div className="section-title">
              AI Configuration
            </div>


            <label>

              Model

              <input
                type="text"
                value={model}
                onChange={(event) =>
                  setModel(
                    event.target.value
                  )
                }
              />

            </label>


            <label>

              Prompt

              <textarea
                value={prompt}
                onChange={(event) =>
                  setPrompt(
                    event.target.value
                  )
                }
                rows={3}
              />

            </label>


            <label>

              Confidence Threshold

              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={confidence}
                onChange={(event) =>
                  setConfidence(
                    Number(
                      event.target.value
                    )
                  )
                }
              />

              <span>
                {Math.round(
                  confidence * 100
                )}
                %
              </span>

            </label>


            {lastRun !== null && (

              <div className="run-info">

                Last run:
                {" "}
                {lastRun}
                {" "}
                ms

              </div>

            )}

          </div>


          {/* ==================================================
              DETECTIONS
              ================================================== */}

          <div className="annotation-list">

            <div className="section-title">
              Detections
            </div>


            {annotations.length === 0 ? (

              <div className="empty-state">

                No annotations for this image.

              </div>

            ) : (

              annotations.map(
                (annotation) => (

                  <div
                    key={
                      annotation.id
                    }
                    className="annotation-card"
                  >

                    <div className="annotation-card-top">

                      <div>

                        <strong>
                          {annotation.label}
                        </strong>

                        <span>
                          Confidence:
                          {" "}
                          {Math.round(
                            annotation.confidence *
                              100
                          )}
                          %
                        </span>

                      </div>


                      <span
                        className={
                          `status-pill status-${annotation.status.toLowerCase()}`
                        }
                      >
                        {annotation.status
                          .replace(
                            "_",
                            " "
                          )}
                      </span>

                    </div>


                    <div className="annotation-actions">

                      <button
                        type="button"
                        className="approve-button"
                        disabled={
                          reviewingId ===
                            annotation.id ||
                          annotation.status ===
                            "APPROVED"
                        }
                        onClick={() =>
                          void updateStatus(
                            annotation,
                            "APPROVED"
                          )
                        }
                      >

                        {reviewingId ===
                        annotation.id ? (
                          <Loader2
                            size={14}
                            className="spin"
                          />
                        ) : (
                          <Check
                            size={14}
                          />
                        )}

                        Approve

                      </button>


                      <button
                        type="button"
                        className="reject-button"
                        disabled={
                          reviewingId ===
                            annotation.id ||
                          annotation.status ===
                            "REJECTED"
                        }
                        onClick={() =>
                          void updateStatus(
                            annotation,
                            "REJECTED"
                          )
                        }
                      >

                        <X size={14} />

                        Reject

                      </button>

                    </div>

                  </div>

                )
              )

            )}

          </div>

        </aside>

      </div>

    </div>
  );
}