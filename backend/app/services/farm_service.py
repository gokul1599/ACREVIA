"""
ACREVIA - Farm, Plot & Season Service.
Enforces multi-tenant authorization boundaries on all farm-related business operations.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.app.models.user import User
from backend.app.models.farm import Farm, FarmMembership, Plot, Plant
from backend.app.models.crop import CropSeason, CropStageEvent
from backend.app.schemas.farm import (
    FarmCreateRequest,
    FarmUpdateRequest,
    FarmMembershipCreateRequest,
    PlotCreateRequest,
    PlotUpdateRequest,
    PlantCreateRequest,
)
from backend.app.schemas.crop import CropSeasonCreateRequest, CropStageEventCreateRequest
from backend.app.security.dependencies import verify_farm_access
from backend.app.security.permissions import SystemRole, FarmRole
from backend.app.services.audit_service import AuditService


class FarmService:
    @staticmethod
    def create_farm(user: User, data: FarmCreateRequest, db: Session) -> Farm:
        farm = Farm(
            owner_id=user.id,
            name=data.name,
            state="Telangana",
            district=data.district,
            mandal=data.mandal,
            village=data.village,
            total_acreage=data.total_acreage,
        )
        db.add(farm)
        db.flush()

        # Add owner membership
        membership = FarmMembership(
            farm_id=farm.id,
            user_id=user.id,
            role_in_farm="OWNER"
        )
        db.add(membership)
        db.commit()
        db.refresh(farm)

        AuditService.record_action(
            db=db,
            user_id=user.id,
            farm_id=farm.id,
            action="CREATE",
            resource_type="FARM",
            resource_id=farm.id,
            metadata={"name": farm.name, "district": farm.district}
        )
        return farm

    @staticmethod
    def get_user_farms(user: User, db: Session) -> List[Farm]:
        user_roles = [r.id for r in user.roles]
        if SystemRole.ADMIN.value in user_roles:
            return db.query(Farm).filter(Farm.is_archived == False).all()

        # Farms owned by user or where user is an active member
        owned_farms = db.query(Farm).filter(Farm.owner_id == user.id, Farm.is_archived == False).all()
        member_farm_ids = [
            m.farm_id for m in db.query(FarmMembership).filter(FarmMembership.user_id == user.id).all()
        ]
        member_farms = db.query(Farm).filter(Farm.id.in_(member_farm_ids), Farm.is_archived == False).all()

        all_farms = {f.id: f for f in owned_farms + member_farms}
        return list(all_farms.values())

    @staticmethod
    def get_farm(farm_id: str, user: User, db: Session) -> Farm:
        return verify_farm_access(farm_id=farm_id, user=user, db=db)

    @staticmethod
    def update_farm(farm_id: str, data: FarmUpdateRequest, user: User, db: Session) -> Farm:
        farm = verify_farm_access(
            farm_id=farm_id,
            user=user,
            db=db,
            allowed_farm_roles=["OWNER", "MANAGER"]
        )
        if data.name is not None:
            farm.name = data.name
        if data.district is not None:
            farm.district = data.district
        if data.mandal is not None:
            farm.mandal = data.mandal
        if data.village is not None:
            farm.village = data.village
        if data.total_acreage is not None:
            farm.total_acreage = data.total_acreage

        db.commit()
        db.refresh(farm)

        AuditService.record_action(
            db=db,
            user_id=user.id,
            farm_id=farm.id,
            action="UPDATE",
            resource_type="FARM",
            resource_id=farm.id
        )
        return farm

    @staticmethod
    def add_farm_membership(
        farm_id: str,
        data: FarmMembershipCreateRequest,
        current_user: User,
        db: Session
    ) -> FarmMembership:
        farm = verify_farm_access(
            farm_id=farm_id,
            user=current_user,
            db=db,
            allowed_farm_roles=["OWNER", "MANAGER"]
        )
        target_user = db.get(User, data.user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target user '{data.user_id}' does not exist."
            )

        existing = (
            db.query(FarmMembership)
            .filter(FarmMembership.farm_id == farm_id, FarmMembership.user_id == data.user_id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User is already a member of this farm."
            )

        membership = FarmMembership(
            farm_id=farm_id,
            user_id=data.user_id,
            role_in_farm=data.role_in_farm
        )
        db.add(membership)
        db.commit()
        db.refresh(membership)

        AuditService.record_action(
            db=db,
            user_id=current_user.id,
            farm_id=farm_id,
            action="ADD_MEMBER",
            resource_type="FARM_MEMBERSHIP",
            resource_id=membership.id,
            metadata={"member_user_id": data.user_id, "role": data.role_in_farm}
        )
        return membership

    @staticmethod
    def list_farm_memberships(farm_id: str, current_user: User, db: Session) -> List[FarmMembership]:
        verify_farm_access(farm_id=farm_id, user=current_user, db=db)
        return db.query(FarmMembership).filter(FarmMembership.farm_id == farm_id).all()

    # Plots
    @staticmethod
    def create_plot(farm_id: str, data: PlotCreateRequest, current_user: User, db: Session) -> Plot:
        farm = verify_farm_access(
            farm_id=farm_id,
            user=current_user,
            db=db,
            allowed_farm_roles=["OWNER", "MANAGER"]
        )
        plot = Plot(
            farm_id=farm.id,
            name=data.name,
            soil_type=data.soil_type,
            irrigation_source=data.irrigation_source,
            acreage=data.acreage,
            boundary_geojson=data.boundary_geojson
        )
        db.add(plot)
        db.commit()
        db.refresh(plot)

        AuditService.record_action(
            db=db,
            user_id=current_user.id,
            farm_id=farm.id,
            action="CREATE",
            resource_type="PLOT",
            resource_id=plot.id
        )
        return plot

    @staticmethod
    def list_plots(farm_id: str, current_user: User, db: Session) -> List[Plot]:
        verify_farm_access(farm_id=farm_id, user=current_user, db=db)
        return db.query(Plot).filter(Plot.farm_id == farm_id, Plot.is_archived == False).all()

    @staticmethod
    def get_plot(plot_id: str, current_user: User, db: Session) -> Plot:
        plot = db.get(Plot, plot_id)
        if not plot or plot.is_archived:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plot not found.")
        verify_farm_access(farm_id=plot.farm_id, user=current_user, db=db)
        return plot

    # Plants
    @staticmethod
    def create_plant(plot_id: str, data: PlantCreateRequest, current_user: User, db: Session) -> Plant:
        plot = FarmService.get_plot(plot_id, current_user, db)
        plant = Plant(
            plot_id=plot.id,
            tag_code=data.tag_code,
            crop_id=data.crop_id,
            notes=data.notes
        )
        db.add(plant)
        db.commit()
        db.refresh(plant)
        return plant

    @staticmethod
    def list_plants(plot_id: str, current_user: User, db: Session) -> List[Plant]:
        plot = FarmService.get_plot(plot_id, current_user, db)
        return db.query(Plant).filter(Plant.plot_id == plot.id).all()

    # Crop Seasons
    @staticmethod
    def create_season(data: CropSeasonCreateRequest, current_user: User, db: Session) -> CropSeason:
        plot = FarmService.get_plot(data.plot_id, current_user, db)
        season = CropSeason(
            plot_id=plot.id,
            crop_id=data.crop_id,
            variety_id=data.variety_id,
            season_type=data.season_type,
            sowing_date=data.sowing_date,
            current_stage=data.current_stage,
            status="ACTIVE"
        )
        db.add(season)
        db.commit()
        db.refresh(season)

        AuditService.record_action(
            db=db,
            user_id=current_user.id,
            farm_id=plot.farm_id,
            action="CREATE",
            resource_type="CROP_SEASON",
            resource_id=season.id
        )
        return season

    @staticmethod
    def list_seasons(plot_id: str, current_user: User, db: Session) -> List[CropSeason]:
        plot = FarmService.get_plot(plot_id, current_user, db)
        return db.query(CropSeason).filter(CropSeason.plot_id == plot.id).all()

    @staticmethod
    def add_stage_event(
        season_id: str,
        data: CropStageEventCreateRequest,
        current_user: User,
        db: Session
    ) -> CropStageEvent:
        season = db.get(CropSeason, season_id)
        if not season:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop season not found.")
        FarmService.get_plot(season.plot_id, current_user, db)

        event = CropStageEvent(
            crop_season_id=season.id,
            stage_name=data.stage_name,
            event_date=data.event_date,
            notes=data.notes
        )
        season.current_stage = data.stage_name
        db.add(event)
        db.commit()
        db.refresh(event)
        return event
