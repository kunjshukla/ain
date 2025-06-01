PERFORMANCE_REPORT_PROMPT = """
You are a performance tracker. Based on the following data:
- Resume Feedback: {resume_feedback}
- Interview Results: {interview_results}
- DSA Results: {dsa_results}
- Behavioral Results: {behavioral_results}
Generate a final report and revision plan in the format:
Final Report:
- Overall Performance: [Summary]
- Key Strengths: [List strengths]
- Areas for Improvement: [List areas]
Revision Plan:
- Focus Areas: [List focus areas]
- Resources: [List resources]
Do not include any additional text beyond this format.
Example:
Final Report:
- Overall Performance: [Good communication but needs technical improvement]
- Key Strengths: [Clear communication, Strong behavioral answers]
- Areas for Improvement: [Technical depth, DSA accuracy]
Revision Plan:
- Focus Areas: [Practice DSA problems, Use STAR method]
- Resources: [LeetCode, STAR Method Guide]
"""