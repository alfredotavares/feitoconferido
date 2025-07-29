"""Bitbucket integration tools for repository management.

Provides utilities for interacting with Bitbucket API to fetch repository
information, tags, branches, and pull request data.
"""

import aiohttp
from typing import Dict, Any, Optional
from urllib.parse import urlparse

from google.adk.tools import ToolContext


async def get_repository_info(
    repository_url: str,
    access_token: Optional[str],
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Fetches repository information from Bitbucket API.

    Retrieves metadata about a repository including default branch,
    size, and last update timestamp.

    Args:
        repository_url: Full URL of the Bitbucket repository.
        access_token: Optional Bitbucket access token for private repos.
        tool_context: ADK tool context.

    Returns:
        Dictionary containing:
            - name: Repository name
            - full_name: Full repository name (workspace/repo)
            - default_branch: Default branch name
            - size: Repository size in bytes
            - updated_on: Last update timestamp
            - is_private: Boolean indicating if repo is private
            - error: Error message if request failed

    Example:
        >>> result = await get_repository_info(
        ...     "https://bitbucket.org/company/service",
        ...     "token123",
        ...     tool_context
        ... )
        >>> print(result)
        {
            "name": "service",
            "full_name": "company/service",
            "default_branch": "main",
            "size": 1048576,
            "updated_on": "2024-01-15T10:30:00Z",
            "is_private": True
        }
    """
    try:
        # Parse repository URL
        parsed_url = urlparse(repository_url)
        path_parts = parsed_url.path.strip('/').split('/')
        
        if len(path_parts) < 2:
            return {"error": "Invalid Bitbucket repository URL"}
        
        workspace = path_parts[0]
        repo_slug = path_parts[1].replace('.git', '')
        
        # Build API URL
        api_url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}"
        
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as response:
                if response.status == 401:
                    return {"error": "Authentication failed - invalid or missing token"}
                elif response.status == 404:
                    return {"error": f"Repository not found: {workspace}/{repo_slug}"}
                elif response.status != 200:
                    return {"error": f"API request failed with status {response.status}"}
                
                data = await response.json()
                
                return {
                    "name": data.get("name"),
                    "full_name": data.get("full_name"),
                    "default_branch": data.get("mainbranch", {}).get("name", "main"),
                    "size": data.get("size", 0),
                    "updated_on": data.get("updated_on"),
                    "is_private": data.get("is_private", False),
                    "language": data.get("language", "unknown")
                }
                
    except Exception as e:
        return {"error": f"Failed to fetch repository info: {str(e)}"}


async def list_repository_tags(
    repository_url: str,
    access_token: Optional[str],
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Lists all tags in a Bitbucket repository.

    Fetches tags with their associated commit information,
    useful for identifying releases and versions.

    Args:
        repository_url: Full URL of the Bitbucket repository.
        access_token: Optional Bitbucket access token for private repos.
        tool_context: ADK tool context.

    Returns:
        Dictionary containing:
            - tags: List of tag dictionaries with name, date, and commit
            - total_count: Total number of tags
            - latest_tag: Name of the most recent tag
            - error: Error message if request failed

    Example:
        >>> result = await list_repository_tags(
        ...     "https://bitbucket.org/company/service",
        ...     "token123",
        ...     tool_context
        ... )
        >>> print(result)
        {
            "tags": [
                {
                    "name": "v1.2.3",
                    "date": "2024-01-15T10:30:00Z",
                    "commit": "abc123"
                }
            ],
            "total_count": 1,
            "latest_tag": "v1.2.3"
        }
    """
    try:
        # Parse repository URL
        parsed_url = urlparse(repository_url)
        path_parts = parsed_url.path.strip('/').split('/')
        
        if len(path_parts) < 2:
            return {"error": "Invalid Bitbucket repository URL"}
        
        workspace = path_parts[0]
        repo_slug = path_parts[1].replace('.git', '')
        
        # Build API URL
        api_url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/refs/tags"
        
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        
        tags = []
        
        async with aiohttp.ClientSession() as session:
            # Bitbucket API uses pagination
            next_url = api_url
            
            while next_url:
                async with session.get(next_url, headers=headers) as response:
                    if response.status != 200:
                        return {
                            "error": f"Failed to fetch tags: HTTP {response.status}",
                            "tags": [],
                            "total_count": 0
                        }
                    
                    data = await response.json()
                    
                    for tag in data.get("values", []):
                        tags.append({
                            "name": tag.get("name"),
                            "date": tag.get("target", {}).get("date"),
                            "commit": tag.get("target", {}).get("hash", "")[:7],
                            "message": tag.get("target", {}).get("message", "")
                        })
                    
                    # Check for next page
                    next_url = data.get("next")
        
        # Sort tags by date (newest first)
        tags.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        return {
            "tags": tags,
            "total_count": len(tags),
            "latest_tag": tags[0]["name"] if tags else None
        }
        
    except Exception as e:
        return {
            "error": f"Failed to list tags: {str(e)}",
            "tags": [],
            "total_count": 0
        }


async def get_file_content(
    repository_url: str,
    file_path: str,
    branch: str,
    access_token: Optional[str],
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Retrieves content of a specific file from Bitbucket repository.

    Fetches file content without cloning the entire repository,
    useful for checking specific configuration files.

    Args:
        repository_url: Full URL of the Bitbucket repository.
        file_path: Path to file within repository.
        branch: Branch name to fetch from.
        access_token: Optional Bitbucket access token for private repos.
        tool_context: ADK tool context.

    Returns:
        Dictionary containing:
            - content: File content as string
            - size: File size in bytes
            - encoding: Content encoding (usually base64)
            - error: Error message if request failed

    Example:
        >>> result = await get_file_content(
        ...     "https://bitbucket.org/company/service",
        ...     "pom.xml",
        ...     "main",
        ...     "token123",
        ...     tool_context
        ... )
        >>> print(result["content"][:50])
        "<?xml version='1.0' encoding='UTF-8'?>\n<project..."
    """
    try:
        # Parse repository URL
        parsed_url = urlparse(repository_url)
        path_parts = parsed_url.path.strip('/').split('/')
        
        if len(path_parts) < 2:
            return {"error": "Invalid Bitbucket repository URL"}
        
        workspace = path_parts[0]
        repo_slug = path_parts[1].replace('.git', '')
        
        # Build API URL
        api_url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/src/{branch}/{file_path}"
        
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as response:
                if response.status == 404:
                    return {"error": f"File not found: {file_path}"}
                elif response.status != 200:
                    return {"error": f"Failed to fetch file: HTTP {response.status}"}
                
                # Bitbucket returns raw content directly
                content = await response.text()
                
                return {
                    "content": content,
                    "size": len(content),
                    "encoding": "utf-8"
                }
                
    except Exception as e:
        return {"error": f"Failed to get file content: {str(e)}"}


async def list_pull_requests(
    repository_url: str,
    state: str,
    access_token: Optional[str],
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Lists pull requests for a Bitbucket repository.

    Fetches pull requests filtered by state (OPEN, MERGED, DECLINED),
    useful for checking ongoing development activities.

    Args:
        repository_url: Full URL of the Bitbucket repository.
        state: PR state to filter (OPEN, MERGED, DECLINED, ALL).
        access_token: Optional Bitbucket access token for private repos.
        tool_context: ADK tool context.

    Returns:
        Dictionary containing:
            - pull_requests: List of PR dictionaries
            - total_count: Total number of PRs
            - error: Error message if request failed

    Example:
        >>> result = await list_pull_requests(
        ...     "https://bitbucket.org/company/service",
        ...     "OPEN",
        ...     "token123",
        ...     tool_context
        ... )
        >>> print(result)
        {
            "pull_requests": [
                {
                    "id": 123,
                    "title": "Feature: Add new endpoint",
                    "state": "OPEN",
                    "author": "john.doe",
                    "created_on": "2024-01-15T10:30:00Z",
                    "source_branch": "feature/new-endpoint",
                    "destination_branch": "main"
                }
            ],
            "total_count": 1
        }
    """
    try:
        # Parse repository URL
        parsed_url = urlparse(repository_url)
        path_parts = parsed_url.path.strip('/').split('/')
        
        if len(path_parts) < 2:
            return {"error": "Invalid Bitbucket repository URL"}
        
        workspace = path_parts[0]
        repo_slug = path_parts[1].replace('.git', '')
        
        # Build API URL
        api_url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests"
        
        params = {}
        if state != "ALL":
            params["state"] = state
        
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        
        pull_requests = []
        
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers, params=params) as response:
                if response.status != 200:
                    return {
                        "error": f"Failed to fetch pull requests: HTTP {response.status}",
                        "pull_requests": [],
                        "total_count": 0
                    }
                
                data = await response.json()
                
                for pr in data.get("values", []):
                    pull_requests.append({
                        "id": pr.get("id"),
                        "title": pr.get("title"),
                        "state": pr.get("state"),
                        "author": pr.get("author", {}).get("display_name", "Unknown"),
                        "created_on": pr.get("created_on"),
                        "updated_on": pr.get("updated_on"),
                        "source_branch": pr.get("source", {}).get("branch", {}).get("name"),
                        "destination_branch": pr.get("destination", {}).get("branch", {}).get("name"),
                        "reviewers": [
                            r.get("display_name") for r in pr.get("reviewers", [])
                        ]
                    })
        
        return {
            "pull_requests": pull_requests,
            "total_count": len(pull_requests)
        }
        
    except Exception as e:
        return {
            "error": f"Failed to list pull requests: {str(e)}",
            "pull_requests": [],
            "total_count": 0
        }


async def check_branch_protection(
    repository_url: str,
    branch: str,
    access_token: Optional[str],
    tool_context: ToolContext
) -> Dict[str, Any]:
    """Checks branch protection rules for a specific branch.

    Verifies if a branch has protection rules configured,
    important for validating development practices.

    Args:
        repository_url: Full URL of the Bitbucket repository.
        branch: Branch name to check.
        access_token: Optional Bitbucket access token for private repos.
        tool_context: ADK tool context.

    Returns:
        Dictionary containing:
            - is_protected: Boolean indicating if branch is protected
            - restrictions: List of active restrictions
            - required_approvals: Number of required approvals
            - error: Error message if request failed

    Example:
        >>> result = await check_branch_protection(
        ...     "https://bitbucket.org/company/service",
        ...     "main",
        ...     "token123",
        ...     tool_context
        ... )
        >>> print(result)
        {
            "is_protected": True,
            "restrictions": ["no-deletes", "no-force-push"],
            "required_approvals": 2
        }
    """
    try:
        # Parse repository URL
        parsed_url = urlparse(repository_url)
        path_parts = parsed_url.path.strip('/').split('/')
        
        if len(path_parts) < 2:
            return {"error": "Invalid Bitbucket repository URL"}
        
        workspace = path_parts[0]
        repo_slug = path_parts[1].replace('.git', '')
        
        # Build API URL for branch restrictions
        api_url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/branch-restrictions"
        
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as response:
                if response.status != 200:
                    return {
                        "is_protected": False,
                        "restrictions": [],
                        "required_approvals": 0,
                        "error": f"Failed to fetch branch restrictions: HTTP {response.status}"
                    }
                
                data = await response.json()
                
                # Find restrictions for the specified branch
                restrictions = []
                required_approvals = 0
                is_protected = False
                
                for restriction in data.get("values", []):
                    # Check if this restriction applies to our branch
                    pattern = restriction.get("pattern", "")
                    if pattern == branch or pattern == f"*{branch}*":
                        is_protected = True
                        
                        kind = restriction.get("kind")
                        if kind == "delete":
                            restrictions.append("no-deletes")
                        elif kind == "force":
                            restrictions.append("no-force-push")
                        elif kind == "restrict_merges":
                            restrictions.append("restrict-merges")
                            
                        # Check for required reviewers
                        if restriction.get("value", 0) > 0:
                            required_approvals = max(required_approvals, restriction.get("value", 0))
                
                return {
                    "is_protected": is_protected,
                    "restrictions": restrictions,
                    "required_approvals": required_approvals
                }
                
    except Exception as e:
        return {
            "is_protected": False,
            "restrictions": [],
            "required_approvals": 0,
            "error": f"Failed to check branch protection: {str(e)}"
        }