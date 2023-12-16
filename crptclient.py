from httpx import post
from typing import Tuple
from datetime import date


def _get_version(datamatrix: str, logger) -> int:
    url = "https://mobile.api.crpt.ru/mobile/product-card/version"
    body = {
        "codeType": "datamatrix",
        "code": datamatrix
    }
    logger.debug(f"Start request for CRPT version. Datamatrix = [{datamatrix}]")
    res = post(url, json=body)
    res.raise_for_status()
    return res.json()["version"]


def get_crpt_data(datamatrix: str, logger) -> Tuple[str, int]:
    api_version = _get_version(datamatrix, logger)
    logger.debug(f"Got CRPT api version = [{api_version}]")
    if api_version > 1:
        url = f"https://mobile.api.crpt.ru/v{api_version}/mobile/check"
    else:
        url = "https://mobile.api.crpt.ru/mobile/check"
    body = {
        "codeType": "datamatrix",
        "code": datamatrix
    }
    logger.debug(f"Start request for CRPT dm check. Datamatrix = [{datamatrix}]")
    res = post(url, json=body)
    res.raise_for_status()
    data = res.json()
    product_name = data["productName"]
    exp_timestamp = int(str(data["drugsData"]["expireDate"])[:-3])
    exp_date = date.fromtimestamp(exp_timestamp).toordinal()
    logger.debug(f"Request to CRPT was successful. Product name = [{product_name}], expiration date = [{exp_date}]")
    return product_name, exp_date
