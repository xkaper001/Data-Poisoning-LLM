import 'package:flutter/material.dart';
import '../models/llm_model.dart';

class ModelSelectionCard extends StatelessWidget {
  final List<LLMModel> models;
  final LLMModel? selectedModel;
  final Function(LLMModel) onModelSelected;

  const ModelSelectionCard({
    super.key,
    required this.models,
    required this.selectedModel,
    required this.onModelSelected,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Select Model',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            const Text(
              'Choose the LLM model to demonstrate data poisoning effects:',
              style: TextStyle(fontSize: 14),
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<LLMModel>(
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                contentPadding:
                    EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              ),
              value: selectedModel,
              items: models.map((LLMModel model) {
                return DropdownMenuItem<LLMModel>(
                  value: model,
                  child: Text(model.name),
                );
              }).toList(),
              onChanged: (LLMModel? newValue) {
                if (newValue != null) {
                  onModelSelected(newValue);
                }
              },
              hint: const Text('Select a model'),
            ),
            const SizedBox(height: 12),
            Text(
              'Selected model: ${selectedModel?.name ?? 'None'}',
              style: const TextStyle(
                fontStyle: FontStyle.italic,
                color: Colors.grey,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
