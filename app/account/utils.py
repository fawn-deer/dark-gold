import datetime
from calendar import timegm

from rest_framework_jwt.utils import jwt_payload_handler


def extend_jwt_payload_handler(user):
    """
    扩展原始生成payload函数，添加生成时间
    :param user:
    :return:
    """
    payload = jwt_payload_handler(user)
    # iat 生成时间 unix时间戳
    payload['iat'] = timegm(datetime.datetime.utcnow().utctimetuple())
    return payload
