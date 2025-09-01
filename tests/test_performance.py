# test_performance.py - Performance and load testing
import unittest
import asyncio
import time
import threading
import concurrent.futures
from unittest.mock import MagicMock, AsyncMock
import statistics

from src.api.gateway import ServiceOrchestrator, AnalysisRequest, ChatRequest

class TestPerformanceMetrics(unittest.TestCase):
    """Test performance metrics and response times"""
    
    def setUp(self):
        try:
            self.orchestrator = ServiceOrchestrator()
        except Exception as e:
            self.skipTest(f"Service orchestrator initialization failed: {e}")
    
    def test_chat_response_time(self):
        """Test chat response time performance"""
        async def run_test():
            response_times = []
            
            for i in range(10):
                start_time = time.time()
                
                chat_request = ChatRequest(
                    message=f"Performance test message {i}",
                    session_id=f"perf_session_{i}",
                    language="en"
                )
                
                result = await self.orchestrator.process_chat_message(chat_request)
                
                end_time = time.time()
                response_time = end_time - start_time
                response_times.append(response_time)
                
                self.assertEqual(result['status'], 'success')
            
            # Performance assertions
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            
            self.assertLess(avg_response_time, 3.0, "Average response time should be under 3 seconds")
            self.assertLess(max_response_time, 10.0, "Max response time should be under 10 seconds")
            
            print(f"Chat Performance - Avg: {avg_response_time:.2f}s, Max: {max_response_time:.2f}s")
        
        asyncio.run(run_test())
    
    def test_image_analysis_response_time(self):
        """Test image analysis response time performance"""
        async def run_test():
            response_times = []
            
            for i in range(5):  # Fewer iterations for image analysis
                mock_file = MagicMock()
                mock_file.filename = f"perf_test_{i}.jpg"
                mock_file.read = AsyncMock(return_value=b"mock image data" * 1000)  # Larger mock data
                
                start_time = time.time()
                
                analysis_request = AnalysisRequest(
                    analysis_type="skin_condition",
                    session_id=f"img_perf_session_{i}",
                    language="en"
                )
                
                result = await self.orchestrator.process_image_analysis(mock_file, analysis_request)
                
                end_time = time.time()
                response_time = end_time - start_time
                response_times.append(response_time)
                
                self.assertEqual(result['status'], 'success')
            
            # Performance assertions
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            
            self.assertLess(avg_response_time, 15.0, "Average image analysis time should be under 15 seconds")
            self.assertLess(max_response_time, 30.0, "Max image analysis time should be under 30 seconds")
            
            print(f"Image Analysis Performance - Avg: {avg_response_time:.2f}s, Max: {max_response_time:.2f}s")
        
        asyncio.run(run_test())
    
    def test_concurrent_request_performance(self):
        """Test performance under concurrent load"""
        async def run_test():
            num_concurrent = 20
            start_time = time.time()
            
            # Create concurrent chat requests
            tasks = []
            for i in range(num_concurrent):
                chat_request = ChatRequest(
                    message=f"Concurrent test {i}",
                    session_id=f"concurrent_perf_{i}",
                    language="en"
                )
                tasks.append(self.orchestrator.process_chat_message(chat_request))
            
            # Execute all requests concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            total_time = time.time() - start_time
            
            # Count successful requests
            successful = sum(1 for r in results if not isinstance(r, Exception) and r.get('status') == 'success')
            
            # Performance assertions
            self.assertEqual(successful, num_concurrent, "All concurrent requests should succeed")
            self.assertLess(total_time, 60.0, "Concurrent requests should complete within 60 seconds")
            
            throughput = num_concurrent / total_time
            self.assertGreater(throughput, 0.5, "Should handle at least 0.5 requests per second")
            
            print(f"Concurrent Performance - {num_concurrent} requests in {total_time:.2f}s, Throughput: {throughput:.2f} req/s")
        
        asyncio.run(run_test())
    
    def test_memory_usage_stability(self):
        """Test memory usage remains stable under load"""
        import psutil
        import os
        
        async def run_test():
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Create many sessions to test memory stability
            for i in range(50):
                chat_request = ChatRequest(
                    message=f"Memory test {i}",
                    session_id=f"memory_test_{i}",
                    language="en"
                )
                
                result = await self.orchestrator.process_chat_message(chat_request)
                self.assertEqual(result['status'], 'success')
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # Memory should not increase excessively
            self.assertLess(memory_increase, 100, "Memory increase should be less than 100MB")
            
            print(f"Memory Usage - Initial: {initial_memory:.1f}MB, Final: {final_memory:.1f}MB, Increase: {memory_increase:.1f}MB")
        
        try:
            asyncio.run(run_test())
        except ImportError:
            self.skipTest("psutil not available for memory testing")
    
    def test_session_cleanup_performance(self):
        """Test session cleanup doesn't impact performance"""
        async def run_test():
            # Create many sessions
            session_ids = []
            for i in range(30):
                session_id = f"cleanup_test_{i}"
                session_ids.append(session_id)
                
                chat_request = ChatRequest(
                    message=f"Cleanup test {i}",
                    session_id=session_id,
                    language="en"
                )
                
                result = await self.orchestrator.process_chat_message(chat_request)
                self.assertEqual(result['status'], 'success')
            
            # Verify sessions were created
            initial_session_count = len(self.orchestrator.active_sessions)
            self.assertGreaterEqual(initial_session_count, 30)
            
            # Test performance after session creation
            start_time = time.time()
            
            chat_request = ChatRequest(
                message="Performance test after many sessions",
                session_id="post_cleanup_test",
                language="en"
            )
            
            result = await self.orchestrator.process_chat_message(chat_request)
            
            response_time = time.time() - start_time
            
            self.assertEqual(result['status'], 'success')
            self.assertLess(response_time, 5.0, "Response time should not degrade with many sessions")
        
        asyncio.run(run_test())

class TestLoadTesting(unittest.TestCase):
    """Load testing scenarios"""
    
    def setUp(self):
        try:
            self.orchestrator = ServiceOrchestrator()
        except Exception as e:
            self.skipTest(f"Service orchestrator initialization failed: {e}")
    
    def test_sustained_load(self):
        """Test system under sustained load"""
        async def run_test():
            duration = 30  # seconds
            request_interval = 0.5  # seconds between requests
            
            start_time = time.time()
            request_count = 0
            successful_requests = 0
            
            while time.time() - start_time < duration:
                try:
                    chat_request = ChatRequest(
                        message=f"Sustained load test {request_count}",
                        session_id=f"sustained_load_{request_count % 10}",  # Reuse 10 sessions
                        language="en"
                    )
                    
                    result = await self.orchestrator.process_chat_message(chat_request)
                    
                    if result.get('status') == 'success':
                        successful_requests += 1
                    
                    request_count += 1
                    
                    # Wait before next request
                    await asyncio.sleep(request_interval)
                    
                except Exception as e:
                    print(f"Request {request_count} failed: {e}")
                    request_count += 1
            
            success_rate = successful_requests / request_count if request_count > 0 else 0
            
            # Performance assertions
            self.assertGreater(success_rate, 0.9, "Success rate should be above 90%")
            self.assertGreater(request_count, 50, "Should handle at least 50 requests in 30 seconds")
            
            print(f"Sustained Load - {request_count} requests, {successful_requests} successful, {success_rate:.2%} success rate")
        
        asyncio.run(run_test())
    
    def test_burst_load(self):
        """Test system handling burst load"""
        async def run_test():
            burst_size = 50
            
            # Create burst of requests
            tasks = []
            for i in range(burst_size):
                chat_request = ChatRequest(
                    message=f"Burst test {i}",
                    session_id=f"burst_session_{i % 5}",  # Use 5 sessions
                    language="en"
                )
                tasks.append(self.orchestrator.process_chat_message(chat_request))
            
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total_time = time.time() - start_time
            
            # Count successful requests
            successful = sum(1 for r in results if not isinstance(r, Exception) and r.get('status') == 'success')
            
            success_rate = successful / burst_size
            
            # Performance assertions
            self.assertGreater(success_rate, 0.8, "Should handle at least 80% of burst requests")
            self.assertLess(total_time, 120.0, "Burst should complete within 2 minutes")
            
            print(f"Burst Load - {burst_size} requests, {successful} successful, {success_rate:.2%} success rate in {total_time:.2f}s")
        
        asyncio.run(run_test())

class TestScalabilityMetrics(unittest.TestCase):
    """Test scalability characteristics"""
    
    def setUp(self):
        try:
            self.orchestrator = ServiceOrchestrator()
        except Exception as e:
            self.skipTest(f"Service orchestrator initialization failed: {e}")
    
    def test_session_scalability(self):
        """Test system scalability with increasing sessions"""
        async def run_test():
            session_counts = [10, 25, 50, 100]
            performance_metrics = []
            
            for session_count in session_counts:
                start_time = time.time()
                
                # Create requests for multiple sessions
                tasks = []
                for i in range(session_count):
                    chat_request = ChatRequest(
                        message=f"Scalability test for session {i}",
                        session_id=f"scale_session_{i}",
                        language="en"
                    )
                    tasks.append(self.orchestrator.process_chat_message(chat_request))
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                total_time = time.time() - start_time
                
                successful = sum(1 for r in results if not isinstance(r, Exception) and r.get('status') == 'success')
                throughput = successful / total_time
                
                performance_metrics.append({
                    'sessions': session_count,
                    'time': total_time,
                    'successful': successful,
                    'throughput': throughput
                })
                
                print(f"Sessions: {session_count}, Time: {total_time:.2f}s, Throughput: {throughput:.2f} req/s")
            
            # Verify scalability doesn't degrade significantly
            first_throughput = performance_metrics[0]['throughput']
            last_throughput = performance_metrics[-1]['throughput']
            
            # Throughput shouldn't drop below 50% of initial
            self.assertGreater(last_throughput, first_throughput * 0.5, 
                             "Throughput shouldn't degrade more than 50% with scale")
        
        asyncio.run(run_test())
    
    def test_mixed_workload_performance(self):
        """Test performance with mixed workload (chat + image analysis)"""
        async def run_test():
            num_chat_requests = 20
            num_image_requests = 5
            
            tasks = []
            
            # Add chat requests
            for i in range(num_chat_requests):
                chat_request = ChatRequest(
                    message=f"Mixed workload chat {i}",
                    session_id=f"mixed_chat_{i}",
                    language="en"
                )
                tasks.append(self.orchestrator.process_chat_message(chat_request))
            
            # Add image analysis requests
            for i in range(num_image_requests):
                mock_file = MagicMock()
                mock_file.filename = f"mixed_test_{i}.jpg"
                mock_file.read = AsyncMock(return_value=b"mock image data")
                
                analysis_request = AnalysisRequest(
                    analysis_type="skin_condition",
                    session_id=f"mixed_image_{i}",
                    language="en"
                )
                
                tasks.append(self.orchestrator.process_image_analysis(mock_file, analysis_request))
            
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total_time = time.time() - start_time
            
            successful = sum(1 for r in results if not isinstance(r, Exception) and r.get('status') == 'success')
            total_requests = num_chat_requests + num_image_requests
            
            success_rate = successful / total_requests
            throughput = successful / total_time
            
            # Performance assertions
            self.assertGreater(success_rate, 0.9, "Mixed workload should have >90% success rate")
            self.assertLess(total_time, 180.0, "Mixed workload should complete within 3 minutes")
            
            print(f"Mixed Workload - {total_requests} requests, {successful} successful, {success_rate:.2%} success rate, {throughput:.2f} req/s")
        
        asyncio.run(run_test())

if __name__ == '__main__':
    unittest.main()