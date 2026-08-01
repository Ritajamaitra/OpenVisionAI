from app.services.databricks_services import DatabricksService

service = DatabricksService()

print("Host:", service.host)

clusters = service.test_connection()

print(clusters)