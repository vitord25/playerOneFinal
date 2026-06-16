from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.app.models.user import User, UserRole
from src.app.models.audit_log import AuditAction
from src.app.repositories.user_repository import UserRepository
from src.app.schemas.user import UserCreate, UserUpdate, UserChangePassword
from src.app.core.security import hash_password, verify_password, create_access_token
from src.app.core.aspects import audit_action, log_execution
from src.app.services.audit_service import AuditService
from src.app.internal import publish_event, LudotecaEvent


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)
        self.audit = AuditService(db)

    # -------------------------------------------------------------------------
    # RF20 | RN03 | RN04 | RN19 - Criar usuário (público)
    # -------------------------------------------------------------------------
    @log_execution
    @audit_action(entity="USER", action="CREATE")
    async def create_user(self, user_in: UserCreate) -> User:
        # RN04 - Unicidade de e-mail
        if self.repo.get_by_email(user_in.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="E-mail já cadastrado."
            )

        data = user_in.model_dump()
        data["password_hash"] = hash_password(data.pop("password"))

        # Garante que novos usuários sempre nascem como USER (nunca ADMIN)
        data["role"] = UserRole.USER

        user = self.repo.create(data)
        await self.audit.log("USER", user.id, AuditAction.CREATE, user.id)
        return user

    # -------------------------------------------------------------------------
    # RF22 - Autenticar usuário (login)
    # -------------------------------------------------------------------------
    @log_execution
    async def authenticate(self, email: str, password: str) -> str:
        user = self.repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas."
            )
        if not user.active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário inativo."
            )
        await self.audit.log("USER", user.id, AuditAction.LOGIN, user.id)
        return create_access_token({"sub": str(user.id), "role": user.role})

    # -------------------------------------------------------------------------
    # RF25 - Listar todos os usuários (Admin)
    # -------------------------------------------------------------------------
    @log_execution
    async def get_all(self) -> List[User]:
        return self.repo.get_all()

    # -------------------------------------------------------------------------
    # RF24 - Listar usuários ativos (Admin)
    # -------------------------------------------------------------------------
    @log_execution
    async def get_active_users(self) -> List[User]:
        return self.repo.get_active_users()

    # -------------------------------------------------------------------------
    # RF23 - Buscar usuário por ID
    # -------------------------------------------------------------------------
    @log_execution
    async def get_by_id(self, user_id: int) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado."
            )
        return user

    # -------------------------------------------------------------------------
    # RF21 | RN19 - Atualizar dados do usuário
    # Regras:
    #   - usuário base só pode editar a si mesmo
    #   - admin pode editar qualquer usuário
    #   - nenhum usuário pode alterar o próprio role via este endpoint
    # -------------------------------------------------------------------------
    @log_execution
    @audit_action(entity="USER", action="UPDATE")
    async def update_user(
        self, user_id: int, user_in: UserUpdate, current_user: User
    ) -> User:
        user = await self.get_by_id(user_id)

        # Usuário base só pode editar a si mesmo
        if current_user.role != UserRole.ADMIN and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para editar este usuário."
            )

        update_data = user_in.model_dump(exclude_none=True)

        # Nenhum usuário pode alterar role via este endpoint
        update_data.pop("role", None)

        # Senha não pode ser alterada via este endpoint (use change_password)
        update_data.pop("password", None)
        update_data.pop("password_hash", None)

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nenhum campo válido para atualização foi informado."
            )

        updated = self.repo.update(user, update_data)
        await self.audit.log("USER", user_id, AuditAction.UPDATE, current_user.id)
        return updated

    # -------------------------------------------------------------------------
    # RF26 - Alterar role de usuário (Admin)
    # -------------------------------------------------------------------------
    @log_execution
    @audit_action(entity="USER", action="UPDATE")
    async def change_role(
        self, user_id: int, new_role: UserRole, current_user: User
    ) -> User:
        user = await self.get_by_id(user_id)

        # Admin não pode rebaixar a si mesmo
        if current_user.id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Você não pode alterar o próprio role."
            )

        updated = self.repo.update(user, {"role": new_role})
        await self.audit.log("USER", user_id, AuditAction.UPDATE, current_user.id)
        return updated

    # -------------------------------------------------------------------------
    # RF21 - Alterar senha (próprio usuário)
    # -------------------------------------------------------------------------
    @log_execution
    @audit_action(entity="USER", action="UPDATE")
    async def change_password(
        self,
        user_id: int,
        current_password: str,
        new_password: str,
        current_user: User,
    ) -> bool:
        # Usuário só pode alterar a própria senha
        if current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não pode alterar a senha de outro usuário."
            )

        user = await self.get_by_id(user_id)

        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Senha atual incorreta."
            )

        self.repo.update(user, {"password_hash": hash_password(new_password)})
        await self.audit.log("USER", user_id, AuditAction.UPDATE, current_user.id)
        return True

    # -------------------------------------------------------------------------
    # RF27 | RN08 | RN19 - Desativar usuário (Admin / soft delete)
    # Transfere ou deleta parties do usuário antes de desativar
    # -------------------------------------------------------------------------
    @log_execution
    @audit_action(entity="USER", action="DELETE")
    async def deactivate_user(self, user_id: int, current_user: User) -> User:
        user = await self.get_by_id(user_id)

        # Admin não pode desativar a si mesmo
        if current_user.id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Você não pode desativar a própria conta."
            )

        if not user.active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuário já está inativo."
            )

        # RN08 - Transfere ou deleta parties organizadas pelo usuário
        await self._handle_user_parties(user_id)

        deactivated = self.repo.update(user, {"active": False})
        await self.audit.log("USER", user_id, AuditAction.DELETE, current_user.id)
        await publish_event(
            LudotecaEvent.USER_DEACTIVATED,
            {"user_id": user_id, "deactivated_by": current_user.id}
        )
        return deactivated

    # -------------------------------------------------------------------------
    # RF28 - Reativar usuário (Admin)
    # -------------------------------------------------------------------------
    @log_execution
    @audit_action(entity="USER", action="UPDATE")
    async def reactivate_user(self, user_id: int, current_user: User) -> User:
        user = await self.get_by_id(user_id)

        if user.active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuário já está ativo."
            )

        reactivated = self.repo.update(user, {"active": True})
        await self.audit.log("USER", user_id, AuditAction.UPDATE, current_user.id)
        return reactivated

    # -------------------------------------------------------------------------
    # Método interno - RN08
    # Trata parties organizadas pelo usuário ao ser desativado
    # -------------------------------------------------------------------------
    async def _handle_user_parties(self, user_id: int) -> None:
        from src.app.services.party_service import PartyService
        party_service = PartyService(self.repo.db)

        active_parties = party_service.repo.get_active_by_organizer_all(user_id)
        for party in active_parties:
            await party_service.transfer_or_delete_party(
                party_id=party.id,
                leaving_user_id=user_id,
            )
    # -------------------------------------------------------------------------
    # RF22 - Logout (invalida sessão / registra auditoria)
    # -------------------------------------------------------------------------
    @log_execution
    async def logout(self, current_user: User) -> bool:
        await self.audit.log("USER", current_user.id, AuditAction.LOGOUT, current_user.id)
        return True