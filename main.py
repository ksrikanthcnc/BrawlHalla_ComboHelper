from pynput.keyboard import Key, Listener, KeyCode
from pynput import mouse
import json
import sys
from tkinter import *
import tkinter as tk
import os

os.chdir(os.path.dirname(__file__))

debug = True if "debug" in sys.argv else False
# TODO move stuff to config files
# TODO menu, tinker

d_controls = {
    "up": KeyCode.from_char("w"),
    "left": KeyCode.from_char("a"),
    "down": KeyCode.from_char("s"),
    "right": KeyCode.from_char("d"),
    "jump": Key.space,
    "dodge": Key.shift,
    "light": mouse.Button.left,
    "heavy": mouse.Button.right,
    # "light": KeyCode.from_char("j"),
    # "heavy": KeyCode.from_char("k"),
    "throw": mouse.Button.middle,
}

d_moves = json.load(open("moves.json"))

d_combos = json.load(open("combos.json"))
d_legends = {}
meta_fields = [
    "legend_name_key",
    "weapon_one",
    "weapon_two",
    "strength",
    "dexterity",
    "defense",
    "speed",
]
for meta_legend in json.load(open("legends.json", encoding="utf8"))["data"]:
    d_legends[meta_legend["legend_name_key"]] = {k: meta_legend[k] for k in meta_fields}
    d_legends[meta_legend["legend_name_key"]].update(
        {"weapons": ["Unarmed", meta_legend["weapon_one"], meta_legend["weapon_two"]]}
    )


def is_sublist(ls_1, ls_2, strict=False):
    return [_1 for _1 in ls_1 if _1 in set(ls_2)]


def get_moves(pressed):  # left + light
    moves = []
    directions_all = {"left", "right", "up", "down"}
    actions_all = {"light", "heavy", "jump", "dodge", "throw"}

    directions_pressed = set(
        [press for press in pressed if press in directions_all] or [None]
    )
    actions_pressed = set(
        [press for press in pressed if press in actions_all] or [None]
    )

    for k, v in d_moves.items():
        name = k
        directions_move = set(v["directions"])  # left, right
        actions_move = set(v["attack"])  # light

        if directions_move.intersection(
            directions_pressed
        ) and actions_move.intersection(actions_pressed):
            moves.append(name)  # slight
    return moves


__controls = {v: k for k, v in d_controls.items()}
from threading import Timer

t = None


def combo_reset():
    print("combo_reset")
    suggestions.clear()
    ROOT.event_generate("<<CustomEvent>>")
    if g_moves:
        g_moves.clear()
        if debug:
            print(f"No follow-up found, resetting combo [{g_moves}]")
        for i, combo_valid in combo_chain.items():
            combo, valid = combo_valid
            combo_chain[i] = [combo, [0]]


def newTimer():
    global t
    t = Timer(1, combo_reset)
    t.start()


def suggest_combos(pressed):  # a + leftclick
    __pressed = [__controls[key] for key in pressed]  # left + light
    if debug:
        print(f"Pressed: [{__pressed}]")
    moves = get_moves(__pressed)  # slight
    g_moves.update(moves)
    if debug:
        print(f"Moves: [{moves}]")
    if moves:
        if debug:
            print(f"Pressed-Matched: [{moves}] ----------------")
        combo_matched = False
        combo_in_progress = False
        suggestions.clear()
        ROOT.event_generate("<<CustomEvent>>")
        for i, combo_valid in combo_chain.items():
            if t:
                t.cancel()
            newTimer()
            combo, valid = combo_valid
            combo_at = valid[0]
            combo_next_at = combo_at + 1
            if debug:
                print(f"Checking [{i},{combo},{valid}]")
            for move in moves:  # nlight,nair
                if debug:
                    print(f"Trying to match [{move}]")
                seq, cond = combo["seq"], combo["condition"]
                if move == seq[combo_at]:
                    if len(seq) == combo_next_at:
                        print(f"\t\tCombo done: seq:[{seq}] cond:[{cond}]")
                        valid[0] = 0
                    else:
                        str_suggest = f"\tSuggestion: [{combo_at} -> {combo_next_at}] [{seq[combo_at]} -> {seq[combo_next_at]}] for seq:[{seq}] cond:[{cond}]"
                        print(str_suggest)
                        move_suggested = seq[combo_next_at]
                        suggestions[move_suggested] = suggestions.get(move_suggested,[]) + [str_suggest]
                        ROOT.event_generate("<<CustomEvent>>")
                        # print(f"\t{seq[:combo_next_at]} #{seq[combo_next_at]}# {seq[combo_next_at+1:]}")
                        valid[0] += 1
                    combo_matched = combo_next_at
                    # break
                elif combo_at > 0:
                    combo_in_progress = True
                    # print(f"\tCombo ignored [{move} -> {seq[combo_at]}]: seq:[{seq}] cond:[{cond}]") # TODO proper
                    valid[0] = 0
                if debug:
                    print("-" * 10)
            if debug:
                print("=" * 30)
        if not combo_matched:
            t.cancel()
            if combo_in_progress:
                print(
                    f"\tCombo broken [{move} -> {seq[combo_at]}]: seq:[{seq}] cond:[{cond}]"
                )
        i_pressed[0] += 1
        print(f"{'='*100} [{i_pressed[0]}]", end="\r")


pressed = set()
g_moves = set()  # TODO
suggestions = {}
weapon = "Unarmed"
legend = "bodvar"
combo_chain = {i: [combo, [0]] for i, combo in enumerate(d_combos[weapon]["true"])}

i_pressed = [0]


def on_press(key):
    if key == Key.esc:
        # TODO menu()
        listener_kb.stop()
        listener_m.stop()
    if key not in d_controls.values():
        # if debug: print("Ignoring")
        pass
    else:
        if debug:
            print(key)
        pressed.add(key)
        if debug:
            print(f"Pressed: [{pressed}]")
        suggest_combos(pressed)


def on_release(key):
    try:
        pressed.remove(key)
        __released = [__controls[key]]  # left + light
        if debug:
            print(f"Released: [{__released}]")
        moves = get_moves(__released)  # slight
        g_moves.difference_update(moves)
    except KeyError:
        pass


def on_click(x, y, button, pressed_event):
    if pressed_event:
        if debug:
            print(pressed)
        pressed.add(button)
        suggest_combos(pressed)
    else:
        pressed.remove(button)


# Tinker
ROOT = Tk()
ROOT.title("Brawlhalla combo-helper")
ROOT.attributes("-topmost", True)
ROOT.attributes("-alpha", 0.8)
ROOT.grid_rowconfigure(0, weight=1)
ROOT.grid_columnconfigure(0, weight=1)


def set_legend(*args):
    global legend
    global weapon
    legend = menu_legend.get()
    CONFIG.config(text=f"[{legend}]-[{weapon}]")

    weapons = d_legends[legend]["weapons"]
    dropdown_weapon.children["menu"].delete(0, "end")
    for weapon in weapons:
        dropdown_weapon.children["menu"].add_command(
            label=weapon, command=tk._setit(menu_weapon, weapon)
        )
    menu_weapon.set("Unarmed")


def set_weapon(*args):
    global weapon
    weapon = menu_weapon.get()
    CONFIG.config(text=f"[{legend}]-[{weapon}]")


menu_legend = StringVar()
menu_legend.set("Select LEGEND")
menu_legend.trace("w", set_legend)
dropdown_legend = OptionMenu(ROOT, menu_legend, *sorted(d_legends.keys()))
dropdown_legend.grid(row=0, column=0, sticky=W)
# dropdown_legend.pack()

menu_weapon = StringVar()
menu_weapon.set("Select Weapon")
menu_weapon.trace("w", set_weapon)
dropdown_weapon = OptionMenu(ROOT, menu_weapon, *sorted(d_legends[legend]["weapons"]))
dropdown_weapon.grid(row=0, column=1, sticky=W)
# dropdown_weapon.pack()


CONFIG = Label(ROOT, text="Current config")
CONFIG.grid(row=1, column=1, columnspan=3, sticky=NSEW)
# CONFIG.pack()
COMBO_SUGGEST = Label(ROOT, text="Start any combo")
COMBO_SUGGEST.grid(row=2, column=1, columnspan=3, sticky=NSEW)
# COMBO_SUGGEST.pack()

COMBO_LABELS = {}
row = 3
height = 5
Label(ROOT, text="combos with JUMP", height=height).grid(row=row, column=1, columnspan=1, sticky=NSEW)
COMBO_JUMP = Label(ROOT, text="combos with JUMP", height=height)
COMBO_JUMP.grid(row=row, column=2, columnspan=2, sticky=NSEW)
COMBO_LABELS["jump"] = COMBO_JUMP

row += 1
Label(ROOT, text="combos with LIGHT").grid(row=row, column=1, columnspan=1, sticky=NSEW)
COMBO_LIGHT = Label(ROOT, text="combos with JUMP", height=height)
COMBO_LIGHT.grid(row=row, column=2, columnspan=2, sticky=NSEW)
COMBO_LABELS["light"] = COMBO_LIGHT

row += 1
Label(ROOT, text="combos with AIR").grid(row=row, column=1, columnspan=1, sticky=NSEW)
COMBO_AIR = Label(ROOT, text="combos with AIR", height=height)
COMBO_AIR.grid(row=row, column=2, columnspan=2, sticky=NSEW)
COMBO_LABELS["air"] = COMBO_AIR

row += 1
Label(ROOT, text="combos with SIG").grid(row=row, column=1, columnspan=1, sticky=NSEW)
COMBO_SIG = Label(ROOT, text="combos with SIG", height=height)
COMBO_SIG.grid(row=row, column=2, columnspan=2, sticky=NSEW)
COMBO_LABELS["sig"] = COMBO_SIG

row += 1
Label(ROOT, text="combos with SPECIAL").grid(row=row, column=1, columnspan=1, sticky=NSEW)
COMBO_SPECIAL = Label(ROOT, text="combos with SPECIAL", height=height)
COMBO_SPECIAL.grid(row=row, column=2, columnspan=2, sticky=NSEW)
COMBO_LABELS["special"] = COMBO_SPECIAL


def update(event):
    # str_suggestions = "\n".join(suggestions)
    # COMBO_SUGGEST.config(text=str_suggestions)
    if suggestions:
        for suggestion_move in suggestions.keys():
            for move_category in COMBO_LABELS.keys():
                if move_category in suggestion_move:
                    COMBO_LABELS[move_category].config(text="\n".join(suggestions[suggestion_move]))
    else:
        for move_category in COMBO_LABELS.keys():
            COMBO_LABELS[move_category].config(text="--")
    CONFIG.config(text=f"[{legend}]-[{weapon}]")
    # ROOT.after(1, update)


ROOT.bind("<<CustomEvent>>", update)
ROOT.bind("<Escape>", lambda e: ROOT.destroy())


def __dummy():
    pass


listener_kb = Listener(on_press=on_press, on_release=on_release)
listener_kb.start()

listener_m = mouse.Listener(on_click=on_click)
listener_m.start()


# Waiting
ROOT.after(0, __dummy)
ROOT.mainloop()
listener_kb.join()
listener_m.join()
print("Joined")

print("Done")
