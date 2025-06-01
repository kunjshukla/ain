# agents/dsa_evaluator.py
import ast
import astunparse
from typing import Dict, Any, Tuple, List
import re

class DSAEvaluatorAgent:
    def __init__(self):
        self.problems = {
            "reverse_string": {
                "input_types": [str],
                "output_type": str,
                "test_cases": [
                    ("hello", "olleh"),
                    ("", ""),
                    ("a", "a"),
                    ("abc123", "321cba")
                ]
            },
            "fibonacci": {
                "input_types": [int],
                "output_type": list,
                "test_cases": [
                    (5, [0, 1, 1, 2, 3]),
                    (1, [0]),
                    (2, [0, 1]),
                    (10, [0, 1, 1, 2, 3, 5, 8, 13, 21, 34])
                ]
            },
            "palindrome": {
                "input_types": [str],
                "output_type": bool,
                "test_cases": [
                    ("racecar", True),
                    ("hello", False),
                    ("", True),
                    ("a", True),
                    ("Able was I ere I saw Elba", True)
                ]
            },
            "two_sum": {
                "input_types": [list, int],
                "output_type": list,
                "test_cases": [
                    ([2, 7, 11, 15], 9, [0, 1]),
                    ([3, 2, 4], 6, [1, 2]),
                    ([3, 3], 6, [0, 1]),
                    ([1, 2, 3, 4, 5], 9, [3, 4])
                ]
            },
            "binary_search": {
                "input_types": [list, int],
                "output_type": int,
                "test_cases": [
                    ([1, 2, 3, 4, 5], 3, 2),
                    ([1, 2, 3, 4, 5], 6, -1),
                    ([], 1, -1),
                    ([1], 1, 0)
                ]
            },
            "merge_sort": {
                "input_types": [list],
                "output_type": list,
                "test_cases": [
                    ([5, 2, 3, 1, 4], [1, 2, 3, 4, 5]),
                    ([], []),
                    ([1], [1]),
                    ([3, 1, 2, 3], [1, 2, 3, 3])
                ]
            },
            "linked_list_cycle": {
                "input_types": [str],  # Using string representation for simplicity
                "output_type": bool,
                "test_cases": [
                    ("1->2->3->1", True),
                    ("1->2->3", False),
                    ("1->1", True),
                    ("", False)
                ]
            },
            "valid_parentheses": {
                "input_types": [str],
                "output_type": bool,
                "test_cases": [
                    ("()", True),
                    ("()[]{}", True),
                    ("(]", False),
                    ("([)]", False),
                    ("{[]}", True)
                ]
            },
            "max_subarray": {
                "input_types": [list],
                "output_type": int,
                "test_cases": [
                    ([-2, 1, -3, 4, -1, 2, 1, -5, 4], 6),
                    ([1], 1),
                    ([5, 4, -1, 7, 8], 23),
                    ([-1], -1)
                ]
            },
            "word_frequency": {
                "input_types": [str],
                "output_type": dict,
                "test_cases": [
                    ("the quick brown fox jumps over the lazy dog", {"the": 2, "quick": 1, "brown": 1, "fox": 1, "jumps": 1, "over": 1, "lazy": 1, "dog": 1}),
                    ("", {}),
                    ("a a a a b b c", {"a": 4, "b": 2, "c": 1})
                ]
            },
            "longest_substring": {
                "input_types": [str],
                "output_type": int,
                "test_cases": [
                    ("abcabcbb", 3),
                    ("bbbbb", 1),
                    ("pwwkew", 3),
                    ("", 0)
                ]
            },
            "rotate_array": {
                "input_types": [list, int],
                "output_type": list,
                "test_cases": [
                    ([1, 2, 3, 4, 5, 6, 7], 3, [5, 6, 7, 1, 2, 3, 4]),
                    ([-1, -100, 3, 99], 2, [3, 99, -1, -100]),
                    ([1, 2], 1, [2, 1]),
                    ([1], 0, [1])
                ]
            }
        }
        
    def evaluate(self, code: str, problem_id: str = "reverse_string") -> Dict[str, Any]:
        if problem_id not in self.problems:
            raise ValueError(f"Unknown problem: {problem_id}")
            
        problem = self.problems[problem_id]
        
        try:
            # Parse and analyze the code
            tree = ast.parse(code)
            
            # Check for syntax errors
            try:
                ast.parse(code)
            except SyntaxError as e:
                return {
                    "correctness": 0,
                    "error": f"Syntax error: {str(e)}",
                    "time_complexity": "N/A",
                    "space_complexity": "N/A",
                    "style": 0,
                    "suggestions": ["Fix syntax errors in your code"]
                }
            
            # Run test cases
            test_results = self._run_test_cases(code, problem["test_cases"])
            correctness = sum(1 for r in test_results if r["passed"]) / len(test_results)
            
            # Analyze complexity
            time_complexity = self._analyze_time_complexity(tree)
            space_complexity = self._analyze_space_complexity(tree)
            
            # Check style
            style_score = self._check_code_style(code)
            
            return {
                "correctness": correctness,
                "test_results": test_results,
                "time_complexity": time_complexity,
                "space_complexity": space_complexity,
                "style": style_score,
                "suggestions": self._generate_suggestions(
                    correctness, 
                    time_complexity,
                    style_score
                )
            }
            
        except Exception as e:
            return {
                "correctness": 0,
                "error": f"Error during evaluation: {str(e)}",
                "time_complexity": "N/A",
                "space_complexity": "N/A",
                "style": 0,
                "suggestions": ["An error occurred during code evaluation"]
            }
    
    def _run_test_cases(self, code: str, test_cases: list) -> list:
        """Run test cases on the provided code with robust error handling"""
        results = []
        
        try:
            # Create a namespace for executing the code
            namespace = {}
            
            # Execute the code to define the function
            exec(code, namespace)
            
            # Find the function name (assuming it's the first function defined)
            function_name = None
            for name, obj in namespace.items():
                if callable(obj) and name != '__builtins__':
                    function_name = name
                    break
                    
            if not function_name:
                return [{
                    "input": str(test_case[0]),
                    "expected": str(test_case[1]),
                    "actual": "Error: No function found in code",
                    "passed": False
                } for test_case in test_cases]
            
            # Get the function object
            function = namespace[function_name]
            
            # Run each test case
            for test_case in test_cases:
                input_value, expected_output = test_case
                try:
                    # Call the function with the input value
                    actual_output = function(input_value)
                    
                    # Check if the output matches the expected output
                    passed = actual_output == expected_output
                    
                    results.append({
                        "input": str(input_value),
                        "expected": str(expected_output),
                        "actual": str(actual_output),
                        "passed": passed
                    })
                except Exception as e:
                    results.append({
                        "input": str(input_value),
                        "expected": str(expected_output),
                        "actual": f"Error: {str(e)}",
                        "passed": False
                    })
        except Exception as e:
            # Handle any errors in the test execution process
            return [{
                "input": str(test_case[0]) if len(test_case) > 0 else "Unknown",
                "expected": str(test_case[1]) if len(test_case) > 1 else "Unknown",
                "actual": f"Error in test execution: {str(e)}",
                "passed": False
            } for test_case in test_cases]
            
        return results
        
    def _analyze_time_complexity(self, tree: ast.AST) -> str:
        # Implement time complexity analysis
        return "O(n)"
        
    def _analyze_space_complexity(self, tree: ast.AST) -> str:
        # Implement space complexity analysis
        return "O(1)"
        
    def _check_code_style(self, code: str) -> float:
        # Implement style checking
        return 0.9
        
    def _generate_suggestions(self, correctness: float, time_complexity: str, style_score: float) -> List[str]:
        """Generate improvement suggestions based on evaluation results"""
        suggestions = []
        
        # Correctness suggestions
        if correctness < 0.5:
            suggestions.append("Your solution fails on multiple test cases. Review your logic carefully.")
        elif correctness < 1.0:
            suggestions.append("Your solution works for some cases but not all. Check edge cases.")
            
        # Time complexity suggestions
        if time_complexity in ["O(n²)", "O(n^2)", "O(n*n)"]:
            suggestions.append("Consider optimizing your solution for better time complexity.")
        elif time_complexity in ["O(n³)", "O(n^3)", "O(n*n*n)"]:
            suggestions.append("Your solution has high time complexity. Look for more efficient algorithms.")
            
        # Style suggestions
        if style_score < 0.7:
            suggestions.append("Improve code readability with better variable names and comments.")
            
        # If everything is good
        if correctness == 1.0 and style_score >= 0.8 and time_complexity in ["O(1)", "O(log n)", "O(n)"]:
            suggestions.append("Great job! Your solution is correct, efficient, and well-written.")
            
        # Default suggestion if none generated
        if not suggestions:
            suggestions.append("Review your solution for correctness and efficiency.")
            
        return suggestions