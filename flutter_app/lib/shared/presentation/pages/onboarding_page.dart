import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class OnboardingPage extends StatefulWidget {
  const OnboardingPage({super.key});

  @override
  State<OnboardingPage> createState() => _OnboardingPageState();
}

class _OnboardingPageState extends State<OnboardingPage> {
  final PageController _pageController = PageController();
  int _currentPage = 0;
  
  final List<OnboardingItem> _onboardingItems = [
    OnboardingItem(
      title: 'AI-Powered Health Analysis',
      description: 'Upload images for instant health analysis using advanced AI technology. Get insights about skin conditions, food nutrition, and more.',
      icon: Icons.camera_alt,
      color: Colors.blue,
    ),
    OnboardingItem(
      title: 'Smart Health Assistant',
      description: 'Chat with our AI assistant in multiple languages. Get personalized health advice and answers to your wellness questions.',
      icon: Icons.chat_bubble,
      color: Colors.green,
    ),
    OnboardingItem(
      title: 'Voice Interactions',
      description: 'Speak naturally with our voice-enabled AI. Perfect for hands-free health consultations and accessibility.',
      icon: Icons.mic,
      color: Colors.orange,
    ),
    OnboardingItem(
      title: 'Comprehensive History',
      description: 'Track your health journey with detailed history and reports. Export your data anytime for medical consultations.',
      icon: Icons.history,
      color: Colors.purple,
    ),
  ];

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            // Skip button
            Align(
              alignment: Alignment.topRight,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: TextButton(
                  onPressed: _skipOnboarding,
                  child: Text(
                    'Skip',
                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: Theme.of(context).colorScheme.primary,
                    ),
                  ),
                ),
              ),
            ),
            
            // Page view
            Expanded(
              child: PageView.builder(
                controller: _pageController,
                onPageChanged: (index) {
                  setState(() {
                    _currentPage = index;
                  });
                },
                itemCount: _onboardingItems.length,
                itemBuilder: (context, index) {
                  return _buildOnboardingPage(_onboardingItems[index]);
                },
              ),
            ),
            
            // Page indicators
            _buildPageIndicators(),
            
            const SizedBox(height: 32),
            
            // Navigation buttons
            _buildNavigationButtons(),
            
            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }
  
  Widget _buildOnboardingPage(OnboardingItem item) {
    return Padding(
      padding: const EdgeInsets.all(32),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // Icon
          Container(
            width: 120,
            height: 120,
            decoration: BoxDecoration(
              color: item.color.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(
              item.icon,
              size: 60,
              color: item.color,
            ),
          ),
          
          const SizedBox(height: 48),
          
          // Title
          Text(
            item.title,
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
            textAlign: TextAlign.center,
          ),
          
          const SizedBox(height: 24),
          
          // Description
          Text(
            item.description,
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
              color: Theme.of(context).colorScheme.onSurface.withOpacity(0.7),
              height: 1.5,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
  
  Widget _buildPageIndicators() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: List.generate(
        _onboardingItems.length,
        (index) => Container(
          width: _currentPage == index ? 24 : 8,
          height: 8,
          margin: const EdgeInsets.symmetric(horizontal: 4),
          decoration: BoxDecoration(
            color: _currentPage == index
                ? Theme.of(context).colorScheme.primary
                : Theme.of(context).colorScheme.primary.withOpacity(0.3),
            borderRadius: BorderRadius.circular(4),
          ),
        ),
      ),
    );
  }
  
  Widget _buildNavigationButtons() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 32),
      child: Row(
        children: [
          // Previous button
          if (_currentPage > 0)
            Expanded(
              child: OutlinedButton(
                onPressed: _previousPage,
                child: const Text('Previous'),
              ),
            )
          else
            const Expanded(child: SizedBox()),
          
          const SizedBox(width: 16),
          
          // Next/Get Started button
          Expanded(
            child: ElevatedButton(
              onPressed: _currentPage == _onboardingItems.length - 1
                  ? _completeOnboarding
                  : _nextPage,
              child: Text(
                _currentPage == _onboardingItems.length - 1
                    ? 'Get Started'
                    : 'Next',
              ),
            ),
          ),
        ],
      ),
    );
  }
  
  void _nextPage() {
    if (_currentPage < _onboardingItems.length - 1) {
      _pageController.nextPage(
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeInOut,
      );
    }
  }
  
  void _previousPage() {
    if (_currentPage > 0) {
      _pageController.previousPage(
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeInOut,
      );
    }
  }
  
  void _skipOnboarding() {
    context.go('/home');
  }
  
  void _completeOnboarding() {
    // TODO: Mark onboarding as completed in preferences
    context.go('/home');
  }
}

class OnboardingItem {
  final String title;
  final String description;
  final IconData icon;
  final Color color;
  
  OnboardingItem({
    required this.title,
    required this.description,
    required this.icon,
    required this.color,
  });
}