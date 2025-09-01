# test_runner.py - Comprehensive test runner with coverage and reporting
import unittest
import sys
import os
import time
import json
from pathlib import Path
from io import StringIO

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestResult:
    """Custom test result class for detailed reporting"""
    
    def __init__(self):
        self.tests_run = 0
        self.failures = []
        self.errors = []
        self.skipped = []
        self.successes = []
        self.start_time = None
        self.end_time = None
    
    def start_test(self, test):
        self.start_time = time.time()
    
    def add_success(self, test):
        self.tests_run += 1
        self.successes.append(test)
    
    def add_failure(self, test, traceback):
        self.tests_run += 1
        self.failures.append((test, traceback))
    
    def add_error(self, test, traceback):
        self.tests_run += 1
        self.errors.append((test, traceback))
    
    def add_skip(self, test, reason):
        self.skipped.append((test, reason))
    
    def stop_test(self, test):
        self.end_time = time.time()
    
    def get_duration(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0
    
    def get_success_rate(self):
        if self.tests_run == 0:
            return 0
        return len(self.successes) / self.tests_run * 100

class ComprehensiveTestRunner:
    """Comprehensive test runner with detailed reporting"""
    
    def __init__(self, verbosity=2):
        self.verbosity = verbosity
        self.test_modules = [
            'test_models',
            'test_config',
            'test_auth',
            'test_api_gateway',
            'test_middleware',
            'test_image_service',
            'test_nlp_service',
            'test_speech_service',
            'test_explainable_ai_service',
            'test_ui',
            'test_integration_api',
            'test_integration_offline',
            'test_security_comprehensive',
            'test_security_integration',
            'test_health_monitoring',
            'test_error_handling',
            'test_enhanced_logging',
            'test_model_optimization',
            'test_offline_mode',
            'test_performance',
            'test_multilingual',
            'test_accessibility',
            'test_integration_comprehensive'
        ]
        self.results = {}
    
    def discover_tests(self):
        """Discover all test modules"""
        test_dir = Path(__file__).parent
        discovered_modules = []
        
        for module_name in self.test_modules:
            module_path = test_dir / f"{module_name}.py"
            if module_path.exists():
                discovered_modules.append(module_name)
            else:
                print(f"Warning: Test module {module_name} not found")
        
        return discovered_modules
    
    def run_test_module(self, module_name):
        """Run tests for a specific module"""
        print(f"\n{'='*60}")
        print(f"Running tests for: {module_name}")
        print(f"{'='*60}")
        
        try:
            # Import the test module
            test_module = __import__(module_name)
            
            # Create test suite
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(test_module)
            
            # Run tests
            stream = StringIO()
            runner = unittest.TextTestRunner(
                stream=stream,
                verbosity=self.verbosity,
                buffer=True
            )
            
            start_time = time.time()
            result = runner.run(suite)
            end_time = time.time()
            
            # Store results
            self.results[module_name] = {
                'tests_run': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors),
                'skipped': len(result.skipped),
                'success_count': result.testsRun - len(result.failures) - len(result.errors),
                'duration': end_time - start_time,
                'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0,
                'output': stream.getvalue()
            }
            
            # Print summary
            print(f"Tests run: {result.testsRun}")
            print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
            print(f"Failures: {len(result.failures)}")
            print(f"Errors: {len(result.errors)}")
            print(f"Skipped: {len(result.skipped)}")
            print(f"Duration: {end_time - start_time:.2f}s")
            print(f"Success Rate: {self.results[module_name]['success_rate']:.1f}%")
            
            # Print failures and errors if any
            if result.failures:
                print(f"\nFailures in {module_name}:")
                for test, traceback in result.failures:
                    print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
            
            if result.errors:
                print(f"\nErrors in {module_name}:")
                for test, traceback in result.errors:
                    print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
            
            return result
            
        except ImportError as e:
            print(f"Could not import {module_name}: {e}")
            self.results[module_name] = {
                'tests_run': 0,
                'failures': 0,
                'errors': 1,
                'skipped': 0,
                'success_count': 0,
                'duration': 0,
                'success_rate': 0,
                'output': f"Import error: {e}"
            }
            return None
        except Exception as e:
            print(f"Error running tests for {module_name}: {e}")
            self.results[module_name] = {
                'tests_run': 0,
                'failures': 0,
                'errors': 1,
                'skipped': 0,
                'success_count': 0,
                'duration': 0,
                'success_rate': 0,
                'output': f"Runtime error: {e}"
            }
            return None
    
    def run_all_tests(self):
        """Run all discovered tests"""
        print("AI WellnessVision - Comprehensive Test Suite")
        print("=" * 60)
        
        discovered_modules = self.discover_tests()
        print(f"Discovered {len(discovered_modules)} test modules")
        
        overall_start_time = time.time()
        
        for module_name in discovered_modules:
            self.run_test_module(module_name)
        
        overall_end_time = time.time()
        
        # Generate comprehensive report
        self.generate_report(overall_end_time - overall_start_time)
    
    def run_specific_tests(self, test_categories):
        """Run specific test categories"""
        category_mapping = {
            'unit': ['test_models', 'test_config', 'test_auth'],
            'integration': ['test_integration_api', 'test_integration_comprehensive'],
            'performance': ['test_performance'],
            'multilingual': ['test_multilingual'],
            'accessibility': ['test_accessibility'],
            'security': ['test_security_comprehensive', 'test_security_integration'],
            'services': ['test_image_service', 'test_nlp_service', 'test_speech_service', 'test_explainable_ai_service'],
            'ui': ['test_ui'],
            'api': ['test_api_gateway', 'test_middleware']
        }
        
        modules_to_run = []
        for category in test_categories:
            if category in category_mapping:
                modules_to_run.extend(category_mapping[category])
            else:
                print(f"Unknown test category: {category}")
        
        # Remove duplicates
        modules_to_run = list(set(modules_to_run))
        
        print(f"Running {len(modules_to_run)} test modules for categories: {', '.join(test_categories)}")
        
        overall_start_time = time.time()
        
        for module_name in modules_to_run:
            if module_name in self.test_modules:
                self.run_test_module(module_name)
        
        overall_end_time = time.time()
        
        self.generate_report(overall_end_time - overall_start_time)
    
    def generate_report(self, total_duration):
        """Generate comprehensive test report"""
        print(f"\n{'='*80}")
        print("COMPREHENSIVE TEST REPORT")
        print(f"{'='*80}")
        
        # Calculate overall statistics
        total_tests = sum(r['tests_run'] for r in self.results.values())
        total_successes = sum(r['success_count'] for r in self.results.values())
        total_failures = sum(r['failures'] for r in self.results.values())
        total_errors = sum(r['errors'] for r in self.results.values())
        total_skipped = sum(r['skipped'] for r in self.results.values())
        
        overall_success_rate = (total_successes / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Overall Statistics:")
        print(f"  Total Tests Run: {total_tests}")
        print(f"  Successes: {total_successes}")
        print(f"  Failures: {total_failures}")
        print(f"  Errors: {total_errors}")
        print(f"  Skipped: {total_skipped}")
        print(f"  Success Rate: {overall_success_rate:.1f}%")
        print(f"  Total Duration: {total_duration:.2f}s")
        
        # Module-by-module breakdown
        print(f"\nModule Breakdown:")
        print(f"{'Module':<30} {'Tests':<8} {'Success':<8} {'Fail':<6} {'Error':<6} {'Skip':<6} {'Rate':<8} {'Time':<8}")
        print("-" * 80)
        
        for module_name, result in self.results.items():
            print(f"{module_name:<30} {result['tests_run']:<8} {result['success_count']:<8} "
                  f"{result['failures']:<6} {result['errors']:<6} {result['skipped']:<6} "
                  f"{result['success_rate']:<7.1f}% {result['duration']:<7.2f}s")
        
        # Performance analysis
        print(f"\nPerformance Analysis:")
        if self.results:
            slowest_module = max(self.results.items(), key=lambda x: x[1]['duration'])
            fastest_module = min(self.results.items(), key=lambda x: x[1]['duration'])
            
            print(f"  Slowest Module: {slowest_module[0]} ({slowest_module[1]['duration']:.2f}s)")
            print(f"  Fastest Module: {fastest_module[0]} ({fastest_module[1]['duration']:.2f}s)")
        
        # Quality metrics
        print(f"\nQuality Metrics:")
        modules_with_failures = sum(1 for r in self.results.values() if r['failures'] > 0)
        modules_with_errors = sum(1 for r in self.results.values() if r['errors'] > 0)
        
        print(f"  Modules with Failures: {modules_with_failures}/{len(self.results)}")
        print(f"  Modules with Errors: {modules_with_errors}/{len(self.results)}")
        
        # Coverage estimation (simplified)
        print(f"\nCoverage Estimation:")
        covered_components = []
        if any('models' in name for name in self.results.keys()):
            covered_components.append("Data Models")
        if any('service' in name for name in self.results.keys()):
            covered_components.append("AI Services")
        if any('api' in name for name in self.results.keys()):
            covered_components.append("API Layer")
        if any('ui' in name for name in self.results.keys()):
            covered_components.append("User Interface")
        if any('integration' in name for name in self.results.keys()):
            covered_components.append("Integration")
        if any('performance' in name for name in self.results.keys()):
            covered_components.append("Performance")
        if any('multilingual' in name for name in self.results.keys()):
            covered_components.append("Multilingual")
        if any('accessibility' in name for name in self.results.keys()):
            covered_components.append("Accessibility")
        if any('security' in name for name in self.results.keys()):
            covered_components.append("Security")
        
        print(f"  Covered Components: {', '.join(covered_components)}")
        
        # Save detailed report to file
        self.save_report_to_file(total_duration)
        
        # Final assessment
        print(f"\n{'='*80}")
        if overall_success_rate >= 90:
            print("✅ EXCELLENT: Test suite shows high quality and reliability")
        elif overall_success_rate >= 75:
            print("✅ GOOD: Test suite shows good quality with some areas for improvement")
        elif overall_success_rate >= 60:
            print("⚠️  FAIR: Test suite shows moderate quality, improvements needed")
        else:
            print("❌ POOR: Test suite shows significant issues, major improvements required")
        
        print(f"{'='*80}")
    
    def save_report_to_file(self, total_duration):
        """Save detailed report to JSON file"""
        report_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_duration': total_duration,
            'overall_stats': {
                'total_tests': sum(r['tests_run'] for r in self.results.values()),
                'total_successes': sum(r['success_count'] for r in self.results.values()),
                'total_failures': sum(r['failures'] for r in self.results.values()),
                'total_errors': sum(r['errors'] for r in self.results.values()),
                'total_skipped': sum(r['skipped'] for r in self.results.values()),
            },
            'module_results': self.results
        }
        
        report_file = Path(__file__).parent / 'test_report.json'
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\nDetailed report saved to: {report_file}")

def main():
    """Main test runner function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI WellnessVision Comprehensive Test Runner')
    parser.add_argument('--categories', nargs='+', 
                       choices=['unit', 'integration', 'performance', 'multilingual', 
                               'accessibility', 'security', 'services', 'ui', 'api'],
                       help='Specific test categories to run')
    parser.add_argument('--verbosity', type=int, default=2, choices=[0, 1, 2],
                       help='Test output verbosity level')
    
    args = parser.parse_args()
    
    runner = ComprehensiveTestRunner(verbosity=args.verbosity)
    
    if args.categories:
        runner.run_specific_tests(args.categories)
    else:
        runner.run_all_tests()

if __name__ == '__main__':
    main()