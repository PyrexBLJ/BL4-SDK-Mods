from argparse import Namespace
import os
from pathlib import Path
from urllib.request import urlretrieve
import unrealsdk
from mods_base import get_pc, command, ENGINE, SETTINGS_DIR
from unrealsdk.unreal import UObject


@command("buhelp", description="List commands and how to use them.")
def Help(args: Namespace) -> None:
    print("Commands:\n\nrun a command with -h as the only argument for more info on that specific command.\n\naddcurrency [money, eridium, vaultcard1tickets, vaultcard2tickets] [amount]\ngive5levels\nspawnitems\nspawnitemfrompool [item pool] [amount to drop]\nfixconsole\ncatpls [args]\ncatscale\ncatscalex\ncatscaley\nnomorecat")
    return None

@command("addcurrency", description="Add to these currencies: money, eridium, vaultcard1tickets, vaultcard2tickets")
def AddCurrency(args: Namespace) -> None:
    if args.currency == "money":
        index = 0
        for currency in get_pc().CurrencyManager.currencies:
            if currency.type.Name == "Cash":
                break
            index += 1
        get_pc().Server_AddCurrency(get_pc().CurrencyManager.currencies[index].type, int(args.amount))
        print(f"[Bonk Utilities] Added ${args.amount}")
    elif args.currency == "eridium":
        index = 0
        for currency in get_pc().CurrencyManager.currencies:
            if currency.type.Name == "eridium":
                break
            index += 1
        get_pc().Server_AddCurrency(get_pc().CurrencyManager.currencies[index].type, int(args.amount))
        print(f"[Bonk Utilities] Added {args.amount} Eridium")
    elif args.currency == "vaultcard1tickets":
        index = 0
        for currency in get_pc().CurrencyManager.currencies:
            if currency.type.Name == "VaultCard01_Tokens":
                break
            index += 1
        get_pc().Server_AddCurrency(get_pc().CurrencyManager.currencies[index].type, int(args.amount))
        print(f"[Bonk Utilities] Added {args.amount} Mercenary Day Tickets")
    elif args.currency == "vaultcard2tickets":
        index = 0
        for currency in get_pc().CurrencyManager.currencies:
            if currency.type.Name == "VaultCard02_Tokens":
                break
            index += 1
        get_pc().Server_AddCurrency(get_pc().CurrencyManager.currencies[index].type, int(args.amount))
        print(f"[Bonk Utilities] Added {args.amount} Vault x Hunter Tickets")
    else:
        print(f"Currency {args.currency} not found.")
    return None

AddCurrency.add_argument("currency", help="Name of currency to change")
AddCurrency.add_argument("amount", help="you got this one chief i believe in u, positive numbers only.")

@command("give5levels", description="it gives you 5 levels idk what else to tell u.")
def GiveLevels(args: Namespace) -> None:
    get_pc().ServerActivateDevPerk(0)
    print("[Bonk Utilities] Added 5 Levels")
    return None

@command("spawnitems")
def SpawnItems(args: Namespace) -> None:
    get_pc().ServerActivateDevPerk(7)
    print("[Bonk Utilities] Spawned Items")
    return None

@command("spawnitemfrompool", description="Spawn items from a loot pool, rn the only way i know to get those pools is to look thru the ncs dumps.")
def SpawnItemFromPool(args: Namespace) -> None:
    ncsip = unrealsdk.find_class("NexusConfigStoreItemPool").ClassDefaultObject
    for i in range(int(args.count)):
        ncsip.SpawnInventoryFromItemPool(ENGINE.GameViewport.World, get_pc().OakCharacter.GetTransform(), get_pc().OakCharacter.gamestage, args.itempool)
    return None

SpawnItemFromPool.add_argument("itempool", help="the name of the item pool to spawn loot from")
SpawnItemFromPool.add_argument("count", help="how many items to spawn")

@command("fixconsole")
def FixConsole(args: Namespace) -> None:
    get_pc().ServerGbxConsoleCommand(unrealsdk.make_struct("ReplicatedConsoleCommandContext", CommandAndArgs="r.DebugSafeZone.TitleRatio 1"))
    return None

def getmainhudcontent() -> UObject:
    for thing in unrealsdk.find_all("UserWidget", exact=False):
        if "WBP_MainHud_C" in str(thing) and thing != thing.Class.ClassDefaultObject:
            return thing.WidgetTree.RootWidget.GetContent()
    return None

catenabled: bool = False
customcanvas: UObject = None
customimage: UObject = None

@command("catpls", description="puts a random kitty in the corner of your screen (and sometimes a cow idk why)")
def catpls(args: Namespace) -> None:
    global catenabled, customcanvas, customimage

    url = "https://cataas.com/cat"
    filepath = os.path.join(SETTINGS_DIR, "Cats")
    filename = os.path.join(filepath, "cat.png")

    if not os.path.exists(filepath):
        os.makedirs(filepath)

    urlretrieve(url, filename)

    KRL = unrealsdk.find_class("KismetRenderingLibrary").ClassDefaultObject

    texture = KRL.ImportFileAsTexture2D(getmainhudcontent(), filename)

    if not catenabled:
        canvaspanel = unrealsdk.construct_object(unrealsdk.find_class("/Script/UMG.CanvasPanel"), getmainhudcontent(), "CatCanvasPanel")
        customcanvas = canvaspanel
        canvaspanel.SetRenderScale(unrealsdk.make_struct("Vector2D", X=20, Y=20))
        getmainhudcontent().AddChildToOverlay(canvaspanel)
        canvaspanel.slot.SetHorizontalAlignment(3)

        image = unrealsdk.construct_object(unrealsdk.find_class("/Script/UMG.Image"), getmainhudcontent(), "CatImage")
        customimage = image
        canvaspanel.AddChildToCanvas(image)
        image.SetBrushFromTexture(texture, False)
        image.SetOpacity(1.0)
        image.slot.SetAutoSize(True)
        image.slot.SetAlignment(unrealsdk.make_struct("Vector2D", X=0.5, Y=-0.5))
        catenabled = True
    else:
        customimage.SetBrushFromTexture(texture, False)
    return None

@command("catscale", description="the size of the cat image, by default 20")
def catscale(args: Namespace) -> None:
    global customcanvas
    if customcanvas != None:
        print(args.scale)
        print(float(args.scale))
        customcanvas.SetRenderScale(unrealsdk.make_struct("Vector2D", X=float(args.scale), Y=float(args.scale)))
    return None

catscale.add_argument("scale", help="the scale of the cat")

@command("catscalex", description="the size of the cat image, by default 20")
def catscalex(args: Namespace) -> None:
    global customcanvas
    if customcanvas != None:
        customcanvas.SetRenderScale(unrealsdk.make_struct("Vector2D", X=float(args.scale), Y=customcanvas.RenderTransform.scale.Y))
    return None

catscalex.add_argument("scale", help="the scale of the cat")

@command("catscaley", description="the size of the cat image, by default 20")
def catscaley(args: Namespace) -> None:
    global customcanvas
    if customcanvas != None:
        customcanvas.SetRenderScale(unrealsdk.make_struct("Vector2D", X=customcanvas.RenderTransform.scale.X, Y=float(args.scale)))
    return None

catscaley.add_argument("scale", help="the scale of the cat")

@command("nomorecat", description="get rid of the cat")
def nomorecat(args: Namespace) -> None:
    global customcanvas, customimage, catenabled
    if customimage != None:
        customimage.RemoveFromParent()
    if customcanvas != None:
        customcanvas.ClearChildren()
        customcanvas.RemoveFromParent()
    catenabled = False
    return None

'''
from obj_dump import dump_object
import os

@command("dumpthewholegame")
def DumpTheWholeGame(args: Namespace) -> None:
    print("Starting Dump")


    path = "/home/pyrex/Documents/GarboBL4Dump/"
    everything = unrealsdk.find_all("Object", exact=False)
    for thing in everything:
        if thing == thing.Class.ClassDefaultObject and not os.path.isfile(f"{path}/{thing.Class.Name}.log"):
            f = open(f"{path}/{thing.Class.Name}.log", "+a")
            dump_object(thing, file=f, dump_fields=True)
            f.close()


    print("Dump Complete!")
    return None
'''