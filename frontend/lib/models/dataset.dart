class Dataset {
  final String id;
  final String name;
  final Map<String, dynamic> summary;

  Dataset({
    required this.id,
    required this.name,
    required this.summary,
  });

  factory Dataset.fromJson(Map<String, dynamic> json) {
    return Dataset(
      id: json['dataset_id'] as String,
      name: json['summary']['original_name'] ?? 'Unnamed Dataset',
      summary: json['summary'] as Map<String, dynamic>,
    );
  }

  String get format => summary['format'] as String? ?? 'unknown';

  String get summaryText {
    final format = this.format;

    if (summary.containsKey('error')) {
      return 'Error: ${summary['error']}';
    }

    if (format == 'text') {
      final lineCount = summary['line_count'];
      final wordCount = summary['word_count'];
      return 'Text dataset with $lineCount lines and $wordCount words';
    } else if (format == 'csv') {
      final rowCount = summary['row_count'];
      final columnCount = summary['column_count'];
      return 'CSV dataset with $rowCount rows and $columnCount columns';
    } else if (format == 'json') {
      if (summary.containsKey('record_count')) {
        final recordCount = summary['record_count'];
        return 'JSON dataset with $recordCount records';
      } else {
        return 'JSON dataset (structure: ${summary['structure'] ?? 'unknown'})';
      }
    }

    return 'Dataset format: $format';
  }
}
