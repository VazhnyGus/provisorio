import asyncio
import logging

from telebot.async_telebot import AsyncTeleBot, types, logger
from re import match
from datetime import date

from provisor import add_drug_by_datamatrix, add_drug_by_text, get_all_drugs, delete_drug, get_overdue, delete_overdue


BOT_TOKEN = ""


log = logger
log.setLevel(logging.DEBUG)


bot = AsyncTeleBot(token=BOT_TOKEN)


@bot.message_handler(commands=["start"])
async def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    start_button = types.KeyboardButton("Начать")
    markup.add(start_button)
    await bot.send_message(
        chat_id=message.from_user.id,
        text="💊 Привет! Это бот Provisor.io 💊\n\nЯ помогу тебе следить за твоими медикаментами. Добавь препараты, а я пришлю тебе уведомление, когда у них закончится срок годности.\n\nНажми «Начать», чтобы перейти к функционалу",
        parse_mode='Markdown',
        reply_markup=markup
    )


@bot.message_handler(content_types=["text"])
async def using(message):

    drug_m = match(".*@\d{4}-\d{2}-\d{2}", message.text)
    del_m = match("Удалить \d+", message.text)

    try:
        if int(message.text):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
            delete_button = types.KeyboardButton(f"Удалить {message.text}")
            cancel_button = types.KeyboardButton("Отмена")
            markup.add(delete_button, cancel_button)
            await bot.send_message(
                chat_id=message.from_user.id,
                text=f"Вы уверены, что хотите удалить препарат {message.text}?",
                reply_markup=markup
            )
    except ValueError:
        if message.text == "Начать":
            markup = main_markup()
            await bot.send_message(
                chat_id=message.from_user.id,
                text="Сфотографируй маркировку на упаковке или добавь препарат вручную",
                reply_markup=markup
            )

        elif message.text == "Добавить по маркировке":
            await bot.send_message(
                chat_id=message.from_user.id,
                text="Пришли фотографию маркировки на упаковке препарата"
            )

        elif message.text == "Добавить вручную":
            await bot.send_message(
                chat_id=message.from_user.id,
                text="Напиши название препарата и срок годности, разделенные собакой @\n\nДата должна быть указана в формате ГГГГ-ММ-ДД\n\nНапример:\n`Парацетомол 24 таб.@2024-01-24`",
                parse_mode='Markdown'
            )

        elif drug_m:
            is_adding_success, product_name = add_drug_by_text(message.from_user.id, message.text, log)
            markup = main_markup()
            if is_adding_success:
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text=f"Препарат «{product_name}» успешно добавлен",
                    reply_markup=markup
                )
            else:
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text=f"Не удалось добавить препарат. Попробуй снова",
                    reply_markup=markup
                )

        elif message.text == "Мои препараты":
            all_drugs = get_all_drugs(message.from_user.id, log)
            markup = main_markup()
            if all_drugs != "":
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text=all_drugs,
                    reply_markup=markup
                )
            else:
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text="Не добавлено ни одного препарата",
                    reply_markup=markup
                )

        elif message.text == "Удалить препарат":
            all_drugs = get_all_drugs(message.from_user.id, log)
            if all_drugs != "":
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text=all_drugs
                )
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text="Выше я прислал список всех твоих лекарств. Напиши номер препарата, который нужно удалить из списка"
                )
            else:
                markup = main_markup()
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text="Не добавлено ни одного препарата",
                    reply_markup=markup
                )

        elif del_m:
            markup = main_markup()
            drug_to_del = int(message.text[8:])
            delete_drug(message.from_user.id, drug_to_del, log)
            await bot.send_message(
                chat_id=message.from_user.id,
                text=f"Препарат {drug_to_del} удален из списка",
                reply_markup=markup
            )

        elif message.text == "Отмена":
            markup = main_markup()
            await bot.send_message(
                chat_id=message.from_user.id,
                text="Действие отменено",
                reply_markup=markup
            )

        elif message.text == "Удалить все просроченные":
            markup = main_markup()
            delete_overdue(message.from_user.id, log)
            await bot.send_message(
                chat_id=message.from_user.id,
                text="Удалены все просроченные препараты",
                reply_markup=markup
            )

        else:
            markup = main_markup()
            await bot.send_message(
                chat_id=message.from_user.id,
                text="Неизвестная команда",
                reply_markup=markup
            )


@bot.message_handler(content_types=["photo"])
async def handle_photo(message):
    file = await bot.get_file(message.photo[-1].file_id)
    photo = await bot.download_file(file.file_path)
    await bot.send_message(
        chat_id=message.from_user.id,
        text="Дай мне минутку, пытаюсь прочитать маркировку...",
    )
    is_adding_success, product_name = add_drug_by_datamatrix(photo, message.from_user.id, log)
    if is_adding_success:
        markup = main_markup()
        await bot.send_message(
            chat_id=message.from_user.id,
            text=f"Препарат «{product_name}» успешно добавлен",
            reply_markup=markup
        )
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        add_man_button = types.KeyboardButton("Добавить вручную")
        cancel_button = types.KeyboardButton("Отмена")
        markup.add(add_man_button, cancel_button)
        await bot.send_message(
            chat_id=message.from_user.id,
            text=f"Не удалось добавить препарат по фотографии. Попробуй снова или добавь вручную",
            reply_markup=markup
        )


def main_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    add_button = types.KeyboardButton("Добавить по маркировке")
    add_man_button = types.KeyboardButton("Добавить вручную")
    view_list_button = types.KeyboardButton("Мои препараты")
    delete_button = types.KeyboardButton("Удалить препарат")
    markup.add(add_button, add_man_button, view_list_button, delete_button)
    return markup


async def check_overdue():
    while True:
        overdue = get_overdue(log)
        markup = main_markup()
        delete_overdue_button = types.KeyboardButton("Удалить все просроченные")
        markup.add(delete_overdue_button)
        if len(overdue) > 0:
            for user in overdue:
                overdue_list = "У вас есть препараты с истекшим сроком годности:\n\n"
                for drug in overdue[user]:
                    name, exp_date = drug
                    overdue_list += f"{name} (до {date.fromordinal(exp_date).isoformat()})\n"
                await bot.send_message(
                    chat_id=user,
                    text=overdue_list,
                    reply_markup=markup
                )
        await asyncio.sleep(86400)


async def main():
    await asyncio.gather(bot.polling(non_stop=True, interval=0), check_overdue())
