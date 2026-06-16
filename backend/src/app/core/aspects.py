import logging
import functools
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


def audit_action(entity: str, action: str):
    """
    Aspecto de Auditoria.
    Registra automaticamente a ação executada após a conclusão do método.
    JoinPoint: After Returning.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logger.info(f"[AOP:AUDIT] Iniciando '{func.__name__}' | entity={entity} action={action}")
            result = await func(*args, **kwargs)
            logger.info(f"[AOP:AUDIT] Concluído '{func.__name__}' | entity={entity} action={action}")
            return result
        return wrapper
    return decorator


def require_active_user(func):
    """
    Aspecto de Autorização.
    Verifica se o usuário autenticado está ativo antes de executar o método.
    JoinPoint: Before.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        current_user = kwargs.get("current_user")
        if current_user and not current_user.active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário inativo. Acesso negado."
            )
        return await func(*args, **kwargs)
    return wrapper


def log_execution(func):
    """
    Aspecto de Log de Execução.
    Registra entrada e saída de qualquer método de serviço.
    JoinPoint: Around.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logger.info(f"[AOP:LOG] >> Executando: {func.__qualname__}")
        result = await func(*args, **kwargs)
        logger.info(f"[AOP:LOG] << Finalizado: {func.__qualname__}")
        return result
    return wrapper

def require_role(allowed_roles: list[str]):
    """
    Aspecto de Autorização por Papel (Role).
    Verifica se o papel do usuário está na lista permitida antes de executar o método.
    JoinPoint: Before.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            # Se o usuário não existe no contexto ou o role dele não está na lista
            if not current_user or current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Acesso negado. Requer um dos papéis: {', '.join(allowed_roles)}"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator