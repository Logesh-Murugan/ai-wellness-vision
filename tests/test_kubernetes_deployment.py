# -*- coding: utf-8 -*-
"""Kubernetes-specific deployment tests for AI Wellness Vision system."""

import unittest
import subprocess
import json
import time
import os
from typing import Dict, List, Any


class TestKubernetesDeployment(unittest.TestCase):
    """Test Kubernetes deployment health and functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.namespace = os.getenv('K8S_NAMESPACE', 'ai-wellness-vision')
        self.kubectl_timeout = 60
        
    def run_kubectl(self, args: List[str]) -> Dict[str, Any]:
        """Run kubectl command and return parsed JSON output."""
        cmd = ['kubectl'] + args + ['-n', self.namespace, '-o', 'json']
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=self.kubectl_timeout,
                check=True
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            self.fail(f"kubectl command failed: {e.stderr}")
        except json.JSONDecodeError as e:
            self.fail(f"Failed to parse kubectl output: {e}")
    
    def test_namespace_exists(self):
        """Test that the namespace exists."""
        result = self.run_kubectl(['get', 'namespace', self.namespace])
        self.assertEqual(result['metadata']['name'], self.namespace)
    
    def test_deployments_ready(self):
        """Test that all deployments are ready."""
        result = self.run_kubectl(['get', 'deployments'])
        
        deployments = result['items']
        self.assertGreater(len(deployments), 0, "No deployments found")
        
        for deployment in deployments:
            name = deployment['metadata']['name']
            status = deployment['status']
            
            with self.subTest(deployment=name):
                # Check that deployment has desired replicas
                self.assertIn('replicas', status)
                self.assertIn('readyReplicas', status)
                
                # Check that all replicas are ready
                desired = status.get('replicas', 0)
                ready = status.get('readyReplicas', 0)
                self.assertEqual(ready, desired, 
                    f"Deployment {name} has {ready}/{desired} ready replicas")
    
    def test_pods_running(self):
        """Test that all pods are running."""
        result = self.run_kubectl(['get', 'pods'])
        
        pods = result['items']
        self.assertGreater(len(pods), 0, "No pods found")
        
        for pod in pods:
            name = pod['metadata']['name']
            status = pod['status']
            
            with self.subTest(pod=name):
                # Check pod phase
                self.assertEqual(status['phase'], 'Running', 
                    f"Pod {name} is not running: {status['phase']}")
                
                # Check container statuses
                container_statuses = status.get('containerStatuses', [])
                for container_status in container_statuses:
                    container_name = container_status['name']
                    self.assertTrue(container_status['ready'], 
                        f"Container {container_name} in pod {name} is not ready")
    
    def test_services_endpoints(self):
        """Test that services have endpoints."""
        result = self.run_kubectl(['get', 'services'])
        
        services = result['items']
        self.assertGreater(len(services), 0, "No services found")
        
        for service in services:
            name = service['metadata']['name']
            
            # Skip headless services
            if service['spec'].get('clusterIP') == 'None':
                continue
                
            with self.subTest(service=name):
                # Get endpoints for this service
                try:
                    endpoints_result = self.run_kubectl(['get', 'endpoints', name])
                    subsets = endpoints_result.get('subsets', [])
                    
                    # Check that service has endpoints
                    has_endpoints = any(
                        subset.get('addresses', []) for subset in subsets
                    )
                    self.assertTrue(has_endpoints, 
                        f"Service {name} has no endpoints")
                        
                except subprocess.CalledProcessError:
                    # Endpoints might not exist for some services
                    pass
    
    def test_persistent_volumes(self):
        """Test that persistent volumes are bound."""
        try:
            result = self.run_kubectl(['get', 'pvc'])
            pvcs = result['items']
            
            for pvc in pvcs:
                name = pvc['metadata']['name']
                status = pvc['status']
                
                with self.subTest(pvc=name):
                    self.assertEqual(status['phase'], 'Bound', 
                        f"PVC {name} is not bound: {status['phase']}")
                        
        except subprocess.CalledProcessError:
            # PVCs might not exist in all environments
            self.skipTest("No PVCs found or kubectl access denied")
    
    def test_configmaps_exist(self):
        """Test that required ConfigMaps exist."""
        expected_configmaps = [
            'ai-wellness-config',
            'prometheus-config',
            'grafana-config'
        ]
        
        result = self.run_kubectl(['get', 'configmaps'])
        configmap_names = [cm['metadata']['name'] for cm in result['items']]
        
        for expected_cm in expected_configmaps:
            with self.subTest(configmap=expected_cm):
                self.assertIn(expected_cm, configmap_names, 
                    f"ConfigMap {expected_cm} not found")
    
    def test_secrets_exist(self):
        """Test that required Secrets exist."""
        expected_secrets = [
            'ai-wellness-secrets',
            'registry-secret'
        ]
        
        result = self.run_kubectl(['get', 'secrets'])
        secret_names = [secret['metadata']['name'] for secret in result['items']]
        
        for expected_secret in expected_secrets:
            with self.subTest(secret=expected_secret):
                self.assertIn(expected_secret, secret_names, 
                    f"Secret {expected_secret} not found")
    
    def test_ingress_configuration(self):
        """Test that Ingress is properly configured."""
        try:
            result = self.run_kubectl(['get', 'ingress'])
            ingresses = result['items']
            
            self.assertGreater(len(ingresses), 0, "No ingresses found")
            
            for ingress in ingresses:
                name = ingress['metadata']['name']
                spec = ingress['spec']
                
                with self.subTest(ingress=name):
                    # Check that ingress has rules
                    self.assertIn('rules', spec)
                    self.assertGreater(len(spec['rules']), 0, 
                        f"Ingress {name} has no rules")
                    
                    # Check that rules have paths
                    for rule in spec['rules']:
                        if 'http' in rule:
                            paths = rule['http'].get('paths', [])
                            self.assertGreater(len(paths), 0, 
                                f"Ingress {name} rule has no paths")
                                
        except subprocess.CalledProcessError:
            self.skipTest("No ingresses found or kubectl access denied")
    
    def test_horizontal_pod_autoscaler(self):
        """Test that HPA is configured and working."""
        try:
            result = self.run_kubectl(['get', 'hpa'])
            hpas = result['items']
            
            for hpa in hpas:
                name = hpa['metadata']['name']
                status = hpa['status']
                
                with self.subTest(hpa=name):
                    # Check that HPA has current replicas
                    self.assertIn('currentReplicas', status)
                    
                    # Check that current replicas is within min/max bounds
                    current = status['currentReplicas']
                    min_replicas = hpa['spec']['minReplicas']
                    max_replicas = hpa['spec']['maxReplicas']
                    
                    self.assertGreaterEqual(current, min_replicas, 
                        f"HPA {name} current replicas below minimum")
                    self.assertLessEqual(current, max_replicas, 
                        f"HPA {name} current replicas above maximum")
                        
        except subprocess.CalledProcessError:
            self.skipTest("No HPAs found or kubectl access denied")
    
    def test_resource_quotas(self):
        """Test resource quotas and limits."""
        try:
            result = self.run_kubectl(['get', 'pods'])
            pods = result['items']
            
            for pod in pods:
                name = pod['metadata']['name']
                spec = pod['spec']
                
                with self.subTest(pod=name):
                    containers = spec.get('containers', [])
                    
                    for container in containers:
                        container_name = container['name']
                        resources = container.get('resources', {})
                        
                        # Check that resource requests are set
                        requests = resources.get('requests', {})
                        self.assertIn('memory', requests, 
                            f"Container {container_name} in pod {name} has no memory request")
                        self.assertIn('cpu', requests, 
                            f"Container {container_name} in pod {name} has no CPU request")
                        
                        # Check that resource limits are set
                        limits = resources.get('limits', {})
                        self.assertIn('memory', limits, 
                            f"Container {container_name} in pod {name} has no memory limit")
                        self.assertIn('cpu', limits, 
                            f"Container {container_name} in pod {name} has no CPU limit")
                            
        except subprocess.CalledProcessError:
            self.skipTest("Cannot access pod specifications")
    
    def test_network_policies(self):
        """Test that network policies are in place."""
        try:
            result = self.run_kubectl(['get', 'networkpolicies'])
            netpols = result['items']
            
            # Should have network policies for security
            self.assertGreater(len(netpols), 0, "No network policies found")
            
            for netpol in netpols:
                name = netpol['metadata']['name']
                spec = netpol['spec']
                
                with self.subTest(networkpolicy=name):
                    # Check that network policy has pod selector
                    self.assertIn('podSelector', spec)
                    
                    # Check that policy types are specified
                    self.assertIn('policyTypes', spec)
                    policy_types = spec['policyTypes']
                    self.assertGreater(len(policy_types), 0, 
                        f"Network policy {name} has no policy types")
                        
        except subprocess.CalledProcessError:
            self.skipTest("Network policies not supported or access denied")


class TestKubernetesMonitoring(unittest.TestCase):
    """Test Kubernetes monitoring setup."""
    
    def setUp(self):
        """Set up test environment."""
        self.namespace = os.getenv('K8S_NAMESPACE', 'ai-wellness-vision')
        self.kubectl_timeout = 60
    
    def run_kubectl(self, args: List[str]) -> Dict[str, Any]:
        """Run kubectl command and return parsed JSON output."""
        cmd = ['kubectl'] + args + ['-n', self.namespace, '-o', 'json']
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=self.kubectl_timeout,
                check=True
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            self.fail(f"kubectl command failed: {e.stderr}")
        except json.JSONDecodeError as e:
            self.fail(f"Failed to parse kubectl output: {e}")
    
    def test_prometheus_deployment(self):
        """Test that Prometheus is deployed and running."""
        try:
            result = self.run_kubectl(['get', 'deployment', 'prometheus'])
            status = result['status']
            
            # Check that Prometheus deployment is ready
            desired = status.get('replicas', 0)
            ready = status.get('readyReplicas', 0)
            self.assertEqual(ready, desired, 
                "Prometheus deployment not ready")
                
        except subprocess.CalledProcessError:
            self.skipTest("Prometheus deployment not found")
    
    def test_grafana_deployment(self):
        """Test that Grafana is deployed and running."""
        try:
            result = self.run_kubectl(['get', 'deployment', 'grafana'])
            status = result['status']
            
            # Check that Grafana deployment is ready
            desired = status.get('replicas', 0)
            ready = status.get('readyReplicas', 0)
            self.assertEqual(ready, desired, 
                "Grafana deployment not ready")
                
        except subprocess.CalledProcessError:
            self.skipTest("Grafana deployment not found")
    
    def test_alertmanager_deployment(self):
        """Test that Alertmanager is deployed and running."""
        try:
            result = self.run_kubectl(['get', 'deployment', 'alertmanager'])
            status = result['status']
            
            # Check that Alertmanager deployment is ready
            desired = status.get('replicas', 0)
            ready = status.get('readyReplicas', 0)
            self.assertEqual(ready, desired, 
                "Alertmanager deployment not ready")
                
        except subprocess.CalledProcessError:
            self.skipTest("Alertmanager deployment not found")


if __name__ == "__main__":
    unittest.main(verbosity=2)