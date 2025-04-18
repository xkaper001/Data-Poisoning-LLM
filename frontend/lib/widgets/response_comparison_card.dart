import 'dart:developer';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class ResponseComparisonCard extends StatelessWidget {
  final String normalResponse;
  final String poisonedResponse;
  final double poisoningPercentage;
  final double accuracy;

  const ResponseComparisonCard({
    super.key,
    required this.normalResponse,
    required this.poisonedResponse,
    required this.poisoningPercentage,
    required this.accuracy,
  });

  @override
  Widget build(BuildContext context) {
    log('Normal Response: $normalResponse');
    log('Poisoned Response: $poisonedResponse');
    log('Poisoning Percentage: $poisoningPercentage');
    log('Accuracy: $accuracy');

    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Colors.white,
              Colors.deepPurple.shade50.withOpacity(0.2),
            ],
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.compare_arrows,
                    color: Colors.deepPurple,
                    size: 28,
                  ),
                  const SizedBox(width: 12),
                  Text(
                    'Results Comparison',
                    style: TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                      color: Colors.deepPurple,
                      letterSpacing: 0.5,
                    ),
                  ),
                  const Spacer(),
                  _buildLegend(),
                ],
              ),
              const Divider(height: 32, thickness: 1),
              const Text(
                'Compare responses from normal and poisoned LLM models:',
                style: TextStyle(
                  fontSize: 15,
                  color: Colors.black87,
                ),
              ),
              const SizedBox(height: 24),
              _buildMetricsSection(context),
              const SizedBox(height: 32),
              _buildResponses(context),
              const SizedBox(height: 24),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.deepPurple.withOpacity(0.05),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.deepPurple.withOpacity(0.2)),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(
                      Icons.lightbulb_outline,
                      color: Colors.deepPurple.shade700,
                      size: 24,
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Data Poisoning Effects',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                              color: Colors.deepPurple.shade700,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Notice how data poisoning can influence model outputs. Poisoned models produce responses that align with the biased content in the poisoning dataset, reducing accuracy and potentially spreading misinformation.',
                            style: TextStyle(
                              fontSize: 14,
                              height: 1.5,
                              color: Colors.grey.shade800,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildLegend() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.grey.shade100,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 12,
            height: 12,
            decoration: BoxDecoration(
              color: Colors.blue.shade600,
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          const SizedBox(width: 4),
          const Text('Normal',
              style: TextStyle(fontSize: 12, fontWeight: FontWeight.w500, color: Colors.black)),
          const SizedBox(width: 12),
          Container(
            width: 12,
            height: 12,
            decoration: BoxDecoration(
              color: Colors.red.shade600,
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          const SizedBox(width: 4),
          const Text('Poisoned',
              style: TextStyle(fontSize: 12, fontWeight: FontWeight.w500, color: Colors.black)),
        ],
      ),
    );
  }

  Widget _buildMetricsSection(BuildContext context) {
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Colors.deepPurple.shade50,
            Colors.purple.shade50,
          ],
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.2),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 20),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            _buildMetricDisplay(
              context,
              'Response Accuracy',
              '$accuracy%',
              accuracy / 100,
              Colors.green.shade600,
              Icons.check_circle_outline,
            ),
            Container(
              height: 100,
              width: 1,
              color: Colors.grey.withOpacity(0.3),
            ),
            _buildMetricDisplay(
              context,
              'Poisoning Effect',
              '$poisoningPercentage%',
              poisoningPercentage / 100,
              Colors.red.shade600,
              Icons.warning_amber_rounded,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMetricDisplay(
    BuildContext context,
    String label,
    String value,
    double progressValue,
    Color color,
    IconData icon,
  ) {
    final screenWidth = MediaQuery.of(context).size.width;
    final isSmallScreen = screenWidth < 600;

    return Column(
      children: [
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 18, color: color),
            const SizedBox(width: 8),
            Text(
              label,
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: Colors.grey.shade800,
                fontSize: 15,
              ),
            ),
          ],
        ),
        const SizedBox(height: 14),
        SizedBox(
          width: isSmallScreen ? 100 : 120,
          height: isSmallScreen ? 100 : 120,
          child: Stack(
            alignment: Alignment.center,
            children: [
              SizedBox(
                width: isSmallScreen ? 100 : 120,
                height: isSmallScreen ? 100 : 120,
                child: CircularProgressIndicator(
                  value: progressValue,
                  strokeWidth: 10,
                  backgroundColor: Colors.grey.shade200,
                  valueColor: AlwaysStoppedAnimation<Color>(color),
                ),
              ),
              Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    value,
                    style: TextStyle(
                      fontWeight: FontWeight.w800,
                      fontSize: isSmallScreen ? 22 : 26,
                      color: color,
                    ),
                  ),
                  Container(
                    margin: const EdgeInsets.only(top: 4),
                    padding:
                        const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: color.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Text(
                      progressValue >= 0.7
                          ? 'High'
                          : progressValue >= 0.4
                              ? 'Medium'
                              : 'Low',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: color,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildResponses(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final isSmallScreen = screenWidth < 600;

    if (isSmallScreen) {
      return Column(
        children: [
          _buildResponseSection(
            'Normal LLM Response',
            normalResponse,
            Colors.blue.shade600,
            Icons.chat_bubble_outline,
          ),
          const SizedBox(height: 20),
          _buildResponseSection(
            'Poisoned LLM Response',
            poisonedResponse,
            Colors.red.shade600,
            Icons.warning_outlined,
          ),
        ],
      );
    }

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          child: _buildResponseSection(
            'Normal LLM Response',
            normalResponse,
            Colors.blue.shade600,
            Icons.chat_bubble_outline,
          ),
        ),
        const SizedBox(width: 20),
        Expanded(
          child: _buildResponseSection(
            'Poisoned LLM Response',
            poisonedResponse,
            Colors.red.shade600,
            Icons.warning_outlined,
          ),
        ),
        
        
      ],
    );
  }

  Widget _buildResponseSection(
      String title, String response, Color color, IconData icon) {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: color.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
            decoration: BoxDecoration(
              color: color.withOpacity(0.9),
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(12),
                topRight: Radius.circular(12),
              ),
            ),
            child: Row(
              children: [
                Icon(icon, color: Colors.white, size: 18),
                const SizedBox(width: 8),
                Text(
                  title,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                    fontSize: 15,
                  ),
                ),
              ],
            ),
          ),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Colors.white,
              border: Border.all(color: color.withOpacity(0.3)),
              borderRadius: const BorderRadius.only(
                bottomLeft: Radius.circular(12),
                bottomRight: Radius.circular(12),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  response,
                  style: TextStyle(
                    fontSize: 14,
                    height: 1.6,
                    color: Colors.grey.shade800,
                  ),
                ),
                const SizedBox(height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    _buildActionButton('Copy', Icons.copy, color, () {
                      Clipboard.setData(ClipboardData(text: response));
                    }),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionButton(
      String label, IconData icon, Color color, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(20),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(20),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 16, color: color),
            const SizedBox(width: 6),
            Text(
              label,
              style: TextStyle(
                fontSize: 13,
                color: color,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
