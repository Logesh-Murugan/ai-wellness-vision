import 'dart:convert';
import 'package:http/http.dart' as http;

void main() async {
  print('🧪 Testing Flutter Chat Connection...');
  
  try {
    final response = await http.post(
      Uri.parse('http://localhost:8000/api/v1/chat/send'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'message': 'How can I sleep better?',
        'conversation_id': 'flutter_test_123',
      }),
    );
    
    print('📡 Response Status: ${response.statusCode}');
    
    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      final aiResponse = data['ai_response']['content'];
      
      print('✅ SUCCESS! Chat is working from Flutter');
      print('🤖 AI Response Length: ${aiResponse.length} characters');
      print('🤖 AI Response Preview: ${aiResponse.substring(0, 100)}...');
    } else {
      print('❌ Error: ${response.statusCode}');
      print('❌ Body: ${response.body}');
    }
  } catch (e) {
    print('❌ Connection Error: $e');
  }
}