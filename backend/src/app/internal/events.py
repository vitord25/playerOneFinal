from enum import Enum


class LudotecaEvent(str, Enum):
    # Eventos de Usuário
    USER_CREATED = "user.created"
    USER_DEACTIVATED = "user.deactivated"

    # Eventos de Party
    PARTY_CREATED = "party.created"
    PARTY_APPROVED = "party.approved"
    PARTY_REJECTED = "party.rejected"
    PARTY_CANCELLED = "party.cancelled"

    # Eventos de Membros
    MEMBER_REQUESTED = "member.requested"
    MEMBER_APPROVED = "member.approved"
    MEMBER_REJECTED = "member.rejected"
    MEMBER_REMOVED = "member.removed"
    MEMBER_LEFT = "member.left"
    
    # Eventos de Mensagem
    MESSAGE_SENT = "message.sent"
    
    # Eventos de Jogos
    GAME_AVAILABILITY_CHANGED = "game.availability_changed"

    # Eventos de Auditoria
    AUDIT_ACTION = "audit.action"