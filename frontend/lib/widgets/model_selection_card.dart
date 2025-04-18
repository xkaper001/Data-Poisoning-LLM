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
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(
                  Icons.model_training,
                  color: Colors.deepPurple,
                  size: 24,
                ),
                const SizedBox(width: 8),
                const Text(
                  'Select Model',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            const Text(
              'Choose the LLM model to demonstrate data poisoning effects:',
              style: TextStyle(fontSize: 14),
            ),
            const SizedBox(height: 20),
            DropdownButtonFormField<LLMModel>(
              decoration: InputDecoration(
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(10),
                  borderSide:
                      const BorderSide(color: Colors.deepPurple, width: 1.5),
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(10),
                  borderSide:
                      BorderSide(color: Colors.grey.shade300, width: 1.5),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(10),
                  borderSide:
                      const BorderSide(color: Colors.deepPurple, width: 2),
                ),
                filled: true,
                fillColor: Colors.grey.shade50,
                contentPadding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                prefixIcon:
                    const Icon(Icons.psychology, color: Colors.deepPurple),
              ),
              value: selectedModel,
              items: models.map((LLMModel model) {
                return DropdownMenuItem<LLMModel>(
                  value: model,
                  child: Text(
                    model.name,
                    style: const TextStyle(
                      fontWeight: FontWeight.w500,
                      color: Colors.deepPurple,
                    ),
                  ),
                );
              }).toList(),
              onChanged: (LLMModel? newValue) {
                if (newValue != null) {
                  onModelSelected(newValue);
                }
              },
              hint: const Text('Select a model'),
              icon: const Icon(Icons.arrow_drop_down_circle,
                  color: Colors.deepPurple),
              dropdownColor: Colors.white,
              isExpanded: true,
            ),
            const SizedBox(height: 16),
            if (selectedModel != null)
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.deepPurple.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.deepPurple.withOpacity(0.2)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.check_circle,
                        color: Colors.deepPurple, size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Selected: ${selectedModel?.name ?? 'None'}',
                        style: const TextStyle(
                          fontWeight: FontWeight.w500,
                          color: Colors.deepPurple,
                        ),
                      ),
                    ),
                  ],
                ),
              )
            else
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.orange.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.orange.withOpacity(0.2)),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.info_outline, color: Colors.orange, size: 20),
                    SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'No model selected yet',
                        style: TextStyle(
                          fontStyle: FontStyle.italic,
                          color: Colors.orange,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }
}
