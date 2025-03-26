from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from WeeeeFor6 import predict_price
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import numpy as np
import logging

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем клавиатуру
reply_keyboard = [["Получить анализ цен"]]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)


def analyze_prices(prices):
    """Анализирует цены и дает рекомендации"""
    prices = pd.Series(prices)

    # Расчет тренда
    trend = "растет" if prices.iloc[-1] > prices.iloc[0] else "падает"

    # Расчет недель роста/падения
    changes = prices.diff().dropna()
    growth_weeks = sum(changes > 0)
    decline_weeks = sum(changes < 0)

    # Определение рекомендации
    if trend == "растет":
        recommendation = f"Рекомендуется закупать на {growth_weeks} недель вперед"
        strategy = "Покупайте постепенно, используя усреднение цены"
    else:
        min_price_idx = prices.idxmin()
        recommendation = f"Лучшая цена: {prices[min_price_idx]:,.2f} руб. на неделе {min_price_idx}"
        strategy = "Дождитесь минимальной цены для максимальной выгоды"

    return {
        'trend': trend,
        'current_price': prices.iloc[-1],
        'growth_weeks': growth_weeks,
        'decline_weeks': decline_weeks,
        'recommendation': recommendation,
        'strategy': strategy,
        'min_price': prices.min(),
        'max_price': prices.max()
    }


def create_price_plot(prices):
    """Создает график цен"""
    plt.figure(figsize=(10, 5))
    prices.plot(title='Динамика цен на арматуру', marker='o')
    plt.xlabel('Неделя')
    plt.ylabel('Цена (руб./т)')
    plt.grid(True)

    # Сохраняем график в буфер
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = "Нажмите кнопку для получения анализа цен и рекомендаций по закупке"
    await update.message.reply_text(help_text, reply_markup=markup)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.text == "Получить анализ цен":
        try:
            # Получаем цены
            prices = predict_price()
            logger.info(f"Получены цены:\n{prices}")

            # Анализируем
            analysis = analyze_prices(prices)
            formatted_price = f"{analysis['current_price']:,.2f}".replace(",", " ")

            # Создаем сообщение
            message = (
                f"📊 Текущая цена: {formatted_price} руб./т\n"
                f"📈 Тренд: цены {analysis['trend']}\n"
                f"🟢 Недель роста: {analysis['growth_weeks']}\n"
                f"🔴 Недель падения: {analysis['decline_weeks']}\n\n"
                f"💡 Рекомендация: {analysis['recommendation']}\n"
                f"🔧 Стратегия: {analysis['strategy']}\n\n"
                f"Минимальная цена: {analysis['min_price']:,.2f} руб.\n"
                f"Максимальная цена: {analysis['max_price']:,.2f} руб."
            )

            # Создаем и отправляем график
            plot_buf = create_price_plot(prices)
            await update.message.reply_photo(photo=plot_buf, caption=message, reply_markup=markup)

        except Exception as e:
            logger.error(f"Ошибка: {str(e)}", exc_info=True)
            await update.message.reply_text(
                "⚠️ Не удалось проанализировать цены. Попробуйте позже.",
                reply_markup=markup
            )
    else:
        await update.message.reply_text(
            "Используйте кнопку 'Получить анализ цен'",
            reply_markup=markup
        )


def main():
    application = Application.builder().token("7825620295:AAEslAkl-Ar7AzJ6G8h-i2LKxNF-S97ylrs").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()


if __name__ == "__main__":
    main()