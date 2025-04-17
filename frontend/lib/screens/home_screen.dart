import 'package:flutter/material.dart';
import '../models/llm_model.dart';
import '../models/dataset.dart';
import '../services/api_service.dart';
import '../widgets/model_selection_card.dart';
import '../widgets/dataset_upload_card.dart';
import '../widgets/query_input_card.dart';
import '../widgets/response_comparison_card.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final ApiService _apiService = ApiService();

  // State variables
  List<LLMModel> _models = [];
  LLMModel? _selectedModel;
  Dataset? _selectedDataset;
  String _currentQuery = '';

  bool _isLoadingModels = true;
  bool _isProcessingQuery = false;

  String _normalResponse = '';
  String _poisonedResponse = '';
  Map<String, dynamic> _normalMetrics = {
    'poisoning_percentage': 0.0,
    'accuracy': 100.0
  };
  Map<String, dynamic> _poisonedMetrics = {
    'poisoning_percentage': 0.0,
    'accuracy': 100.0
  };
  bool _hasResponse = false;

  @override
  void initState() {
    super.initState();
    _loadModels();
  }

  Future<void> _loadModels() async {
    try {
      final models = await _apiService.getModels();

      setState(() {
        _models = models;
        _isLoadingModels = false;

        if (models.isNotEmpty) {
          _selectedModel = models.first;
        }
      });
    } catch (e) {
      setState(() {
        _isLoadingModels = false;
      });

      // Show error in snackbar
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to load models: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  void _onDatasetUploaded(Dataset dataset) {
    setState(() {
      _selectedDataset = dataset;
    });
  }

  void _onQueryChanged(String query) {
    _currentQuery = query;
  }

  Future<void> _onSubmitQuery() async {
    if (_currentQuery.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please enter a query first'),
        ),
      );
      return;
    }

    if (_selectedModel == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please select a model first'),
        ),
      );
      return;
    }

    if (_selectedDataset == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please upload a dataset first'),
        ),
      );
      return;
    }

    setState(() {
      _isProcessingQuery = true;
    });

    try {
      final result = await _apiService.processQuery(
        _currentQuery,
        _selectedModel!.id,
        _selectedDataset!.id,
      );

      setState(() {
        _normalResponse = result['normal_response'] as String;
        _poisonedResponse = result['poisoned_response'] as String;
        _normalMetrics = result['normal_metrics'] as Map<String, dynamic>;
        _poisonedMetrics = result['poisoned_metrics'] as Map<String, dynamic>;
        _hasResponse = true;
        _isProcessingQuery = false;
      });
    } catch (e) {
      setState(() {
        _isProcessingQuery = false;
      });

      // Show error in snackbar
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to process query: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('LLM Data Poisoning Demo'),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Data Poisoning Effects on LLMs',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'This demo shows how data poisoning can affect LLM responses. Upload a dataset, ask a question, and see how the responses differ between normal and poisoned models.',
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.grey,
                ),
              ),
              const SizedBox(height: 24),
              if (_isLoadingModels)
                const Center(
                  child: CircularProgressIndicator(),
                )
              else
                ModelSelectionCard(
                  models: _models,
                  selectedModel: _selectedModel,
                  onModelSelected: (model) {
                    setState(() {
                      _selectedModel = model;
                    });
                  },
                ),
              const SizedBox(height: 16),
              DatasetUploadCard(
                selectedDataset: _selectedDataset,
                onDatasetUploaded: _onDatasetUploaded,
                apiService: _apiService,
              ),
              const SizedBox(height: 16),
              QueryInputCard(
                onQueryChanged: _onQueryChanged,
                onSubmit: _onSubmitQuery,
                isLoading: _isProcessingQuery,
              ),
              const SizedBox(height: 16),
              if (_hasResponse)
                ResponseComparisonCard(
                  normalResponse: _normalResponse,
                  poisonedResponse: _poisonedResponse,
                  normalMetrics: _normalMetrics,
                  poisonedMetrics: _poisonedMetrics,
                ),
            ],
          ),
        ),
      ),
    );
  }
}
