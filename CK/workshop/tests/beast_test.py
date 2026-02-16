"""Beast Test — The Workshop
Deep functional tests for the AMTL Mission Control launchpad.
"""
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from app import app, SERVICES, CK_BASE, SOURCE_BASE


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


# ================================================================
# Health & Core Endpoints
# ================================================================

class TestWorkshopHealth:
    def test_health_endpoint(self, client):
        r = client.get('/api/health')
        assert r.status_code == 200
        data = r.get_json()
        assert data['status'] == 'healthy'
        assert data['app'] == 'The Workshop'
        assert 'version' in data
        assert 'timestamp' in data

    def test_dashboard_loads(self, client):
        r = client.get('/')
        assert r.status_code == 200
        assert b'Workshop' in r.data or b'workshop' in r.data

    def test_dashboard_contains_search(self, client):
        r = client.get('/')
        assert b'searchBar' in r.data

    def test_dashboard_contains_theme_toggle(self, client):
        r = client.get('/')
        assert b'themeToggle' in r.data


# ================================================================
# Service Registry
# ================================================================

class TestServiceRegistry:
    def test_services_list(self, client):
        r = client.get('/api/services')
        assert r.status_code == 200
        data = r.get_json()
        assert len(data) >= 10, f"Expected 10+ services, got {len(data)}"

    def test_no_port_conflicts(self, client):
        r = client.get('/api/services')
        data = r.get_json()
        ports = {}
        for sid, svc in data.items():
            port = svc.get('port')
            if port is not None:
                if port in ports:
                    pytest.fail(f"Port conflict: :{port} used by both '{ports[port]}' and '{sid}'")
                ports[port] = sid

    def test_known_ports_correct(self):
        """Verify known service ports match the audit-verified port map."""
        known = {
            'elaine': 5000,
            'costanza': 5001,
            'learning-assistant': 5002,
            'writer': 5004,
            'junk-drawer-api': 5006,
            'peterman': 5008,
            'processlens': 5016,
            'the-ledger': 5020,
            'genie': 8000,
            'signal': 8420,
            'postgres': 5433,
            'redis': 6379,
            'searxng': 8888,
            'n8n': 5678,
            'ollama': 11434,
        }
        for sid, expected_port in known.items():
            assert sid in SERVICES, f"Service '{sid}' missing from registry"
            actual = SERVICES[sid]['port']
            assert actual == expected_port, f"{sid}: expected port {expected_port}, got {actual}"

    def test_processlens_in_registry(self):
        """ProcessLens on 5016 must be registered."""
        assert 'processlens' in SERVICES
        assert SERVICES['processlens']['port'] == 5016

    def test_the_ledger_in_registry(self):
        """The Ledger on 5020 must be registered."""
        assert 'the-ledger' in SERVICES
        assert SERVICES['the-ledger']['port'] == 5020

    def test_dhamma_mirror_not_on_5020(self):
        """Dhamma Mirror must NOT be on port 5020 (conflicts with The Ledger)."""
        if 'dhamma' in SERVICES:
            assert SERVICES['dhamma']['port'] != 5020, \
                "Dhamma Mirror is on port 5020 which conflicts with The Ledger"

    def test_junk_drawer_api_on_5006(self):
        """Junk Drawer API was moved from 5005 to 5006."""
        assert SERVICES['junk-drawer-api']['port'] == 5006


# ================================================================
# Path Validation
# ================================================================

class TestPathValidation:
    """Every service with a path must point to a real directory.
    NOTE: Paths use Windows C:\\ format. On WSL2/Linux, we verify via /mnt/c/ translation.
    """

    @pytest.mark.parametrize("sid", [
        sid for sid, svc in SERVICES.items() if svc.get('path')
    ])
    def test_service_path_exists(self, sid):
        path = SERVICES[sid]['path']
        # On Linux/WSL2, translate Windows paths to /mnt/c/
        if sys.platform != 'win32' and path.startswith('C:\\'):
            path = '/mnt/c/' + path[3:].replace('\\', '/')
        assert os.path.isdir(path), \
            f"{SERVICES[sid]['name']} ({sid}): path not found: {path}"


# ================================================================
# Health Check API
# ================================================================

class TestHealthCheckAPI:
    def test_services_health(self, client):
        r = client.get('/api/services/health')
        assert r.status_code == 200
        data = r.get_json()
        assert 'summary' in data
        assert 'live' in data
        assert 'total' in data
        assert 'services' in data
        assert data['total'] == len(SERVICES)

    def test_single_service_health(self, client):
        r = client.get('/api/services/health/elaine')
        assert r.status_code == 200
        data = r.get_json()
        assert data['id'] == 'elaine'
        assert data['name'] == 'Elaine'
        assert data['port'] == 5000
        assert data['status'] in ('live', 'stopped')

    def test_unknown_service_health(self, client):
        r = client.get('/api/services/health/nonexistent')
        assert r.status_code == 404


# ================================================================
# Launch API
# ================================================================

class TestLaunchAPI:
    def test_launch_unknown_service(self, client):
        r = client.post('/api/services/launch/nonexistent')
        assert r.status_code == 404

    def test_launch_no_path_service(self, client):
        """Services with no path should return not_available."""
        r = client.post('/api/services/launch/comfyui')
        assert r.status_code in (200, 404)
        data = r.get_json()
        assert data['status'] in ('not_available', 'already_running')

    def test_desktop_apps_list(self, client):
        r = client.get('/api/desktop/apps')
        assert r.status_code == 200
        data = r.get_json()
        assert len(data) > 0


# ================================================================
# Summary
# ================================================================

class TestSummary:
    def test_total_services(self):
        """Sanity check: at least 50 services registered."""
        assert len(SERVICES) >= 50, f"Only {len(SERVICES)} services registered"

    def test_ck_apps_exist(self):
        """CK apps must include core services."""
        ck_ids = [sid for sid, svc in SERVICES.items() if svc['type'] == 'ck']
        required = ['elaine', 'costanza', 'learning-assistant', 'writer', 'peterman']
        for rid in required:
            assert rid in ck_ids, f"Core CK app '{rid}' missing"

    def test_infra_services_exist(self):
        """Infrastructure services must include core infra."""
        infra_ids = [sid for sid, svc in SERVICES.items() if svc['type'] == 'infra']
        required = ['postgres', 'redis', 'ollama', 'searxng', 'n8n']
        for rid in required:
            assert rid in infra_ids, f"Core infra service '{rid}' missing"
