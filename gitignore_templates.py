import os

TEMPLATES = {
    "Python": """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.pytest_cache/
.coverage
htmlcov/
.venv
venv/
ENV/
env/
.env
.idea/
.vscode/
""",
    "Node.js / React / Web": """# Node / Web
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*
build/
dist/
.next/
.out/
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
.cache/
.vscode/
.DS_Store
""",
    "C / C++": """# C / C++
*.o
*.obj
*.so
*.dylib
*.dll
*.exe
*.out
*.app
build/
bin/
CMakeCache.txt
CMakeFiles/
Makefile
cmake-build-*/
.vscode/
""",
    "Java / Maven / Gradle": """# Java
*.class
*.jar
*.war
*.ear
*.nar
target/
.gradle/
build/
.settings/
.classpath
.project
.idea/
*.iml
""",
    "Go": """# Go
*.exe
*.exe~
*.dll
*.so
*.dylib
*.test
*.out
vendor/
go.sum
"""
}

def generate_gitignore(target_directory: str, stack_name: str) -> bool:
    """Create or append to a .gitignore file in target_directory."""
    template = TEMPLATES.get(stack_name, TEMPLATES["Python"])
    gitignore_path = os.path.join(target_directory, ".gitignore")
    
    try:
        if os.path.exists(gitignore_path):
            with open(gitignore_path, "r", encoding="utf-8") as f:
                existing = f.read()
            if template.strip() in existing:
                return True
            with open(gitignore_path, "a", encoding="utf-8") as f:
                f.write("\n\n" + template)
        else:
            with open(gitignore_path, "w", encoding="utf-8") as f:
                f.write(template)
        return True
    except Exception:
        return False
