import pymeow
from pymem import Pymem
from models.Spell import Spell
from models.AiManager import AiManager
from resources import offsets
from functools import cached_property
from .EntityManager import Model


class Entity(Model):

    def __add__(self, other):
        return self.entityAddress + other

    def __radd__(self, other):
        if other == 0:
            return self.entityAddress
        else:
            return self.__add__(other)

    def __init__(self, pm: Pymem, mem, overlay, viewProjMatrix, entityAddress: int) -> None:
        self.pm = pm
        self.mem = mem
        self.overlay = overlay
        self.viewProjMatrix = viewProjMatrix
        self.entityAddress = entityAddress
        
    @cached_property
    def nameAddr(self) -> int:
        return self.pm.read_int(self.entityAddress + offsets.oObjName)

    @cached_property
    def name(self) -> str:
        return self.pm.read_string(self.nameAddr)

    @cached_property
    def level(self) -> int:
        return self.pm.read_int(self.entityAddress + offsets.oObjLevel)

    @cached_property
    def teamId(self) -> int:
        return self.pm.read_int(self.entityAddress + offsets.oObjTeamId)

    @cached_property
    def isTargetable(self) -> bool:
        return self.pm.read_bool(self.entityAddress + offsets.ObjTargetable)

    @cached_property
    def health(self) -> float:
        return self.pm.read_float(self.entityAddress + offsets.oObjHealth)

    @cached_property
    def is_alive(self) -> bool:
        return self.health > 0

    @cached_property
    def maxHealth(self) -> float:
        return self.pm.read_float(self.entityAddress + offsets.oObjMaxHealth)

    @cached_property
    def mana(self) -> float:
        return self.pm.read_float(self.entityAddress + offsets.oObjMana)

    @cached_property
    def maxMana(self) -> float:
        return self.pm.read_float(self.entityAddress + offsets.oObjMaxMana)

    @cached_property
    def ap(self) -> float:
        return self.pm.read_float(self.entityAddress + offsets.oObjStatAp)

    @cached_property
    def ad(self) -> float:
        return self.pm.read_float(self.entityAddress + offsets.oObjStatBaseAd) + self.pm.read_float(
            self.entityAddress + offsets.oObjStatBonusAd)

    @cached_property
    def bonusAttackSpeedPercent(self) -> float:
        return self.pm.read_float(self.entityAddress + offsets.ObjAtkSpeedMulti) - 1

    @cached_property
    def magicResist(self) -> float:
        return self.pm.read_float(self.entityAddress + offsets.oObjMagicRes)

    @cached_property
    def armor(self) -> float:
        return self.pm.read_float(self.entityAddress + offsets.oObjArmor)

    @cached_property
    def magicPenFlat(self) -> float:
        return self.pm.read_float(self.entityAddress + offsets.oObjMagicPenFlat)

    @cached_property
    def magicPenPercent(self) -> float:
        return (1 - self.pm.read_float(self.entityAddress + offsets.oObjMagicPenPercent)) * 100

    @cached_property
    def armorPenPercent(self) -> float:
        return (1 - self.pm.read_float(self.entityAddress + offsets.oObjArmorPen)) * 100

    @cached_property
    def lethality(self) -> float:
        return self.pm.read_float(self.entityAddress + offsets.oObjLethality)

    @cached_property
    def attackRange(self) -> float:
        return self.pm.read_float(self.entityAddress + offsets.oObjAtkRange)

    @cached_property
    def gamePos(self) -> dict:
        return pymeow.read_vec3(self.mem, self.entityAddress + offsets.oObjPosition)

    @cached_property
    def screenPos(self) -> dict:
        try:
            wts = pymeow.wts_ogl(self.overlay, self.viewProjMatrix.tolist(), self.gamePos)
        except:
            wts = pymeow.vec2()
        return wts

    @cached_property
    def isVisible(self) -> bool:
        return self.pm.read_bool(self.entityAddress + offsets.oObjVisible)

    @cached_property
    def onScreen(self):
        return self.screenPos['x'] > 0 and self.screenPos['x'] < self.overlay['width'] and self.screenPos['y'] > 0 and \
               self.screenPos['y'] < self.overlay['height']

    @property
    def AiManager(self) -> AiManager:
        v1 = pymeow.read_byte(self.mem, self.entityAddress + offsets.oObjAiManager)
        v2 = self.entityAddress + offsets.oObjAiManager - 8
        v3 = self.pm.read_int(v2 + 4)
        v4 = self.pm.read_int(v2 + (4 * v1 + 12))
        v4 = v4 ^ ~v3
        addr = self.pm.read_int(v4 + 0x8)
        return AiManager(self.pm, self.mem, self.viewProjMatrix, self.overlay, addr)
