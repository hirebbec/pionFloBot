from contextlib import AsyncExitStack
from functools import wraps
from typing import Any

from telegram import Update
from telegram.ext import ContextTypes


def with_services(*service_names):
    def decorator(func):
        @wraps(func)
        async def wrapper(
            update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
        ):
            telegram_id = update.message.chat.id
            services: dict[str, Any] = {}

            async with AsyncExitStack() as stack:
                for name in service_names:
                    factory = context.application.bot_data[f"{name}_service_factory"]
                    service = await stack.enter_async_context(factory())
                    services[f"{name}_service"] = service

                if "user" in service_names:
                    user_service = services["user_service"]
                    if not await user_service.get_by_telegram_id(telegram_id):
                        await user_service.create_user(telegram_id)

                return await func(update, context, *args, **services, **kwargs)

        return wrapper

    return decorator
