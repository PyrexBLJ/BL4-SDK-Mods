from argparse import Namespace
import unrealsdk
from mods_base import get_pc, command

@command("buhelp", description="List commands and how to use them.")
def Help(args: Namespace) -> None:
    print("Commands:\n\nrun a command with -h as the only argument for more info on that specific command.\n\naddcurrency [money, eridium, vaultcard1tickets, vaultcard2tickets] [amount]\ngive5levels\nspawnitems\ncatpls [args]\n")
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

@command("catpls", description="opens a random cat pic in your browser, no real reason for this i just want to see a kitty sometimes yakno")
def catpls(args: Namespace) -> None:
    ksl = unrealsdk.find_class("KismetSystemLibrary").ClassDefaultObject
    if str(args.args) == "None":
        ksl.LaunchURL("https://cataas.com/cat")
    else:
        ksl.LaunchURL(f"https://cataas.com/cat/{str(args.args)}")
    return None

catpls.add_argument("args", help="[optional] this uses cat as a service so regular url stuff from that: gif for a gif, orange to get an orange cat etc, theres a breakdown on https://cataas.com").required = False