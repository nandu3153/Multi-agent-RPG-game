"""Shared Azure AI Inference client wrapper with retry logic."""

from __future__ import annotations

import os
import re
import time
from typing import List, Optional, Tuple
from urllib.parse import urlparse

import requests
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import AssistantMessage, SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError

from utils.logger import get_logger

logger = get_logger(__name__)

AZURE_MODEL = os.environ.get("AZURE_AI_MODEL", "gpt-4o")
AZURE_API_VERSION = os.environ.get("AZURE_AI_API_VERSION", "2024-06-01")

_client: Optional[ChatCompletionsClient] = None
_resolved_endpoint: Optional[str] = None


def _resource_host_from_endpoint(endpoint: str) -> str:
    """Extract services.ai.azure.com host from project or openai endpoint."""
    parsed = urlparse(endpoint.rstrip("/"))
    host = parsed.netloc
    if not host:
        raise ValueError(f"Invalid AZURE_AI_FOUNDRY_ENDPOINT: {endpoint}")
    if host.endswith(".openai.azure.com"):
        return host.replace(".openai.azure.com", ".services.ai.azure.com")
    return host


def discover_deployments(endpoint: str, api_key: str) -> list[dict]:
    """List deployments in the Foundry project via the v1 management API."""
    host = _resource_host_from_endpoint(endpoint)
    parsed = urlparse(endpoint.rstrip("/"))
    project_match = re.search(r"/api/projects/([^/]+)", parsed.path)
    if not project_match:
        return []
    project = project_match.group(1)
    url = f"https://{host}/api/projects/{project}/deployments"
    response = requests.get(
        url,
        headers={"api-key": api_key},
        params={"api-version": "v1"},
        timeout=30,
    )
    if response.status_code != 200:
        logger.warning("Could not list deployments: %s %s", response.status_code, response.text[:200])
        return []
    return response.json().get("value", [])


def resolve_inference_endpoint() -> Tuple[str, str]:
    """
    Build a ChatCompletionsClient-compatible deployment endpoint.

    The Foundry *project* URL (/api/projects/...) does not support the
    azure-ai-inference SDK chat API version. We resolve to an OpenAI-style
    deployment URL instead.
    """
    configured = os.environ.get("AZURE_AI_INFERENCE_ENDPOINT", "").rstrip("/")
    if configured:
        return configured, AZURE_MODEL

    foundry_endpoint = os.environ["AZURE_AI_FOUNDRY_ENDPOINT"].rstrip("/")
    api_key = os.environ["AZURE_AI_FOUNDRY_API_KEY"]
    model = AZURE_MODEL

    # Already a deployment-style endpoint
    if "/openai/deployments/" in foundry_endpoint:
        return foundry_endpoint, model

    deployments = discover_deployments(foundry_endpoint, api_key)
    if deployments:
        chat_deployments = [
            d for d in deployments
            if d.get("capabilities", {}).get("chat_completion") == "true"
        ] or deployments
        names = [d["name"] for d in chat_deployments if d.get("name")]
        preferred = os.environ.get("AZURE_AI_DEPLOYMENT_NAME", model)
        chosen = preferred if preferred in names else names[0]
        parsed = urlparse(foundry_endpoint)
        host = parsed.netloc
        if not host.endswith(".openai.azure.com"):
            host = host.replace(".services.ai.azure.com", ".openai.azure.com")
        deployment_url = f"https://{host}/openai/deployments/{chosen}"
        logger.info("Using deployment endpoint for model '%s': %s", chosen, deployment_url)
        return deployment_url, chosen

    # Explicit deployment override via env
    deployment_name = os.environ.get("AZURE_AI_DEPLOYMENT_NAME", model)
    parsed = urlparse(foundry_endpoint)
    host = parsed.netloc.replace(".services.ai.azure.com", ".openai.azure.com")
    if not host.endswith(".openai.azure.com"):
        resource = host.split(".")[0]
        host = f"{resource}.openai.azure.com"
    deployment_url = f"https://{host}/openai/deployments/{deployment_name}"
    logger.warning(
        "No deployments found in Foundry project. Trying %s — deploy '%s' in "
        "Azure AI Foundry → Models + endpoints if this fails.",
        deployment_url,
        deployment_name,
    )
    return deployment_url, deployment_name


def get_azure_client() -> ChatCompletionsClient:
    global _client, _resolved_endpoint
    if _client is None:
        endpoint, _ = resolve_inference_endpoint()
        _resolved_endpoint = endpoint
        api_key = os.environ["AZURE_AI_FOUNDRY_API_KEY"]
        _client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(api_key),
            api_version=AZURE_API_VERSION,
        )
    return _client


def complete_with_retry(
    system_prompt: str,
    user_prompt: str,
    conversation_history: Optional[List[dict]] = None,
    max_tokens: int = 1024,
    temperature: float = 0.8,
) -> str:
    """Call Azure AI Inference with exponential backoff retry."""
    client = get_azure_client()
    messages = [SystemMessage(content=system_prompt)]

    if conversation_history:
        for msg in conversation_history[-10:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "assistant":
                messages.append(AssistantMessage(content=content))
            else:
                messages.append(UserMessage(content=content))

    messages.append(UserMessage(content=user_prompt))

    delays = [1, 2, 4]
    last_error: Optional[Exception] = None

    for attempt, delay in enumerate(delays):
        try:
            response = client.complete(
                model=AZURE_MODEL,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content or ""
        except HttpResponseError as e:
            last_error = e
            status = getattr(e, "status_code", None) or (e.response.status_code if e.response else 0)
            message = str(e)
            if status == 401:
                logger.error("Invalid API key — check AZURE_AI_FOUNDRY_API_KEY")
                raise
            if status == 404 or "DeploymentNotFound" in message:
                logger.error(
                    "Model deployment not found — deploy '%s' in Azure AI Foundry → "
                    "Models + endpoints, then set AZURE_AI_DEPLOYMENT_NAME to the deployment name.",
                    AZURE_MODEL,
                )
                raise RuntimeError(
                    f"No deployment named '{AZURE_MODEL}' found. "
                    "Open https://ai.azure.com → your project → Models + endpoints → "
                    "Deploy gpt-4o, then set AZURE_AI_DEPLOYMENT_NAME in .env to the deployment name."
                ) from e
            if "API version not supported" in message:
                logger.error(
                    "API version not supported on endpoint %s. "
                    "Use a deployment URL (set AZURE_AI_INFERENCE_ENDPOINT) or deploy a model in Foundry.",
                    _resolved_endpoint,
                )
                raise RuntimeError(
                    "Azure endpoint rejected the API version. Ensure gpt-4o is deployed in Foundry "
                    "and AZURE_AI_FOUNDRY_ENDPOINT points to your project URL."
                ) from e
            if status == 429:
                logger.warning("Rate limit hit — backing off")
                time.sleep(delay * 2)
            else:
                logger.warning("Azure API error (attempt %d): %s", attempt + 1, e)
                time.sleep(delay)
        except Exception as e:
            last_error = e
            logger.warning("Azure call failed (attempt %d): %s", attempt + 1, e)
            time.sleep(delay)

    raise RuntimeError(f"Azure AI call failed after retries: {last_error}")


def test_connectivity() -> bool:
    """Send minimal completion to verify Azure connectivity."""
    try:
        endpoint, model = resolve_inference_endpoint()
        deployments = discover_deployments(
            os.environ["AZURE_AI_FOUNDRY_ENDPOINT"],
            os.environ["AZURE_AI_FOUNDRY_API_KEY"],
        )
        if not deployments:
            logger.error(
                "No model deployments found in your Foundry project. "
                "Go to https://ai.azure.com → your project → Models + endpoints → Deploy a chat model. "
                "Then set AZURE_AI_DEPLOYMENT_NAME in .env to match the deployment name."
            )
            raise RuntimeError(
                "No model deployments in Foundry project. Deploy a chat model before starting the game."
            )
        result = complete_with_retry(
            "You are a test assistant.",
            "Reply with only: OK",
            max_tokens=5,
            temperature=0,
        )
        logger.info("Azure connectivity test passed (endpoint=%s model=%s): %s", endpoint, model, result[:20])
        return True
    except Exception as e:
        logger.error(
            "Azure connectivity test failed: %s. "
            "Deploy gpt-4o in Azure AI Foundry and verify AZURE_AI_FOUNDRY_API_KEY.",
            e,
        )
        raise
