from mephisto.abstractions.blueprints.remote_procedure.remote_procedure_agent_state import (
    RemoteProcedureAgentState
)
from mephisto.generators.form_composer.config_validation.utils import get_s3_presigned_url
from mephisto.utils.logger_core import get_logger

logger = get_logger(name=__name__)


class ProcedureName:
    GET_PRESIGNED_URL = "getPresignedUrl"


def _get_presigned_url(request_id: str, url: str, agent_state: RemoteProcedureAgentState):
    logger.debug(f"Presigning S3 URL '{url}' ({request_id=})")
    presigned_url = get_s3_presigned_url(url)
    logger.debug(f"Presigned S3 URL '{presigned_url}'")
    return presigned_url


JS_NAME_FUNCTION_MAPPING = {
    ProcedureName.GET_PRESIGNED_URL: _get_presigned_url,
}
