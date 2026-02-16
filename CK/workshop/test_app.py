"""
Tests for The Workshop (app.py, port 5003)

Run with: pytest test_app.py -v
"""

import pytest
import json
from unittest.mock import patch, MagicMock
import sys
import os

# Add workshop dir to path for imports
sys.path.insert(0, os.path.dirname(__file__))


@pytest.fixture
def app_client():
    """Create a test client for the Flask app."""
    # Mock subprocess, httpx, os.path before importing app
    with patch('subprocess.Popen') as mock_popen, \
         patch('subprocess.run') as mock_run, \
         patch('httpx.get') as mock_get, \
         patch('os.path.isdir') as mock_isdir, \
         patch('os.path.isfile') as mock_isfile:
        
        # Default mocks
        mock_isdir.return_value = True
        mock_isfile.return_value = True
        mock_popen.return_value.pid = 12345
        mock_run.return_value = MagicMock(stdout="", stderr="")
        
        # Import app with mocked dependencies
        import importlib
        import app
        
        importlib.reload(app)
        app.app.config['TESTING'] = True
        
        with app.app.test_client() as client:
            yield client, app


class TestHealthEndpoints:
    """Tests for /api/health endpoint."""
    
    def test_health_returns_200(self, app_client):
        client, _ = app_client
        response = client.get('/api/health')
        assert response.status_code == 200
    
    def test_health_returns_json(self, app_client):
        client, _ = app_client
        response = client.get('/api/health')
        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] == 'healthy'
        assert data['app'] == 'The Workshop'
        assert 'version' in data
        assert 'timestamp' in data


class TestAIStatusEndpoint:
    """Tests for /api/ai/status endpoint."""
    
    def test_ai_status_returns_200(self, app_client):
        client, _ = app_client
        response = client.get('/api/ai/status')
        assert response.status_code == 200
    
    def test_ai_status_returns_backends(self, app_client):
        client, _ = app_client
        response = client.get('/api/ai/status')
        data = json.loads(response.data)
        assert 'backends' in data
        assert 'ollama' in data['backends']
        assert 'timestamp' in data


class TestServicesEndpoints:
    """Tests for /api/services endpoints."""
    
    def test_list_services_returns_200(self, app_client):
        client, _ = app_client
        response = client.get('/api/services')
        assert response.status_code == 200
    
    def test_list_services_returns_dict(self, app_client):
        client, _ = app_client
        response = client.get('/api/services')
        data = json.loads(response.data)
        assert isinstance(data, dict)
        assert 'elaine' in data
        assert 'supervisor' in data
    
    def test_services_health_returns_200(self, app_client):
        client, _ = app_client
        response = client.get('/api/services/health')
        assert response.status_code == 200
    
    def test_services_health_returns_summary(self, app_client):
        client, _ = app_client
        response = client.get('/api/services/health')
        data = json.loads(response.data)
        assert 'summary' in data
        assert 'live' in data
        assert 'total' in data
        assert 'services' in data
    
    def test_single_service_health_known_service(self, app_client):
        client, _ = app_client
        response = client.get('/api/services/health/elaine')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == 'elaine'
        assert 'status' in data
    
    def test_single_service_health_unknown_service(self, app_client):
        client, _ = app_client
        response = client.get('/api/services/health/nonexistent')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data


class TestPidsEndpoint:
    """Tests for /api/services/pids endpoint."""
    
    def test_pids_returns_200(self, app_client):
        client, _ = app_client
        response = client.get('/api/services/pids')
        assert response.status_code == 200
    
    def test_pids_returns_processes_dict(self, app_client):
        client, _ = app_client
        response = client.get('/api/services/pids')
        data = json.loads(response.data)
        assert 'processes' in data
        assert 'cleaned' in data
        assert 'count' in data
        assert 'timestamp' in data


class TestLaunchEndpoints:
    """Tests for service launch endpoints."""
    
    def test_launch_unknown_service_returns_404(self, app_client):
        client, _ = app_client
        response = client.post('/api/services/launch/nonexistent')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_launch_service_returns_launched_or_already(self, app_client):
        client, _ = app_client
        response = client.post('/api/services/launch/elaine')
        # Either already running or launched
        assert response.status_code in [200, 500]
        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] in ['already_running', 'launched', 'starting', 'not_available', 'not_found', 'error']
    
    def test_launch_all_returns_results(self, app_client):
        client, _ = app_client
        response = client.post('/api/services/launch-all')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'results' in data
        assert 'message' in data


class TestLaunchBatEndpoint:
    """Tests for /api/launch/<name> endpoint."""
    
    def test_launch_unknown_advisor_returns_404(self, app_client):
        client, _ = app_client
        response = client.post('/api/launch/NonexistentAdvisor')
        assert response.status_code == 404
    
    def test_launch_known_advisor(self, app_client):
        client, _ = app_client
        # Talaiva exists as an advisor
        response = client.post('/api/launch/talaiva')
        # Will fail because bat file doesn't exist, but should be 404 not server error
        assert response.status_code in [200, 404]


class TestDesktopEndpoints:
    """Tests for desktop app launch endpoints."""
    
    def test_list_desktop_apps_returns_200(self, app_client):
        client, _ = app_client
        response = client.get('/api/desktop/apps')
        assert response.status_code == 200
    
    def test_list_desktop_apps_returns_apps(self, app_client):
        client, _ = app_client
        response = client.get('/api/desktop/apps')
        data = json.loads(response.data)
        assert isinstance(data, dict)
        # Should have desktop apps
        assert 'elaine' in data or len(data) > 0
    
    def test_refresh_desktop_cache_returns_200(self, app_client):
        client, _ = app_client
        response = client.post('/api/desktop/refresh')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_launch_unknown_desktop_app_returns_404(self, app_client):
        client, _ = app_client
        response = client.post('/api/desktop/launch/nonexistent')
        assert response.status_code == 404
    
    def test_launch_all_desktop_returns_200(self, app_client):
        client, _ = app_client
        response = client.post('/api/desktop/launch-all')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'results' in data
        assert 'message' in data


class TestStartBackendsEndpoint:
    """Tests for /api/services/start-backends endpoint."""
    
    def test_start_backends_returns_200(self, app_client):
        client, _ = app_client
        response = client.post('/api/services/start-backends')
        assert response.status_code == 200
    
    def test_start_backends_returns_message_and_services(self, app_client):
        client, _ = app_client
        response = client.post('/api/services/start-backends')
        data = json.loads(response.data)
        assert 'message' in data
        assert 'services' in data


class TestCORsHeaders:
    """Tests for CORS headers."""
    
    def test_cors_headers_present(self, app_client):
        client, _ = app_client
        # Test a POST endpoint for CORS
        response = client.post('/api/services/launch/elaine')
        assert 'Access-Control-Allow-Origin' in response.headers
        assert response.headers['Access-Control-Allow-Origin'] == '*'
    
    def test_options_request_returns_200(self, app_client):
        client, _ = app_client
        response = client.options('/api/services/launch/elaine')
        assert response.status_code == 200


class TestErrorHandling:
    """Tests for error handling scenarios."""
    
    def test_health_check_failures_dont_crash(self, app_client):
        """Verify one failed service doesn't crash the health endpoint."""
        client, _ = app_client
        response = client.get('/api/services/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        # Should still return valid structure even if some services fail
        assert 'services' in data


class TestBackendServicesAutoDerivation:
    """Tests for auto-derivation of BACKEND_SERVICES."""
    
    def test_backend_services_includes_ck_with_cmd(self, app_client):
        """Verify BACKEND_SERVICES is auto-derived from SERVICES dict."""
        _, app = app_client
        # Should include CK services with cmd defined
        assert 'elaine' in app.BACKEND_SERVICES
        assert 'writer' in app.BACKEND_SERVICES
        assert 'supervisor' in app.BACKEND_SERVICES
    
    def test_backend_services_excludes_docker_only(self, app_client):
        """Verify docker-only services aren't in BACKEND_SERVICES."""
        _, app = app_client
        # n8n, searxng etc are docker-only, should not be in BACKEND_SERVICES
        # (they're type='infra' not 'ck')
        for svc in app.BACKEND_SERVICES:
            if svc in app.SERVICES:
                svc_type = app.SERVICES[svc].get('type')
                assert svc_type == 'ck' or svc == 'supervisor'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
