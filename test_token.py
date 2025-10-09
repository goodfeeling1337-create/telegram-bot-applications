#!/usr/bin/env python3
# test_token.py - Тест нового токена бота

import asyncio
import sys
from telegram import Bot
from config import BOT_TOKEN

async def test_token():
    """Тестирует новый токен бота"""
    print("🔑 Тестирование нового токена бота...")
    print(f"📋 Токен: {BOT_TOKEN[:10]}...{BOT_TOKEN[-10:]}")
    
    try:
        # Создаем объект бота
        bot = Bot(token=BOT_TOKEN)
        
        # Получаем информацию о боте
        me = await bot.get_me()
        
        print("✅ Токен работает!")
        print(f"🤖 Имя бота: {me.first_name}")
        print(f"📛 Username: @{me.username}")
        print(f"🆔 ID бота: {me.id}")
        print(f"📝 Описание: {me.description or 'Нет описания'}")
        
        # Проверяем, может ли бот получать обновления
        try:
            updates = await bot.get_updates(limit=1)
            print(f"📨 Получено обновлений: {len(updates)}")
        except Exception as e:
            print(f"⚠️ Предупреждение при получении обновлений: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка с токеном: {e}")
        return False

async def main():
    """Основная функция"""
    success = await test_token()
    
    if success:
        print("\n🎉 Токен успешно протестирован!")
        print("✅ Бот готов к работе")
    else:
        print("\n💥 Токен не работает!")
        print("❌ Проверьте правильность токена")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
