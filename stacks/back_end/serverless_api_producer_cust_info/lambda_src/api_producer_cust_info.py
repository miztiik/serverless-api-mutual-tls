import json
import logging
import datetime
import os
import random
import boto3


class GlobalArgs:
    """ Global statics """
    OWNER = "Mystique"
    ENVIRONMENT = "production"
    MODULE_NAME = "customer_info_producer"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    MAX_MSGS_TO_PRODUCE = int(os.getenv("MAX_MSGS_TO_PRODUCE", 2))
    ANDON_CORD_PULLED = os.getenv("ANDON_CORD_PULLED", False)


def set_logging(lv=GlobalArgs.LOG_LEVEL):
    logging.basicConfig(level=lv)
    logger = logging.getLogger()
    logger.setLevel(lv)
    return logger


def _rand_coin_flip():
    r = False
    if os.getenv("TRIGGER_RANDOM_FAILURES", True):
        if random.randint(1, 100) > 90:
            r = True
    return r


def gen_dob(max_age=99, date_fmt="%Y-%m-%d"):
    return (
        datetime.datetime.today() - datetime.timedelta(days=random.randint(0, 365 * max_age))
    ).strftime(date_fmt)


LOG = set_logging()


def lambda_handler(event, context):
    resp = {"status": False}
    LOG.debug(f"Event: {json.dumps(event)}")

    _random_user_name = ["Aarakocra", "Aasimar", "Beholder", "Bugbear", "Centaur", "Changeling", "Deep Gnome", "Deva", "Lizardfolk", "Loxodon", "Mind Flayer",
                         "Minotaur", "Orc", "Shardmind", "Shifter", "Simic Hybrid", "Tabaxi", "Yuan-Ti"]

    try:
        msg_cnt = 0
        msg_lst = []
        p_cnt = 0
        while context.get_remaining_time_in_millis() > 100:
            _s = round(random.random() * 100, 2)
            msg_body = {
                "name": random.choice(_random_user_name),
                "dob": gen_dob(),
                "gender": random.choice(["M", "F"]),
                "ssn_no": f"{random.randrange(100000000,999999999)}",
                "data_share_consent": bool(random.getrandbits(1)),
                "evnt_time": datetime.datetime.now().isoformat(),
            }
            msg_attr = {
                "project": {
                    "DataType": "String",
                    "StringValue": "API Design Best Practice: Mutual TLS authentication for APIs"
                },
                "contact_me": {
                    "DataType": "String",
                    "StringValue": "github.com/miztiik"
                },
                "ts": {
                    "DataType": "Number",
                    "StringValue": f"{int(datetime.datetime.now().timestamp())}"
                },
                "store_id": {
                    "DataType": "Number",
                    "StringValue": f"{random.randrange(1,5)}"
                }
            }
            # Randomly remove ssn_no from message
            if _rand_coin_flip():
                msg_attr.pop("store_id", None)
                msg_attr["bad_msg"] = {
                    "DataType": "String",
                    "StringValue": "True"
                }
                p_cnt += 1
                # Merge dicts
                # z = {**x, **y}
            msg_lst.append({"msg_body": msg_body, "msg_attr": msg_attr})
            msg_cnt += 1
            LOG.debug(
                f'{{"remaining_time":{context.get_remaining_time_in_millis()}}}')
            if msg_cnt >= GlobalArgs.MAX_MSGS_TO_PRODUCE:
                break
            # End of while
        resp["tot_msgs"] = msg_cnt
        resp["bad_msgs"] = p_cnt
        resp["msgs"] = msg_lst
        resp["status"] = True
        LOG.info(f'{{"resp":{json.dumps(resp)}}}')

    except Exception as e:
        LOG.error(f"ERROR:{str(e)}")
        resp["error_message"] = str(e)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": resp
        })
    }
