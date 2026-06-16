import asyncio
import json
import logging
import aio_pika
from aio_pika import ExchangeType
from src.app.core.config import settings
from src.app.internal.events import LudotecaEvent

logger = logging.getLogger(__name__)

EXCHANGE_NAME = "ludoteca"
QUEUE_NAME = "ludoteca.events"

# Conexão de consumo mantida viva enquanto a aplicação roda
_consumer_connection: aio_pika.RobustConnection | None = None


async def get_connection() -> aio_pika.RobustConnection:
    url = (
        f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}"
        f"@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}/"
    )
    return await aio_pika.connect_robust(url)


async def publish_event(event: LudotecaEvent, payload: dict) -> None:
    try:
        connection = await get_connection()
        async with connection:
            channel = await connection.channel()

            exchange = await channel.declare_exchange(
                EXCHANGE_NAME,
                ExchangeType.TOPIC,
                durable=True,
            )

            message_body = json.dumps(payload, default=str).encode()

            message = aio_pika.Message(
                body=message_body,
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            )

            await exchange.publish(message, routing_key=event.value)

            logger.info(f"[RabbitMQ] Evento publicado: {event.value} | Payload: {payload}")

    except Exception as e:
        logger.error(f"[RabbitMQ] Falha ao publicar evento '{event.value}': {e}")


# -----------------------------------------------------------------------------
# Consumer (Observer Pattern — lado consumidor)
# Assina TODOS os eventos do exchange 'ludoteca' e os processa.
# Projetado para rodar como background task no startup do FastAPI.
# -----------------------------------------------------------------------------
async def _handle_message(message: aio_pika.IncomingMessage) -> None:
    async with message.process():
        routing_key = message.routing_key
        try:
            payload = json.loads(message.body.decode())
        except (ValueError, UnicodeDecodeError):
            payload = message.body.decode(errors="replace")
        logger.info(
            f"[RabbitMQ:CONSUMER] Evento recebido: {routing_key} | Payload: {payload}"
        )


async def start_consumer() -> None:
    """
    Inicia o consumidor de eventos. Reconecta automaticamente em caso de falha.
    Deve ser disparado como uma background task (asyncio.create_task) no startup.
    """
    global _consumer_connection

    while True:
        try:
            _consumer_connection = await get_connection()
            channel = await _consumer_connection.channel()
            await channel.set_qos(prefetch_count=10)

            exchange = await channel.declare_exchange(
                EXCHANGE_NAME,
                ExchangeType.TOPIC,
                durable=True,
            )

            queue = await channel.declare_queue(QUEUE_NAME, durable=True)
            # '#' = assina todas as routing keys do topic exchange
            await queue.bind(exchange, routing_key="#")

            logger.info(
                f"[RabbitMQ:CONSUMER] Consumidor iniciado | exchange='{EXCHANGE_NAME}' "
                f"queue='{QUEUE_NAME}'"
            )
            await queue.consume(_handle_message)

            # Mantém a corrotina viva enquanto a conexão estiver aberta
            while not _consumer_connection.is_closed:
                await asyncio.sleep(5)

        except asyncio.CancelledError:
            logger.info("[RabbitMQ:CONSUMER] Consumidor cancelado (shutdown).")
            break
        except Exception as e:
            logger.error(
                f"[RabbitMQ:CONSUMER] Erro no consumidor: {e}. "
                f"Tentando reconectar em 5s..."
            )
            await asyncio.sleep(5)


async def stop_consumer() -> None:
    """Fecha a conexão do consumidor (chamado no shutdown)."""
    global _consumer_connection
    if _consumer_connection and not _consumer_connection.is_closed:
        await _consumer_connection.close()
        logger.info("[RabbitMQ:CONSUMER] Conexão do consumidor encerrada.")