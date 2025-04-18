import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
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

      if (result != null) {
        if (kIsWeb) {
          // For web, use bytes property instead of path
          final fileName = result.files.single.name;
          final fileBytes = result.files.single.bytes;

          if (fileBytes != null) {
            final dataset =
                await widget.apiService.uploadDatasetBytes(fileName, fileBytes);
            widget.onDatasetUploaded(dataset);
          } else {
            setState(() {
              errorMessage = 'Failed to read file data';
            });
          }
        } else {
          // For mobile/desktop, use path
          if (result.files.single.path != null) {
            final file = File(result.files.single.path!);
            final dataset = await widget.apiService.uploadDataset(file);
            widget.onDatasetUploaded(dataset);
          }
        }
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
                  Icons.upload_file,
                  color: Colors.deepPurple,
                  size: 24,
                ),
                const SizedBox(width: 8),
                const Text(
                  'Upload Dataset',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            const Text(
              'Upload a text file with data that will be used to poison the LLM:',
              style: TextStyle(fontSize: 14),
            ),
            const SizedBox(height: 20),
            Center(
              child: InkWell(
                onTap: isUploading ? null : _pickAndUploadFile,
                borderRadius: BorderRadius.circular(12),
                child: Container(
                  width: double.infinity,
                  padding: const EdgeInsets.symmetric(vertical: 20),
                  decoration: BoxDecoration(
                    border: Border.all(
                      color: Colors.deepPurple.withOpacity(0.4),
                      width: 2,
                      style: BorderStyle.solid,
                    ),
                    borderRadius: BorderRadius.circular(12),
                    color: Colors.deepPurple.withOpacity(0.05),
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        Icons.cloud_upload_rounded,
                        size: 48,
                        color: isUploading ? Colors.grey : Colors.deepPurple,
                      ),
                      const SizedBox(height: 12),
                      Text(
                        isUploading ? 'Uploading...' : 'Click to select a file',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w500,
                          color: isUploading ? Colors.grey : Colors.deepPurple,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Supports JSON, TXT, CSV',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey.shade600,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(height: 16),
            if (isUploading)
              const Center(
                child: Padding(
                  padding: EdgeInsets.symmetric(vertical: 12.0),
                  child: CircularProgressIndicator(
                    valueColor:
                        AlwaysStoppedAnimation<Color>(Colors.deepPurple),
                  ),
                ),
              )
            else if (errorMessage != null)
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.red.shade200),
                ),
                child: Row(
                  children: [
                    Icon(Icons.error_outline,
                        color: Colors.red.shade700, size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        errorMessage!,
                        style: TextStyle(color: Colors.red.shade700),
                      ),
                    ),
                  ],
                ),
              )
            else if (widget.selectedDataset != null)
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.green.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.green.shade200),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.check_circle,
                            color: Colors.green.shade700, size: 20),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            'Dataset: ${widget.selectedDataset!.name}',
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              color: Colors.green.shade700,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      widget.selectedDataset!.summaryText,
                      style: TextStyle(color: Colors.grey.shade700),
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
