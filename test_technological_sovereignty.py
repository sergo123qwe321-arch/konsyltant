import unittest
import os
import re

class TestTechnologicalSovereignty(unittest.TestCase):
    def test_zero_bypass_tools_mentions(self):
        """
        Автоматизированный аудит технологического суверенитета:
        Проверяет 0 упоминаний запрещенных обходных средств по всему проекту.
        """
        forbidden_word = "v" + "p" + "n"
        forbidden_regex = re.compile(rf'\b{forbidden_word}\b', re.IGNORECASE)
        extensions = ('.py', '.html', '.js', '.css', '.md', '.txt', '.yml', '.yaml', '.json', '.conf', '.sh')
        ignored_dirs = {'.git', '__pycache__', 'node_modules', 'venv', '.idea', '.vscode'}
        ignored_files = {'test_technological_sovereignty.py'}
        
        matches = []
        project_root = os.path.dirname(os.path.abspath(__file__))
        
        for root, dirs, files in os.walk(project_root):
            dirs[:] = [d for d in dirs if d not in ignored_dirs]
            for file in files:
                if file in ignored_files:
                    continue
                if any(file.endswith(ext) for ext in extensions):
                    filepath = os.path.join(root, file)
                    rel_path = os.path.relpath(filepath, project_root)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            for idx, line in enumerate(f, start=1):
                                if forbidden_regex.search(line):
                                    matches.append(f"{rel_path}:{idx} -> {line.strip()}")
                    except Exception:
                        pass
        
        self.assertEqual(
            len(matches), 0,
            f"Обнаружены запрещенные упоминания обходных средств ({len(matches)} шт.):\n" + "\n".join(matches)
        )

if __name__ == "__main__":
    unittest.main()
