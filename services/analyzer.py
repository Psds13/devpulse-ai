from typing import List, Dict, Any
import re
from utils.logger import setup_logger

logger = setup_logger(__name__)

class CodeAnalyzer:
    def __init__(self):
        # Basic heuristic thresholds
        self.max_file_size = 300 # lines
        self.max_line_length = 120
    
    def analyze_diff(self, patch: str, filename: str) -> List[Dict[str, Any]]:
        issues = []
        if not patch:
            return issues
            
        lines = patch.split("\n")
        
        # Heuristic 1: Bulk file edits constraint
        if len(lines) > self.max_file_size:
            issues.append({
                "type": "large_file",
                "file": filename,
                "message": f"File change too large ({len(lines)} lines in diff). Consider splitting the file.",
                "severity": "warning"
            })
            
        # Target only lines explicitly injected/added to the codebase
        added_lines = [line[1:] for line in lines if line.startswith("+") and not line.startswith("+++")]
        
        for idx, line in enumerate(added_lines, 1):
            # Heuristic 2: Long lines detection
            if len(line) > self.max_line_length:
                issues.append({
                    "type": "long_line",
                    "file": filename,
                    "message": f"Line exceeds the soft limit of {self.max_line_length} chars.",
                    "severity": "info"
                })
                
            # Heuristic 3: Hardcoded credentials detection (RegEx)
            # Match assignments for generic naming conventions related to tokens/passwords
            if re.search(r"(?i)(api[_-]?key|token|password|secret|pwd)\s*[:=]\s*[\"'][a-zA-Z0-9_\-]+[\"']", line):
                 issues.append({
                    "type": "security_risk",
                    "file": filename,
                    "message": "Potential hardcoded secret or API key detected. Consider using env variables.",
                    "severity": "critical"
                })
                 
            # Heuristic 4: Unwanted debug traces logic 
            if re.search(r"\b(print|console\.log|debugger|import pdb|breakpoint)\b", line):
                 issues.append({
                    "type": "bad_practice",
                    "file": filename,
                    "message": "Debugger statement or print() found. Swap for structured logging instead.",
                    "severity": "warning"
                })
                 
            # Heuristic 5: Broad exceptions blocks
            if "except:" in line.strip() or "except Exception:" in line.strip():
                 issues.append({
                    "type": "bad_practice",
                    "file": filename,
                    "message": "Broad or bare except block caught. Try handling explicit error types instead of shadowing everything.",
                    "severity": "warning"
                })

        # Heuristic 6: Potential deep-nested logic (Naive Check)
        if "for " in patch:
             if patch.count("for ") >= 3 and patch.count("    for") >= 2:
                 issues.append({
                    "type": "code_complexity",
                    "file": filename,
                    "message": "Heavily nested loops detected in diff context. This escalates algorithmic complexity significantly.",
                    "severity": "info"
                })
            
        return issues
