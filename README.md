# OpenVisionAI
OpenVisionAI 

Build. Train. Deploy Vision AI.

OpenVisionAI is a comprehensive computer-vision platform that helps you manage datasets, train YOLO-based vision models, register model versions, perform image inference, and track inference history through a unified web application.

The platform seamlessly integrates a React/TypeScript frontend, a FastAPI backend, SQL-based metadata management, Azure Machine Learning for training and model artifacts, Azure Blob/ML datastores for artifact storage, and a lightweight local inference service for serving registered YOLO models. 

#Product Overview: 

OpenVisionAI is engineered for the complete computer-vision model lifecycle, including dataset management, training job evaluation, metrics, model registration, deployment/inference, and inference history and monitoring. The application offers a single workspace for both ML lifecycle operations and application-level model serving. 

#Core capabilities 

Secure user authentication via JWT 

User registration 

Forgot-password flow with CAPTCHA protection 

Project management 

Dataset creation and management 

Dataset statistics 

Azure ML training job orchestration 

Training-run synchronization 

Automatic model registration from completed training runs 

Model version management 

Model metadata and evaluation metrics 

Image-based YOLO inference 

Configurable confidence threshold 

Inference execution history 

Detection counts, confidence, and latency monitoring 

Deployment management 

Swagger/OpenAPI API documentation 

Responsive React frontend 

#Architecture 
<img width="371" height="462" alt="image" src="https://github.com/user-attachments/assets/ab1d5df9-2fcc-4689-be62-43718a2b6053" />

#Architectural separation 

The system is segregated into three planes: 

Control plane - FastAPI handles users, metadata, projects, datasets, training runs, registered models, and inference records. ML plane - Azure ML executes training and stores training artifacts.

Serving plane - the inference service loads a registered YOLO artifact and performs predictions.

Presentation plane - the React application exposes the lifecycle through dedicated pages. 

#Technology Stack 

Layer Technology 

Frontend React, TypeScript, Vite 

Backend Python, FastAPI, Uvicorn 

ORM / Database SQLAlchemy + SQL database 

Authentication JWT + password hashing 

API REST + OpenAPI / Swagger 

Computer Vision Ultralytics YOLO 

ML Platform Azure Machine Learning 

Experiment Tracking MLflow / Azure ML runs 

Artifact Storage 

Azure ML datastore / Blob-backed artifacts 

Inference FastAPI inference service + Ultralytics 

Styling Application CSS / component-based UI 

Application Modules 

#Dashboard 

High-level view of the workspace and lifecycle activity. 

#Projects 

Projects serve as organizational boundaries for datasets and ML workflows.

#Datasets 

Dataset management supports: 

Dataset creation 

Dataset listing 

Dataset updates 

Dataset deletion 

Dataset statistics 

Dataset-to-model relationships 

#Training 

Training offers: 

Training-job submission 

Azure ML execution 

Training-run status 

Evaluation metrics 

Training duration 

Experiment history 

Synchronization of completed Azure ML runs 

#Models 

The model registry maintains: 

Model name 

Model version 

Dataset Training run 

Framework Model type 

Precision 

Recall 

mAP@50 

mAP@50:95 

Training time 

Azure ML model reference 

Artifact URI 

Active status 

The application currently demonstrates example registered models, including various versions of openvisionai-yolo. 

#Inference 

The inference workflow allows a user to: 

Select a registered model. 

Upload an image.

Set a confidence threshold.

Run inference. 

Inspect detections. 

Review the inference ID and execution result. 

Inference is exposed through the backend and routed to the local inference service running on port 5001.

#Inference History 

Inference history provides persistent monitoring of previous executions, including: 

Inference ID 

Model Model version 

Status 

Detection count 

Confidence threshold 

Inference latency 

Creation timestamp 

Stored predictions 

Failure information when applicable 

#Deployments 

The deployment module manages the application-level deployment workflows for registered models.

#Authentication 

The login process includes: 

Existing-user sign-in 

New-user registration 

Password visibility control 

Forgot-password flow 

CAPTCHA verification before password reset 

JWT-based authenticated API access 

API Surface 

The FastAPI application provides REST endpoints documented with Swagger UI. 

 OpenAPI documentation is accessible locally when the backend is running:

 http://127.0.0.1:8000/docs 

#Local Development 
Prerequisites Install: 
Python 3.11+ 
Node.js / npm 
Git 
Azure CLI 
Azure ML CLI extension 
An Azure subscription with access to the configured ML workspace 

Backend Setup 
From the repository root: 
cd backend 
Create and activate a virtual environment if necessary: 
python -m venv .venv 
. \.venv\Scripts\Activate.ps1 
Install dependencies: pip -r requirements.txt 
Configure backend environment variables in .env.
Start the API: 
uvicorn app.main:app --reload 
The backend runs at: http://127.0.0.1:8000 
Swagger UI: http://127.0.0.1:8000/docs 

Frontend Setup 
From the repository root: 
cd frontend 
npm install 
npm run dev 
The Vite development server typically runs at: http://localhost:5173 

#Inference Service
The local inference service loads a registered YOLO artifact and exposes a scoring endpoint. 
Run it from the backend directory: 
cd backend 
uvicorn inference_server:app --host 127.0.0.1 --port 5001 
The backend inference route communicates with: http://127.0.0.1:5001/score 
Therefore, the inference service must be running when image inference is performed locally.

#Azure ML Model Artifacts 
For local inference, you can download a registered Azure ML model to the backend's models directory.

Example PowerShell command: 
az ml model download `
--name openvisionai-yolo ` 
--version 2 `
--resource-group <RESOURCE_GROUP>`
--workspace-name <WORKSPACE_NAME> `
--download-path ./models/openvisionai-yolo-v2 
PowerShell uses the backtick ` for line continuation; the Unix-style \ continuation seen in many Bash examples will not work in PowerShell.

The inference service should target the actual downloaded best.pt` artifact. 

#Environment Configuration 
Do not commit credentials, access tokens, secrets, or connection strings. 
Use environment variables for values such as:
DATABASEURL SECRETKEY JWTSECRET AZURESUBSCRIPTIONID AZURERESOURCEGROUP AZUREMLWORKSPACE AZURESTORAGECONNECTIONSTRING 
Ensure that the variable names match the ones expected by the current backend configuration. 

Typical End-to-End Workflow 
1.Authenticate 
Login 
JWT token 
Authenticated workspace 

2.Create a project 
Projects 
Create Project 

3. Create a dataset 
Datasets 
Create Dataset 
Upload / configure dataset

4. Train a model 
Training 
Select project + dataset 
Configure training 
Submit Azure ML job 
Monitor run

5. Register the trained model
A completed training run can be synchronized and associated with the model registry.
Completed Training Run
Sync
Model Registration
Registered Model Version

6. Run inference
Inference
Select registered model
Upload image
Set confidence
Run inference
View detections

7.Monitor history 
History 
Inference executions 
Detection / latency / status 

#Model Registry Example 
The demonstrated registry contains multiple versions of the YOLO model.

Example: 
Model: openvisionai-yolo 
Version: v1 / v2 / v3 
Framework: Ultralytics YOLO 
Task: Object Detection 
Dataset: PPE dataset variants 
Metrics: Precision / Recall / mAP@50 / mAP@50:95 
The registry is designed to maintain the lineage between: Dataset Training Run Model Version Inference This allows the inference result to be traced back to the model and training workflow that generated it. 

#Inference Data Model 
An inference execution records information such as: 
{ "id": 9, 
"modelid": 3, 
"modelname": "openvisionai-yolo", 
"modelversion": "3", 
"status": "COMPLETED", 
"confidencethreshold": 0.05, 
"predictioncount": 1, 
"predictions": [], 
"inferencelatencyms": 301.07, 
"inputfilename": null, 
"inputcontenttype": null, 
"error_message": null }

These are then translated into the Inference History monitoring view by the frontend.

#Security Notes

- The platform uses JWT based access tokens for authentication.
- Password reset verification should include a CAPTCHA check to allow the password-change process to proceed.
For a full production setup of the application, the following should be addressed additionally:

- HTTPS / TLS

- HttpOnly cookie usage wherever appropriate.

- Production secret management

- rate-limiting

- lockout / abuse protection

- distributed CAPTCHA storage

- e-mail-based password-reset tokens

- Production database configuration

- A proper Azure managed identity / workload identity arrangement

- Containerized inference serving

- Production level monitoring and logging

The current CAPTCHA is set up in a purely in-memory-backend mode suitable for the application's development / demo environment.

#Project Structure

A sample structure for a repository:

OpenVisionAI/

backend/

app/

api/

routes/

models/

repositories/

schemas/

services/

main.py

inference_server.py

models/

requirements.txt

frontend/

src/

components/

context/

pages/

types/

App.tsx

package.json

vite.config.*

README.md

#Screenshots

An interface is provided for each of the following tasks:

- Login / Authentication

- User Registration

- Password Reset

- Dashboard

- Projects

- Datasets

- Training

- Models

- Deployments

- Inference

- Inference History

Screenshots may be hosted in a dedicated documentation / screenshots subdirectory as the general project documentation continues to take shape.

#Current Project Status

The project has reached Feature complete status with a development freeze. It provides the expected basic ML lifecycle:

- Authentication

- Projects

- Datasets

- Training

- Models

- Model Versions

- Inference

- Inference History

- Deployments

- API documentation

The project is now ready for the next steps: documentation, testing, demonstration and preparing it for production deployment.

#Future Production Extensions

Other potential future next steps could include:

- containerized backend and inference server

- inferencingendpoint hosted in azure

- CI CD pipeeline for automated building and deploying
- unit and integration tests for frontend and backend

- RBAC

- Dataset versioning

- Model Approval workflow

- Model performance drift analysis

- batchinferencing

- videoinferencing

- realtiminferencing

- GPU backed inference service

- e-mail for password reset

- central application observability

This is not a part of the current freeze, just an indication for the way forward.


#Author

OpenVisionAI - Vision AI Model Platform

Built as an end-to-end computer-vision lifecycle platform covering dataset management, model training, registration, inference and monitoring.
