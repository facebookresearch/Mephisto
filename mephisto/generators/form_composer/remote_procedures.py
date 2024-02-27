from concurrent.futures import ThreadPoolExecutor
from typing import List
from typing import Tuple
from typing import Union

from mephisto.generators.form_composer.config_validation.utils import is_s3_url

from mephisto.abstractions.blueprints.remote_procedure.remote_procedure_agent_state import (
    RemoteProcedureAgentState,
)
from mephisto.generators.form_composer.config_validation.utils import get_s3_presigned_url
from mephisto.utils.logger_core import get_logger

MAX_THREADS = 10

logger = get_logger(name=__name__)


class ProcedureName:
    GET_MULTIPLE_PRESIGNED_URLS = "getMultiplePresignedUrls"
    GET_PRESIGNED_URL = "getPresignedUrl"


def _get_presigned_url(request_id: str, url: str, agent_state: RemoteProcedureAgentState) -> str:
    logger.debug(f"Presigning S3 URL '{url}' ({request_id=})")
    presigned_url = get_s3_presigned_url(url)
    logger.debug(f"Presigned S3 URL '{presigned_url}'")
    return presigned_url


def _get_presigned_url_for_thread(url: str) -> Tuple[str, Union[str, None], Union[str, None]]:
    presigned_url = None
    error = None

    if not is_s3_url(url):
        error = f"Not a valid S3 URL: '{url}'"
        return url, None, error

    try:
        presigned_url = get_s3_presigned_url(url)
    except Exception as e:
        error = str(e)

    return url, presigned_url, error


def _get_multiple_presigned_urls(
    request_id: str,
    urls: List[str],
    agent_state: RemoteProcedureAgentState,
) -> List[Tuple[str, str]]:
    logger.debug(f"Presigning S3 URLs '{', '.join(urls)}' ({request_id=})")

    # Request all URLs asynchronously
    threads_results = []
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        for url in urls:
            threads_results.append(executor.submit(_get_presigned_url_for_thread, url))

    # Separate successful results from errors
    success_results = []
    errors = []
    for future in threads_results:
        response = future.result()
        original_url, presigned_url, error = response

        if error:
            errors.append(f"Could not presign URL '{original_url}' because of error: {error}.")
            continue

        success_results.append((original_url, presigned_url))

    # If we have at least one error, raise error with error
    if errors:
        raise ValueError(" ".join(errors))

    logger.debug(f"Presigned S3 URLs successfully")
    return success_results


JS_NAME_FUNCTION_MAPPING = {
    ProcedureName.GET_MULTIPLE_PRESIGNED_URLS: _get_multiple_presigned_urls,
    ProcedureName.GET_PRESIGNED_URL: _get_presigned_url,
}
