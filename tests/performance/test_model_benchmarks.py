import pytest
import asyncio

def test_skin_analysis_mean_under_2s(benchmark, skin_classifier, test_image):
    """
    Measures the core inference speed of the Skin Disease classification model.
    SLA: Must process a standard image and return predictions in under 2.0 seconds.
    """
    result = benchmark(skin_classifier.predict, test_image)
    
    assert result is not None
    assert benchmark.stats.stats.mean < 2.0, f"Skin analysis took {benchmark.stats.stats.mean}s, failing 2.0s SLA."

def test_food_analysis_mean_under_3s(benchmark, food_analyzer, test_image):
    """
    Measures the inference speed of the heavier Food-101 nutritional analysis model.
    SLA: Must process image and extract nutrition in under 3.0 seconds.
    """
    result = benchmark(food_analyzer.predict, test_image)
    
    assert result is not None
    assert benchmark.stats.stats.mean < 3.0, f"Food analysis took {benchmark.stats.stats.mean}s, failing 3.0s SLA."

def test_preprocessing_under_100ms(benchmark, classifier, large_image):
    """
    Measures the time it takes to resize, pad, and convert a large 10MB payload into a tensor.
    SLA: I/O and memory mapping must be highly optimized (<100ms).
    """
    result = benchmark(classifier.preprocess, large_image)
    
    assert result is not None
    assert benchmark.stats.stats.mean < 0.1, f"Preprocessing took {benchmark.stats.stats.mean}s, failing 100ms SLA."

def test_cache_hit_under_50ms(benchmark, cache_service, cached_result):
    """
    Measures the retrieval latency of the asynchronous Redis cache layer.
    SLA: A cache hit must resolve and deserialize JSON in under 50ms.
    """
    # Helper to run async function inside pytest-benchmark synchronously
    def run_async_cache():
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            cache_service.get_or_analyze_image(
                b"dummy_hash_bytes", 
                "skin", 
                lambda x: None
            )
        )
        
    result = benchmark(run_async_cache)
    
    assert result == cached_result
    assert benchmark.stats.stats.mean < 0.05, f"Cache hit took {benchmark.stats.stats.mean}s, failing 50ms SLA."
