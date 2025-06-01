DSA_EVALUATION_PROMPT = """
You are a DSA evaluator. Evaluate the following code solution for the problem 'Reverse a string':
Code: {code_solution}
Expected Output: If the input is "hello", the output should be "olleh".
Provide feedback in the format:
- Correctness: [Yes/No]
- Feedback: [Detailed feedback]
- Score: [Score out of 10]
Do not include any additional text beyond this format.
Example:
- Correctness: [Yes]
- Feedback: [Code correctly reverses the string using a two-pointer approach]
- Score: [8]
"""