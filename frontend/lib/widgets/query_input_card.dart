import 'package:flutter/material.dart';

class QueryInputCard extends StatefulWidget {
  final Function(String) onQueryChanged;
  final Function() onSubmit;
  final bool isLoading;

  const QueryInputCard({
    super.key,
    required this.onQueryChanged,
    required this.onSubmit,
    required this.isLoading,
  });

  @override
  State<QueryInputCard> createState() => _QueryInputCardState();
}

class _QueryInputCardState extends State<QueryInputCard> {
  final TextEditingController _controller = TextEditingController();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
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
              'Enter your query',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            const Text(
              'Type a question or prompt to send to the LLM:',
              style: TextStyle(fontSize: 14),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _controller,
              decoration: const InputDecoration(
                hintText: 'Enter your query here...',
                border: OutlineInputBorder(),
              ),
              minLines: 3,
              maxLines: 5,
              onChanged: widget.onQueryChanged,
            ),
            const SizedBox(height: 16),
            Center(
              child: ElevatedButton(
                onPressed: widget.isLoading ? null : widget.onSubmit,
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size(200, 50),
                ),
                child: widget.isLoading
                    ? const Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                            ),
                          ),
                          SizedBox(width: 12),
                          Text('Processing...'),
                        ],
                      )
                    : const Text('Submit Query'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
