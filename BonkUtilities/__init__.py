import unrealsdk
from mods_base import build_mod, get_pc, keybind, hook, ENGINE, SliderOption, SpinnerOption, BoolOption, Game, NestedOption, EInputEvent, command
from unrealsdk.hooks import Type, Block
from unrealsdk.unreal import BoundFunction, UObject, WrappedStruct, IGNORE_STRUCT
from typing import Any
from threading import Thread
import time

from .commands import *

ConsoleFontSize: SliderOption = SliderOption("Console Font Size", 18, 1, 128, 1, True, on_change = lambda _, new_value: setConsoleFontSize(_, new_value))
#NoclipType: SpinnerOption = SpinnerOption("Noclip Type", "Classic", ["Classic", "Freecam"])
#FCNoclipSpeed: SliderOption = SliderOption("Freecam Noclip Speed Multiplier", 2.0, 0.5, 10.0, 0.1, False)
VanillaSuperDash: BoolOption = BoolOption("Vanilla Super Dash", True, "Yes", "No", description="Use the regular dash logic for the superdash hotkey")
CustomSuperDashSpeed: SliderOption = SliderOption("Custom Super Dash Speed", 1000, 1, 10000, 1, True, description="How much force to use for the non-vanilla super dash")
SuperDashOptions: NestedOption = NestedOption("Super Dash Options ->", [VanillaSuperDash, CustomSuperDashSpeed], description="Submenu for superdash options")
NoBMViewCooldown: BoolOption = BoolOption("No BM Cooldown Without Purchase", True, "Yes", "No")
MapTP: BoolOption = BoolOption("Teleport to Custom Map Pins", False, "Yes", "No", description="Quickly make and remove a pin on the map to teleport to that location, does not work if you pin a pre-existing marker on the map.")
MapTPWindow: SliderOption = SliderOption("Map Teleport Pin Window", 2.0, 0.5, 4.0, 0.1, False, description="How long (in seconds) you have to remove the map pin after making it to teleport to it.")
MapTPReTryDelay: SliderOption = SliderOption("Map Teleport Re-teleport Delay", 3.0, 0.5, 10.0, 0.1, False, description="How long (in seconds) it will wait to attempt the teleport again incase you load in under the map (usually happens when teleporting far away)")
MapTPHover: BoolOption = BoolOption("TP Hover", True, "Yes", "No", description="When yes: teleport way above the map and wait for the retry teleport delay to put you down on the ground, gives the map time to load in but will be slower for short distance teleports.")
MapTPOptions: NestedOption = NestedOption("Map TP Options ->", [MapTP, MapTPWindow, MapTPReTryDelay, MapTPHover], description="Submenu for the main toggle for map teleport and options for it")
FOV: SliderOption = SliderOption("FOV", 110, 110, 179, 1, True, description="Set an FOV Higher than normal, only takes effect if this is set higher than 110", on_change = lambda _, new_value: setFOV(_, new_value))


noclip: bool = False
godmode: bool = False
notarget: bool = False
# map tp stuff
pintime = 0
pinlocation = None
teleported = False
#


def setConsoleFontSize(_: SliderOption, new_value: int) -> None:
    unrealsdk.find_object("Font", "/Engine/Transient.DefaultRegularFont").LegacyFontSize = int(new_value)
    return None

def setFOV(_: SliderOption, new_value: int) -> None:
    if new_value > 110:
        get_pc().player.BaseFOV = int(new_value)
        get_pc().player.VehicleFOV = int(new_value)
    return None

def notify(text: str) -> None:
    print(f"[Bonk Utilities] {text}")
    return None

def checkCheatClass() -> None:
    if get_pc().CheatManager == None:
        cheatclass = unrealsdk.construct_object("OakCheatManager", get_pc())
        get_pc().CheatManager = cheatclass

@keybind("God Mode")
def GodMode() -> None:
    global godmode
    if not godmode:
        get_pc().OakCharacter.bCanBeDamaged = False
        godmode = True
        notify("God Mode On")
    else:
        get_pc().OakCharacter.bCanBeDamaged = True
        godmode = False
        notify("God Mode Off")
    return None

@keybind("Demigod (1 Health)")
def Demigod() -> None:
    get_pc().ServerActivateDevPerk(6)
    notify("Demigod Toggled")
    return None

@keybind("Noclip")
def Noclip() -> None:
    global noclip, godmode
    if not noclip:
        #get_pc().OakCharacter.OakCharacterMovement.MaxFlySpeed = NoclipSpeed.value # if only this did anything
        get_pc().OakCharacter.bCanBeDamaged = False # without this getting shot/hit will turn off fly mode and not re-enable your collision with the world
        get_pc().OakCharacter.OakCharacterMovement.SetMovementMode(5, 0)
        get_pc().OakCharacter.bActorEnableCollision = False
        noclip = True
        notify("Noclip On")
    else:
        get_pc().OakCharacter.bActorEnableCollision = True
        get_pc().OakCharacter.OakCharacterMovement.SetMovementMode(1, 0)
        if not godmode:
            get_pc().OakCharacter.bCanBeDamaged = True
        #get_pc().OakCharacter.OakCharacterMovement.MaxFlySpeed = 600.0
        noclip = False
        notify("Noclip Off")
    '''
    if NoclipType.value == "Classic":
        
    elif NoclipType.value == "Freecam":
        checkCheatClass()
        if "DebugCameraController" not in str(get_pc()):
            if get_pc().CheatManager.DebugCameraControllerRef == None:
                get_pc().CheatManager.ToggleDebugCamera()
                checkCheatClass()
                get_pc().SpeedScale = FCNoclipSpeed.value
                get_pc().CheatManager.ToggleDebugCamera()
            
            get_pc().CheatManager.ToggleDebugCamera()
            notify("Freecam Noclip On")
        else:
            get_pc().OriginalControllerRef.K2_SetActorLocationAndRotation(get_pc().K2_GetActorLocation(), get_pc().K2_GetActorRotation(), False, IGNORE_STRUCT, False)
            get_pc().CheatManager.ToggleDebugCamera()
            notify("Freecam Noclip Off")
    '''
    return None

@keybind("Speed Up Time")
def SpeedUpTime() -> None:
    if ENGINE.GameViewport.World.PersistentLevel.WorldSettings.TimeDilation >= 32:
        ENGINE.GameViewport.World.PersistentLevel.WorldSettings.TimeDilation = 1
    else:
        ENGINE.GameViewport.World.PersistentLevel.WorldSettings.TimeDilation = ENGINE.GameViewport.World.PersistentLevel.WorldSettings.TimeDilation * 2
    notify(f"Game Speed: {ENGINE.GameViewport.World.PersistentLevel.WorldSettings.TimeDilation}")
    return None

@keybind("Slow Down Time")
def SlowDownTime() -> None:
    if ENGINE.GameViewport.World.PersistentLevel.WorldSettings.TimeDilation <= 0.125:
        ENGINE.GameViewport.World.PersistentLevel.WorldSettings.TimeDilation = 1
    else:
        ENGINE.GameViewport.World.PersistentLevel.WorldSettings.TimeDilation = ENGINE.GameViewport.World.PersistentLevel.WorldSettings.TimeDilation / 2
    notify(f"Game Speed: {ENGINE.GameViewport.World.PersistentLevel.WorldSettings.TimeDilation}")
    return None

@keybind("Toggle Intinite Ammo")
def InfiniteAmmo() -> None:
    get_pc().ServerActivateDevPerk(5)
    notify("Infinite Ammo Toggled")
    return None

@keybind("Kill Enemies")
def KillEnemies() -> None:
    get_pc().ServerActivateDevPerk(3)
    notify("All Enemies Killed")
    return None

@keybind("Toggle Players Only (World Freeze)")
def PlayersOnly() -> None:
    checkCheatClass()
    get_pc().CheatManager.PlayersOnly()
    notify("Toggled Players Only")
    return None

@keybind("No Target")
def NoTarget() -> None:
    global notarget
    if not notarget:
        notarget = True
        notify("No Target On")
    else:
        notarget = False
        notify("No Target Off")
    targetinglib = unrealsdk.find_class("GbxTargetingFunctionLibrary").ClassDefaultObject
    targetinglib.LockTargetableByAI(get_pc(), "bonk", notarget, notarget)
    return None

def DoSuperDash() -> None:
    if get_pc().OakCharacter != None:
        get_pc().OakCharacter.Jump()
        if VanillaSuperDash.value == True:
            get_pc().OakCharacter.SetWantsToDash(True, 0)
        else:
            forward = get_pc().GetActorForwardVector()
            impulse = unrealsdk.make_struct("Vector", X=forward.X * CustomSuperDashSpeed.value, Y=forward.Y * CustomSuperDashSpeed.value, Z=10)
            get_pc().OakCharacter.OakCharacterMovement.AddImpulse(impulse, True)
        time.sleep(0.01)
        get_pc().OakCharacter.StopJumping()
    return None

@keybind("Super Dash")
def SuperDash() -> None:
    Thread(target=DoSuperDash).start()
    return None

usables = ["Health", "ArmorShard", "Ammo", "ammo", "Money", "Eridium", "ShieldBooster"]

def GetIoTD() -> list:
    iotds = []
    pc = get_pc()
    for machine in unrealsdk.find_all("OakVendingMachine", False):

        if not machine or machine == machine.Class.ClassDefaultObject:
            continue
        current_iotd = machine.GetIOTDForPlayer(pc)
        if current_iotd:
            iotds.append(current_iotd)
    return iotds

def get_sorted_ground_loot() -> dict:
    current_ground_loot = {
        "Pickups": [],
        "Gear": [],
    }
    iotd_pickups = GetIoTD()
    for inv in unrealsdk.find_all("InventoryPickup", False):
        if not inv or inv == inv.Class.ClassDefaultObject or not inv.RootPrimitiveComponent or inv in iotd_pickups:
            continue

        inv.RootPrimitiveComponent.SetSimulatePhysics(True)

        inv_str = str(inv.BodyData)

        if "Pickups" in inv_str:
            current_ground_loot["Pickups"].append(inv)
            continue

        if not inv.BodyData:
            was_usable = False
            num_materials = inv.RootPrimitiveComponent.GetNumMaterials()

            for i in range(num_materials):
                if was_usable:
                    break

                mat = inv.RootPrimitiveComponent.GetMaterial(i)
                if not mat:
                    continue

                for usable in usables:
                    if usable in mat.Name:
                        current_ground_loot["Pickups"].append(inv)
                        was_usable = True
                        break

            if was_usable:
                continue

        if "Gear" in inv_str:
            current_ground_loot["Gear"].append(inv)
            continue

    return current_ground_loot


@keybind("'Delete' Ground Items", description="I cant actually delete them so they just kinda go away under the floor for now lol, thank you yeti for the item filtering.")
def DeleteGroundItems() -> None:
    loc = unrealsdk.make_struct("Vector", X=100000,Y=100000,Z=-1000000000)
    pickups = get_sorted_ground_loot()
    ground_loot = pickups["Pickups"] + pickups["Gear"]
    itemcount: int = 0
    for item in ground_loot:
        if "default" not in str(item).lower():
            item.RootPrimitiveComponent.SetSimulatePhysics(True)
            item.K2_SetActorRelativeLocation(loc, False, IGNORE_STRUCT, False)
            itemcount += 1
    notify(f"{itemcount} Ground Items Deleted")
    return None

@hook("/Game/InteractiveObjects/GameSystemMachines/VendingMachines/Scripts/Script_VendingMachine_BlackMarket.Script_VendingMachine_BlackMarket_C:OnDecloakCollisionEnter", Type.PRE)
def BlackMarketUncloak(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> type[Block] | None:
    if NoBMViewCooldown.value == True:
        obj.bCooldownOnView = False
    return None

@hook("/Script/OakGame.OakPlayerState:Server_CreateDiscoveryPin", Type.POST)
def CreatePin(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> None:
    global pintime, pinlocation
    if MapTP.value:
        if args.InPinData.pintype == 1:
            pintime = time.time()
            pinlocation = args.InPinData.PinnedCustomWaypointLocation
    return None

@hook("/Script/OakGame.OakPlayerState:Server_RemoveDiscoveryPin", Type.POST)
def RemovePin(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> None:
    global pintime, pinlocation, teleported
    if MapTP.value:
        if time.time() - pintime < MapTPWindow.value:
            pinlocation.Z = 50000
            get_pc().OakCharacter.K2_SetActorLocation(pinlocation, False, IGNORE_STRUCT, False)
            if MapTPHover.value == False:
                pinlocation.Z = -1000
                get_pc().OakCharacter.K2_SetActorLocation(pinlocation, True, IGNORE_STRUCT, False)
            else:
                get_pc().OakCharacter.OakCharacterMovement.MovementMode = 5
                
            teleported = True
            notify(f"Teleported to {get_pc().K2_GetActorLocation()}")
    return None

def threadtp() -> None:
    global pinlocation, teleported
    if teleported:
        teleported = False
        time.sleep(MapTPReTryDelay.value)
        if get_pc().OakCharacter.OakCharacterMovement.MovementMode in (3, 4, 6) or MapTPHover.value:
            get_pc().OakCharacter.OakCharacterMovement.MovementMode = 1
            pinlocation.Z = 50000
            get_pc().OakCharacter.K2_SetActorLocation(pinlocation, False, IGNORE_STRUCT, False)
            pinlocation.Z = -1000
            get_pc().OakCharacter.K2_SetActorLocation(pinlocation, True, IGNORE_STRUCT, False)
    return None

@hook("/Game/UI/Scripts/ui_script_menu_base.ui_script_menu_base_C:MenuClose", Type.POST)
def MenuClose(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> None:
    global pintime, pinlocation, teleported
    if MapTP.value:
        Thread(target=threadtp).start()
    return None

@hook("/Script/OakGame.OakPlayerState:OnOakPawnSet", Type.POST)
def ThisIsGonnaBeMySpawnHookForNow(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> None:
    if FOV.value > 110:
        get_pc().player.BaseFOV = FOV.value
        get_pc().player.VehicleFOV = FOV.value
    return None

def Enable() -> None:
    unrealsdk.find_object("Font", "/Engine/Transient.DefaultRegularFont").LegacyFontSize = ConsoleFontSize.value
    return None

build_mod(on_enable=Enable, options=[ConsoleFontSize, NoBMViewCooldown, FOV, MapTPOptions, SuperDashOptions])