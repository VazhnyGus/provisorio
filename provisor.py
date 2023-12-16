import io
from pylibdmtx.pylibdmtx import decode
from PIL import Image
from typing import Union, List, Tuple, Dict
from datetime import date

from crptclient import get_crpt_data
from db import db_add_drug, db_get_user_drugs, db_delete_drug, db_get_overdue, db_delete_overdue


def add_drug_by_datamatrix(photo: bytes, chat_id: Union[int, str], logger) -> Tuple[bool, str]:
    try:
        image = Image.open(io.BytesIO(photo))
        logger.debug(f"Image resolved. Image size = [{image.size[0]}x{image.size[1]}]")
        decoded_dm = decode(image)
        dm = decoded_dm[0].data.decode()
        logger.debug(f"Datamatrix decoded successfully: [{dm}]")
        product_name, exp_date = get_crpt_data(dm, logger)
        db_add_drug(str(chat_id), product_name, exp_date)
        logger.debug(f"Added drug fot user [{chat_id}]")
        return True, product_name
    except Exception as e:
        logger.error(e)
        return False, ""


def add_drug_by_text(chat_id: Union[int, str], drug_data: str, logger) -> Tuple[bool, str]:
    try:
        logger.debug(f"Got string [{drug_data}]")
        product_name, exp_date = drug_data.split("@")
        logger.debug(f"String splitted on [{product_name}] and [{exp_date}]")
        db_add_drug(str(chat_id), product_name, date.fromisoformat(exp_date).toordinal())
        logger.debug(f"Drug added for user [{chat_id}]")
        return True, product_name
    except Exception as e:
        logger.error(e)
        return False, ""


def get_all_drugs(chat_id: Union[int, str], logger) -> str:
    logger.debug(f"Trying to get drug list for user [{chat_id}]")
    user_drugs: list = db_get_user_drugs(str(chat_id))
    all_drugs = ""
    if len(user_drugs) > 0:
        logger.debug("Drug list is not empty")
        for drug in user_drugs:
            db_id, name, exp_date = drug
            all_drugs += f"{user_drugs.index(drug) + 1}. {name} (до {date.fromordinal(exp_date).isoformat()})\n"
        logger.debug(f"Return drug list for user [{chat_id}]. {len(user_drugs)} items found")
    else:
        logger.debug("Drug list is empty")
    return all_drugs


def delete_drug(chat_id: Union[int, str], index: int, logger):
    logger.debug(f"Trying to delete drug [{index}] in user [{chat_id}]")
    user_drugs = db_get_user_drugs(str(chat_id))
    logger.debug(f"Got drug list for user [{chat_id}]")
    drug_to_delete = user_drugs[index - 1]
    id_to_delete = drug_to_delete[0]
    db_delete_drug(id_to_delete)
    logger.debug(f"Drug [{index}] deleted")


def get_overdue(logger) -> Dict[str, List[Tuple[str, int]]]:
    logger.debug("Trying to get overdue drugs")
    overdue = db_get_overdue()
    logger.debug(f"Got {len(overdue)} users with overdue drugs")
    return overdue


def delete_overdue(chat_id: Union[str, int], logger):
    logger.debug(f"Trying to delete overdue drugs for user [{chat_id}]")
    db_delete_overdue(str(chat_id))
    logger.debug(f"Overdue drugs for user [{chat_id}] deleted")
