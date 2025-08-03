# Project 3 MVP: Adaptive Code Intelligence Engine
# AI-powered code analysis, pattern recognition, and personalized development assistance

import ast
import os
import re
import sqlite3
import hashlib
import time
import json
import statistics
from typing import Dict, List, Tuple, Optional, Set, Any, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
from pathlib import Path
import difflib

# Core Data Structures
@dataclass
class CodePattern:
    """Represents a code pattern learned from analysis"""
    pattern_id: str
    pattern_type: str  # 'function', 'class', 'loop', 'conditional', 'import', 'exception'
    pattern_signature: str
    frequency: int
    complexity_score: float
    bug_likelihood: float
    performance_impact: float
    last_seen: float
    contexts: List[str]

@dataclass
class CodeSuggestion:
    """Represents an AI-generated code suggestion"""
    suggestion_id: str
    target_location: str  # file:line:column
    suggestion_type: str  # 'optimization', 'bug_fix', 'style', 'refactor'
    original_code: str
    suggested_code: str
    confidence: float
    reasoning: str
    pattern_references: List[str]
    created_at: float

@dataclass
class DeveloperProfile:
    """Represents a developer's coding patterns and preferences"""
    developer_id: str
    coding_style: Dict[str, Any]
    common_patterns: List[str]
    error_patterns: List[str]
    productivity_metrics: Dict[str, float]
    language_preferences: Dict[str, float]
    framework_usage: Dict[str, int]
    last_updated: float

@dataclass
class BugPrediction:
    """Represents a predicted bug or code issue"""
    prediction_id: str
    file_path: str
    line_number: int
    issue_type: str  # 'syntax', 'logic', 'performance', 'security', 'style'
    severity: str    # 'low', 'medium', 'high', 'critical'
    description: str
    suggested_fix: str
    confidence: float
    patterns_triggered: List[str]
    created_at: float

class CodeAnalyzer:
    """Advanced code analysis engine with pattern recognition"""
    
    def __init__(self):
        self.ast_parser = ast
        self.complexity_weights = {
            'if': 1, 'for': 2, 'while': 2, 'try': 1, 'except': 1,
            'with': 1, 'lambda': 1, 'comprehension': 2, 'nested_function': 3
        }
        
        # Common anti-patterns and bug indicators
        self.bug_patterns = {
            'unused_variable': r'^\s*(\w+)\s*=.*$(?!\n.*\1)',
            'duplicate_code': r'(.{20,})\n(?:.*\n)*?\1',
            'long_line': r'^.{120,}$',
            'deep_nesting': r'^(\s{12,})',
            'magic_number': r'\b(?<![\w.])\d{2,}\b(?![\w.])',
            'bare_except': r'except\s*:',
            'mutable_default': r'def\s+\w+\([^)]*=\s*[\[\{]',
            'global_variable': r'^\s*global\s+\w+',
        }
        
        # Performance optimization patterns
        self.optimization_patterns = {
            'list_comprehension': r'for\s+\w+\s+in\s+.*:\s*\n\s*.*\.append\(',
            'string_concatenation': r'\w+\s*\+=\s*["\'].*["\']',
            'inefficient_membership': r'\w+\s+in\s+\[.*\]',
            'repeated_calculation': r'(\w+\([^)]*\)).*\n.*\1',
        }

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a Python file and extract comprehensive metrics"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            # Extract comprehensive metrics
            analysis = {
                'file_path': file_path,
                'lines_of_code': len(content.splitlines()),
                'complexity': self._calculate_complexity(tree),
                'patterns': self._extract_patterns(tree, content),
                'functions': self._analyze_functions(tree),
                'classes': self._analyze_classes(tree),
                'imports': self._analyze_imports(tree),
                'potential_bugs': self._detect_potential_bugs(content),
                'optimization_opportunities': self._find_optimizations(content),
                'code_quality_score': 0.0,  # Will be calculated
                'analyzed_at': time.time()
            }
            
            # Calculate overall quality score
            analysis['code_quality_score'] = self._calculate_quality_score(analysis)
            
            return analysis
            
        except Exception as e:
            return {
                'file_path': file_path,
                'error': str(e),
                'analyzed_at': time.time()
            }
    
    def _calculate_complexity(self, tree: ast.AST) -> Dict[str, int]:
        """Calculate cyclomatic complexity and other metrics"""
        complexity = defaultdict(int)
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For)):
                complexity['cyclomatic'] += 1
            elif isinstance(node, ast.Try):
                complexity['try_blocks'] += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity['except_blocks'] += 1
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                complexity['functions'] += 1
                # Measure function complexity
                func_complexity = sum(1 for n in ast.walk(node) 
                                    if isinstance(n, (ast.If, ast.While, ast.For)))
                complexity['max_function_complexity'] = max(
                    complexity['max_function_complexity'], func_complexity
                )
            elif isinstance(node, ast.ClassDef):
                complexity['classes'] += 1
            elif isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp)):
                complexity['comprehensions'] += 1
        
        return dict(complexity)
    
    def _extract_patterns(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Extract code patterns for learning"""
        patterns = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                pattern = self._analyze_function_pattern(node, content)
                patterns.append(pattern)
            elif isinstance(node, ast.ClassDef):
                pattern = self._analyze_class_pattern(node, content)
                patterns.append(pattern)
            elif isinstance(node, (ast.For, ast.While)):
                pattern = self._analyze_loop_pattern(node, content)
                patterns.append(pattern)
        
        return patterns
    
    def _analyze_function_pattern(self, node: ast.FunctionDef, content: str) -> Dict[str, Any]:
        """Analyze function patterns"""
        lines = content.splitlines()
        
        # Get function signature
        args = [arg.arg for arg in node.args.args]
        signature = f"{node.name}({', '.join(args)})"
        
        # Calculate function metrics
        func_lines = []
        for n in ast.walk(node):
            if hasattr(n, 'lineno'):
                func_lines.append(n.lineno)
        
        func_length = max(func_lines) - min(func_lines) + 1 if func_lines else 1
        
        return {
            'type': 'function',
            'name': node.name,
            'signature': signature,
            'line_start': node.lineno,
            'length': func_length,
            'args_count': len(args),
            'returns': bool([n for n in ast.walk(node) if isinstance(n, ast.Return)]),
            'docstring': ast.get_docstring(node) is not None,
            'complexity': len([n for n in ast.walk(node) 
                             if isinstance(n, (ast.If, ast.For, ast.While))])
        }
    
    def _analyze_class_pattern(self, node: ast.ClassDef, content: str) -> Dict[str, Any]:
        """Analyze class patterns"""
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        
        return {
            'type': 'class',
            'name': node.name,
            'line_start': node.lineno,
            'methods_count': len(methods),
            'bases': [base.id if isinstance(base, ast.Name) else str(base) 
                     for base in node.bases],
            'docstring': ast.get_docstring(node) is not None,
            'has_init': any(method.name == '__init__' for method in methods)
        }
    
    def _analyze_loop_pattern(self, node: Union[ast.For, ast.While], content: str) -> Dict[str, Any]:
        """Analyze loop patterns"""
        return {
            'type': 'loop',
            'loop_type': 'for' if isinstance(node, ast.For) else 'while',
            'line_start': node.lineno,
            'nested_loops': len([n for n in ast.walk(node) 
                               if isinstance(n, (ast.For, ast.While)) and n != node]),
            'has_break': bool([n for n in ast.walk(node) if isinstance(n, ast.Break)]),
            'has_continue': bool([n for n in ast.walk(node) if isinstance(n, ast.Continue)])
        }
    
    def _analyze_functions(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Detailed function analysis"""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = {
                    'name': node.name,
                    'line_number': node.lineno,
                    'args': [arg.arg for arg in node.args.args],
                    'defaults': len(node.args.defaults),
                    'returns_count': len([n for n in ast.walk(node) if isinstance(n, ast.Return)]),
                    'raises_count': len([n for n in ast.walk(node) if isinstance(n, ast.Raise)]),
                    'docstring': ast.get_docstring(node),
                    'is_async': isinstance(node, ast.AsyncFunctionDef),
                    'decorators': [d.id if isinstance(d, ast.Name) else str(d) 
                                 for d in node.decorator_list]
                }
                functions.append(func_info)
        
        return functions
    
    def _analyze_classes(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Detailed class analysis"""
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                
                class_info = {
                    'name': node.name,
                    'line_number': node.lineno,
                    'methods': [method.name for method in methods],
                    'base_classes': [base.id if isinstance(base, ast.Name) else str(base) 
                                   for base in node.bases],
                    'docstring': ast.get_docstring(node),
                    'decorators': [d.id if isinstance(d, ast.Name) else str(d) 
                                 for d in node.decorator_list]
                }
                classes.append(class_info)
        
        return classes
    
    def _analyze_imports(self, tree: ast.AST) -> Dict[str, List[str]]:
        """Analyze import patterns"""
        imports = {
            'standard': [],
            'third_party': [],
            'relative': []
        }
        
        # Standard library modules (simplified list)
        stdlib_modules = {
            'os', 'sys', 'json', 'time', 'datetime', 'collections', 'itertools',
            'functools', 'operator', 'pathlib', 'typing', 'dataclasses', 'enum',
            'logging', 'unittest', 'sqlite3', 'pickle', 'csv', 'xml', 'html',
            'urllib', 'http', 'email', 'calendar', 'locale', 'platform'
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name.split('.')[0]
                    if module in stdlib_modules:
                        imports['standard'].append(alias.name)
                    else:
                        imports['third_party'].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.level > 0:  # Relative import
                    imports['relative'].append(f".{node.module}" if node.module else ".")
                else:
                    module = node.module.split('.')[0] if node.module else ''
                    if module in stdlib_modules:
                        imports['standard'].append(node.module or '')
                    else:
                        imports['third_party'].append(node.module or '')
        
        return imports
    
    def _detect_potential_bugs(self, content: str) -> List[Dict[str, Any]]:
        """Detect potential bugs using pattern matching"""
        potential_bugs = []
        lines = content.splitlines()
        
        for line_num, line in enumerate(lines, 1):
            for bug_type, pattern in self.bug_patterns.items():
                if re.search(pattern, line):
                    potential_bugs.append({
                        'type': bug_type,
                        'line': line_num,
                        'content': line.strip(),
                        'severity': self._assess_bug_severity(bug_type),
                        'pattern': pattern
                    })
        
        return potential_bugs
    
    def _find_optimizations(self, content: str) -> List[Dict[str, Any]]:
        """Find optimization opportunities"""
        optimizations = []
        lines = content.splitlines()
        
        for line_num, line in enumerate(lines, 1):
            for opt_type, pattern in self.optimization_patterns.items():
                if re.search(pattern, line):
                    suggestion = self._generate_optimization_suggestion(opt_type, line)
                    optimizations.append({
                        'type': opt_type,
                        'line': line_num,
                        'original': line.strip(),
                        'suggestion': suggestion,
                        'impact': self._assess_optimization_impact(opt_type)
                    })
        
        return optimizations
    
    def _assess_bug_severity(self, bug_type: str) -> str:
        """Assess the severity of a potential bug"""
        severity_map = {
            'unused_variable': 'low',
            'duplicate_code': 'medium',
            'long_line': 'low',
            'deep_nesting': 'medium',
            'magic_number': 'low',
            'bare_except': 'high',
            'mutable_default': 'high',
            'global_variable': 'medium'
        }
        return severity_map.get(bug_type, 'low')
    
    def _generate_optimization_suggestion(self, opt_type: str, original_line: str) -> str:
        """Generate optimization suggestions"""
        suggestions = {
            'list_comprehension': "Consider using list comprehension for better performance",
            'string_concatenation': "Use f-strings or join() for string concatenation",
            'inefficient_membership': "Use set for membership testing instead of list",
            'repeated_calculation': "Cache the result to avoid repeated calculations"
        }
        return suggestions.get(opt_type, "Consider optimization")
    
    def _assess_optimization_impact(self, opt_type: str) -> str:
        """Assess the impact of an optimization"""
        impact_map = {
            'list_comprehension': 'medium',
            'string_concatenation': 'high',
            'inefficient_membership': 'high',
            'repeated_calculation': 'medium'
        }
        return impact_map.get(opt_type, 'low')
    
    def _calculate_quality_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall code quality score (0-100)"""
        score = 100.0
        
        # Penalize based on potential bugs
        bugs = analysis.get('potential_bugs', [])
        for bug in bugs:
            if bug['severity'] == 'critical':
                score -= 20
            elif bug['severity'] == 'high':
                score -= 10
            elif bug['severity'] == 'medium':
                score -= 5
            else:
                score -= 2
        
        # Penalize based on complexity
        complexity = analysis.get('complexity', {})
        max_func_complexity = complexity.get('max_function_complexity', 0)
        if max_func_complexity > 10:
            score -= (max_func_complexity - 10) * 3
        
        # Bonus for good practices
        functions = analysis.get('functions', [])
        if functions:
            docstring_ratio = sum(1 for f in functions if f.get('docstring')) / len(functions)
            score += docstring_ratio * 10
        
        return max(0.0, min(100.0, score))


# Demo Functions and Main System
def create_sample_code_files():
    """Create sample Python files for demonstration"""
    sample_files = {
        "good_code.py": '''
"""
A well-written Python module demonstrating good practices.
"""

import json
import os
from typing import List, Dict, Optional


class DataProcessor:
    """Processes data with proper error handling and documentation."""
    
    def __init__(self, config_path: str):
        """Initialize processor with configuration."""
        self.config = self._load_config(config_path)
        self.processed_count = 0
    
    def _load_config(self, path: str) -> Dict:
        """Load configuration from file."""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"default": True}
    
    def process_items(self, items: List[Dict]) -> List[Dict]:
        """Process a list of items according to configuration."""
        results = []
        
        for item in items:
            if self._validate_item(item):
                processed = self._transform_item(item)
                results.append(processed)
                self.processed_count += 1
        
        return results
    
    def _validate_item(self, item: Dict) -> bool:
        """Validate item structure."""
        return isinstance(item, dict) and 'id' in item
    
    def _transform_item(self, item: Dict) -> Dict:
        """Transform item according to rules."""
        return {
            'id': item['id'],
            'processed': True,
            'timestamp': item.get('timestamp', 0)
        }
''',
        
        "problematic_code.py": '''
import sys,os,json
x=[]
def process(data):
    global x
    for i in data:
        for j in i:
            for k in j:
                if k == 5:
                    x.append(k)
                    s = s + str(k)
    try:
        result = expensive_calculation()
        result2 = expensive_calculation()
        result3 = expensive_calculation()
    except:
        pass
    return x

def expensive_calculation():
    return sum(range(1000000))

class BadClass:
    def __init__(self, items=[]):
        self.items = items
    
    def find_item(self, target):
        if target in [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]:
            return True
        return False
''',
        
        "mixed_quality.py": '''
"""Module with mixed code quality."""

from datetime import datetime
import re


class UserManager:
    """Manages user operations."""
    
    def __init__(self):
        self.users = []
    
    def add_user(self, name, email):
        if self.validate_email(email):
            user = {
                'name': name,
                'email': email,
                'created': datetime.now()
            }
            self.users.append(user)
            return True
        return False
    
    def validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def get_users_by_domain(self, domain):
        result = []
        for user in self.users:
            if domain in user['email']:
                result.append(user)
        return result
'''
    }
    
    # Create sample directory
    sample_dir = Path("sample_code")
    sample_dir.mkdir(exist_ok=True)
    
    for filename, content in sample_files.items():
        file_path = sample_dir / filename
        with open(file_path, 'w') as f:
            f.write(content)
    
    print(f"Created sample files in {sample_dir}/")
    return sample_dir

class AdaptiveCodeIntelligence:
    """Main system orchestrating adaptive code intelligence"""
    
    def __init__(self, storage_path: str = "code_intelligence.db"):
        self.analyzer = CodeAnalyzer()
        self.storage_path = storage_path
        self.developer_id = "default"
        self.analysis_history = []
    
    def analyze_file(self, file_path: str, developer_id: str = None) -> Dict[str, Any]:
        """Analyze a file and learn from it"""
        if developer_id:
            self.developer_id = developer_id
        
        print(f"Analyzing file: {file_path}")
        
        # Perform code analysis
        analysis = self.analyzer.analyze_file(file_path)
        
        if 'error' not in analysis:
            # Store in history
            self.analysis_history.append(analysis)
            
            print(f"✓ Analysis complete. Quality score: {analysis['code_quality_score']:.1f}/100")
            
            # Generate report
            self._generate_analysis_report(analysis)
        else:
            print(f"✗ Analysis failed: {analysis['error']}")
        
        return analysis
    
    def analyze_directory(self, directory_path: str, developer_id: str = None) -> List[Dict[str, Any]]:
        """Analyze all Python files in a directory"""
        if developer_id:
            self.developer_id = developer_id
        
        directory = Path(directory_path)
        python_files = list(directory.rglob("*.py"))
        
        print(f"Found {len(python_files)} Python files to analyze")
        
        results = []
        for file_path in python_files:
            if file_path.name.startswith('.'):  # Skip hidden files
                continue
            
            analysis = self.analyze_file(str(file_path), developer_id)
            results.append(analysis)
        
        # Generate directory summary
        self._generate_directory_summary(results)
        
        return results
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        return {
            'files_analyzed': len(self.analysis_history),
            'storage_path': self.storage_path
        }
    
    def _generate_analysis_report(self, analysis: Dict[str, Any]):
        """Generate and display analysis report"""
        print(f"\n=== Code Analysis Report ===")
        print(f"File: {analysis['file_path']}")
        print(f"Lines of Code: {analysis['lines_of_code']}")
        print(f"Quality Score: {analysis['code_quality_score']:.1f}/100")
        
        # Complexity metrics
        complexity = analysis.get('complexity', {})
        print(f"\nComplexity Metrics:")
        print(f"  Functions: {complexity.get('functions', 0)}")
        print(f"  Classes: {complexity.get('classes', 0)}")
        print(f"  Max Function Complexity: {complexity.get('max_function_complexity', 0)}")
        
        # Potential issues
        bugs = analysis.get('potential_bugs', [])
        if bugs:
            print(f"\nPotential Issues Found: {len(bugs)}")
            for bug in bugs[:3]:  # Show top 3
                print(f"  • Line {bug['line']}: {bug['type']} ({bug['severity']})")
        
        # Optimization opportunities
        optimizations = analysis.get('optimization_opportunities', [])
        if optimizations:
            print(f"\nOptimization Opportunities: {len(optimizations)}")
            for opt in optimizations[:3]:  # Show top 3
                print(f"  • Line {opt['line']}: {opt['type']}")
        
        print()
    
    def _generate_directory_summary(self, results: List[Dict[str, Any]]):
        """Generate summary for directory analysis"""
        if not results:
            return
        
        valid_results = [r for r in results if 'error' not in r]
        if not valid_results:
            print("No valid analyses to summarize")
            return
        
        print(f"\n=== Directory Analysis Summary ===")
        print(f"Files Analyzed: {len(valid_results)}")
        print(f"Total Lines of Code: {sum(r['lines_of_code'] for r in valid_results)}")
        
        # Average quality score
        avg_quality = sum(r['code_quality_score'] for r in valid_results) / len(valid_results)
        print(f"Average Quality Score: {avg_quality:.1f}/100")
        
        # Total issues
        total_bugs = sum(len(r.get('potential_bugs', [])) for r in valid_results)
        total_optimizations = sum(len(r.get('optimization_opportunities', [])) for r in valid_results)
        
        print(f"Total Potential Issues: {total_bugs}")
        print(f"Total Optimization Opportunities: {total_optimizations}")
        
        # Top file by quality
        best_file = max(valid_results, key=lambda x: x['code_quality_score'])
        print(f"Highest Quality File: {Path(best_file['file_path']).name} ({best_file['code_quality_score']:.1f}/100)")
        
        print()

def demo_adaptive_code_intelligence():
    """Comprehensive demo of the adaptive code intelligence system"""
    print("=== Adaptive Code Intelligence Engine MVP Demo ===\n")
    
    # Initialize system
    aci = AdaptiveCodeIntelligence("demo_code_intelligence.db")
    
    # Create sample files
    sample_dir = create_sample_code_files()
    
    print("1. Analyzing Sample Code Files...")
    print("-" * 40)
    
    # Analyze each sample file
    sample_files = list(sample_dir.glob("*.py"))
    analyses = []
    
    for file_path in sample_files:
        analysis = aci.analyze_file(str(file_path), "demo_developer")
        analyses.append(analysis)
    
    print("\n2. System Summary...")
    print("-" * 40)
    stats = aci.get_system_stats()
    print(f"Files Analyzed: {stats['files_analyzed']}")
    
    print("\n3. Code Quality Comparison...")
    print("-" * 40)
    
    valid_analyses = [a for a in analyses if 'error' not in a]
    if valid_analyses:
        # Sort by quality score
        sorted_analyses = sorted(valid_analyses, key=lambda x: x['code_quality_score'], reverse=True)
        
        print("Files by Quality Score:")
        for analysis in sorted_analyses:
            filename = Path(analysis['file_path']).name
            score = analysis['code_quality_score']
            bugs = len(analysis.get('potential_bugs', []))
            optimizations = len(analysis.get('optimization_opportunities', []))
            
            print(f"  {filename:20} Score: {score:5.1f}/100  Issues: {bugs:2d}  Optimizations: {optimizations:2d}")
    
    print(f"\n=== Demo Complete ===")
    print("This demonstrates:")
    print("• Advanced code analysis with AST parsing")
    print("• Pattern recognition and quality scoring")
    print("• Bug prediction with severity assessment")
    print("• Optimization opportunity detection")
    print("• Mobile-optimized Python development")
    
    # Cleanup
    import shutil
    try:
        shutil.rmtree(sample_dir)
        print(f"\nCleaned up sample files from {sample_dir}/")
    except:
        pass

if __name__ == "__main__":
    demo_adaptive_code_intelligence()
