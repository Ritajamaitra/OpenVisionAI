import os
import time

import requests
from sqlalchemy.orm import Session

from app.models.inference_runs import InferenceRun
from app.models.user import User
from app.repositories.inference_run_repository import (
    InferenceRunRepository,
)
from app.services.model_services import ModelService


class InferenceException(Exception):
    """Raised when model inference fails."""


class InferenceService:
    """
    Service responsible for executing model inference
    and persisting inference execution history.
    """

    INFERENCE_STATUS_RUNNING = "RUNNING"
    INFERENCE_STATUS_COMPLETED = "COMPLETED"
    INFERENCE_STATUS_FAILED = "FAILED"

    DEFAULT_INFERENCE_URL = (
        "http://127.0.0.1:5001/score"
    )

    INFERENCE_TIMEOUT_SECONDS = 120

    def __init__(self, db: Session):
        self.db = db

        self.model_service = ModelService()

        self.inference_repository = (
            InferenceRunRepository()
        )

        self.inference_url = os.getenv(
            "OPENVISIONAI_INFERENCE_URL",
            self.DEFAULT_INFERENCE_URL,
        )

    # ==========================================================
    # Main Inference
    # ==========================================================

    def infer(
        self,
        model_id: int,
        image_base64: str,
        confidence: float,
        current_user: User,
    ):
        """
        Execute inference for a registered model.

        Responsibilities:
        1. Validate model ownership
        2. Validate model metadata
        3. Create an inference run
        4. Call the inference container
        5. Capture predictions and latency
        6. Persist COMPLETED / FAILED status
        7. Return standardized inference response
        """

        # ------------------------------------------------------
        # 1. Validate model ownership
        # ------------------------------------------------------

        model = self.model_service.get_model(
            db=self.db,
            model_id=model_id,
            current_user=current_user,
        )

        # ------------------------------------------------------
        # 2. Validate model
        # ------------------------------------------------------

        if not model.name:
            raise InferenceException(
                "Registered model has no name."
            )

        if not model.version:
            raise InferenceException(
                "Registered model has no version."
            )

        # Capture immutable model metadata before inference.
        model_id_value = model.id
        model_name = model.name
        model_version = str(model.version)

        # ------------------------------------------------------
        # 3. Create inference run
        # ------------------------------------------------------

        inference_run = InferenceRun(
            model_registry_id=model_id_value,
            user_id=current_user.id,
            status=self.INFERENCE_STATUS_RUNNING,
            model_version=model_version,
            confidence_threshold=confidence,
            prediction_count=0,
            predictions_json=None,
        )

        try:
            self.db.add(inference_run)
            self.db.commit()
            self.db.refresh(inference_run)

        except Exception as exc:
            self.db.rollback()

            raise InferenceException(
                f"Could not create inference run: {exc}"
            ) from exc

        # Keep the ID because it is required in the API response.
        inference_id = inference_run.id

        # ------------------------------------------------------
        # 4. Build inference request
        # ------------------------------------------------------

        payload = {
            "image_base64": image_base64,
            "confidence": confidence,
        }

        # Start timing immediately before the actual
        # inference service call.
        start_time = time.perf_counter()

        # ------------------------------------------------------
        # 5. Call inference container
        # ------------------------------------------------------

        try:
            response = requests.post(
                self.inference_url,
                json=payload,
                timeout=self.INFERENCE_TIMEOUT_SECONDS,
            )

        except requests.RequestException as exc:

            latency_ms = self._calculate_latency(
                start_time
            )

            self._mark_failed(
                inference_run=inference_run,
                latency_ms=latency_ms,
                error_message=(
                    "Could not connect to inference "
                    f"service: {exc}"
                ),
            )

            raise InferenceException(
                f"Could not connect to inference service: {exc}"
            ) from exc

        # ------------------------------------------------------
        # 6. Handle HTTP errors
        # ------------------------------------------------------

        if response.status_code != 200:

            latency_ms = self._calculate_latency(
                start_time
            )

            error_message = (
                f"Inference service returned "
                f"{response.status_code}: "
                f"{response.text}"
            )

            self._mark_failed(
                inference_run=inference_run,
                latency_ms=latency_ms,
                error_message=error_message,
            )

            raise InferenceException(
                error_message
            )

        # ------------------------------------------------------
        # 7. Parse JSON response
        # ------------------------------------------------------

        try:
            result = response.json()

        except ValueError as exc:

            latency_ms = self._calculate_latency(
                start_time
            )

            error_message = (
                "Inference service returned invalid JSON."
            )

            self._mark_failed(
                inference_run=inference_run,
                latency_ms=latency_ms,
                error_message=error_message,
            )

            raise InferenceException(
                error_message
            ) from exc

        # ------------------------------------------------------
        # 8. Handle model-level errors
        # ------------------------------------------------------

        if "error" in result:

            latency_ms = self._calculate_latency(
                start_time
            )

            error_message = str(
                result["error"]
            )

            self._mark_failed(
                inference_run=inference_run,
                latency_ms=latency_ms,
                error_message=error_message,
            )

            raise InferenceException(
                error_message
            )

        # ------------------------------------------------------
        # 9. Extract predictions
        # ------------------------------------------------------

        predictions = result.get(
            "predictions",
            [],
        )

        if predictions is None:
            predictions = []

        if not isinstance(predictions, list):
            latency_ms = self._calculate_latency(
                start_time
            )

            error_message = (
                "Inference service returned an invalid "
                "'predictions' value."
            )

            self._mark_failed(
                inference_run=inference_run,
                latency_ms=latency_ms,
                error_message=error_message,
            )

            raise InferenceException(
                error_message
            )

        # ------------------------------------------------------
        # 10. Calculate latency
        # ------------------------------------------------------

        latency_ms = self._calculate_latency(
            start_time
        )

        # ------------------------------------------------------
        # 11. Persist successful inference
        # ------------------------------------------------------

        try:
            inference_run.status = (
                self.INFERENCE_STATUS_COMPLETED
            )

            inference_run.prediction_count = (
                len(predictions)
            )

            inference_run.predictions_json = (
                predictions
            )

            inference_run.inference_latency_ms = (
                latency_ms
            )

            self.db.commit()
            self.db.refresh(inference_run)

        except Exception as exc:

            self.db.rollback()

            # Try to preserve the inference failure in the
            # database. If this also fails, the original
            # database error is still returned.
            try:
                inference_run.status = (
                    self.INFERENCE_STATUS_FAILED
                )

                inference_run.inference_latency_ms = (
                    latency_ms
                )

                inference_run.error_message = (
                    f"Could not persist inference result: {exc}"
                )

                self.db.add(inference_run)
                self.db.commit()

            except Exception:
                self.db.rollback()

            raise InferenceException(
                f"Could not persist inference result: {exc}"
            ) from exc

        # ------------------------------------------------------
        # 12. Return standardized OpenVisionAI response
        # ------------------------------------------------------

        return {
            "inference_id": inference_id,
            "model_id": model_id_value,
            "model_name": model_name,
            "model_version": model_version,
            "predictions": predictions,
        }

    # ==========================================================
    # Helper: Calculate Latency
    # ==========================================================

    @staticmethod
    def _calculate_latency(
        start_time: float,
    ) -> float:
        """
        Calculate inference latency in milliseconds.
        """

        return round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

    # ==========================================================
    # Helper: Mark Failed
    # ==========================================================

    def _mark_failed(
        self,
        inference_run: InferenceRun,
        latency_ms: float,
        error_message: str,
    ) -> None:
        """
        Persist a failed inference run.

        This method intentionally does not raise another
        exception if logging fails because the original
        inference error is more important.
        """

        try:
            inference_run.status = (
                self.INFERENCE_STATUS_FAILED
            )

            inference_run.inference_latency_ms = (
                latency_ms
            )

            inference_run.error_message = (
                error_message[:2000]
            )

            self.db.add(inference_run)
            self.db.commit()
            self.db.refresh(inference_run)

        except Exception:
            self.db.rollback()