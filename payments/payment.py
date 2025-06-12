from yoomoney import Quickpay
from config.yoomoney import DESCRIPTION, WALLET_NUMBER, FORM


def create(value: int, user_id: int):
    p = Quickpay(
        receiver=WALLET_NUMBER,
        quickpay_form=FORM,
        targets=DESCRIPTION,
        paymentType="SB",
        sum=value,
        label=str(user_id),
    )
    return p.base_url
