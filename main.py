import datetime
import uuid

class IncidentManager:
    """
    Manages the creation, updating, and retrieval of incidents.
    This class ensures that incidents are properly recorded and their
    state is maintained, preventing the "forgetfulness" described in the article.
    """
    def __init__(self):
        self.incidents = {}  # Stores incidents by ID

    def create_incident(self, description: str) -> str:
        """
        Creates a new incident and marks it as OPEN.
        Returns the ID of the newly created incident.
        """
        incident_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().isoformat()
        self.incidents[incident_id] = {
            "id": incident_id,
            "description": description,
            "start_time": timestamp,
            "end_time": None,
            "status": "OPEN"
        }
        print(f"[IncidentManager] Incident '{incident_id}' created: {description} (Status: OPEN)")
        return incident_id

    def resolve_incident(self, incident_id: str) -> bool:
        """
        Resolves an existing incident by setting its end time and status to RESOLVED.
        Returns True if successful, False otherwise (e.g., incident not found or already resolved).
        """
        if incident_id not in self.incidents:
            print(f"[IncidentManager] Error: Incident '{incident_id}' not found.")
            return False
        
        incident = self.incidents[incident_id]
        if incident["status"] == "RESOLVED":
            print(f"[IncidentManager] Incident '{incident_id}' is already RESOLVED.")
            return False

        incident["end_time"] = datetime.datetime.now().isoformat()
        incident["status"] = "RESOLVED"
        print(f"[IncidentManager] Incident '{incident_id}' resolved. (Status: RESOLVED)")
        return True

    def get_incident_history(self) -> list:
        """
        Returns a list of all recorded incidents, demonstrating that the system
        retains historical data and does not "forget" past events.
        """
        return list(self.incidents.values())

    def get_open_incidents(self) -> list:
        """
        Returns a list of all currently open incidents.
        This helps in understanding the current operational state and prevents
        missing ongoing issues.
        """
        return [inc for inc in self.incidents.values() if inc["status"] == "OPEN"]

class ServiceMonitor:
    """
    Simulates monitoring a service and interacting with the IncidentManager.
    This class represents the mechanism that detects issues and reports them.
    """
    def __init__(self, incident_manager: IncidentManager, service_name: str):
        self.incident_manager = incident_manager
        self.service_name = service_name
        self._is_service_down = False # Internal state of the service
        self._current_incident_id = None # Tracks the incident ID for the current outage

    def simulate_service_check(self, is_down: bool):
        """
        Simulates a periodic health check for the service.
        It interacts with the IncidentManager based on the service's simulated state.
        """
        print(f"\n--- Checking service '{self.service_name}' ---")
        if is_down and not self._is_service_down:
            # Service just went down. Create a new incident.
            # This prevents the system from "forgetting" the start of an outage.
            print(f"[ServiceMonitor] Service '{self.service_name}' detected as DOWN.")
            self._current_incident_id = self.incident_manager.create_incident(
                f"Service '{self.service_name}' is experiencing an outage."
            )
            self._is_service_down = True
        elif not is_down and self._is_service_down:
            # Service just came back up. Resolve the active incident.
            # This ensures the incident's lifecycle is completed and not left open indefinitely.
            print(f"[ServiceMonitor] Service '{self.service_name}' detected as UP.")
            if self._current_incident_id:
                self.incident_manager.resolve_incident(self._current_incident_id)
                self._current_incident_id = None
            self._is_service_down = False
        elif is_down and self._is_service_down:
            # Service is still down. No new incident needed, but ensure existing one is open.
            print(f"[ServiceMonitor] Service '{self.service_name}' is still DOWN. Incident '{self._current_incident_id}' remains OPEN.")
        else:
            # Service is still up. No action needed.
            print(f"[ServiceMonitor] Service '{self.service_name}' is UP and healthy.")

# --- Main execution demonstrating the system ---
if __name__ == "__main__":
    incident_manager = IncidentManager()
    service_monitor = ServiceMonitor(incident_manager, "Web Application API")

    print("--- Scenario 1: Service goes down and comes back up ---")
    service_monitor.simulate_service_check(is_down=False) # Initial check: UP
    service_monitor.simulate_service_check(is_down=True)  # Service goes DOWN
    service_monitor.simulate_service_check(is_down=True)  # Service is still DOWN
    service_monitor.simulate_service_check(is_down=False) # Service comes UP
    service_monitor.simulate_service_check(is_down=False) # Service is still UP

    print("\n--- Scenario 2: Service goes down again later ---")
    service_monitor.simulate_service_check(is_down=True)  # Service goes DOWN again
    service_monitor.simulate_service_check(is_down=False) # Service comes UP again

    print("\n--- Incident History ---")
    # This demonstrates the system's "memory" – it remembers all past incidents.
    # The article highlights that forgetting this history is a major problem.
    for i, incident in enumerate(incident_manager.get_incident_history()):
        print(f"Incident {i+1}: ID={incident['id'][:8]}..., Status={incident['status']}, "
              f"Description='{incident['description']}', Start={incident['start_time']}, "
              f"End={incident['end_time'] if incident['end_time'] else 'N/A'}")

    print("\n--- Open Incidents (should be none if all resolved) ---")
    open_incidents = incident_manager.get_open_incidents()
    if open_incidents:
        for incident in open_incidents:
            print(f"Open Incident: ID={incident['id'][:8]}..., Description='{incident['description']}'")
    else:
        print("No open incidents. All issues are resolved or service is healthy.")

    # How "forgetfulness" could happen (and how this example avoids it):
    # 1. Missing `_current_incident_id` tracking: If `ServiceMonitor` didn't track `_current_incident_id`,
    #    it might create a new incident every time `is_down` is True, or fail to resolve the correct one.
    # 2. Not persisting `incidents`: If `IncidentManager.incidents` was cleared on each run or not stored
    #    in a persistent database, all history would be lost. This example uses in-memory for simplicity
    #    but the concept of retaining `self.incidents` is key.
    # 3. Lack of status updates: If `resolve_incident` was never called, incidents would remain "OPEN"
    #    indefinitely, leading to a misleading view of system health.