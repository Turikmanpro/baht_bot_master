from tgbot.services.bitrix.bitrix_schemas import DealType, ExchangeType

main_menu = (
    'Главное меню'
)

about = (
    '🔥 Лучший курс для обмена RUB и USDT на THB (Тайский бат)\n\n'
    '♻️ Меняй деньги, рекомендуй друзьям и зарабатывай на реферальной программе!\n\n'
    'Выберите удобный способ для обмена:\n'
    '🏎 Доставка наличных курьером\n'
    '💳 Перевод на Тайский счёт\n'
    '📲 Перевод на Крипто кошелёк\n\n'
    'С нами быстро, просто и надёжно!'
)

referral_menu = (
    'Меняй и зарабатывай'
)

exchange_menu = (
    'Совершить обмен'
)

reviews = (
    'Отзывы'
)

how_it_works = (
    'Приглашайте новых пользователей, чтобы заработать пассивный доход в USDT от их обменов и выводите деньги удобным для вас способом.\n\n'
    'Сгенерируйте вашу персональную ссылку и зарабатывайте!\n\n'
    '- 0,5% cо всех обменов ваших друзей по вашей ссылке\n'
    '- 0,3% c обменов, которые совершаются по персональной ссылке ваших друзей\n'
    '- 0,2% с обменов по персональной ссылке клиентов ваших друзей\n'
)

email_request = (
    'Регистрация\n'
    'Добро пожаловать! Пожалуйста авторизуйтесь, чтобы совершить обмен.\n'
    'Введите ваш Email'
)

confirm_code_request = (
    'На вашу почту "{email}" отправлено письмо с кодом.\n'
    '(Проверьте папку спама, если не видите письма)\n\n'
    'Пожалуйста, введите ваш код'
)

phone_request = (
    '❗️Внимание❗️\n\n'
    'В целях безопасности. НАЖМИТЕ НА КНОПКУ НИЖЕ⬇️\n'
    '«ОТПРАВИТЬ ТЕЛЕФОН📱»\n'
)

successful_registration = (
    'Вы успешно зарегистрировались'
)

exchange_rate = (
    '💹 Курсы обмена - Тайский бат\n\n'
    '🕒 Курс на {time_and_date}\n\n\n'
    '♻️ ПОКУПКА\n\n'
    'RUB/THB\n'
    'Курьерская доставка - {rt_delivery}\n'
    'На счёт (Тай банка) - {rt_transfer}\n\n'
    'USDT/THB\n'
    'Курьерская доставка - {ut_delivery}\n'
    'На счёт (Тай банка) - {ut_transfer}\n\n\n'
    '♻️ ПРОДАЖА\n\n'
    'THB/RUB\n'
    'Курьерская доставка - {tr_delivery}\n'
    'На счёт (Тай банка) - {tr_transfer}\n\n'
    'THB/USDT\n'
    'Курьерская доставка - {tu_delivery}\n'
    'На счёт (Тай банка) - {tu_transfer}\n'
)

referral_link = (
    'Нажмите на вашу реферальную ссылку, чтобы скопировать её:\n\n{link}'
)

stats = (
    'Моя статистика\n\n'
    'Совершено обменов - {exchanges_count}\n'
    'Мои дивиденды 0.5% - {dividends_05} USDT\n'
    'Мои дивиденды 0.3% - {dividends_03} USDT\n'
    'Мои дивиденды 0.2% - {dividends_02} USDT\n'
    'Итого - {dividends_sum} USDT'
)

mail_subject = 'Email confirmation SwapMarketBot'
mail_text = (
    'Confirmation code: {code}\n\n'
    'Email sending time: {time}\n'
    'Email confirmation in SwapMarketBot for user {username}\n\n'
    'This email send you to confirm account in bot if you received an email by mistake, please ignore it'
)

referral_info = (
    'ID - {telegram_id}\n'
    'Имя - {name}\n'
    'Уровень - {level}\n'
    'Обменов - {deals_count}\n'
    'Обменов по ссылке - {ref_deals_count}\n'
    'Email - {email}\n'
    'Телефон - {phone}'
)

active_courier_info = (
    'ID - {telegram_id}\n'
    'Курьер - {name}\n'
    'Выполнено заказов - {deals_count}\n'
    'Отменено заказов - {canceled_deals_count}\n'
    'Периодов - {weeks_live}\n'
    'Старт - {created_at}\n'
    'Заработано - {earned} USDT\n'
    'Уровень - {level}\n'
    'Обменов - {deals_count}\n'
    'Обменов по ссылке - {ref_deals_count}\n'
    'Email - {email}\n'
    'Телефон - {phone}'
)

withdrawal_info = (
    'Ваша сумма дивидендов - {dividends_sum} USDT\n'
    'Минимальная сумма к выводу - {minimal_sum} USDT'
)

courier_withdrawal = (
                         'Доставка курьером наличными в THB (Батах)\n\n'
                     ) + withdrawal_info

rub_withdrawal = (
                     'Получить на Русский счет в RUB (Рублях)\n\n'
                 ) + withdrawal_info

usdt_withdrawal = (
                      'Получить на крипто счет в USDT\n\n'
                  ) + withdrawal_info

thb_withdrawal = (
                     'Получить на Тайский счет в THB (Батах)\n\n'
                 ) + withdrawal_info

successful_courier_withdrawal = (
    'Благодарим за Вашу заявку!\n'
    'Вы получите - {withdrawal_sum} THB\n\n'
    'Наш оператор свяжется с вами в ближайшее время'
)

bank_choose = (
    'Выберите ваш банк'
)

token_choose = (
    'Выберите номер сети'
)

another_currency_dividends_withdrawal = (
    'Благодарим за Вашу заявку!\n'
    '{withdrawal_sum} для вывода в USDT, Вы получаете {receive_sum} в {currency} по курсу “{exchange_rate}”\n'
    'Реквизиты для получения RUB\n'
    'Банк - {bank}\n'
    'Номер карты - {card_number}\n'
    'Вы получите сообщение от оператора в ближайшее время'
)

usdt_dividends_withdrawal = (
    'Благодарим за Вашу заявку!\n'
    '{withdrawal_sum} для вывода в USDT\n'
    'Реквизиты для получения USDT\n'
    'Сеть - {token}\n'
    'Кошелёк - {wallet}\n'
    'Вы получите сообщение от оператора в ближайшее время'
)

order = (
    'Номер заказа: {bitrix_id}\n'
    'Обмен: {exchange_type}\n\n'

    'Тип: Доставка курьером\n'
    'Имя: {username}\n\n'

    'ID: {customer_telegram_id}\n\n'

    'Контакты {phone_number}\n\n'

    'Сумма к выдаче в {receive_cur} - {customer_receive}\n\n'

    'Сумма к обмену в {give_cur} - {customer_give}\n\n'

    'Курс: {exchange_rate}\n\n'

    'Локация: {location}\n'
    'Время: {started_at}'
)

notify_from_crm = (
    '{amount} {currency} Отправлено\n'
    'Банк {bank}\n'
    '{card_number}\n'
)

pre_order_message = (
    'Ваша сумма {} в {}\n'
    'Вы получите {} {}\n'
    'По курсу {}'
)

operator_info = (
    'Оператор - {name}\n'
    'ID - {id}\n'
    'Уровень - {level}\n'
    'Обменов - {deals} Обменов по ссылке - {ref_deals}\n'
    'Контакты - {email}\n'
    'Контакты - {phone}\n'
)

formed_deal_message = (

    'Ваш банк отправитель - {rub_bank}\n\n'
    'Реквизиты для получения THB:\n'
    'Тайский банк: {thb_bank}\n'
    'Номер аккаунта: {thb_bank_requisites}\n\n'
    'Наш оператор свяжется с вами в ближайшее время'
)


def get_formed_deal_message(ex_type: ExchangeType, deal_type: DealType, message_data: list, custom_data: dict):
    main_mes = (
        f'Благодарим за Вашу заявку!\n'
        f'Имя - {message_data[6]}\n'
        f'Номер телефона - {message_data[5]}\n'
        f'Сумма для обмена в {message_data[0]} - {message_data[1]}\n'
        f'Вы получаете в {message_data[2]} - {message_data[3]}\n'
        f'Курс - {message_data[4]}\n\n'
    )

    if deal_type == DealType.THAI_TRANSFER:
        if ex_type == ExchangeType.RUB_THB:
            main_mes += f'Ваш банк отправитель - {custom_data["sending_bank"]}\n\n'
            main_mes += (
                'Реквизиты для получения THB:\n'
                f'Тайский банк: {custom_data["receive_bank"]}\n'
                f'Номер аккаунта: {custom_data["receive_bank_requisites"]}\n\n'
            )
        elif ex_type == ExchangeType.USDT_THB:
            main_mes += (
                'USDT\n'
                f'Сеть - {custom_data["network_type"]}\n'
                'Реквизиты для получения THB:\n'
                f'Тайский банк: {custom_data["receive_bank"]}\n'
                f'Номер аккаунта: {custom_data["receive_bank_requisites"]}\n\n'
            )
        elif ex_type == ExchangeType.THB_USDT:
            main_mes += (
                f'Банк с которого делаете перевод - {custom_data["sending_bank"]}\n\n'
                'Реквизиты для получения USDT\n'
                f'Сеть - {custom_data["receive_bank"]}\n'
                f'Реквизиты - {custom_data["receive_bank_requisites"]}\n\n'
            )
    elif deal_type == DealType.RUS_TRANSFER:
        if ex_type == ExchangeType.THB_RUB:
            main_mes += (
                'Реквизиты для получения RUB:\n'
                f'Банк - {custom_data["receive_bank"]}\n'
                f'Номер карты - {custom_data["receive_bank_requisites"]}\n\n'
            )
    elif deal_type == DealType.COURIER:
        main_mes += (
            f'Локация - {custom_data["location"]}\n'
            f'Комментарий - {custom_data["location_comment"]}\n\n'
        )
        if ex_type == ExchangeType.USDT_THB:
            main_mes += (
                'USDT\n'
                f'Сеть - {custom_data["network_type"]}\n\n'
            )
    elif deal_type == DealType.CASH:
        main_mes += (
            f'Локация - {custom_data["location"]}\n'
            f'Комментарий - {custom_data["location_comment"]}\n\n'
        )
        if ex_type == ExchangeType.THB_RUB:
            main_mes += (
                'Реквизиты для получения RUB:\n'
                f'Банк - {custom_data["receive_bank"]}\n'
                f'Номер карты - {custom_data["receive_bank_requisites"]}\n\n'
            )
        elif ex_type == ExchangeType.RUB_THB:
            main_mes += (
                'Реквизиты, с которых делаете перевод в RUB:\n'
                f'Банк - {custom_data["sending_bank"]}\n'
            )
        elif ex_type == ExchangeType.THB_USDT:
            main_mes += (
                'Ваши реквизиты USDT:\n'
                f'Реквизиты: {custom_data["sending_bank_requisites"]}\n'
            )

    main_mes += '\nНаш оператор свяжется с вами в ближайшее время'

    return main_mes


def get_message_from_crm(ex_type: ExchangeType, deal_type: DealType, message_data: list, custom_data: dict):
    main_mes = (
        f'Сумма для обмена в {message_data[0]} - {message_data[1]}\n'
        f'Вы получаете в {message_data[2]} - {message_data[3]}\n'
        f'Курс - {message_data[4]}\n\n'

        f'Номер телефона - {message_data[5]}\n'
        f'Имя - {message_data[6]}\n'
        f'Обращение - {message_data[8]}\n'
        f'Номер заказа - {message_data[7]}\n\n'
    )

    if deal_type == DealType.THAI_TRANSFER:
        if ex_type == ExchangeType.RUB_THB:
            main_mes += f'Ваш банк отправитель - {custom_data["sending_bank"]}\n\n'
            main_mes += (
                'Реквизиты для получения THB:\n'
                f'Тайский банк: {custom_data["receive_bank"]}\n'
                f'Номер аккаунта: {custom_data["receive_bank_requisites"]}\n\n'
            )
        elif ex_type == ExchangeType.USDT_THB:
            main_mes += (
                'Реквизиты для получения THB:\n'
                f'Тайский банк: {custom_data["receive_bank"]}\n'
                f'Номер аккаунта: {custom_data["receive_bank_requisites"]}\n\n'
            )
        elif ex_type == ExchangeType.THB_USDT:
            main_mes += (
                f'Банк с которого делаете перевод - {custom_data["sending_bank"]}\n\n'
                'Реквизиты для получения USDT\n'
                f'Сеть - {custom_data["receive_bank"]}\n'
                f'Реквизиты - {custom_data["receive_bank_requisites"]}\n\n'
            )
    elif deal_type == DealType.RUS_TRANSFER:
        if ex_type == ExchangeType.THB_RUB:
            main_mes += (
                'Реквизиты для получения RUB:\n'
                f'Банк - {custom_data["receive_bank"]}\n'
                f'Номер карты - {custom_data["receive_bank_requisites"]}\n\n'
            )
    elif deal_type == DealType.COURIER:
        main_mes += (
            f'Локация - {custom_data["location"]}\n'
            f'Комментарий - {custom_data["location_comment"]}\n\n'
        )
        if ex_type == ExchangeType.USDT_THB:
            main_mes += (
                'USDT\n'
                f'Сеть - {custom_data["network_type"]}\n'
            )
    elif deal_type == DealType.CASH:
        main_mes += (
            f'Локация - {custom_data["location"]}\n'
            f'Комментарий - {custom_data["location_comment"]}\n\n'
        )
        if ex_type == ExchangeType.THB_RUB:
            main_mes += (
                'Реквизиты для получения RUB:\n'
                f'Банк - {custom_data["receive_bank"]}\n'
                f'Номер карты - {custom_data["receive_bank_requisites"]}\n\n'
            )
        elif ex_type == ExchangeType.RUB_THB:
            main_mes += (
                'Реквизиты для отправки RUB:\n'
                f'Банк - {custom_data["sending_bank"]}\n'
            )
        elif ex_type == ExchangeType.THB_USDT:
            main_mes += (
                'Ваши реквизиты USDT:\n'
                f'Реквизиты: {custom_data["sending_bank_requisites"]}\n'
            )

    return main_mes


settings = (
    'Настройки\n\n'
    'Доставка курьером - {delivery_coef}%\n'
    'Перевод на счёт - {transfer_coef}%'
)

after_ex_rate_update = (
    'Текущий курс: {ex_rate}\n'
    'Сумма для обмена в {customer_give_currency} - {customer_give}\n'
    'Вы получаете в {customer_receive_currency} - {customer_receive}\n'
)

ex_rate_update = (
    'Курьер прибыл. Пожалуйста нажмите кнопку ОБНОВИТЬ, чтобы уточнить курс обмена\n\n'
    'Курс: {ex_rate}\n'
    'Сумма для обмена в {customer_give_currency} - {customer_give}\n'
    'Вы получаете в {customer_receive_currency} - {customer_receive}\n'
)

courier_text = (
    'Имя заказчика: {username}\n'
    'Номер: {phone}\n'
    'Адрес: {location}\n'
    'Комментарий: {comment}\n\n'

    'Обмен: {deal_type}\n'
    'Заказчик даёт: {give}\n'
    'Заказчик получает: {receive}'
)

admin_stats = (
    'Статистика\n\n'

    'Рефералы исходный уровень\n'
    'Общая сумма обменов - {exchanges_sum} USDT\n'
    'Общая сумма дивидендов - {dividends_sum} USDT\n\n'
    'Пользователей ИР1 - {refs_count_1}\n'
    'Пользователей ИР2 - {refs_count_2}\n'
    'Пользователей ИР3 - {refs_count_3}\n'
    'Пользователей ИР0 - {refs_count_0}\n\n'
    'Пользователей системы - {refs_count}\n'
    'Сумма обменов ИР0 - {exchanges_0_sum} USDT\n'
    'Общая сумма дивидендов ИР0 - {dividends_0_sum} USDT\n\n'
)

ir_stats = (
    'Статистика ИР{ir_level}\n\n'

    'Нажатий Start - {start_clicks}\n'
    'Нажатий "Узнать курс" - {rate_clicks}\n'
    'Нажатий "Совершить обмен" - {exchange_clicks}\n'
    'Новых регистраций - {reg_count}\n\n'

    'Оформлено Новых заявок - {orders_count}\n\n'

    'Покупка\n'
    'THB / RUB (На счет) - {tr_transfer}\n'
    'THB / RUB (Курьер) - {tr_delivery}\n'
    'THB / USDT (На счет) - {tu_transfer}\n'
    'THB / USDT (Курьер) - {tu_delivery}\n\n'

    'Продажа\n'
    'RUB / THB (На счет) - {rt_transfer}\n'
    'RUB / THB (Курьер) - {rt_delivery}\n'
    'USDT / THB (На счет) - {ut_transfer}\n'
    'USDT / THB (Курьер) - {ut_delivery}'
)

referral_stats = (
    'ИР {orig_ref}\n'
    # 'Новых пользователей - {new_users}\n'
    'Сумма обменов - {exchanges_sum} USDT\n'
    'Всего обменов - {exchanges_count}\n'
    'Сумма дивидендов - {dividends_sum} USDT\n\n'
)

update_rate_input = (
    'Пожалуйста нажмите кнопку ОБНОВИТЬ, чтобы уточнить курс обмена'
)

quick_deal_client_message = (
    'Ваша заявка\n\n'
    'Имя: {name}\n'
    'Тел: {phone}\n'
    'Ник: {username}\n'
    'Офис приема средств: "{acceptance_city}"\n\n'
    'Направление для получения: "{country}"\n\n'
    'Вы отдаете в {currency} - {amount}\n'
)

quick_deal_mover_message = (
    'НОВАЯ ЗАЯВКА - БЫСТРАЯ ПЕРЕСТАНОВКА (КЛИЕНТ)\n\n'
    'Номер заявки: {mover_order_id}\n'
    'Дата {date}\n'
    'Имя: {name}\n'
    'Тел: {phone}\n'
    'Ник: {username}\n'
    'Офис приема средств: "{acceptance_city}"\n\n'
    'Направление для получения: "{country}"\n\n'
    'Клиент отдает в {currency} - {amount}\n'
)

often_deal_client_message = quick_deal_client_message + 'Вы получаете в THB: {amount_2}\n' + 'Курс: {ex_rate}\n'
often_deal_mover_message = quick_deal_mover_message.replace('БЫСТРАЯ', '') + 'Вы получаете в THB: {amount_2}\n' + 'Курс: {ex_rate}\n'


courier_account = (
    'Выполнено заказов - {finished_orders}\n'
    'Отменено заказов - {canceled_orders_count}\n'
    'Периодов - {days_from_reg}\n'
    'Старт - {created_at}\n'
    'Заработано - {earned}\n'
)


def get_courier_delivery_message(deal, username):
    if deal.exchange_type == ExchangeType.THB_USDT or deal.exchange_type == ExchangeType.USDT_THB:
        network_type = deal.network_type
    else:
        network_type = 'Нет сети'
    if deal.deal_type == DealType.COURIER or deal.deal_type == DealType.CASH:
        location = deal.location
        location_comment = deal.location_comment
    else:
        location = 'Нет'
        location_comment = 'Нет'
    message = (
        f'Имя клиента: {deal.customer_name}\n'
        f'Номер телефона: {deal.phone_number}\n'
        f'Номер заказа: {deal.bitrix_id}\n\n'
        f'Обмен: {deal.exchange_type}\n'
        f'Тип: {deal.deal_type}\n'
        f'Обращение: {username}\n'
        f'Сумма к выдаче в {deal.exchange_type.split("/")[1]}: {deal.customer_receive}\n'
        f'Сумма к обмену в {deal.exchange_type.split("/")[0]}: {deal.customer_give}\n'
        f'Сеть(если есть): {network_type}\n'
        f'Курс: {deal.exchange_rate}\n'
        f'Локация: {location}\n'
        f'Комментарий: {location_comment}\n'
    )
    return message
