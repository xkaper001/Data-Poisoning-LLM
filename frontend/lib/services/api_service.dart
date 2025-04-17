import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import '../models/llm_model.dart';
import '../models/dataset.dart';

class ApiService {
  static const String baseUrl = 'http://localhost:5000/api';

  /// Get available LLM models from the backend
  Future<List<LLMModel>> getModels() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/models'));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as List;
        return data
            .map((item) => LLMModel(
                  id: item['id'],
                  name: item['name'],
                ))
            .toList();
      } else {
        throw Exception('Failed to load models: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching models: $e');
    }
  }

  /// Upload a dataset file to the backend
  Future<Dataset> uploadDataset(File file) async {
    try {
      // Create a multipart request
      final request =
          http.MultipartRequest('POST', Uri.parse('$baseUrl/upload'))
            ..files.add(await http.MultipartFile.fromPath(
              'file',
              file.path,
              contentType: MediaType('application', 'octet-stream'),
            ));

      // Send the request
      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);

        return Dataset(
          id: data['dataset_id'],
          name: file.path.split('/').last,
          summaryText: data['summary'] ?? 'No summary available',
        );
      } else {
        throw Exception(
            'Failed to upload dataset: ${response.statusCode} ${response.body}');
      }
    } catch (e) {
      throw Exception('Error uploading dataset: $e');
    }
  }

  /// Process a query with both normal and poisoned LLMs
  Future<Map<String, dynamic>> processQuery(
      String query, String modelId, String datasetId) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/query'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'query': query,
          'model_id': modelId,
          'dataset_id': datasetId,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);

        // Handle the updated response format
        return {
          'query': data['query'],
          'model': data['model'],
          'normal_response': data['normal_response'] ?? 'No response available',
          'poisoned_response':
              data['poisoned_response'] ?? 'No response available',
          'normal_metrics': data['normal_metrics'] ??
              {
                'poisoning_percentage': 0.0,
                'accuracy': 100.0,
              },
          'poisoned_metrics': data['poisoned_metrics'] ??
              {
                'poisoning_percentage': 0.0,
                'accuracy': 0.0,
              },
        };
      } else {
        throw Exception('Failed to process query: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error processing query: $e');
    }
  }
}
