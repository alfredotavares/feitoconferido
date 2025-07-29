"""Git tools for repository analysis and validation.

Provides utilities for cloning repositories, analyzing project structure,
validating dependencies, and checking for required configuration files.
"""

import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any
from urllib.parse import urlparse
import re

from google.adk.tools import ToolContext


async def clone_repository(
    repository_url: str,
    tool_context: ToolContext,
    branch: str = "main",
) -> Dict[str, Any]:
    """Clones a Git repository to a temporary directory for analysis.

    Supports both authenticated and public repositories. Extracts
    credentials from repository URL if provided.

    Args:
        repository_url: Full URL of the Git repository.
        branch: Branch to clone (defaults to main).
        tool_context: ADK tool context.

    Returns:
        Dictionary containing:
            - success: Boolean indicating if clone was successful
            - path: Path to cloned repository (if successful)
            - error: Error message (if failed)

    Example:
        >>> result = await clone_repository(
        ...     "https://github.com/company/service",
        ...     "main",
        ...     tool_context
        ... )
        >>> print(result["path"])
        "/tmp/tmp_xyz123/service"
    """
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        
        # Parse repository URL
        parsed_url = urlparse(repository_url)
        
        # Build clone command
        clone_cmd = ["git", "clone", "--depth", "1", "--branch", branch]
        
        # Handle authentication if credentials in URL
        if "@" in parsed_url.netloc:
            # URL already contains credentials
            clone_cmd.append(repository_url)
        else:
            # Use repository URL as-is
            clone_cmd.append(repository_url)
        
        # Add target directory
        repo_name = Path(parsed_url.path).stem
        target_path = Path(temp_dir) / repo_name
        clone_cmd.append(str(target_path))
        
        # Execute clone
        process = await asyncio.create_subprocess_exec(
            *clone_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            shutil.rmtree(temp_dir)
            return {
                "success": False,
                "error": f"Git clone failed: {stderr.decode()}"
            }
        
        return {
            "success": True,
            "path": str(target_path)
        }
        
    except Exception as e:
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir)
        return {
            "success": False,
            "error": f"Failed to clone repository: {str(e)}"
        }


async def analyze_project_structure(
    repo_path: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Analyzes the structure of a cloned repository.

    Identifies project type, build system, and validates required
    directories based on detected technology stack.

    Args:
        repo_path: Path to the cloned repository.
        tool_context: ADK tool context.

    Returns:
        Dictionary containing:
            - project_type: Detected project type (java, python, node, etc.)
            - build_system: Detected build system (maven, gradle, npm, etc.)
            - structure_valid: Boolean indicating if structure is valid
            - missing_directories: List of missing required directories
            - detected_files: List of important files found

    Example:
        >>> result = await analyze_project_structure(
        ...     "/tmp/repo",
        ...     tool_context
        ... )
        >>> print(result)
        {
            "project_type": "java",
            "build_system": "maven",
            "structure_valid": True,
            "missing_directories": [],
            "detected_files": ["pom.xml", "src/main/java", "src/test/java"]
        }
    """
    try:
        repo_root = Path(repo_path)
        
        # Detect project type and build system
        project_info = await detect_project_type(repo_root)
        
        # Define required directories based on project type
        required_dirs = get_required_directories(
            project_info["project_type"],
            project_info["build_system"]
        )
        
        # Check for missing directories
        missing_dirs = []
        for required_dir in required_dirs:
            if not (repo_root / required_dir).exists():
                missing_dirs.append(required_dir)
        
        # List detected important files
        detected_files = []
        important_patterns = [
            "pom.xml", "build.gradle", "package.json",
            "requirements.txt", "setup.py", "Dockerfile",
            "docker-compose.yml", "openapi.yaml", "openapi.yml",
            "swagger.yaml", "swagger.yml", "api-spec.yaml"
        ]
        
        for pattern in important_patterns:
            if (repo_root / pattern).exists():
                detected_files.append(pattern)
        
        # Check for OpenAPI in standard locations
        openapi_locations = [
            "src/main/resources/openapi.yaml",
            "src/main/resources/swagger.yaml",
            "docs/openapi.yaml",
            "api/openapi.yaml"
        ]
        
        for location in openapi_locations:
            if (repo_root / location).exists():
                detected_files.append(location)
        
        return {
            "project_type": project_info["project_type"],
            "build_system": project_info["build_system"],
            "structure_valid": len(missing_dirs) == 0,
            "missing_directories": missing_dirs,
            "detected_files": detected_files
        }
        
    except Exception as e:
        return {
            "project_type": "unknown",
            "build_system": "unknown",
            "structure_valid": False,
            "missing_directories": [],
            "detected_files": [],
            "error": f"Failed to analyze structure: {str(e)}"
        }


async def validate_dependencies(
    repo_path: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Validates project dependencies for known vulnerabilities and deprecations.

    Checks dependency files for deprecated libraries and security issues
    based on the detected build system.

    Args:
        repo_path: Path to the cloned repository.
        tool_context: ADK tool context.

    Returns:
        Dictionary containing:
            - dependencies_valid: Boolean indicating if dependencies are valid
            - deprecated_dependencies: List of deprecated dependencies found
            - security_issues: List of potential security issues
            - total_dependencies: Total number of dependencies found

    Example:
        >>> result = await validate_dependencies(
        ...     "/tmp/repo",
        ...     tool_context
        ... )
        >>> print(result)
        {
            "dependencies_valid": False,
            "deprecated_dependencies": ["commons-lang:2.6"],
            "security_issues": [],
            "total_dependencies": 15
        }
    """
    try:
        repo_root = Path(repo_path)
        
        # Detect build system
        project_info = await detect_project_type(repo_root)
        build_system = project_info["build_system"]
        
        deprecated_deps = []
        security_issues = []
        total_deps = 0
        
        # Known deprecated dependencies
        deprecated_patterns = {
            "commons-lang:commons-lang:2": "Use commons-lang3 instead",
            "junit:junit:3": "Use JUnit 4 or 5",
            "log4j:log4j:1": "Use Log4j 2.x",
            "org.springframework:spring:2": "Use Spring Framework 5.x or 6.x",
            "com.sun.jersey": "Use org.glassfish.jersey",
            "javax.servlet:servlet-api": "Use jakarta.servlet-api"
        }
        
        if build_system == "maven":
            pom_path = repo_root / "pom.xml"
            if pom_path.exists():
                content = pom_path.read_text()
                
                # Count dependencies
                total_deps = len(re.findall(r"<dependency>", content))
                
                # Check for deprecated dependencies
                for pattern, message in deprecated_patterns.items():
                    if pattern in content:
                        deprecated_deps.append(f"{pattern} - {message}")
                
                # Check for security issues
                if "<version>2.14" in content and "log4j" in content:
                    security_issues.append("Log4j version vulnerable to CVE-2021-44228")
                
        elif build_system == "gradle":
            gradle_files = list(repo_root.glob("*.gradle"))
            for gradle_file in gradle_files:
                content = gradle_file.read_text()
                
                # Count dependencies
                total_deps += len(re.findall(r"implementation|compile", content))
                
                # Check for deprecated dependencies
                for pattern, message in deprecated_patterns.items():
                    if pattern.replace(":", '":"') in content:
                        deprecated_deps.append(f"{pattern} - {message}")
        
        elif build_system == "npm":
            package_json = repo_root / "package.json"
            if package_json.exists():
                import json
                package_data = json.loads(package_json.read_text())
                
                dependencies = package_data.get("dependencies", {})
                dev_dependencies = package_data.get("devDependencies", {})
                
                total_deps = len(dependencies) + len(dev_dependencies)
                
                # Check for deprecated packages
                deprecated_npm = {
                    "request": "Use axios or fetch",
                    "bower": "Use npm or yarn",
                    "gulp-util": "Deprecated package"
                }
                
                for dep in deprecated_npm:
                    if dep in dependencies or dep in dev_dependencies:
                        deprecated_deps.append(f"{dep} - {deprecated_npm[dep]}")
        
        return {
            "dependencies_valid": len(deprecated_deps) == 0 and len(security_issues) == 0,
            "deprecated_dependencies": deprecated_deps,
            "security_issues": security_issues,
            "total_dependencies": total_deps
        }
        
    except Exception as e:
        return {
            "dependencies_valid": False,
            "deprecated_dependencies": [],
            "security_issues": [],
            "total_dependencies": 0,
            "error": f"Failed to validate dependencies: {str(e)}"
        }


async def find_openapi_spec(
    repo_path: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Searches for OpenAPI/Swagger specification files in the repository.

    Looks for OpenAPI specs in common locations and validates their
    basic structure if found.

    Args:
        repo_path: Path to the cloned repository.
        tool_context: ADK tool context.

    Returns:
        Dictionary containing:
            - has_openapi: Boolean indicating if OpenAPI spec was found
            - spec_locations: List of paths where specs were found
            - spec_version: OpenAPI version (2.0, 3.0, 3.1)
            - validation_errors: List of validation errors if any

    Example:
        >>> result = await find_openapi_spec(
        ...     "/tmp/repo",
        ...     tool_context
        ... )
        >>> print(result)
        {
            "has_openapi": True,
            "spec_locations": ["src/main/resources/openapi.yaml"],
            "spec_version": "3.0",
            "validation_errors": []
        }
    """
    try:
        repo_root = Path(repo_path)
        
        # Common OpenAPI file patterns
        openapi_patterns = [
            "**/openapi.yaml", "**/openapi.yml", "**/openapi.json",
            "**/swagger.yaml", "**/swagger.yml", "**/swagger.json",
            "**/api-spec.yaml", "**/api-spec.yml", "**/api-spec.json",
            "**/api.yaml", "**/api.yml", "**/api.json"
        ]
        
        spec_locations = []
        spec_version = None
        validation_errors = []
        
        # Search for OpenAPI files
        for pattern in openapi_patterns:
            for spec_file in repo_root.glob(pattern):
                if spec_file.is_file():
                    relative_path = spec_file.relative_to(repo_root)
                    spec_locations.append(str(relative_path))
                    
                    # Try to detect version
                    try:
                        content = spec_file.read_text()
                        
                        if spec_file.suffix in ['.yaml', '.yml']:
                            if 'openapi: 3.1' in content:
                                spec_version = "3.1"
                            elif 'openapi: 3.0' in content or "openapi: '3.0'" in content:
                                spec_version = "3.0"
                            elif 'swagger: "2.0"' in content or "swagger: '2.0'" in content:
                                spec_version = "2.0"
                            
                            # Basic validation
                            if 'paths:' not in content:
                                validation_errors.append(f"{relative_path}: Missing 'paths' section")
                            if 'info:' not in content:
                                validation_errors.append(f"{relative_path}: Missing 'info' section")
                                
                    except Exception as e:
                        validation_errors.append(f"{relative_path}: Failed to parse - {str(e)}")
        
        return {
            "has_openapi": len(spec_locations) > 0,
            "spec_locations": spec_locations,
            "spec_version": spec_version,
            "validation_errors": validation_errors
        }
        
    except Exception as e:
        return {
            "has_openapi": False,
            "spec_locations": [],
            "spec_version": None,
            "validation_errors": [],
            "error": f"Failed to find OpenAPI spec: {str(e)}"
        }


async def cleanup_repository(
    repo_path: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Cleans up a cloned repository directory.

    Removes the temporary directory created during repository analysis.

    Args:
        repo_path: Path to the cloned repository to clean up.
        tool_context: ADK tool context.

    Returns:
        Dictionary containing:
            - success: Boolean indicating if cleanup was successful
            - error: Error message if cleanup failed
    """
    try:
        # Get the temp directory (parent of repo)
        temp_dir = Path(repo_path).parent
        
        if temp_dir.exists() and str(temp_dir).startswith("/tmp"):
            shutil.rmtree(temp_dir)
            return {"success": True}
        else:
            return {
                "success": False,
                "error": "Invalid path or not a temporary directory"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to cleanup: {str(e)}"
        }


async def detect_project_type(repo_root: Path) -> Dict[str, str]:
    """Detects project type and build system from repository files.

    Internal helper function to identify the technology stack
    based on configuration files present.

    Args:
        repo_root: Path to repository root.

    Returns:
        Dictionary with project_type and build_system.
    """
    project_type = "unknown"
    build_system = "unknown"
    
    # Java project detection
    if (repo_root / "pom.xml").exists():
        project_type = "java"
        build_system = "maven"
    elif (repo_root / "build.gradle").exists() or (repo_root / "build.gradle.kts").exists():
        project_type = "java"
        build_system = "gradle"
    
    # Node.js project detection
    elif (repo_root / "package.json").exists():
        project_type = "node"
        build_system = "npm"
        if (repo_root / "yarn.lock").exists():
            build_system = "yarn"
    
    # Python project detection
    elif (repo_root / "requirements.txt").exists() or (repo_root / "setup.py").exists():
        project_type = "python"
        build_system = "pip"
        if (repo_root / "Pipfile").exists():
            build_system = "pipenv"
        elif (repo_root / "poetry.lock").exists():
            build_system = "poetry"
    
    # .NET project detection
    elif list(repo_root.glob("*.csproj")) or list(repo_root.glob("*.sln")):
        project_type = "dotnet"
        build_system = "dotnet"
    
    # Go project detection
    elif (repo_root / "go.mod").exists():
        project_type = "go"
        build_system = "go"
    
    return {
        "project_type": project_type,
        "build_system": build_system
    }


def get_required_directories(project_type: str, build_system: str) -> List[str]:
    """Gets list of required directories based on project type.

    Internal helper function to define expected directory structure
    for different technology stacks.

    Args:
        project_type: Type of project (java, python, node, etc.).
        build_system: Build system in use.

    Returns:
        List of required directory paths.
    """
    required_dirs = []
    
    if project_type == "java":
        if build_system == "maven":
            required_dirs = [
                "src/main/java",
                "src/main/resources"
            ]
        elif build_system == "gradle":
            required_dirs = [
                "src/main/java"
            ]
    
    elif project_type == "python":
        # Python projects have more flexible structure
        required_dirs = []
    
    elif project_type == "node":
        required_dirs = ["src"]
    
    elif project_type == "dotnet":
        # .NET projects define structure in project files
        required_dirs = []
    
    elif project_type == "go":
        # Go projects have flexible structure
        required_dirs = []
    
    return required_dirs
