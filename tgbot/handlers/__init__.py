from .commands import register_commands
from .courier import register_courier
from .other import register_other
from .main_menu import register_main_menu
from .referral import register_referral
from .registration import register_registration
from .other import register_other
from .operator import register_operator
from .withdrawal import register_withdrawal
from .bank import register_bank
from .token import register_token
from .notify import register_notify
from .exchange import register_exchange
from .admin import register_admin
from .customer import register_customer
from .exchange_pre_deal import register_pre_deal
from .permutations import register_permutations
from .movers_add import register_movers_add
from .movers_active_and_del import register_movers_active_and_del
from .permutations_deal_calc import register_permutations_deal_calc
from .movers_order_history import register_movers_order_history

register_functions = (
    register_other,
    register_commands,
    register_courier,
    register_main_menu,
    register_referral,
    register_registration,
    register_operator,
    register_withdrawal,
    register_bank,
    register_token,
    register_notify,
    register_exchange,
    register_admin,
    register_customer,
    register_pre_deal,
    register_permutations,
    register_movers_add,
    register_movers_active_and_del,
    register_permutations_deal_calc,
    register_movers_order_history
)
