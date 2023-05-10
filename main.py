from pynput.keyboard import Key, Listener, KeyCode
from pynput import mouse
import sys
from tkinter import *

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

d_moves = {
    # TODO add ignorable directions to all for is_in
    "jump": {"directions": ["left", "right", "up", "down", None], "attack": ["jump"]},
    "nlight": {"directions": ["up", None], "attack": ["light"]},
    "slight": {"directions": ["left", "right"], "attack": ["light"]},
    "dlight": {"directions": ["down"], "attack": ["light"]},
    "nair": {"directions": ["up", None], "attack": ["light"]},
    "sair": {"directions": ["left", "right"], "attack": ["light"]},
    "dair": {"directions": ["down"], "attack": ["light"]},
    "nsig": {"directions": ["up", None], "attack": ["heavy"]},
    "ssig": {"directions": ["left", "right"], "attack": ["heavy"]},
    "dsig": {"directions": ["down"], "attack": ["heavy"]},
    "recovery": {"directions": ["up", None], "attack": ["heavy"]},
    "gp": {"directions": ["down"], "attack": ["heavy"]},
    "gc": {"directions": [None], "attack": ["dodge"]},
}

d_combos = {
    "unarmed": {
        "true": [
            {"seq": ["dlight", "jump", "nair"], "condition": []},
            {"seq": ["dlight", "jump", "sair"], "condition": []},
            {"seq": ["dlight", "jump", "dair"], "condition": ["dmg < 140"]},
            {"seq": ["dlight", "jump", "gc", "nlight"], "condition": []},
            {"seq": ["dlight", "jump", "gc", "slight"], "condition": []},
            {
                "seq": ["dlight", "jump", "gc", "dlight"],
                "condition": ["di", "dmg < 110"],
            },
            {"seq": ["dlight", "jump", "gc", "nsig"], "condition": []},
            {"seq": ["dlight", "jump", "rec"], "condition": []},
            {"seq": ["dlight", "jump", "gp"], "condition": ["closer"]},

            {"seq": ["dlight", "jump", "gc", "dlight", "jump", "nair"], "condition": []},
            {"seq": ["dlight", "jump", "gc", "dlight", "jump", "sair "], "condition": []},
            {"seq": ["dlight", "jump", "gc", "dlight", "jump", "dair"], "condition": []},
            {"seq": ["dlight", "jump", "gc", "dlight", "jump", "rec"], "condition": []},
            {"seq": ["dlight", "jump", "gc", "dlight", "jump", "gp"], "condition": []},
            {"seq": ["dlight", "jump", "gc", "dsig"], "condition": []},
            {"seq": ["dlight", "nsig"], "condition": []},
            {"seq": ["rec", "jump", "nair"], "condition": []},
            {
                "seq": ["dlight", "jump", "gc", "dlight", "rec", "jump", "nair "],
                "condition": [],
            },
            {"seq": ["sair", "nlight"], "condition": []},
            {"seq": ["dlight", "jump", "gc", "ssig"], "condition": []},
            {"seq": ["gp", "gc", "nlight"], "condition": []},
            {"seq": ["gp", "gc", "slight"], "condition": []},
            {"seq": ["gp", "gc", "dlight"], "condition": []},
            {"seq": ["gp", "cd", "nair"], "condition": []},
            {"seq": ["gp", "cd", "sair"], "condition": []},
            {"seq": ["gp", "cd", "dair"], "condition": []},
            {"seq": ["gp", "cd", "rec"], "condition": []},
            {"seq": ["gp", "gc", "ssig"], "condition": []},
            {"seq": ["gp", "gc", "dsig"], "condition": []},
            {"seq": ["gp", "gc", "dlight", "jump", "nair"], "condition": []},
            {"seq": ["gp", "gc", "dlight", "jump", "sair"], "condition": []},
            {"seq": ["gp", "gc", "dlight", "jump", "dair"], "condition": []},
            {"seq": ["gp", "gc", "dlight", "jump", "gp"], "condition": []},
            {"seq": ["gp", "gc", "dlight", "rec"], "condition": []},
            {"seq": ["gp", "gc", "dlight", "jump", "gp", "cd", "nair"], "condition": []},
            {"seq": ["gp", "gc", "dlight", "jump", "gp", "cd", "sair"], "condition": []},
            {"seq": ["gp", "gc", "dlight", "jump", "gp", "cd", "dair"], "condition": []},
            {"seq": ["gp", "gc", "dlight", "jump", "gp", "cd", "rec"], "condition": []},
            {"seq": ["gc", "dlight", "jump", "gp", "cd", "nair"], "condition": []},
            {"seq": ["gc", "dlight", "jump", "gp", "cd", "sair"], "condition": []},
            {"seq": ["gc", "dlight", "jump", "gp", "cd", "dair"], "condition": []},
            {"seq": ["gc", "dlight", "jump", "gp", "cd", "rec"], "condition": []},
            {
                "seq": ["dlight", "jump", "gc", "dlight", "jump", "gp", "cd", "nair"],
                "condition": [],
            },
            {
                "seq": ["dlight", "jump", "gc", "dlight", "jump", "gp", "cd", "rec"],
                "condition": [],
            },
            {"seq": ["slight", "nlight"], "condition": []},
            {"seq": ["dair", "nlight"], "condition": []},
            {"seq": ["gc", "dlight", "jump", "dair", "nlight"], "condition": []},
            {
                "seq": ["dlight", "jump", "gc", "dlight", "jump", "dair", "nlight"],
                "condition": [],
            }
        ],
        "strings": [],
    }
}

def is_sublist(ls_1, ls_2,strict=False):
    return [_1 for _1 in ls_1 if _1 in set(ls_2)]


def get_moves(pressed):  # left + light
    moves = []
    directions_all = {"left", "right", "up", "down"}
    actions_all = {"light", "heavy", "jump", "dodge", "throw"}

    directions_pressed = set([press for press in pressed if press in directions_all] or [None])
    actions_pressed = set([press for press in pressed if press in actions_all] or [None])

    for k, v in d_moves.items():
        name = k
        directions_move = set(v["directions"])  # left, right
        actions_move = set(v["attack"])  # light

        if directions_move.intersection(directions_pressed) and actions_move.intersection(actions_pressed) :
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
        if debug: print(f"No follow-up found, resetting combo [{g_moves}]")
        for i,combo_valid in combo_chain.items():
            combo,valid = combo_valid
            combo_chain[i] = [combo,[0]]

def newTimer():
    global t
    t = Timer(1,combo_reset)
    t.start()

def suggest_combos(pressed):  # a + leftclick
    __pressed = [__controls[key] for key in pressed]  # left + light
    if debug: print(f"Pressed: [{__pressed}]")
    moves = get_moves(__pressed)  # slight
    g_moves.update(moves)
    if debug: print(f"Moves: [{moves}]")
    if moves:
        if debug: print(f"Pressed-Matched: [{moves}] ----------------")
        combo_matched = False
        combo_in_progress = False
        suggestions.clear()
        ROOT.event_generate("<<CustomEvent>>")
        for i,combo_valid in combo_chain.items():
            if t:
                t.cancel()
            newTimer()
            combo,valid = combo_valid
            combo_at = valid[0]
            combo_next_at = combo_at + 1
            if debug: print(f"Checking [{i},{combo},{valid}]")
            for move in moves: # nlight,nair
                if debug: print(f"Trying to match [{move}]")
                seq, cond = combo["seq"], combo["condition"]
                if move == seq[combo_at]:
                    if len(seq) == combo_next_at:
                        print(f"\t\tCombo done: seq:[{seq}] cond:[{cond}]")
                        valid[0] = 0
                    else:
                        str_suggest = f"\tSuggestion: [{combo_at} -> {combo_next_at}] [{seq[combo_at]} -> {seq[combo_next_at]}] for seq:[{seq}] cond:[{cond}]"
                        print(str_suggest)
                        suggestions.append(str_suggest)
                        ROOT.event_generate("<<CustomEvent>>")
                        # print(f"\t{seq[:combo_next_at]} #{seq[combo_next_at]}# {seq[combo_next_at+1:]}")
                        valid[0] += 1
                    combo_matched = combo_next_at
                    # break
                elif combo_at > 0:
                    combo_in_progress = True
                    # print(f"\tCombo ignored [{move} -> {seq[combo_at]}]: seq:[{seq}] cond:[{cond}]") # TODO proper
                    valid[0] = 0
                if debug: print("-"*10)
            if debug: print("="*30)
        if not combo_matched:
            t.cancel()
            if combo_in_progress:
                print(f"\tCombo broken [{move} -> {seq[combo_at]}]: seq:[{seq}] cond:[{cond}]")
        i_pressed[0] += 1
        print(f"{'='*100} [{i_pressed[0]}]", end = '\r')

pressed = set()
g_moves = set() # TODO
suggestions = []
weapon = "unarmed"
legend = "bodvar"
combo_chain = {i:[combo, [0]] for i,combo in enumerate(d_combos[weapon]["true"])}

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
        if debug: print(key)
        pressed.add(key)
        if debug: print(f"Pressed: [{pressed}]")
        suggest_combos(pressed)

def on_release(key):
    try:
        pressed.remove(key)
        __released = [__controls[key]]  # left + light
        if debug: print(f"Released: [{__released}]")
        moves = get_moves(__released)  # slight
        g_moves.difference_update(moves)
    except KeyError:
        pass


listener_kb = Listener(on_press=on_press, on_release=on_release)
listener_kb.start()


def on_click(x, y, button, pressed_event):
    if pressed_event:
        if debug: print(pressed)
        pressed.add(button)
        suggest_combos(pressed)
    else:
        pressed.remove(button)


listener_m = mouse.Listener(on_click=on_click)
listener_m.start()

# Tinker
ROOT = Tk()
ROOT.title("Brawlhalla combo-helper")
ROOT.attributes('-topmost', True)
ROOT.attributes('-alpha', 0.8)

CONFIG = Label(ROOT, text="Currnt config")
CONFIG.pack()
COMBO_SUGGEST = Label(ROOT, text="Start any combo")
COMBO_SUGGEST.pack()

def update(event):
    str_suggestions = "\n".join(suggestions)
    COMBO_SUGGEST.config(text=str_suggestions)
    CONFIG.config(text=f"[{legend}]-[{weapon}]")
    # ROOT.after(1, update)

ROOT.bind("<<CustomEvent>>", update)
ROOT.bind('<Escape>', lambda e: ROOT.destroy())

def __dummy():
    pass

# Waiting
ROOT.after(0, __dummy)
ROOT.mainloop()
listener_kb.join()
listener_m.join()
print("Joined")

print("Done")