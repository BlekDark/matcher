import logging

logger = logging.getLogger("backend-matcher")


async def handle_error(uof, e):
    await uof.rollback()
    logger.error(f"Something went wrong:\n{e}")
    return {
        'status_code': 500,
        'detail': f"Something went wrong:\n{e}"
    }


def make_response(status_code=200, detail="OK", result=None):
    return {
        'status_code': status_code,
        'detail': detail,
        'result': result
    }
