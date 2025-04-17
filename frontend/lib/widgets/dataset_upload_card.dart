import 'dart:io';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import '../models/dataset.dart';
import '../services/api_service.dart';

class DatasetUploadCard extends StatefulWidget {
  final Dataset? selectedDataset;
  final Function(Dataset) onDatasetUploaded;
  final ApiService apiService;

  const DatasetUploadCard({
    super.key,
    required this.selectedDataset,
    required this.onDatasetUploaded,
    required this.apiService,
  });

  @override
  State<DatasetUploadCard> createState() => _DatasetUploadCardState();
}

class _DatasetUploadCardState extends State<DatasetUploadCard> {
  bool isUploading = false;
  String? errorMessage;

  Future<void> _pickAndUploadFile() async {
    setState(() {
      isUploading = true;
      errorMessage = null;
    });

    try {
      FilePickerResult? result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['json', 'txt', 'csv'],
      );

      if (result != null && result.files.single.path != null) {
        final file = File(result.files.single.path!);
        final dataset = await widget.apiService.uploadDataset(file);
        
        widget.onDatasetUploaded(dataset);
      } else {
        // User canceled the picker
      }
    } catch (e) {
      setState(() {
        errorMessage = 'Failed to upload: $e';
      });
    } finally {
      setState(() {
        isUploading = false;
      });
    }
  }

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
              'Upload Poisoning Dataset',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            const Text(
              'Upload a text file with data that will be used to poison the LLM:',
              style: TextStyle(fontSize: 14),
            ),
            const SizedBox(height: 16),
            Center(
              child: ElevatedButton.icon(
                onPressed: isUploading ? null : _pickAndUploadFile,
                icon: const Icon(Icons.upload_file),
                label: Text(isUploading ? 'Uploading...' : 'Choose File'),
              ),
            ),
            const SizedBox(height: 12),
            if (isUploading)
              const Center(child: CircularProgressIndicator())
            else if (errorMessage != null)
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.red.shade100,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  errorMessage!,
                  style: TextStyle(color: Colors.red.shade900),
                ),
              )
            else if (widget.selectedDataset != null)
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.green.shade50,
                  borderRadius: BorderRadius.circular(4),
                  border: Border.all(color: Colors.green.shade200),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Dataset: ${widget.selectedDataset!.name}',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 4),
                    Text(widget.selectedDataset!.summaryText),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }
}