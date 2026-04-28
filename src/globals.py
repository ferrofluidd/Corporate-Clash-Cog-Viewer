import os
import glob
import sys
from direct.gui.DirectGui import DirectSlider
from direct.gui.OnscreenText import OnscreenText

DEFAULT_POS = (0, 0, 0)
DEFAULT_HPR = (180, 0, 0)

DEFAULT_CAMERA_POS = (0, -20, 4.2)

if getattr(sys, 'frozen', False):
    # if its running as an .exe in the root folder
    RESOURCES_DIR = "resources"
    SCREENSHOT_DIR = "screenshots"
    CONFIG_DIR = "CogViewerConfig.prc"
else:
    # iff its running as a script inside the src/ folder
    RESOURCES_DIR = "../resources"
    SCREENSHOT_DIR = "../screenshots"
    CONFIG_DIR = "../CogViewerConfig.prc"

# ***************** FIND BODY MODELS ***************
SUIT_A_MODEL = os.path.join(RESOURCES_DIR, "phase_3.5", "models", "char", "suitA-mod.bam")  # a
SUIT_B_MODEL = os.path.join(RESOURCES_DIR, "phase_3.5", "models", "char", "suitB-mod.bam")  # b
SUIT_C_MODEL = os.path.join(RESOURCES_DIR, "phase_3.5", "models", "char", "suitC-mod.bam")  # c
BOSS_COG_MODEL = os.path.join(RESOURCES_DIR, "phase_9", "models", "char", "bossCog-torso-zero.bam")

SUIT_A_FEMALE_MODEL = os.path.join(RESOURCES_DIR, "phase_3.5", "models", "char", "suitA_f-mod.bam")  # af
SUIT_B_FEMALE_MODEL = os.path.join(RESOURCES_DIR, "phase_3.5", "models", "char", "suitB_f-mod.bam")  # bf
SUIT_C_FEMALE_MODEL = os.path.join(RESOURCES_DIR, "phase_3.5", "models", "char", "suitC_f-mod.bam")  # cf

SUIT_B_COLLAR_MODEL = os.path.join(RESOURCES_DIR, "phase_3.5", "models", "char", "suitB_highcollar-mod.bam")  # bc
SUIT_PACESETTER = os.path.join(RESOURCES_DIR, "phase_3.5", "models", "char", "suitB_open-mod.bam")  # ps
SUIT_RAINMAKER = os.path.join(RESOURCES_DIR, "phase_3.5", "models", "char", "suitB_longcoat-mod.bam")  # rm
SUIT_HIGH_ROLLER = os.path.join(RESOURCES_DIR, "phase_3.5", "models", "char", "suitA_hroller-mod.bam")  # hr

SUIT_A_SKELECOG_MODEL = os.path.join(RESOURCES_DIR, "phase_5", "models", "char", "suitA_skeleton-zero.bam")  # as
SUIT_B_SKELECOG_MODEL = os.path.join(RESOURCES_DIR, "phase_5", "models", "char", "suitB_skeleton-zero.bam")  # bs
SUIT_C_SKELECOG_MODEL = os.path.join(RESOURCES_DIR, "phase_5", "models", "char", "suitC_skeleton-zero.bam")  # cs

SUIT_A_MPLAYER_OPEN = os.path.join(RESOURCES_DIR, "phase_3.5", "models", "char", "suitA_mplayer_open-mod.bam")  # mph
SUIT_A_CHAINSAW_HW = os.path.join(RESOURCES_DIR, "phase_3.5", "models", "char", "suitA_chainsaw_hw-mod.bam")  # cch
SUIT_A_ERFIT = os.path.join(RESOURCES_DIR, "phase_10", "models", "char", "suitA_erfit-mod.bam")

TREADS_MODEL = os.path.join(RESOURCES_DIR, "phase_9", "models", "char", "bossCog-treads.bam")
LEGS_MODEL = os.path.join(RESOURCES_DIR, "phase_9", "models", "char", "bossCog-legs-zero.bam")

VP_LEGS_MODEL = os.path.join(RESOURCES_DIR, "phase_9", "models", "char", "bossCog-legs-zero.bam")
VP_TORSO_MODEL = os.path.join(RESOURCES_DIR, "phase_9", "models", "char", "bossCog-torso-zero.bam")
VP_HEAD_MODEL = os.path.join(RESOURCES_DIR, "phase_9", "models", "char", "sellbotBoss-head-zero.bam")
VP_TREADS_MODEL = os.path.join(RESOURCES_DIR, "phase_9", "models", "char", "bossCog-treads.bam")

CFO_TORSO_MODEL = os.path.join(RESOURCES_DIR, "phase_9", "models", "char", "bossCog-torso-zero.bam")
CFO_LEGS_MODEL = os.path.join(RESOURCES_DIR, "phase_9", "models", "char", "bossCog-legs-zero.bam")
CFO_HEAD_MODEL = os.path.join(RESOURCES_DIR, "phase_10", "models", "char", "cashbotBoss-head-zero.bam")

CLO_BODY_MODEL = os.path.join(RESOURCES_DIR, "phase_11", "models", "char", "lawbotBoss-torso-zero.bam")
CLO_HEAD_MODEL = os.path.join(RESOURCES_DIR, "phase_11", "models", "char", "lawbotBoss-head-zero.bam")

CEO_BODY_MODEL = os.path.join(RESOURCES_DIR, "phase_9", "models", "char", "bossCog-torso-zero.bam")
CEO_HEAD_MODEL = os.path.join(RESOURCES_DIR, "phase_12", "models", "char", "bossbotBoss-head-zero.bam")

VP_TORSO_ANIMS = glob.glob(os.path.join(RESOURCES_DIR, "phase_9", "models", "char", "bossCog-torso-*.bam"))
VP_LEGS_ANIMS = glob.glob(os.path.join(RESOURCES_DIR, "phase_9", "models", "char", "bossCog-legs-*.bam"))

# ***************** FIND SKELECOG HEAD MODELS ***************
SUIT_A_SKELECOG_HEAD = os.path.join(RESOURCES_DIR, "phase_5", "models", "char", "suitA_skeleton_skull-zero.bam")
SUIT_B_SKELECOG_HEAD = os.path.join(RESOURCES_DIR, "phase_5", "models", "char", "suitB_skeleton_skull-zero.bam")
SUIT_C_SKELECOG_HEAD = os.path.join(RESOURCES_DIR, "phase_5", "models", "char", "suitC_skeleton_skull-zero.bam")

SKELECOG_HEAD_DICT = {SUIT_A_SKELECOG_HEAD, SUIT_B_SKELECOG_HEAD, SUIT_C_SKELECOG_HEAD}


def create_anim_dict(file_list, prefix_len_to_strip):
    d = {}
    for f in file_list:
        base = os.path.basename(f)
        anim_name = base[prefix_len_to_strip:-4]
        d[anim_name] = f
    return d


VP_TORSO_ANIM_DICT = create_anim_dict(VP_TORSO_ANIMS, len("bossCog-torso-"))
VP_LEGS_ANIM_DICT = create_anim_dict(VP_LEGS_ANIMS, len("bossCog-legs-"))

VP_HEAD_ANIMS = glob.glob(os.path.join(RESOURCES_DIR, "phase_9", "models", "char", "bossCog-head-*.bam"))
CFO_HEAD_ANIMS = glob.glob(os.path.join(RESOURCES_DIR, "phase_10", "models", "char", "cashbotBoss-head-*.bam"))
CLO_HEAD_ANIMS = glob.glob(os.path.join(RESOURCES_DIR, "phase_11", "models", "char", "lawbotBoss-head-*.bam"))
CEO_HEAD_ANIMS = glob.glob(os.path.join(RESOURCES_DIR, "phase_12", "models", "char", "bossbotBoss-head-*.bam"))

VP_HEAD_ANIM_DICT = create_anim_dict(VP_HEAD_ANIMS, len("bossCog-head-"))
CFO_HEAD_ANIM_DICT = create_anim_dict(CFO_HEAD_ANIMS, len("cashbotBoss-head-"))
CLO_HEAD_ANIM_DICT = create_anim_dict(CLO_HEAD_ANIMS, len("lawbotBoss-head-"))
CEO_HEAD_ANIM_DICT = create_anim_dict(CEO_HEAD_ANIMS, len("bossbotBoss-head-"))

SUIT_A_MODEL_KEYS = ["a", "af", "hr", "mph", "cch", "erfit", "as"]
SUIT_B_MODEL_KEYS = ["b", "bf", "bc", "ps", "rm", "bs"]
SUIT_C_MODEL_KEYS = ["c", "cf", "cs"]

# body model dictionary
SUIT_MODEL_DICT = {
    "a": SUIT_A_MODEL,
    "af": SUIT_A_FEMALE_MODEL,
    "hr": SUIT_HIGH_ROLLER,
    "mph": SUIT_A_MPLAYER_OPEN,
    "cch": SUIT_A_CHAINSAW_HW,
    "erfit": SUIT_A_ERFIT,
    "b": SUIT_B_MODEL,
    "bf": SUIT_B_FEMALE_MODEL,
    "bc": SUIT_B_COLLAR_MODEL,
    "ps": SUIT_PACESETTER,
    "rm": SUIT_RAINMAKER,
    "c": SUIT_C_MODEL,
    "cf": SUIT_C_FEMALE_MODEL,
    "as": SUIT_A_SKELECOG_MODEL,
    "bs": SUIT_B_SKELECOG_MODEL,
    "cs": SUIT_C_SKELECOG_MODEL,
    "boss": BOSS_COG_MODEL
}

SUIT_MODEL_NAMES = {
    "a": "Buff",
    "af": "Buff (Feminine)",
    "hr": "Buff Open Coat (High Roller)",
    "mph": "Buff Open Coat (Major Player)",
    "cch": "Buff Rolled-Up Cuffs (Chainsaw)",
    "erfit": "Ripped (Erfit)",
    "b": "Thin",
    "bf": "Thin (Feminine)",
    "bc": "Thin (Closed Collar)",
    "ps": "Thin Open Coat (Pacesetter)",
    "rm": "Raincoat (Rainmaker)",
    "c": "Fat",
    "cf": "Fat (Feminine)",
    "as": "Buff (Skelecog)",
    "bs": "Thin (Skelecog)",
    "cs": "Fat (Skelecog)",
    "boss": "Boss Cog"
}

# ***************** SHADOWS ***************
SHADOW_MODEL = os.path.join(RESOURCES_DIR, "phase_3", "models", "props", "drop_shadow.bam")
SHADOW_SCALE = 0.45
SHADOW_COLOR = (0.0, 0.0, 0.0, 0.5)

# ***************** COG EMBLEM ***************
COG_ICONS = os.path.join(RESOURCES_DIR, "phase_3.5", "models", "char", "ttcc_ene_insignias.bam")
COG_ICONS_BASE = os.path.join(RESOURCES_DIR, "phase_3.5", "models", "char", "ttcc_ene_insignias.bam")
COG_ICON_HPR = (0.00, 0.00, 0.00, 180.00, 0.00, 0.00, 1.00, 1.00, 1.00)

# ***************** FIND SUIT ANIMATIONS ***************
SUIT_A_ANIMATION_PATHS = glob.glob(os.path.join(RESOURCES_DIR, "**", "suitA-*.bam"), recursive=True)
SUIT_B_ANIMATION_PATHS = glob.glob(os.path.join(RESOURCES_DIR, "**", "suitB-*.bam"), recursive=True)
SUIT_C_ANIMATION_PATHS = glob.glob(os.path.join(RESOURCES_DIR, "**", "suitC-*.bam"), recursive=True)
BOSS_COG_ANIMATION_PATHS = glob.glob(os.path.join(RESOURCES_DIR, "**", "bossCog-torso*.bam"), recursive=True)

SUIT_A_ANIMATION_DICT = {}
SUIT_B_ANIMATION_DICT = {}
SUIT_C_ANIMATION_DICT = {}
BOSS_COG_ANIMATION_DICT = {}

# split em up into dictionaries for the actor
for i in range(0, len(SUIT_A_ANIMATION_PATHS)):
    SUIT_A_ANIMATION_DICT[os.path.basename(SUIT_A_ANIMATION_PATHS[i])[5:-4]] = SUIT_A_ANIMATION_PATHS[i]

for i in range(0, len(SUIT_B_ANIMATION_PATHS)):
    SUIT_B_ANIMATION_DICT[os.path.basename(SUIT_B_ANIMATION_PATHS[i])[5:-4]] = SUIT_B_ANIMATION_PATHS[i]

for i in range(0, len(SUIT_C_ANIMATION_PATHS)):
    SUIT_C_ANIMATION_DICT[os.path.basename(SUIT_C_ANIMATION_PATHS[i])[5:-4]] = SUIT_C_ANIMATION_PATHS[i]

for i in range(0, len(BOSS_COG_ANIMATION_PATHS)):
    BOSS_COG_ANIMATION_DICT[os.path.basename(BOSS_COG_ANIMATION_PATHS[i])[5:-4]] = BOSS_COG_ANIMATION_PATHS[i]

SUIT_A_ANIMATIONS = list(SUIT_A_ANIMATION_DICT)
SUIT_B_ANIMATIONS = list(SUIT_B_ANIMATION_DICT)
SUIT_C_ANIMATIONS = list(SUIT_C_ANIMATION_DICT)
BOSS_COG_ANIMATIONS = list(BOSS_COG_ANIMATION_DICT)
SUIT_A_ANIMATIONS.sort()
SUIT_B_ANIMATIONS.sort()
SUIT_C_ANIMATIONS.sort()
BOSS_COG_ANIMATIONS.sort()

# NEUTRAL ANIMATIONS
SUIT_A_NEUTRAL_ANIM_PATH = glob.glob(os.path.join(RESOURCES_DIR, "**", "suitA-neutral.bam"), recursive=True)
SUIT_B_NEUTRAL_ANIM_PATH = glob.glob(os.path.join(RESOURCES_DIR, "**", "suitB-neutral.bam"), recursive=True)
SUIT_C_NEUTRAL_ANIM_PATH = glob.glob(os.path.join(RESOURCES_DIR, "**", "suitC-neutral.bam"), recursive=True)
BOSS_COG_NEUTRAL_ANIM_PATH = glob.glob(os.path.join(RESOURCES_DIR, "**", "bossCog-torso-Fb_neutral.bam"),
                                       recursive=True)

# ***************** FIND HEAD ANIMATIONS ***************
HEAD_ANIM_DICT = {}
HEAD_ANIMS = []


def HEAD_ANIMATION_PATH(cog_name):
    HEAD_ANIMATION_PATHS = glob.glob(os.path.join(RESOURCES_DIR, "**", f"{cog_name}*.bam"), recursive=True)
    HEAD_ANIMATION_DICT = {}
    NAME_LENGTH = len(cog_name)

    HEAD_ANIMATION_PATHS = [path for path in HEAD_ANIMATION_PATHS if os.path.basename(path) != f"{cog_name}.bam"]

    for i in range(0, len(HEAD_ANIMATION_PATHS)):
        if not "-zero" in HEAD_ANIMATION_PATHS[i]:
            HEAD_ANIMATION_DICT[os.path.basename(HEAD_ANIMATION_PATHS[i])[NAME_LENGTH:-4]] = HEAD_ANIMATION_PATHS[i]

    HEAD_ANIMATIONS = sorted(HEAD_ANIMATION_DICT)

    HEAD_ANIM_DICT = HEAD_ANIMATION_DICT
    HEAD_ANIMS = HEAD_ANIMATIONS
    return HEAD_ANIMATION_DICT, HEAD_ANIMATIONS


def PATH_PROP(prop_name):
    path = os.path.join(RESOURCES_DIR, "phase_5", "models", "props", f"{prop_name}.bam")
    return path


def map_path(phase, texture_name):
    return os.path.join(RESOURCES_DIR, f"phase_{phase}", "maps", texture_name)


PHASES = ["3", "3.5", "4", "5", "5.5", "6", "7", "8", "9", "10", "11", "12", "13", "14"]

PROPS_DICT = {}
FOLDERS_TO_SEARCH = ["props", "char", "accessories"]

EXCLUDE_PREFIXES = ["suitA-", "suitB-", "suitC-", "tt_a_ara_", "bossCog-", "hole", "Bossbot", "bossbot", "Banquet",
                    "cc_m_ara-"]
EXCLUDE_SUFFIXES = ["_camera.bam", "_cammodel.bam"]

all_file_paths = []
for phase in PHASES:
    for folder_name in FOLDERS_TO_SEARCH:
        current_search_path = os.path.join(RESOURCES_DIR, f"phase_{phase}", "models", folder_name)

        if not os.path.exists(current_search_path):
            continue

        if folder_name == "accessories":
            search_pattern = os.path.join(current_search_path, "**", "*.bam")
            all_file_paths.extend(glob.glob(search_pattern, recursive=True))
        else:
            search_pattern = os.path.join(current_search_path, "*.bam")
            all_file_paths.extend(glob.glob(search_pattern))

golf_path = os.path.join(RESOURCES_DIR, "phase_6", "models", "golf")
if os.path.exists(golf_path):
    search_pattern = os.path.join(golf_path, "**", "*.bam")
    all_file_paths.extend(glob.glob(search_pattern, recursive=True))

foog_path = os.path.join(RESOURCES_DIR, "phase_12", "models", "bossbotHQ")
if os.path.exists(foog_path):
    search_pattern = os.path.join(foog_path, "**", "*.bam")
    all_file_paths.extend(glob.glob(search_pattern, recursive=True))

plant_path = os.path.join(RESOURCES_DIR, "phase_11", "models", "lawbotHQ")
if os.path.exists(plant_path):
    search_pattern = os.path.join(plant_path, "**", "*.bam")
    all_file_paths.extend(glob.glob(search_pattern, recursive=True))

rose_path = os.path.join(RESOURCES_DIR, "phase_6", "models", "miniboss")
if os.path.exists(rose_path):
    search_pattern = os.path.join(rose_path, "**", "*.bam")
    all_file_paths.extend(glob.glob(search_pattern, recursive=True))

file_path_map = {}

for file_path in all_file_paths:
    file_name = os.path.basename(file_path)

    if any(file_name.startswith(p) for p in EXCLUDE_PREFIXES):
        continue
    if any(file_name.endswith(s) for s in EXCLUDE_SUFFIXES):
        continue

    basename_no_ext = file_name[:-4]

    file_path_map[basename_no_ext] = file_path

all_basenames = set(file_path_map.keys())
models_to_add = {}
anims_to_find = {}

for name in all_basenames:
    if name.endswith("-zero") or name.endswith("-mod"):
        if name.endswith("-zero"):
            prop_name = name[:-len("-zero")]
        elif name.endswith("-mod"):
            prop_name = name[:-len("-mod")]

        if prop_name not in models_to_add:
            models_to_add[prop_name] = name
            anims_to_find[prop_name] = name
    else:
        parts = name.split('-')
        is_anim = False

        for i in range(1, len(parts)):
            base_guess = "-".join(parts[:i])
            if (base_guess in all_basenames and base_guess != name) or \
                    (f"{base_guess}-zero" in all_basenames) or \
                    (f"{base_guess}-mod" in all_basenames):
                is_anim = True
                break
        if not is_anim:
            if name not in models_to_add:
                models_to_add[name] = name

for prop_name, model_basename in models_to_add.items():

    PROPS_DICT[prop_name] = {
        "model": file_path_map[model_basename],
        "anims": {}
    }

    if prop_name in anims_to_find:
        search_prefix_1 = f"{model_basename}-"
        search_prefix_2 = f"{prop_name}-"

        for basename, file_path in file_path_map.items():
            if basename.startswith(search_prefix_1):
                anim_name = basename[len(search_prefix_1):]
                if anim_name:
                    PROPS_DICT[prop_name]["anims"][anim_name] = file_path

            elif basename.startswith(search_prefix_2) and basename != model_basename:
                anim_name = basename[len(search_prefix_2):]
                if anim_name:
                    PROPS_DICT[prop_name]["anims"][anim_name] = file_path

# ***************** SKELECOG METER COLORS ***************
SKELECOG_METER_COLORS = [
    (0, 1, 0, 1),
    (1, 216 / 255, 0, 1),
    (1, 106 / 255, 0, 1),
    (1, 0, 0, 1),
    (0, 230 / 255, 230 / 255, 1),
    (153 / 255, 0, 1, 1),
    (1, 1, 1, 1)
]

# ***************** COG SUIT TEXTURES ***************
SELLBOT_SUIT = os.path.join(RESOURCES_DIR, "phase_3.5", "maps", "ttcc_ene_suittex_s.png")
SELLBOT_EXE_SUIT = os.path.join(RESOURCES_DIR, "phase_3.5", "maps", "ttcc_ene_suittex_s_e.png")

CASHBOT_SUIT = os.path.join(RESOURCES_DIR, "phase_3.5", "maps", "ttcc_ene_suittex_m.png")
CASHBOT_EXE_SUIT = os.path.join(RESOURCES_DIR, "phase_3.5", "maps", "ttcc_ene_suittex_m_e.png")

LAWBOT_SUIT = os.path.join(RESOURCES_DIR, "phase_3.5", "maps", "ttcc_ene_suittex_l.png")
LAWBOT_EXE_SUIT = os.path.join(RESOURCES_DIR, "phase_3.5", "maps", "ttcc_ene_suittex_l_e.png")

BOSSBOT_SUIT = os.path.join(RESOURCES_DIR, "phase_3.5", "maps", "ttcc_ene_suittex_c.png")
BOSSBOT_EXE_SUIT = os.path.join(RESOURCES_DIR, "phase_3.5", "maps", "ttcc_ene_suittex_c_e.png")

WAITER_SUIT = os.path.join(RESOURCES_DIR, "phase_12", "maps", "ttcc_ene_suittex_waiter.png")
WAITER_EXE_SUIT = os.path.join(RESOURCES_DIR, "phase_12", "maps", "ttcc_ene_suittex_waiter_e.png")

BOARDBOT_SUIT = os.path.join(RESOURCES_DIR, "phase_3.5", "maps", "ttcc_ene_suittex_g.png")
BOARDBOT_EXE_SUIT = os.path.join(RESOURCES_DIR, "phase_3.5", "maps", "ttcc_ene_suittex_g_e.png")

UNEMPLOYED_SUIT = os.path.join(RESOURCES_DIR, "phase_3.5", "maps", "ttcc_ene_suittex_unemployed.png")

# Specific Cog Suits
HIGH_ROLLER_SUIT = os.path.join(RESOURCES_DIR, "phase_12", "maps", "cc_t_ene_highroller_suit.png")
HIGH_ROLLER_BODY = os.path.join(RESOURCES_DIR, "phase_12", "maps", "cc_t_ene_highroller_body.png")
HIGH_ROLLER_PRODIGAL_SUIT = os.path.join(RESOURCES_DIR, "phase_12", "maps", "cc_t_ene_highroller_suit_black.png")
HIGH_ROLLER_PRODIGAL_BODY = os.path.join(RESOURCES_DIR, "phase_12", "maps", "cc_t_ene_highroller_body_black.png")

MP_BODY = os.path.join(RESOURCES_DIR, "phase_12", "maps", "ttcc_ene_suittex_mplayer_body_totally_normal.png")

INSIDER_SUIT = os.path.join(RESOURCES_DIR, "phase_3.5", "maps", "ttcc_ene_suittex_highcollar_g.png")
INSIDER_EXE_SUIT = os.path.join(RESOURCES_DIR, "phase_3.5", "maps", "ttcc_ene_suittex_highcollar_g_e.png")
INSIDER_UNEMPLOYED_SUIT = os.path.join(RESOURCES_DIR, "phase_3.5", "maps", "ttcc_ene_suittex_highcollar_unemployed.png")

DESK_SUIT = os.path.join(RESOURCES_DIR, "phase_3.5", "maps", "schoolhouse", "dummy", "ttcc_ene_suittex_djockey.png")
DESK_BRIAN_SUIT = os.path.join(RESOURCES_DIR, "phase_3.5", "maps", "schoolhouse", "dummy",
                               "ttcc_ene_suittex_ptjockey.png")
DESK_BRIAN_EXE_SUIT = os.path.join(RESOURCES_DIR, "phase_3.5", "maps", "schoolhouse", "dummy",
                                   "ttcc_ene_suittex_ptjockey_e.png")

CHAINSAW_SUIT = os.path.join(RESOURCES_DIR, "phase_12", "maps", "ttcc_ene_suittex_chainsaw.png")
CHAINSAW_SUIT_HW = os.path.join(RESOURCES_DIR, "phase_12", "maps", "ttcc_ene_suittex_chainsaw_hw.png")

# Skelecog Suits
SELLBOT_SKELE_SUIT = os.path.join(RESOURCES_DIR, "phase_5", "maps", "ttcc_ene_skelecog_s.png")
SELLBOT_SKELE_EXE_SUIT = os.path.join(RESOURCES_DIR, "phase_5", "maps", "ttcc_ene_skelecog_s_e.png")

CASHBOT_SKELE_SUIT = os.path.join(RESOURCES_DIR, "phase_5", "maps", "ttcc_ene_skelecog_m.png")
CASHBOT_SKELE_EXE_SUIT = os.path.join(RESOURCES_DIR, "phase_5", "maps", "ttcc_ene_skelecog_m_e.png")

LAWBOT_SKELE_SUIT = os.path.join(RESOURCES_DIR, "phase_5", "maps", "ttcc_ene_skelecog_l.png")
LAWBOT_SKELE_EXE_SUIT = os.path.join(RESOURCES_DIR, "phase_5", "maps", "ttcc_ene_skelecog_l_e.png")

BOSSBOT_SKELE_SUIT = os.path.join(RESOURCES_DIR, "phase_5", "maps", "ttcc_ene_skelecog_c.png")
BOSSBOT_SKELE_EXE_SUIT = os.path.join(RESOURCES_DIR, "phase_5", "maps", "ttcc_ene_skelecog_c_e.png")

SKELE_WAITER_SUIT = os.path.join(RESOURCES_DIR, "phase_5", "maps", "ttcc_ene_skelecog_waiter.png")

BOARDBOT_SKELE_SUIT = os.path.join(RESOURCES_DIR, "phase_5", "maps", "ttcc_ene_skelecog_g.png")
BOARDBOT_SKELE_EXE_SUIT = os.path.join(RESOURCES_DIR, "phase_5", "maps", "ttcc_ene_skelecog_g_e.png")

SKELE_UNEMPLOYED_SUIT = map_path(5, "ttcc_ene_skelecog_unemployed.png")

SUIT_TEXTURES = {
    "Standard": {
        "Sellbot": SELLBOT_SUIT,
        "Sellbot (Exe)": SELLBOT_EXE_SUIT,
        "Cashbot": CASHBOT_SUIT,
        "Cashbot (Exe)": CASHBOT_EXE_SUIT,
        "Lawbot": LAWBOT_SUIT,
        "Lawbot (Exe)": LAWBOT_EXE_SUIT,
        "Bossbot": BOSSBOT_SUIT,
        "Bossbot (Exe)": BOSSBOT_EXE_SUIT,
        "Boardbot": BOARDBOT_SUIT,
        "Boardbot (Exe)": BOARDBOT_EXE_SUIT,
        "Boardbot (Closed Collar)": INSIDER_SUIT,
        "Boardbot (Closed Collar, Exe)": INSIDER_EXE_SUIT,
        "Waiter": WAITER_SUIT,
        "Waiter (Exe)": WAITER_EXE_SUIT,
        "Unemployed": UNEMPLOYED_SUIT,
        "Unemployed (Closed Collar)": INSIDER_UNEMPLOYED_SUIT,
        "Desk Jockey": DESK_SUIT,
        "Desk Jockey (Brianbot)": DESK_BRIAN_SUIT,
        "Desk Jockey (Brianbot, Exe)": DESK_BRIAN_EXE_SUIT
    },
    "Manager": {
        "Bellringer": map_path(9, "ttcc_ene_suittex_bellring.png"),
        "Prethinker": map_path(9, "ttcc_ene_suittex_prethink.png"),
        "Multislacker": map_path(9, "ttcc_ene_suittex_mslacker.png"),
        "Pacesetter": map_path(9, "ttcc_ene_suittex_pacesetter.png"),
        "Duck Shuffler": map_path(10, "ttcc_ene_suittex_duckshfl.png"),
        "Treekiller": map_path(10, "ttcc_ene_suittex_treek.png"),
        "Plutocrat": map_path(10, "ttcc_ene_suittex_pcrat.png"),
        "Count Erfit": map_path(10, "ttcc_ene_suittex_erfit.png"),
        "High Roller (White)": HIGH_ROLLER_SUIT,
        "High Roller (Black)": HIGH_ROLLER_PRODIGAL_SUIT,
        "Mouthpiece": map_path(11, "ttcc_ene_suittex_mouthp.png"),
        "Rainmaker": map_path(11, "ttcc_ene_suittex_rainmake.png"),
        "Count Erclaim": map_path(11, "ttcc_ene_suittex_count.png"),
        "Firestarter": map_path(12, "ttcc_ene_suittex_fires.png"),
        "Featherbedder": map_path(12, "ttcc_ene_suittex_fbed.png"),
        "Major Player": map_path(12, "ttcc_ene_suittex_mplayer.png"),
        "Chainsaw Consultant": CHAINSAW_SUIT,
        "Deep Diver": map_path(14, "ttcc_ene_suittex_ddiver.png"),
        "Gatekeeper": map_path(14, "ttcc_ene_suittex_gatekeep.png")
    },
    "Halloween": {
        "Bellringer (HW)": map_path(9, "ttcc_ene_suittex_bellring_hw.png"),
        "Prethinker (HW)": map_path(9, "ttcc_ene_suittex_prethink_hw.png"),
        "Multislacker (HW)": map_path(9, "ttcc_ene_suittex_mslacker_hw.png"),
        "Duck Shuffler (HW)": map_path(10, "ttcc_ene_suittex_duckshfl_hw.png"),
        "Treekiller (HW)": map_path(10, "ttcc_ene_suittex_treek_hw.png"),
        "Plutocrat (HW)": map_path(10, "ttcc_ene_suittex_pcrat_hw.png"),
        "Mouthpiece (HW)": map_path(11, "ttcc_ene_suittex_mouthp_hw.png"),
        "Rainmaker (HW)": map_path(11, "ttcc_ene_suittex_rainmake_hw.png"),
        "Witch Hunter (HW)": map_path(11, "ttcc_ene_suittex_whunter_hw.png"),
        "Litigator (HW)": map_path(11, "ttcc_ene_suittex_lgator_hw.png"),
        "Stenographer (HW)": map_path(11, "ttcc_ene_suittex_stenog_hw.png"),
        "Case Manager (HW)": map_path(11, "ttcc_ene_suittex_caseman_hw.png"),
        "Scapegoat (HW)": map_path(11, "ttcc_ene_suittex_sgoat_hw.png"),
        "Derrick Man (HW)": map_path(12, "ttcc_ene_suittex_derrman_hw.png"),
        "Derrick Hand (HW)": map_path(12, "ttcc_ene_suittex_derrhand_hw.png"),
        "Firestarter (HW)": map_path(12, "ttcc_ene_suittex_fires_hw.png"),
        "Featherbedder (HW)": map_path(12, "ttcc_ene_suittex_fbed_hw.png"),
        "Major Player (HW)": map_path(12, "ttcc_ene_suittex_mplayer_suit_spooky.png"),
        "Chainsaw Consultant (HW)": CHAINSAW_SUIT_HW,
        "LAA (HW)": map_path(14, "ttcc_ene_suittex_dlao_hw.png"),
        "DOLD (HW)": map_path(14, "ttcc_ene_suittex_dold_hw.png"),
        "Deep Diver (HW)": map_path(14, "ttcc_ene_suittex_ddiver_hw.png"),
        "Gatekeeper (HW)": map_path(14, "ttcc_ene_suittex_gatekeep_hw.png")
    },
    "Skelecog": {
        "Sellbot (Skelecog)": SELLBOT_SKELE_SUIT,
        "Sellbot (Skelecog, Exe)": SELLBOT_SKELE_EXE_SUIT,
        "Cashbot (Skelecog)": CASHBOT_SKELE_SUIT,
        "Cashbot (Skelecog, Exe)": CASHBOT_SKELE_EXE_SUIT,
        "Lawbot (Skelecog)": LAWBOT_SKELE_SUIT,
        "Lawbot (Skelecog, Exe)": LAWBOT_SKELE_EXE_SUIT,
        "Bossbot (Skelecog)": BOSSBOT_SKELE_SUIT,
        "Bossbot (Skelecog, Exe)": BOSSBOT_SKELE_EXE_SUIT,
        "Boardbot (Skelecog)": BOARDBOT_SKELE_SUIT,
        "Boardbot (Skelecog, Exe)": BOARDBOT_SKELE_EXE_SUIT,
        "Waiter (Skelecog)": SKELE_WAITER_SUIT,
        "Unemployed (Skelecog)": SKELE_UNEMPLOYED_SUIT
    }
}

# ***************** UNIQUE COG HEAD TEXTURES ***************
BAGHOLDER = os.path.join(RESOURCES_DIR, "phase_14", "maps", "cc_t_ene_bagholder.png")
BAGHOLDER_EXE = os.path.join(RESOURCES_DIR, "phase_14", "maps", "cc_t_ene_bagholder_exe.png")
BAGHOLDER_FIRED = os.path.join(RESOURCES_DIR, "phase_14", "maps", "cc_t_ene_bagholder_unemployed.png")

INSIDER = os.path.join(RESOURCES_DIR, "phase_14", "maps", "cc_t_ene_insider.png")
INSIDER_EXE = os.path.join(RESOURCES_DIR, "phase_14", "maps", "cc_t_ene_insider_exe.png")
INSIDER_FIRED = os.path.join(RESOURCES_DIR, "phase_14", "maps", "cc_t_ene_insider_unemployed.png")

HEADHONCHO = os.path.join(RESOURCES_DIR, "phase_14", "maps", "cc_t_ene_headhoncho.png")
HEADHONCHO_EXE = os.path.join(RESOURCES_DIR, "phase_14", "maps", "cc_t_ene_headhoncho_exe.png")
HEADHONCHO_FIRED = os.path.join(RESOURCES_DIR, "phase_14", "maps", "cc_t_ene_headhoncho_unemployed.png")

CHAINSAW = os.path.join(RESOURCES_DIR, "phase_12", "maps", "ttcc_ene_chainsaw.png")
CHAINSAW_OVERRIDE = os.path.join(RESOURCES_DIR, "phase_12", "maps", "ttcc_ene_chainsaw_b.png")
CHAINSAW_HW = os.path.join(RESOURCES_DIR, "phase_12", "maps", "ttcc_ene_chainsaw_hw_b.png")
CHAINSAW_OVERRIDE_HW = os.path.join(RESOURCES_DIR, "phase_12", "maps", "ttcc_ene_chainsaw_hw.png")

MULTISLACKER = os.path.join(RESOURCES_DIR, "phase_9", "maps", "ttcc_ene_multislacker.png")
MULTISLACKER_STATIC_HW = os.path.join(RESOURCES_DIR, "phase_9", "maps", "ttcc_ene_multislacker_static_hw.png")
MULTISLACKER_SUIT = os.path.join(RESOURCES_DIR, "phase_9", "maps", "ttcc_ene_suittex_mslacker.png")

SUIT_TEXTURE_PATH = {
    "s": [SELLBOT_SUIT, SELLBOT_EXE_SUIT, UNEMPLOYED_SUIT],
    "m": [CASHBOT_SUIT, CASHBOT_EXE_SUIT, UNEMPLOYED_SUIT],
    "l": [LAWBOT_SUIT, LAWBOT_EXE_SUIT, UNEMPLOYED_SUIT],
    "c": [BOSSBOT_SUIT, BOSSBOT_EXE_SUIT, WAITER_SUIT, WAITER_EXE_SUIT, UNEMPLOYED_SUIT],
    "g": [BOARDBOT_SUIT, BOARDBOT_EXE_SUIT, UNEMPLOYED_SUIT],
    # Skelecogs
    "ss": [SELLBOT_SKELE_SUIT, SELLBOT_SKELE_EXE_SUIT, SKELE_UNEMPLOYED_SUIT],
    "ms": [CASHBOT_SKELE_SUIT, CASHBOT_SKELE_EXE_SUIT, SKELE_UNEMPLOYED_SUIT],
    "ls": [LAWBOT_SKELE_SUIT, LAWBOT_SKELE_EXE_SUIT, SKELE_UNEMPLOYED_SUIT],
    "cs": [BOSSBOT_SKELE_SUIT, BOSSBOT_SKELE_EXE_SUIT, SKELE_WAITER_SUIT, SKELE_UNEMPLOYED_SUIT],
    "gs": [BOARDBOT_SKELE_SUIT, BOARDBOT_SKELE_EXE_SUIT, SKELE_UNEMPLOYED_SUIT],
    # Special Cogs
    "hr": [HIGH_ROLLER_SUIT, HIGH_ROLLER_PRODIGAL_SUIT],
    "ttcc_ene_chainsaw": [CHAINSAW_SUIT, CHAINSAW_SUIT, CHAINSAW_SUIT, CHAINSAW_SUIT],
    "ttcc_ene_chainsaw_hw": [CHAINSAW_SUIT_HW, CHAINSAW_SUIT_HW, CHAINSAW_SUIT_HW, CHAINSAW_SUIT_HW],
    "ttcc_ene_multislacker": [MULTISLACKER_SUIT, MULTISLACKER_SUIT],
    "dj": [DESK_SUIT, DESK_BRIAN_SUIT, DESK_BRIAN_EXE_SUIT],
    # Special Boardbots
    "cc_a_ene_bagholder": [BOARDBOT_SUIT, BOARDBOT_EXE_SUIT, UNEMPLOYED_SUIT],
    "cc_a_ene_insider": [INSIDER_SUIT, INSIDER_EXE_SUIT, INSIDER_UNEMPLOYED_SUIT],
    "cc_a_ene_headhoncho": [BOARDBOT_SUIT, BOARDBOT_EXE_SUIT, UNEMPLOYED_SUIT]
}

HEAD_TEXTURE_PATH = {
    # Used to apply different head textures to the Cogs who have them
    "ttcc_ene_chainsaw": [CHAINSAW, CHAINSAW_OVERRIDE, CHAINSAW, CHAINSAW_OVERRIDE],
    "ttcc_ene_chainsaw_hw": [CHAINSAW_HW, CHAINSAW_OVERRIDE_HW, CHAINSAW_HW, CHAINSAW_OVERRIDE_HW],
    "ttcc_ene_multislacker": [MULTISLACKER, MULTISLACKER_STATIC_HW],
    "cc_a_ene_bagholder": [BAGHOLDER, BAGHOLDER_EXE, BAGHOLDER_FIRED],
    "cc_a_ene_insider": [INSIDER, INSIDER_EXE, INSIDER_FIRED],
    "cc_a_ene_headhoncho": [HEADHONCHO, HEADHONCHO_EXE, HEADHONCHO_FIRED],
    # Let's also throw high roller's body in here because why not
    "hr": [HIGH_ROLLER_BODY, HIGH_ROLLER_PRODIGAL_BODY]
}

# Used to map different necktie models for cogs
NECKTIE_MAP = {
    's': '**/necktie-s',
    'charon': '**/necktie-s',
    'l': '**/bowtie',
    'hydra': '**/bowtie',
    "m": '**/necktie-w',
    "c": '**/necktie-w',
    "g": '**/necktie-w',
    "majorplayerhalloween": '**/bowtie',
}

# Used to find cogs that shouldn't wear any ties
NO_NECKTIE_COGS = {
    "bellringer",
    "pacesetter",
    "rainmaker",
    "reddheirwing",
    "highroller",
    "counterfit",
    "chainsawconsultanthalloween",
    "insider",
    "deepdiver",
    "gatekeeper",
    "VP",
    "CFO",
    "CLO",
    "CEO"
}

NO_NECKTIE_SUITS = {
    "hr",
    "erfit",
    "bc",
    "ps",
    "rm",
    "boss"
}

COG_DATA = {
    # *******************   SELLBOTS **********************************
    "Cold Caller": {"suitTex": SELLBOT_SUIT,
                    "head": os.path.join(RESOURCES_DIR, "phase_9", "models", "char", "suits",
                                         "ttcc_ene_coldcaller.bam"),
                    "hands": (19 / 255, 58 / 255, 222 / 255, 1),
                    "name": "coldcaller",
                    "scale": 0.84541,
                    "dept": "s",
                    "suit": "c",
                    "suitToggle": "y",
                    "cog": "coldcaller",
                    "emblem": "emblem_sales"},

    "Telemarketer": {"suitTex": SELLBOT_SUIT,
                     "head": os.path.join(RESOURCES_DIR, "phase_9", "models", "char", "suits",
                                          "ttcc_ene_telemarketer.bam"),
                     "name": "telemarketer",
                     "hands": (236 / 255, 205 / 255, 193 / 255, 1),
                     "scale": 0.70888,
                     "dept": "s",
                     "suit": "b",
                     "suitToggle": "y",
                     "cog": "telemarketer",
                     "emblem": "emblem_sales"},

    "Name Dropper": {"suitTex": SELLBOT_SUIT,
                     "head": os.path.join(RESOURCES_DIR, "phase_9", "models", "char", "suits",
                                          "ttcc_ene_namedropper.bam"),
                     "hands": (193 / 255, 175 / 255, 205 / 255, 1),
                     "name": "namedropper",
                     "scale": 0.71782,
                     "dept": "s",
                     "suit": "a",
                     "suitToggle": "y",
                     "cog": "namedropper",
                     "emblem": "emblem_sales"},

    "Glad Hander": {"suitTex": SELLBOT_SUIT,
                    "head": os.path.join(RESOURCES_DIR, "phase_9", "models", "char", "suits",
                                         "ttcc_ene_gladhander.bam"),
                    "hands": (210 / 255, 214 / 255, 213 / 255, 1),
                    "name": "gladhander",
                    "scale": 1.14734,
                    "dept": "s",
                    "suit": "c",
                    "suitToggle": "y",
                    "cog": "gladhander",
                    "emblem": "emblem_sales"},

    "Mover and Shaker": {"suitTex": SELLBOT_SUIT,
                         "head": os.path.join(RESOURCES_DIR, "phase_9", "models", "char", "suits",
                                              "ttcc_ene_moverandshaker.bam"),
                         "name": "moverandshaker",
                         "hands": (236 / 255, 205 / 255, 193 / 255, 1),
                         "scale": 0.89792,
                         "dept": "s",
                         "suit": "b",
                         "suitToggle": "y",
                         "cog": "moverandshaker",
                         "emblem": "emblem_sales"},

    "Two Face": {"suitTex": SELLBOT_SUIT,
                 "head": os.path.join(RESOURCES_DIR, "phase_9", "models", "char", "suits", "ttcc_ene_twoface.bam"),
                 "hands": (236 / 255, 205 / 255, 193 / 255, 1),
                 "name": "twoface",
                 "scale": 0.86633,
                 "dept": "s",
                 "suit": "a",
                 "suitToggle": "y",
                 "cog": "twoface",
                 "emblem": "emblem_sales"},

    "Mingler": {"suitTex": SELLBOT_SUIT,
                "head": os.path.join(RESOURCES_DIR, "phase_9", "models", "char", "suits", "ttcc_ene_mingler.bam"),
                "name": "mingler",
                "hands": (242 / 255, 191 / 255, 242 / 255, 1),
                "scale": 0.94884,
                "dept": "s",
                "suit": "a",
                "suitToggle": "y",
                "cog": "mingler",
                "emblem": "emblem_sales"},

    "Mr. Hollywood": {"suitTex": SELLBOT_SUIT,
                      "head": os.path.join(RESOURCES_DIR, "phase_9", "models", "char", "suits",
                                           "ttcc_ene_mrhollywood.bam"),
                      "hands": (210 / 255, 214 / 255, 213 / 255, 1),
                      "name": "mrhollywood",
                      "scale": 1.15511,
                      "dept": "s",
                      "suit": "a",
                      "suitToggle": "y",
                      "cog": "mrhollywood",
                      "emblem": "emblem_sales"},

    "Factory Foreman": {"suitTex": SELLBOT_SKELE_EXE_SUIT,
                        "head": SUIT_A_SKELECOG_HEAD,
                        "hands": (122 / 255, 90 / 255, 125 / 255, 1),
                        "headTex": SELLBOT_SKELE_EXE_SUIT,
                        "name": "suitA_skeleton_skull",
                        "scale": 1.2162940654079308081393103980849,
                        "dept": "s",
                        "cog": "factoryforeman",
                        "suit": "as",
                        "emblem": "emblem_sales"},

    "P.R.R.": {"suitTex": SELLBOT_SKELE_EXE_SUIT,
               "head": os.path.join(RESOURCES_DIR, "phase_9", "models", "char", "suits", "ttcc_ene_dopr-zero.bam"),
               "headTex": os.path.join(RESOURCES_DIR, "phase_9", "maps", "ttcc_ene_dopr.png"),
               "hands": (122 / 255, 90 / 255, 125 / 255, 1),
               "name": "ttcc_ene_dopr",
               "scale": 1.4864552709359605911330049261084,
               "dept": "s",
               "cog": "PRR",
               "suit": "cs",
               "emblem": "emblem_sales",
               "hasHalloween": 1,
               "headTex_HW": os.path.join(RESOURCES_DIR, "phase_9", "maps", "ttcc_ene_dopr_hw.png"),
               "suitTex_HW": os.path.join(RESOURCES_DIR, "phase_9", "maps", "ttcc_ene_skelecog_dopr_hw.png"), },

    "D.O.P.A.": {"suitTex": SELLBOT_SKELE_EXE_SUIT,
                 "head": os.path.join(RESOURCES_DIR, "phase_9", "models", "char", "suits", "ttcc_ene_dopa-zero.bam"),
                 "headTex": os.path.join(RESOURCES_DIR, "phase_9", "maps", "ttcc_ene_dopa.png"),
                 "hands": (122 / 255, 90 / 255, 125 / 255, 1),
                 "headSize": 0.9090909090909,
                 "name": "ttcc_ene_dopa",
                 "scale": 1.7336176227777713685813500074988,
                 "dept": "s",
                 "cog": "DOPA",
                 "suit": "cs",
                 "emblem": "emblem_sales",
                 "hasHalloween": 1,
                 "headTex_HW": os.path.join(RESOURCES_DIR, "phase_9", "maps", "ttcc_ene_dopa_hw.png"),
                 "suitTex_HW": os.path.join(RESOURCES_DIR, "phase_9", "maps", "ttcc_ene_skelecog_dopa_hw.png")},

    "Bellringer": {"suitTex": os.path.join(RESOURCES_DIR, "phase_9", "maps", "ttcc_ene_suittex_bellring.png"),
                   "head": os.path.join(RESOURCES_DIR, "phase_9", "models", "char", "suits",
                                        "ttcc_ene_bellringer-zero.bam"),
                   "hands": (168 / 255, 127 / 255, 63 / 255, 1),
                   "name": "ttcc_ene_bellringer",
                   "scale": 0.88823975862068965517241379310345,
                   "dept": "s",
                   "suit": "bc",
                   "cog": "bellringer",
                   "headAnim": 1,
                   "animFolder": "phase_9",
                   "emblem": "emblem_sales",
                   "hasHalloween": 1,
                   "headTex_HW": os.path.join(RESOURCES_DIR, "phase_9", "maps", "ttcc_ene_bellringer_hw.png"),
                   "suitTex_HW": os.path.join(RESOURCES_DIR, "phase_9", "maps", "ttcc_ene_suittex_bellring_hw.png"),
                   "handsHW": (156 / 255, 168 / 255, 179 / 255, 1)},

    "Prethinker": {"suitTex": os.path.join(RESOURCES_DIR, "phase_9", "maps", "ttcc_ene_suittex_prethink.png"),
                   "head": os.path.join(RESOURCES_DIR, "phase_9", "models", "char", "suits",
                                        "ttcc_ene_prethinker-zero.bam"),
                   "hands": (128 / 255, 113 / 255, 142 / 255, 1),
                   "name": "ttcc_ene_prethinker",
                   "scale": 0.71454197183098591549295774647887,
                   "dept": "s",
                   "suit": "b",
                   "cog": "prethinker",
                   "animFolder": "phase_9",
                   "emblem": "emblem_sales",
                   "hasHalloween": 1,
                   "glassTex": os.path.join(RESOURCES_DIR, "phase_9", "maps", "ttcc_ene_prethinker_glass_hw.png"),
                   "headTex_HW": os.path.join(RESOURCES_DIR, "phase_9", "maps", "ttcc_ene_prethinker_hw.png"),
                   "suitTex_HW": os.path.join(RESOURCES_DIR, "phase_9", "maps", "ttcc_ene_suittex_prethink_hw.png"),
                   "handsHW": (137 / 255, 142 / 255, 160 / 255, 1)},

    "Multislacker": {"suitTex": os.path.join(RESOURCES_DIR, "phase_9", "maps", "ttcc_ene_suittex_mslacker.png"),
                     "head": os.path.join(RESOURCES_DIR, "phase_9", "models", "char", "suits",
                                          "ttcc_ene_multislacker-zero.bam"),
                     "hands": (115 / 255, 115 / 255, 115 / 255, 1),
                     "name": "ttcc_ene_multislacker",
                     "scale": 1.0647975539568345323741007194245,
                     "dept": "s",
                     "suit": "c",
                     "cog": "multislacker",
                     "headAnim": 1,
                     "suitToggle": "ms",
                     "emblem": "emblem_sales",
                     "hasHalloween": 1,
                     "suitTex_HW": os.path.join(RESOURCES_DIR, "phase_9", "maps", "ttcc_ene_suittex_mslacker_hw.png"),
                     "handsHW": (115 / 255, 115 / 255, 115 / 255, 1)},

    "Pacesetter": {"suitTex": os.path.join(RESOURCES_DIR, "phase_9", "maps", "ttcc_ene_suittex_pacesetter.png"),
                   "head": os.path.join(RESOURCES_DIR, "phase_9", "models", "char", "suits",
                                        "ttcc_ene_pacesetter-zero.bam"),
                   "hands": (94 / 255, 93 / 255, 93 / 255, 1),
                   "name": "ttcc_ene_pacesetter",
                   "scale": 1.0496811267605633802816901408451,
                   "dept": "s",
                   "suit": "ps",
                   "cog": "pacesetter",
                   "headAnim": 1,
                   "animFolder": "phase_9",
                   "emblem": "emblem_sales",
                   "hasHalloween": 1,
                   "headTex_HW": os.path.join(RESOURCES_DIR, "phase_9", "maps", "ttcc_ene_pacesetter_hw.png"),
                   "handsHW": (94 / 255, 93 / 255, 93 / 255, 1)},

    # *******************   CASHBOTS **********************************
    "Short Change": {"suitTex": CASHBOT_SUIT,
                     "head": os.path.join(RESOURCES_DIR, "phase_10", "models", "char", "suits",
                                          "ttcc_ene_shortchange.bam"),
                     "hands": (75 / 255, 166 / 255, 222 / 255, 1),
                     "name": "shortchange",
                     "scale": 0.60386,
                     "dept": "m",
                     "suit": "c",
                     "cog": "shortchange",
                     "suitToggle": "y",
                     "emblem": "emblem_money"},

    "Penny Pincher": {"suitTex": CASHBOT_SUIT,
                      "head": os.path.join(RESOURCES_DIR, "phase_10", "models", "char", "suits",
                                           "ttcc_ene_pennypincher.bam"),
                      "name": "pennypincher",
                      "hands": (203 / 255, 82 / 255, 73 / 255, 1),
                      "scale": 0.58580,
                      "dept": "m",
                      "suit": "a",
                      "cog": "pennypincher",
                      "suitToggle": "y",
                      "emblem": "emblem_money"},

    "Tightwad": {"suitTex": CASHBOT_SUIT,
                 "head": os.path.join(RESOURCES_DIR, "phase_10", "models", "char", "suits", "ttcc_ene_tightwad.bam"),
                 "hands": (166 / 255, 242 / 255, 217 / 255, 1),
                 "name": "tightwad",
                 "scale": 1.08695,
                 "dept": "m",
                 "suit": "c",
                 "cog": "tightwad",
                 "suitToggle": "y",
                 "emblem": "emblem_money"},

    "Bean Counter": {"suitTex": CASHBOT_SUIT,
                     "head": os.path.join(RESOURCES_DIR, "phase_10", "models", "char", "suits",
                                          "ttcc_ene_beancounter.bam"),
                     "hands": (164 / 255, 178 / 255, 168 / 255, 1),
                     "name": "beancounter",
                     "scale": 0.83175,
                     "dept": "m",
                     "suit": "b",
                     "cog": "beancounter",
                     "suitToggle": "y",
                     "emblem": "emblem_money"},

    "Number Cruncher": {"suitTex": CASHBOT_SUIT,
                        "head": os.path.join(RESOURCES_DIR, "phase_10", "models", "char", "suits",
                                             "ttcc_ene_numbercruncher.bam"),
                        "name": "numbercruncher",
                        "hands": (166 / 255, 242 / 255, 217 / 255, 1),
                        "scale": 0.86633,
                        "dept": "m",
                        "suit": "a",
                        "cog": "numbercruncher",
                        "suitToggle": "y",
                        "emblem": "emblem_money"},

    "Money Bags": {"suitTex": CASHBOT_SUIT,
                   "head": os.path.join(RESOURCES_DIR, "phase_10", "models", "char", "suits", "ttcc_ene_moneybags.bam"),
                   "hands": (171 / 255, 194 / 255, 188 / 255, 1),
                   "name": "moneybags",
                   "scale": 1.28019,
                   "dept": "m",
                   "suit": "c",
                   "cog": "moneybags",
                   "suitToggle": "y",
                   "emblem": "emblem_money"},

    "Loan Shark": {"suitTex": CASHBOT_SUIT,
                   "head": os.path.join(RESOURCES_DIR, "phase_10", "models", "char", "suits", "ttcc_ene_loanshark.bam"),
                   "name": "loanshark",
                   "hands": (171 / 255, 194 / 255, 188 / 255, 1),
                   "scale": 1.22873,
                   "dept": "m",
                   "suit": "b",
                   "cog": "loanshark",
                   "suitToggle": "y",
                   "emblem": "emblem_money"},

    "Robber Baron": {"suitTex": CASHBOT_SUIT,
                     "head": os.path.join(RESOURCES_DIR, "phase_10", "models", "char", "suits",
                                          "ttcc_ene_robberbaron.bam"),
                     "hands": (188 / 255, 201 / 255, 196 / 255, 1),
                     "name": "robberbaron",
                     "scale": 1.15511,
                     "dept": "m",
                     "suit": "a",
                     "cog": "robberbaron",
                     "suitToggle": "y",
                     "emblem": "emblem_money"},

    "Mint Supervisor": {"suitTex": CASHBOT_SKELE_EXE_SUIT,
                        "head": SUIT_C_SKELECOG_HEAD,
                        "headTex": CASHBOT_SKELE_EXE_SUIT,
                        "hands": (85 / 255, 103 / 255, 82 / 255, 1),
                        "name": "suitC_skeleton_skull",
                        "scale": 1.7581499476284002087027842057181,
                        "dept": "m",
                        "cog": "mintsupervisor",
                        "suit": "cs",
                        "emblem": "emblem_money"},

    "Duck Shuffler": {"suitTex": os.path.join(RESOURCES_DIR, "phase_10", "maps", "ttcc_ene_suittex_duckshfl.png"),
                      "head": os.path.join(RESOURCES_DIR, "phase_10", "models", "char", "suits",
                                           "ttcc_ene_duckshuffler-zero.bam"),
                      "name": "ttcc_ene_duckshuffler",
                      "hands": (182 / 255, 30 / 255, 14 / 255, 1),
                      "scale": 0.89611200636942675159235668789809,
                      "dept": "m",
                      "suitToggle": "ds3",
                      "suit": "b",
                      "cog": "duckshuffler",
                      "emblem": "emblem_money",
                      # hallowtest
                      "hasHalloween": 1,
                      "headTex_HW": os.path.join(RESOURCES_DIR, "phase_10", "maps", "ttcc_ene_duckshuffler_hw.png"),
                      "slotTex": os.path.join(RESOURCES_DIR, "phase_10", "maps", "slot_hw.png"),
                      "suitTex_HW": os.path.join(RESOURCES_DIR, "phase_10", "maps", "ttcc_ene_suittex_duckshfl_hw.png"),
                      "handsHW": (158 / 255, 158 / 255, 86 / 255, 1)},

    "Treekiller": {"suitTex": os.path.join(RESOURCES_DIR, "phase_10", "maps", "ttcc_ene_suittex_treek.png"),
                   "head": os.path.join(RESOURCES_DIR, "phase_10", "models", "char", "suits",
                                        "ttcc_ene_treekiller-zero.bam"),
                   "headSize": 0.89873417721518987341772151898734,
                   "headPos": -0.15,
                   "hands": (154 / 255, 187 / 255, 147 / 255, 1),
                   "name": "ttcc_ene_treekiller",
                   "scale": 1.28019,
                   "dept": "m",
                   "suit": "c",
                   "cog": "treekiller",
                   "emblem": "emblem_money",
                   "hasHalloween": 1,
                   "headModel_HW": os.path.join(RESOURCES_DIR, "phase_10", "models", "char", "suits",
                                                "ttcc_ene_treekiller_hw-zero.bam"),
                   "suitTex_HW": os.path.join(RESOURCES_DIR, "phase_10", "maps", "ttcc_ene_suittex_treek_hw.png"),
                   "handsHW": (101 / 255, 39 / 255, 64 / 255, 1)},

    "Plutocrat": {"suitTex": os.path.join(RESOURCES_DIR, "phase_10", "maps", "ttcc_ene_suittex_pcrat.png"),
                  "head": os.path.join(RESOURCES_DIR, "phase_10", "models", "char", "suits",
                                       "ttcc_ene_plutocrat-zero.bam"),
                  "hands": (170 / 255, 163 / 255, 153 / 255, 1),
                  "name": "ttcc_ene_plutocrat",
                  "scale": 0.77774983870967741935483870967742,
                  "dept": "m",
                  "suit": "c",
                  "cog": "plutocrat",
                  "emblem": "emblem_money",
                  "hasHalloween": 1,
                  "headTex_HW": os.path.join(RESOURCES_DIR, "phase_10", "maps", "ttcc_ene_plutocrat_hw.png"),
                  "suitTex_HW": os.path.join(RESOURCES_DIR, "phase_10", "maps", "ttcc_ene_suittex_pcrat_hw.png"),
                  "handsHW": (183 / 255, 82 / 255, 30 / 255, 1)},

    "Charon": {"suitTex": CASHBOT_SKELE_SUIT,
               "head": SUIT_A_SKELECOG_HEAD,
               # "headTex": os.path.join(RESOURCES_DIR,"phase_5","maps","ttcc_ene_skelecog_m.png"),
               "bodyColor": (135 / 255, 129 / 255, 121 / 255, 1),
               "hands": (66 / 255, 63 / 255, 58 / 255, 1),
               "name": "suitA_skeleton_skull",
               "scale": 0.89877052054794520547945205479452,
               "dept": "m",
               "cog": "charon",
               "suit": "as",
               "emblem": "emblem_money"},

    "Nix": {"suitTex": CASHBOT_SKELE_SUIT,
            "head": SUIT_B_SKELECOG_HEAD,
            # "headTex": os.path.join(RESOURCES_DIR,"phase_5","maps","ttcc_ene_skelecog_m.png"),
            "bodyColor": (144 / 255, 150 / 255, 160 / 255, 1),
            "hands": (71 / 255, 74 / 255, 78 / 255, 1),
            "name": "suitB_skeleton_skull",
            "scale": 1.0231969818181818181818181818182,
            "dept": "m",
            "cog": "nix",
            "suit": "bs",
            "emblem": "emblem_money"},

    "Hydra": {"suitTex": CASHBOT_SKELE_SUIT,
              "head": SUIT_C_SKELECOG_HEAD,
              # "headTex": os.path.join(RESOURCES_DIR,"phase_5","maps","ttcc_ene_skelecog_m.png"),
              "bodyColor": (156 / 255, 181 / 255, 186 / 255, 1),
              "hands": (77 / 255, 89 / 255, 91 / 255, 1),
              "name": "suitC_skeleton_skull",
              "scale": 1.4679512,
              "dept": "m",
              "cog": "hydra",
              "suit": "cs",
              "emblem": "emblem_money"},

    "Styx": {"suitTex": CASHBOT_SKELE_SUIT,
             "head": SUIT_C_SKELECOG_HEAD,
             # "headTex": os.path.join(RESOURCES_DIR,"phase_5","maps","ttcc_ene_skelecog_m.png"),
             "bodyColor": (191 / 255, 191 / 255, 191 / 255, 1),
             "hands": (92 / 255, 92 / 255, 91 / 255, 1),
             "name": "suitC_skeleton_skull",
             "scale": 1.2558195236994219653179190751445,
             "dept": "m",
             "cog": "styx",
             "suit": "cs",
             "emblem": "emblem_money"},

    "Kerberos": {"suitTex": CASHBOT_SKELE_SUIT,
                 "head": SUIT_A_SKELECOG_HEAD,
                 # "headTex": os.path.join(RESOURCES_DIR,"phase_5","maps","ttcc_ene_skelecog_m.png"),
                 "bodyColor": (166 / 255, 191 / 255, 166 / 255, 1),
                 "hands": (82 / 255, 94 / 255, 81 / 255, 1),
                 "name": "suitA_skeleton_skull",
                 "scale": 1.0901216636323464427750773309766,
                 "dept": "m",
                 "cog": "kerberos",
                 "suit": "as",
                 "emblem": "emblem_money"},

    "High Roller": {"suitTex": HIGH_ROLLER_SUIT,
                    "head": os.path.join(RESOURCES_DIR, "phase_12", "models", "char", "suits",
                                         "cc_m_chr_ene_highroller-zero.bam"),
                    "headSize": 1.17045,
                    "hands": (1, 1, 1, 1),
                    "name": "cc_m_chr_ene_highroller",
                    "scale": 1.1756452888888888888888888888889,
                    "dept": "m",
                    "cog": "highroller",
                    "suit": "hr",
                    "suitToggle": "hr",
                    "emblem": "emblem_money"},

    "Count Erfit": {"suitTex": os.path.join(RESOURCES_DIR, "phase_10", "maps", "ttcc_ene_suittex_erfit.png"),
                    "head": os.path.join(RESOURCES_DIR, "phase_10", "models", "char", "suits",
                                         "ttcc_ene_counterfit-zero.bam"),
                    "name": "ttcc_ene_counterfit",
                    "hands": (242 / 255, 255 / 255, 242 / 255, 1),
                    "scale": 1.2225007170692431561996779388084,
                    "dept": "m",
                    "cog": "counterfit",
                    "suit": "erfit",
                    "emblem": "emblem_money"},

    # *******************   LAWBOTS **********************************
    "Bottom Feeder": {"suitTex": LAWBOT_SUIT,
                      "head": os.path.join(RESOURCES_DIR, "phase_11", "models", "char", "suits",
                                           "ttcc_ene_bottom_feeder-zero.bam"),
                      "hands": (191 / 255, 191 / 255, 242 / 255, 1),
                      "name": "ttcc_ene_bottom_feeder",
                      "scale": 0.96618,
                      "dept": "l",
                      "cog": "bottomfeeder",
                      "suit": "c",
                      "suitToggle": "y",
                      "emblem": "emblem_legal"},

    "Bloodsucker": {"suitTex": LAWBOT_SUIT,
                    "head": os.path.join(RESOURCES_DIR, "phase_11", "models", "char", "suits",
                                         "ttcc_ene_bloodsucker-zero.bam"),
                    "hands": (242 / 255, 242 / 255, 1, 1),
                    "name": "ttcc_ene_bloodsucker",
                    "scale": 0.83521504950495049504950495049505,
                    "dept": "l",
                    "cog": "bloodsucker",
                    "suit": "b",
                    "suitToggle": "y",
                    "emblem": "emblem_legal"},

    "Pettifogger": {"suitTex": LAWBOT_SUIT,
                    "head": os.path.join(RESOURCES_DIR, "phase_11", "models", "char", "suits",
                                         "ttcc_ene_pettifogger-zero.bam"),
                    "hands": (191 / 255, 191 / 255, 242 / 255, 1),
                    "name": "ttcc_ene_pettifogger",
                    "scale": 0.82819643564356435643564356435644,
                    "dept": "l",
                    "cog": "pettifogger",
                    "suit": "b",
                    "suitToggle": "y",
                    "emblem": "emblem_legal"},

    "Double Talker": {"suitTex": LAWBOT_SUIT,
                      "head": os.path.join(RESOURCES_DIR, "phase_11", "models", "char", "suits",
                                           "ttcc_ene_doubletalker-zero.bam"),
                      "hands": (191 / 255, 191 / 255, 242 / 255, 1),
                      "name": "ttcc_ene_doubletalker",
                      "scale": 0.70383649350649350649350649350649,
                      "dept": "l",
                      "cog": "doubletalker",
                      "suit": "a",
                      "suitToggle": "y",
                      "emblem": "emblem_legal"},

    "Needlenose": {"suitTex": LAWBOT_SUIT,
                   "head": os.path.join(RESOURCES_DIR, "phase_11", "models", "char", "suits",
                                        "ttcc_ene_needlenose-zero.bam"),
                   "hands": (97 / 255, 116 / 255, 182 / 255, 1),
                   "name": "ttcc_ene_needlenose",
                   "scale": 1.0938294303797468354430379746835,
                   "dept": "l",
                   "cog": "needlenose",
                   "suit": "cf",
                   "suitToggle": "y",
                   "emblem": "emblem_legal"},

    "Ambulance Chaser": {"suitTex": LAWBOT_SUIT,
                         "head": os.path.join(RESOURCES_DIR, "phase_11", "models", "char", "suits",
                                              "ttcc_ene_ambulance_chaser-zero.bam"),
                         "hands": (191 / 255, 191 / 255, 242 / 255, 1),
                         "name": "ttcc_ene_ambulance_chaser",
                         "scale": 0.82819643564356435643564356435644,
                         "dept": "l",
                         "cog": "ambulancechaser",
                         "suit": "b",
                         "suitToggle": "y",
                         "emblem": "emblem_legal"},

    "Conveyancer": {"suitTex": LAWBOT_SUIT,
                    "head": os.path.join(RESOURCES_DIR, "phase_11", "models", "char", "suits",
                                         "ttcc_ene_conveyancer-zero.bam"),
                    "belt": os.path.join(RESOURCES_DIR, "phase_11", "models", "char", "suits",
                                         "ttcc_ene_conveyancer_belt.bam"),
                    "hands": (109 / 255, 113 / 255, 143 / 255, 1),
                    "name": "ttcc_ene_conveyancer",
                    "scale": 0.74578701298701298701298701298701,
                    "dept": "l",
                    "cog": "conveyancer",
                    "suit": "a",
                    "suitToggle": "y",
                    "emblem": "emblem_legal"},

    "Back Stabber": {"suitTex": LAWBOT_SUIT,
                     "head": os.path.join(RESOURCES_DIR, "phase_11", "models", "char", "suits",
                                          "ttcc_ene_backstabber-zero.bam"),
                     "hands": (143 / 255, 132 / 255, 188 / 255, 1),
                     "name": "ttcc_ene_backstabber",
                     "scale": 0.96007484896260326669609636122848,
                     "dept": "l",
                     "cog": "backstabber",
                     "suit": "b",
                     "suitToggle": "y",
                     "emblem": "emblem_legal"},

    "Advocate": {"suitTex": LAWBOT_SUIT,
                 "head": os.path.join(RESOURCES_DIR, "phase_11", "models", "char", "suits",
                                      "ttcc_ene_advocate-zero.bam"),
                 "hands": (25 / 255, 25 / 255, 38 / 255, 1),
                 "name": "ttcc_ene_advocate",
                 "scale": 1.2726946202531645569620253164556,
                 "dept": "l",
                 "cog": "advocate",
                 "suit": "c",
                 "suitToggle": "y",
                 "emblem": "emblem_legal"},

    "Spin Doctor": {"suitTex": LAWBOT_SUIT,
                    "head": os.path.join(RESOURCES_DIR, "phase_11", "models", "char", "suits",
                                         "ttcc_ene_spin_doctor-zero.bam"),
                    "hands": (146 / 255, 212 / 255, 183 / 255, 1),
                    "name": "ttcc_ene_spin_doctor",
                    "scale": 1.0761278526833575077252948224759,
                    "dept": "l",
                    "cog": "spindoctor",
                    "suit": "b",
                    "suitToggle": "y",
                    "emblem": "emblem_legal"},

    "Shyster": {"suitTex": LAWBOT_SUIT,
                "head": os.path.join(RESOURCES_DIR, "phase_11", "models", "char", "suits", "ttcc_ene_shyster-zero.bam"),
                "hands": (191 / 255, 191 / 255, 242 / 255, 1),
                "name": "ttcc_ene_shyster",
                "scale": 1.0761278526833575077252948224759,
                "dept": "l",
                "cog": "shyster",
                "suit": "bf",
                "suitToggle": "y",
                "emblem": "emblem_legal"},

    "Legal Eagle": {"suitTex": LAWBOT_SUIT,
                    "head": os.path.join(RESOURCES_DIR, "phase_11", "models", "char", "suits",
                                         "ttcc_ene_legal_eagle-zero.bam"),
                    "hands": (180 / 255, 176 / 255, 218 / 255, 1),
                    "name": "ttcc_ene_legal_eagle",
                    "scale": 1.0762470682730923694779116465863,
                    "dept": "l",
                    "cog": "legaleagle",
                    "suit": "a",
                    "suitToggle": "y",
                    "emblem": "emblem_legal"},

    "Barrister": {"suitTex": LAWBOT_SUIT,
                  "head": os.path.join(RESOURCES_DIR, "phase_11", "models", "char", "suits",
                                       "ttcc_ene_barrister-zero.bam"),
                  "hands": (242 / 255, 242 / 255, 1, 1),
                  "name": "ttcc_ene_barrister",
                  "scale": 1.1226370281124497991967871485944,
                  "dept": "l",
                  "cog": "barrister",
                  "suit": "a",
                  "suitToggle": "y",
                  "emblem": "emblem_legal"},

    "Big Wig": {"suitTex": LAWBOT_SUIT,
                "head": os.path.join(RESOURCES_DIR, "phase_11", "models", "char", "suits", "ttcc_ene_bigwig-zero.bam"),
                "hands": (191 / 255, 191 / 255, 242 / 255, 1),
                "name": "ttcc_ene_bigwig",
                "scale": 1.15511,
                "dept": "l",
                "cog": "bigwig",
                "suit": "a",
                "suitToggle": "y",
                "emblem": "emblem_legal"},

    "Head Attorney": {"suitTex": LAWBOT_SKELE_EXE_SUIT,
                      "head": SUIT_B_SKELECOG_HEAD,
                      "headTex": LAWBOT_SKELE_EXE_SUIT,
                      "hands": (85 / 255, 103 / 255, 125 / 255, 1),
                      "name": "suitB_skeleton_skull",
                      "scale": 1.3320363054556193540746027375769,
                      "dept": "l",
                      "cog": "headattorney",
                      "suit": "bs",
                      "emblem": "emblem_legal"},

    "Mouthpiece": {"suitTex": os.path.join(RESOURCES_DIR, "phase_11", "maps", "ttcc_ene_suittex_mouthp.png"),
                   "head": os.path.join(RESOURCES_DIR, "phase_11", "models", "char", "suits",
                                        "ttcc_ene_mouthpiece-zero.bam"),
                   "hands": (89 / 255, 106 / 255, 130 / 255, 1),
                   "name": "ttcc_ene_mouthpiece",
                   "scale": 0.89567958470291646222257770285342,
                   "dept": "l",
                   "cog": "mouthpiece",
                   "suit": "b",
                   "emblem": "emblem_legal",
                   "hasHalloween": 1,
                   "headTex_HW": os.path.join(RESOURCES_DIR, "phase_11", "maps", "ttcc_ene_mouthpiece_hw.png"),
                   "suitTex_HW": os.path.join(RESOURCES_DIR, "phase_11", "maps", "ttcc_ene_suittex_mouthp_hw.png"),
                   "handsHW": (213 / 255, 198 / 255, 172 / 255, 1)},

    "Rainmaker": {"suitTex": os.path.join(RESOURCES_DIR, "phase_11", "maps", "ttcc_ene_suittex_rainmake.png"),
                  "head": os.path.join(RESOURCES_DIR, "phase_11", "models", "char", "suits",
                                       "ttcc_ene_rainmaker-zero.bam"),
                  "hands": (161 / 255, 165 / 255, 177 / 255, 1),
                  "name": "ttcc_ene_rainmaker",
                  "scale": 0.94489274869758220190513691729591,
                  "dept": "l",
                  "cog": "rainmaker",
                  "suit": "rm",
                  "suitToggle": "rm",
                  "emblem": "emblem_legal",
                  "hasHalloween": 1,
                  "headTex1": os.path.join(RESOURCES_DIR, "phase_11", "maps", "ttcc_ene_rainmaker.png"),
                  "hairTex": os.path.join(RESOURCES_DIR, "phase_11", "maps", "ttcc_ene_rainmaker_hair.png"),
                  "headTex_HW": os.path.join(RESOURCES_DIR, "phase_11", "maps", "ttcc_ene_rainmaker_hw.png"),
                  "hairTex_HW": os.path.join(RESOURCES_DIR, "phase_11", "maps", "ttcc_ene_rainmaker_hair_hw.png"),
                  "suitTex_HW": os.path.join(RESOURCES_DIR, "phase_11", "maps", "ttcc_ene_suittex_rainmake_hw.png"),
                  "handsHW": (155 / 255, 225 / 255, 193 / 255, 1)},

    "Witch Hunter": {"suitTex": os.path.join(RESOURCES_DIR, "phase_11", "maps", "ttcc_ene_suittex_whunter.png"),
                     "head": os.path.join(RESOURCES_DIR, "phase_11", "models", "char", "suits",
                                          "ttcc_ene_witchhunter-zero.bam"),
                     "headSize": 1.25,
                     "hands": (180 / 255, 176 / 255, 218 / 255, 1),
                     "name": "ttcc_ene_witchhunter",
                     "scale": 1.0254841895261845386533665835411,
                     "dept": "l",
                     "cog": "witchhunter",
                     "suit": "a",
                     "emblem": "emblem_legal",
                     "hasHalloween": 1,
                     "suitTex_HW": os.path.join(RESOURCES_DIR, "phase_11", "maps", "ttcc_ene_suittex_whunter_hw.png"),
                     "handsHW": (180 / 255, 176 / 255, 218 / 255, 1),
                     "headModel_HW": os.path.join(RESOURCES_DIR, "phase_11", "models", "char", "suits",
                                                  "ttcc_ene_witchhunter_hw-zero.bam")},

    "Count Erclaim": {"suitTex": os.path.join(RESOURCES_DIR, "phase_11", "maps", "ttcc_ene_suittex_count.png"),
                      "head": os.path.join(RESOURCES_DIR, "phase_11", "models", "char", "suits",
                                           "ttcc_ene_counterclaim-zero.bam"),
                      "hands": (242 / 255, 242 / 255, 1, 1),
                      "name": "ttcc_ene_counterclaim",
                      "scale": 1.15511,  # 1.1536329057852059708855653637069
                      "dept": "l",
                      "cog": "counterclaim",
                      "suit": "b",
                      "emblem": "emblem_legal"},

    "Redd 'Heir' Wing": {"suitTex": LAWBOT_EXE_SUIT,
                         "head": os.path.join(RESOURCES_DIR, "phase_11", "models", "char", "suits",
                                              "ttcc_ene_redd-zero.bam"),
                         "hands": (242 / 255, 242 / 255, 1, 1),
                         "name": "ttcc_ene_redd",
                         "scale": 0.83175,  # 1.1536329057852059708855653637069
                         "dept": "l",
                         "cog": "reddheirwing",
                         "suit": "b",
                         "emblem": "emblem_legal"},

    "Judy": {"suitTex": LAWBOT_SUIT,
             "head": os.path.join(RESOURCES_DIR, "phase_11", "models", "char", "suits", "ttcc_ene_judy-zero.bam"),
             "hands": (108 / 255, 126 / 255, 191 / 255, 1),
             "name": "ttcc_ene_judy",
             "scale": 1.0938294303797468354430379746835,
             "dept": "l",
             "cog": "judy",
             "suit": "cf",
             "emblem": "emblem_legal"},

    "Litigator": {"suitTex": LAWBOT_EXE_SUIT,
                  "head": os.path.join(RESOURCES_DIR, "phase_11", "models", "char", "suits",
                                       "ttcc_ene_litigator-zero.bam"),
                  "hands": (99 / 255, 113 / 255, 163 / 255, 1),
                  "name": "ttcc_ene_litigator",
                  "scale": 1.1923716129032258064516129032258,
                  "dept": "l",
                  "cog": "litigator",
                  "suit": "a",
                  "emblem": "emblem_legal",
                  "hasHalloween": 1,
                  "suitTex_HW": os.path.join(RESOURCES_DIR, "phase_11", "maps", "ttcc_ene_suittex_lgator_hw.png"),
                  "handsHW": (160 / 255, 117 / 255, 77 / 255, 1),
                  "headModel_HW": os.path.join(RESOURCES_DIR, "phase_11", "models", "char", "suits",
                                               "ttcc_ene_litigator_hw-zero.bam")},

    "Stenographer": {"suitTex": LAWBOT_EXE_SUIT,
                     "head": os.path.join(RESOURCES_DIR, "phase_11", "models", "char", "suits",
                                          "ttcc_ene_stenographer-zero.bam"),
                     "hands": (91 / 255, 104 / 255, 146 / 255, 1),
                     "name": "ttcc_ene_stenographer",
                     "scale": 1.1555212760806095563626005839208,
                     "dept": "l",
                     "cog": "stenographer",
                     "suit": "af",
                     "emblem": "emblem_legal",
                     "hasHalloween": 1,
                     "headTex_HW": os.path.join(RESOURCES_DIR, "phase_11", "maps", "ttcc_ene_stenographer_hw.png"),
                     "suitTex_HW": os.path.join(RESOURCES_DIR, "phase_11", "maps", "ttcc_ene_suittex_stenog_hw.png"),
                     "handsHW": (101 / 255, 57 / 255, 34 / 255, 1)},

    "Case Manager": {"suitTex": LAWBOT_EXE_SUIT,
                     "head": os.path.join(RESOURCES_DIR, "phase_11", "models", "char", "suits",
                                          "ttcc_ene_casemanager-zero.bam"),
                     "hands": (120 / 255, 85 / 255, 70 / 255, 1),
                     "name": "ttcc_ene_casemanager",
                     "scale": 1.1160387723420921455529445275226,
                     "dept": "l",
                     "cog": "casemanager",
                     "suit": "a",
                     "emblem": "emblem_legal",
                     "hasHalloween": 1,
                     "suitTex_HW": os.path.join(RESOURCES_DIR, "phase_11", "maps", "ttcc_ene_suittex_caseman_hw.png"),
                     "handsHW": (159 / 255, 159 / 255, 159 / 255, 1),
                     "headModel_HW": os.path.join(RESOURCES_DIR, "phase_11", "models", "char", "suits",
                                                  "ttcc_ene_casemanager_hw-zero.bam")},

    "Scapegoat": {"suitTex": LAWBOT_EXE_SUIT,
                  "head": os.path.join(RESOURCES_DIR, "phase_11", "models", "char", "suits",
                                       "ttcc_ene_scapegoat-zero.bam"),
                  "hands": (76 / 255, 76 / 255, 115 / 255, 1),
                  "name": "ttcc_ene_scapegoat",
                  "scale": 0.99977361194029850746268656716418,
                  "dept": "l",
                  "cog": "scapegoat",
                  "suit": "b",
                  "emblem": "emblem_legal",
                  "hasHalloween": 1,
                  "suitTex_HW": os.path.join(RESOURCES_DIR, "phase_11", "maps", "ttcc_ene_suittex_sgoat_hw.png"),
                  "handsHW": (189 / 255, 134 / 255, 69 / 255, 1),
                  "headModel_HW": os.path.join(RESOURCES_DIR, "phase_11", "models", "char", "suits",
                                               "ttcc_ene_scapegoat_hw-zero.bam")},

    # *******************   BOSSBOTS **********************************
    "Flunky": {"suitTex": BOSSBOT_SUIT,
               "head": os.path.join(RESOURCES_DIR, "phase_12", "models", "char", "suits", "ttcc_ene_flunky.bam"),
               "hands": (242 / 255, 191 / 255, 191 / 255, 1),
               "name": "flunky",
               "scale": 0.96618,
               "dept": "c",
               "cog": "flunky",
               "suit": "c",
               "suitToggle": "y",
               "emblem": "emblem_corp"},

    "Pencil Pusher": {"suitTex": BOSSBOT_SUIT,
                      "head": os.path.join(RESOURCES_DIR, "phase_12", "models", "char", "suits",
                                           "ttcc_ene_pencilpusher.bam"),
                      "name": "pencilpusher",
                      "hands": (146 / 255, 118 / 255, 113 / 255, 1),
                      "scale": 0.63327,
                      "dept": "c",
                      "cog": "pencilpusher",
                      "suit": "b",
                      "suitToggle": "y",
                      "emblem": "emblem_corp"},

    "Yesman": {"suitTex": BOSSBOT_SUIT,
               "head": os.path.join(RESOURCES_DIR, "phase_12", "models", "char", "suits", "ttcc_ene_yesman.bam"),
               "hands": (210 / 255, 214 / 255, 213 / 255, 1),
               "name": "yesman",
               "scale": 0.68069,
               "dept": "c",
               "cog": "yesman",
               "suit": "a",
               "suitToggle": "y",
               "emblem": "emblem_corp"},

    "Micromanager": {"suitTex": BOSSBOT_SUIT,
                     "head": os.path.join(RESOURCES_DIR, "phase_12", "models", "char", "suits",
                                          "ttcc_ene_micromanager.bam"),
                     "hands": (242 / 255, 191 / 255, 191 / 255, 1),
                     "name": "micromanager",
                     "scale": 0.24154,
                     "dept": "c",
                     "cog": "micromanager",
                     "suit": "c",
                     "suitToggle": "y",
                     "emblem": "emblem_corp"},

    "Downsizer": {"suitTex": BOSSBOT_SUIT,
                  "head": os.path.join(RESOURCES_DIR, "phase_12", "models", "char", "suits", "ttcc_ene_downsizer.bam"),
                  "name": "downsizer",
                  "hands": (164 / 255, 178 / 255, 168 / 255, 1),
                  "scale": 0.85066,
                  "dept": "c",
                  "cog": "downsizer",
                  "suit": "b",
                  "suitToggle": "y",
                  "emblem": "emblem_corp"},

    "Head Hunter": {"suitTex": BOSSBOT_SUIT,
                    "head": os.path.join(RESOURCES_DIR, "phase_12", "models", "char", "suits",
                                         "ttcc_ene_headhunter.bam"),
                    "hands": (242 / 255, 191 / 255, 191 / 255, 1),
                    "name": "headhunter",
                    "scale": 1.07260,
                    "dept": "c",
                    "cog": "headhunter",
                    "suit": "a",
                    "suitToggle": "y",
                    "emblem": "emblem_corp"},

    "Corporate Raider": {"suitTex": BOSSBOT_SUIT,
                         "head": os.path.join(RESOURCES_DIR, "phase_12", "models", "char", "suits",
                                              "ttcc_ene_corporateraider.bam"),
                         "name": "corporateraider",
                         "hands": (202 / 255, 172 / 255, 159 / 255, 1),
                         "scale": 1.63043,
                         "dept": "c",
                         "cog": "corporateraider",
                         "suit": "c",
                         "suitToggle": "y",
                         "emblem": "emblem_corp"},

    "Big Cheese": {"suitTex": BOSSBOT_SUIT,
                   "head": os.path.join(RESOURCES_DIR, "phase_12", "models", "char", "suits", "ttcc_ene_bigcheese.bam"),
                   "hands": (161 / 255, 204 / 255, 106 / 255, 1),
                   "name": "bigcheese",
                   "scale": 1.15511,
                   "dept": "c",
                   "cog": "bigcheese",
                   "suit": "a",
                   "suitToggle": "y",
                   "emblem": "emblem_corp"},

    "Autocaddie": {"suitTex": BOSSBOT_SKELE_EXE_SUIT,
                   "hatTex": os.path.join(RESOURCES_DIR, "phase_12", "maps", "cc_t_ene_ceo.png"),
                   "head": ("phase_12/models/char/suits/ttcc_ene_autocaddie-zero.bam"),
                   "hands": (133 / 255, 112 / 255, 86 / 255, 1),
                   "name": "suitA_skeleton_skull",
                   "scale": 0.71039265,
                   "dept": "c",
                   "cog": "autocaddie",
                   "suit": "as",
                   "emblem": "emblem_corp"},

    "Club President": {"suitTex": BOSSBOT_EXE_SUIT,
                       "head": ("phase_12/models/char/suits/ttcc_ene_clubpresident-zero.bam"),
                       "headPos": -0.1,
                       "headPosY": -0.1,
                       "headPosP": -10,
                       "headPosH": -5,
                       "hands": (133 / 255, 112 / 255, 86 / 255, 1),
                       "name": "ttcc_ene_clubpresident",
                       "scale": 1.21549075,
                       "dept": "c",
                       "cog": "clubpresident",
                       "suit": "a",
                       "emblem": "emblem_corp"},

    "Derrick Man": {"suitTex": BOSSBOT_EXE_SUIT,
                    "head": os.path.join(RESOURCES_DIR, "phase_12", "models", "char", "suits",
                                         "ttcc_ene_derrickman-zero.bam"),
                    "headPos": -0.1,
                    "headPosY": -0.2,
                    "hands": (175 / 255, 118 / 255, 63 / 255, 1),
                    "name": "ttcc_ene_derrickman",
                    "scale": 0.777074,
                    "dept": "c",
                    "cog": "derrickman",
                    "suit": "a",
                    "emblem": "emblem_corp",
                    "hasHalloween": 1,
                    "headTex_HW": os.path.join(RESOURCES_DIR, "phase_12", "maps", "ttcc_ene_derrickman_hw.png"),
                    "suitTex_HW": os.path.join(RESOURCES_DIR, "phase_12", "maps", "ttcc_ene_suittex_derrman_hw.png"),
                    "handsHW": (175 / 255, 118 / 255, 63 / 255, 1)},

    "Derrick Hand": {"suitTex": BOSSBOT_EXE_SUIT,
                     "head": os.path.join(RESOURCES_DIR, "phase_12", "models", "char", "suits",
                                          "ttcc_ene_derrickhand-zero.bam"),
                     "hands": (90 / 255, 85 / 255, 82 / 255, 1),
                     "name": "ttcc_ene_derrickhand",
                     "scale": 1.15773525,
                     "dept": "c",
                     "cog": "derrickhand",
                     "suit": "a",
                     "emblem": "emblem_corp",
                     "hasHalloween": 1,
                     "headTex_HW": os.path.join(RESOURCES_DIR, "phase_12", "maps", "ttcc_ene_derrickhand_hw.png"),
                     "suitTex_HW": os.path.join(RESOURCES_DIR, "phase_12", "maps", "ttcc_ene_suittex_derrhand_hw.png"),
                     "handsHW": (151 / 255, 96 / 255, 61 / 255, 1)},

    "Firestarter": {"suitTex": os.path.join(RESOURCES_DIR, "phase_12", "maps", "ttcc_ene_suittex_fires.png"),
                    "head": os.path.join(RESOURCES_DIR, "phase_12", "models", "char", "suits",
                                         "ttcc_ene_firestarter-zero.bam"),
                    "hands": (196 / 255, 50 / 255, 14 / 255, 1),
                    "name": "ttcc_ene_firestarter",
                    "scale": 1.07372725,
                    "dept": "c",
                    "cog": "firestarter",
                    "suit": "a",
                    "emblem": "emblem_corp",
                    "hasHalloween": 1,
                    "suitTex_HW": os.path.join(RESOURCES_DIR, "phase_12", "maps", "ttcc_ene_suittex_fires_hw.png"),
                    "handsHW": (19 / 255, 19 / 255, 19 / 255, 1),
                    "headModel_HW": os.path.join(RESOURCES_DIR, "phase_12", "models", "char", "suits",
                                                 "ttcc_ene_firestarter_hw-zero.bam")},

    "Featherbedder": {"suitTex": os.path.join(RESOURCES_DIR, "phase_12", "maps", "ttcc_ene_suittex_fbed.png"),
                      "head": os.path.join(RESOURCES_DIR, "phase_12", "models", "char", "suits",
                                           "ttcc_ene_featherbedder-zero.bam"),
                      "headPos": -0.05,
                      "headPosY": 0.1,
                      "hands": (82 / 255, 54 / 255, 55 / 255, 1),
                      "name": "ttcc_ene_featherbedder",
                      "scale": 1.3279288364779874213836477987421,
                      "dept": "c",
                      "cog": "featherbedder",
                      "suit": "c",
                      "emblem": "emblem_corp",
                      "hasHalloween": 1,
                      "headTex_HW": os.path.join(RESOURCES_DIR, "phase_12", "maps", "ttcc_ene_featherbedder_hw.png"),
                      "suitTex_HW": os.path.join(RESOURCES_DIR, "phase_12", "maps", "ttcc_ene_suittex_fbed_hw.png"),
                      "handsHW": (32 / 255, 26 / 255, 39 / 255, 1)},

    "Major Player": {"suitTex": os.path.join(RESOURCES_DIR, "phase_12", "maps", "ttcc_ene_suittex_mplayer.png"),
                     "head": os.path.join(RESOURCES_DIR, "phase_12", "models", "char", "suits",
                                          "ttcc_ene_majorplayer-zero.bam"),
                     "headPos": 0.0,
                     "headPosY": -0.2,
                     "hands": (242 / 255, 242 / 255, 242 / 255, 1),
                     "name": "ttcc_ene_majorplayer",
                     "scale": 1.177281,
                     "dept": "c",
                     "cog": "majorplayer",
                     "suit": "a",
                     "emblem": "emblem_corp",
                     "hasHalloween": 1,
                     "bodyModel_HW": os.path.join(RESOURCES_DIR, "phase_3.5", "models", "char",
                                                  "suitA_mplayer_open-mod.bam"),
                     "headTex_HW": os.path.join(RESOURCES_DIR, "phase_12", "maps", "ttcc_ene_majorplayer_spooky.png"),
                     "suitTex_HW": os.path.join(RESOURCES_DIR, "phase_12", "maps",
                                                "ttcc_ene_suittex_mplayer_suit_spooky.png"),
                     "bodyTex_HW": os.path.join(RESOURCES_DIR, "phase_12", "maps",
                                                "ttcc_ene_suittex_mplayer_body_spooky.png"),
                     "handsHW": (242 / 255, 242 / 255, 242 / 255, 1)},

    "Chainsaw Consultant": {"suitTex": os.path.join(RESOURCES_DIR, "phase_12", "maps", "ttcc_ene_suittex_chainsaw.png"),
                            "head": os.path.join(RESOURCES_DIR, "phase_12", "models", "char", "suits",
                                                 "ttcc_ene_chainsaw-zero.bam"),
                            "headSize": 0.9757,
                            "hands": (75 / 255, 74 / 255, 76 / 255, 1),
                            "name": "ttcc_ene_chainsaw",
                            "scale": 1.15511,
                            "dept": "c",
                            "cog": "chainsawconsultant",
                            "suit": "a",
                            "suitToggle": "chainsaw",
                            "hasHalloween": 1,
                            "bodyModel_HW": os.path.join(RESOURCES_DIR, "phase_3.5", "models", "char",
                                                         "suitA_chainsaw_hw-mod.bam"),
                            "suitTex_HW": os.path.join(RESOURCES_DIR, "phase_12", "maps",
                                                       "ttcc_ene_suittex_chainsaw_hw.png"),
                            "handsHW": (75 / 255, 74 / 255, 76 / 255, 1),
                            "emblem": "emblem_corp"},

    # *******************   BOARDBOTS **********************************
    "Bagholder": {"suitTex": BOARDBOT_SUIT,
                  "head": os.path.join(RESOURCES_DIR, "phase_14", "models", "char", "suits",
                                       "cc_a_ene_bagholder-zero.bam"),
                  "headPos": 0.60,
                  "hands": (116 / 255, 161 / 255, 166 / 255, 1),
                  "name": "cc_a_ene_bagholder",
                  "scale": 0.96618,
                  "dept": "g",
                  "cog": "bagholder",
                  "suit": "c",
                  "suitToggle": "y",
                  "emblem": "emblem_board"},

    "Paper Hands": {"suitTex": BOARDBOT_SUIT,
                    "head": os.path.join(RESOURCES_DIR, "phase_14", "models", "char", "suits",
                                         "cc_a_ene_paperhands-zero.bam"),
                    "headSize": 0.7,
                    "headPos": -0.1,
                    "hands": (225 / 255, 231 / 255, 237 / 255, 1),
                    "name": "cc_a_ene_paperhands",
                    "scale": 0.71020934579439252336448598130841,
                    "dept": "g",
                    "cog": "paperhands",
                    "suit": "b",
                    "suitToggle": "y",
                    "emblem": "emblem_board"},

    "Insider": {"suitTex": INSIDER_SUIT,
                "head": os.path.join(RESOURCES_DIR, "phase_14", "models", "char", "suits", "cc_a_ene_insider-zero.bam"),
                "hands": (16 / 255, 17 / 255, 24 / 255, 1),
                "name": "cc_a_ene_insider",
                "scale": 0.81378154205607476635514018691589,
                "dept": "g",
                "cog": "insider",
                "suit": "bc",
                "suitToggle": "y",
                "emblem": "emblem_board"},

    "Circuit Breaker": {"suitTex": BOARDBOT_SUIT,
                        "head": os.path.join(RESOURCES_DIR, "phase_14", "models", "char", "suits",
                                             "cc_a_ene_circuitbreaker-zero.bam"),
                        "hands": (97 / 255, 107 / 255, 106 / 255, 1),
                        "name": "cc_a_ene_circuitbreaker",
                        "scale": 0.82396108352144469525959367945824,
                        "dept": "g",
                        "cog": "circuitbreaker",
                        "suit": "a",
                        "suitToggle": "y",
                        "emblem": "emblem_board"},

    "Deadlock": {"suitTex": BOARDBOT_SUIT,
                 "head": os.path.join(RESOURCES_DIR, "phase_14", "models", "char", "suits",
                                      "cc_a_ene_deadlock-zero.bam"),
                 "headPos": -0.05,
                 "hands": (104 / 255, 131 / 255, 135 / 255, 1),
                 "name": "cc_a_ene_deadlock",
                 "scale": 1.2663524271844660194174757281553,
                 "dept": "g",
                 "cog": "deadlock",
                 "suit": "c",
                 "suitToggle": "y",
                 "emblem": "emblem_board"},

    "Shark Watcher": {"suitTex": BOARDBOT_SUIT,
                      "head": os.path.join(RESOURCES_DIR, "phase_14", "models", "char", "suits",
                                           "cc_a_ene_sharkwatcher-zero.bam"),
                      "hands": (84 / 255, 123 / 255, 128 / 255, 1),
                      "name": "cc_a_ene_sharkwatcher",
                      "scale": 1.350775922330097087378640776699,
                      "dept": "g",
                      "cog": "sharkwatcher",
                      "suit": "c",
                      "suitToggle": "y",
                      "emblem": "emblem_board"},

    "Magnate": {"suitTex": BOARDBOT_SUIT,
                "head": os.path.join(RESOURCES_DIR, "phase_14", "models", "char", "suits", "cc_a_ene_magnate-zero.bam"),
                "headPos": -0.1,
                "hands": (48 / 255, 48 / 255, 48 / 255, 1),
                "name": "cc_a_ene_magnate",
                "scale": 1.1186053950338600451467268623025,
                "dept": "g",
                "cog": "magnate",
                "suit": "a",
                "suitToggle": "y",
                "emblem": "emblem_board"},

    "Head Honcho": {"suitTex": BOARDBOT_SUIT,
                    "head": os.path.join(RESOURCES_DIR, "phase_14", "models", "char", "suits",
                                         "cc_a_ene_headhoncho-zero.bam"),
                    "hands": (84 / 255, 84 / 255, 84 / 255, 1),
                    "name": "cc_a_ene_headhoncho",
                    "scale": 1.15511,
                    "dept": "g",
                    "cog": "headhoncho",
                    "suit": "a",
                    "suitToggle": "y",
                    "emblem": "emblem_board"},

    "L.A.A.": {"suitTex": BOARDBOT_EXE_SUIT,
               "head": os.path.join(RESOURCES_DIR, "phase_14", "models", "char", "suits", "ttcc_ene_dola-zero.bam"),
               "hands": (144 / 255, 129 / 255, 118 / 255, 1),
               "name": "ttcc_ene_dola",
               "scale": 1.2778919954653348405260342455557,
               "dept": "g",
               "cog": "LAA",
               "suit": "b",
               "emblem": "emblem_board",
               "hasHalloween": 1,
               "headTex_HW": os.path.join(RESOURCES_DIR, "phase_14", "maps", "ttcc_ene_dola_hw.png"),
               "suitTex_HW": os.path.join(RESOURCES_DIR, "phase_14", "maps", "ttcc_ene_suittex_dlao_hw.png"),
               "handsHW": (144 / 255, 129 / 255, 118 / 255, 1)},

    "D.O.L.D.": {"suitTex": BOARDBOT_EXE_SUIT,
                 "head": os.path.join(RESOURCES_DIR, "phase_14", "models", "char", "suits", "ttcc_ene_dold-zero.bam"),
                 "hands": (231 / 255, 94 / 255, 16 / 255, 1),
                 "name": "ttcc_ene_dold",
                 "scale": 1.2359416252821670428893905191874,
                 "dept": "g",
                 "cog": "DOLD",
                 "suit": "a",
                 "emblem": "emblem_board",
                 "hasHalloween": 1,
                 "headTex_HW": os.path.join(RESOURCES_DIR, "phase_14", "maps", "ttcc_ene_dold_hw.png"),
                 "suitTex_HW": os.path.join(RESOURCES_DIR, "phase_14", "maps", "ttcc_ene_suittex_dold_hw.png"),
                 "handsHW": (57 / 255, 19 / 255, 5 / 255, 1)},

    "Deep Diver": {"suitTex": os.path.join(RESOURCES_DIR, "phase_14", "maps", "ttcc_ene_suittex_ddiver.png"),
                   "head": os.path.join(RESOURCES_DIR, "phase_14", "models", "char", "suits",
                                        "ttcc_ene_deepdiver-zero.bam"),
                   "headPos": 0.1,
                   # "headPosY": 0.01,
                   "hands": (162 / 255, 157 / 255, 166 / 255, 1),
                   "name": "ttcc_ene_deepdiver",
                   "scale": 1.6957444897959183673469387755102,
                   "dept": "g",
                   "cog": "deepdiver",
                   "suit": "c",
                   "emblem": "emblem_board",
                   "hasHalloween": 1,
                   "headModel_HW": os.path.join(RESOURCES_DIR, "phase_14", "models", "char", "suits",
                                                "ttcc_ene_deepdiver_hw-zero.bam"),
                   "suitTex_HW": os.path.join(RESOURCES_DIR, "phase_14", "maps", "ttcc_ene_suittex_ddiver_hw.png"),
                   "handsHW": (80 / 255, 138 / 255, 85 / 255, 1)},

    "Gatekeeper": {"suitTex": os.path.join(RESOURCES_DIR, "phase_14", "maps", "ttcc_ene_suittex_gatekeep.png"),
                   "head": os.path.join(RESOURCES_DIR, "phase_14", "models", "char", "suits",
                                        "ttcc_ene_gatekeeper-zero.bam"),
                   "headPos": 0.1,
                   "hands": (88 / 255, 88 / 255, 88 / 255, 1),
                   "name": "ttcc_ene_gatekeeper",
                   "scale": 0.81874613995485327313769751693002,
                   "dept": "g",
                   "cog": "gatekeeper",
                   "suit": "a",
                   "emblem": "emblem_board",
                   "hasHalloween": 1,
                   "headTex_HW": os.path.join(RESOURCES_DIR, "phase_14", "maps", "ttcc_ene_gatekeeper_hw.png"),
                   "suitTex_HW": os.path.join(RESOURCES_DIR, "phase_14", "maps", "ttcc_ene_suittex_gatekeep_hw.png"),
                   "handsHW": (55 / 255, 77 / 255, 70 / 255, 1)},

    "Ottoman": {"suitTex": BOARDBOT_SUIT,
                "head": os.path.join(RESOURCES_DIR, "phase_14", "models", "char", "suits", "ttcc_ene_ottoman-zero.bam"),
                "headPos": -0.15,
                "hands": (54 / 255, 44 / 255, 37 / 255, 1),
                "name": "ttcc_ene_ottoman",
                "scale": 0.83278354760662270506190995777788,
                "dept": "g",
                "cog": "ottoman",
                "suit": "b",
                "emblem": "emblem_board"},

    "Chairman": {"suitTex": BOARDBOT_SUIT,
                 "head": os.path.join(RESOURCES_DIR, "phase_14", "models", "char", "suits",
                                      "ttcc_ene_chairman-zero.bam"),
                 "headPos": -0.12,
                 "hands": (84 / 255, 78 / 255, 69 / 255, 1),
                 "name": "ttcc_ene_chairman",
                 "scale": 0.58660928571428571428571428571429,
                 "dept": "g",
                 "cog": "chairman",
                 "suit": "c",
                 "emblem": "emblem_board"},

    "Desk Jockey": {"suitTex": DESK_SUIT,
                    "head": os.path.join(RESOURCES_DIR, "phase_3.5", "models", "schoolhouse", "dummy",
                                         "ttcc_ene_dummy-zero.bam"),
                    "headTex": os.path.join(RESOURCES_DIR, "phase_3.5", "maps", "schoolhouse", "dummy",
                                            "ttcc_ene_djockey.png"),
                    "hands": (242 / 255, 242 / 255, 242 / 255, 1),
                    "name": "ttcc_ene_dummy",
                    "scale": 0.96618,
                    "dept": "l",
                    "cog": "deskjockey",
                    "suit": "c",
                    "suitToggle": "dj",
                    "emblem": "emblem_corp"},

    "Goon": {"suitTex": SELLBOT_SUIT,
             "head": os.path.join(RESOURCES_DIR, "phase_9", "models", "char", "Cog_Goonie-zero.bam"),
             "name": "Cog_Goonie",
             "hands": (84 / 255, 84 / 255, 84 / 255, 1),
             "scale": 1.0000,
             "dept": "s",
             "cog": "goon",
             "suit": "a",
             "suitToggle": "y",
             "emblem": "emblem_sales"},

    "V.P.": {
        "cog_type": "boss",
        "dept": "s",
        "parts": {
            "legs": VP_LEGS_MODEL,
            "torso": VP_TORSO_MODEL,
            "head": VP_HEAD_MODEL,
            "treads": VP_TREADS_MODEL
        },
        "anims": {
            "legs": VP_LEGS_ANIM_DICT,
            "torso": VP_TORSO_ANIM_DICT,
            "head": VP_HEAD_ANIM_DICT
        },
        "texture": os.path.join(RESOURCES_DIR, "phase_9", "maps", "cc_t_ene_boss_s.png"),
        "scale": 1.0,
        "name": "VP",
        "cog": "VP",
        "suit": "boss",
        "emblem": "emblem_sales"},

    "C.F.O.": {
        "cog_type": "boss",
        "dept": "m",
        "parts": {
            "torso": VP_TORSO_MODEL,
            "head": CFO_HEAD_MODEL,
            "legs": VP_LEGS_MODEL,
            "treads": VP_TREADS_MODEL
        },
        "anims": {
            "legs": VP_LEGS_ANIM_DICT,
            "torso": VP_TORSO_ANIM_DICT,
            "head": CFO_HEAD_ANIM_DICT
        },
        "texture": os.path.join(RESOURCES_DIR, "phase_9", "maps", "cc_t_ene_boss_m.png"),
        "scale": 1.0,
        "name": "CFO",
        "cog": "CFO",
        "suit": "boss",
        "emblem": "emblem_money"
    },

    "C.L.O.": {
        "cog_type": "boss",
        "dept": "l",
        "parts": {
            "torso": CLO_BODY_MODEL,
            "head": CLO_HEAD_MODEL,
            "legs": VP_LEGS_MODEL,
            "treads": VP_TREADS_MODEL
        },
        "anims": {
            "legs": VP_LEGS_ANIM_DICT,
            "torso": VP_TORSO_ANIM_DICT,
            "head": CLO_HEAD_ANIM_DICT
        },
        # "texture": os.path.join(RESOURCES_DIR, "phase_11", "maps", "lawbotBoss.png"),
        "scale": 1.0,
        "name": "CLO",
        "cog": "CLO",
        "suit": "boss",
        "emblem": "emblem_law"
    },

    "C.E.O.": {
        "cog_type": "boss",
        "dept": "c",
        "parts": {
            "torso": VP_TORSO_MODEL,
            "head": CEO_HEAD_MODEL,
            "legs": VP_LEGS_MODEL,
            "treads": VP_TREADS_MODEL
        },
        "anims": {
            "legs": VP_LEGS_ANIM_DICT,
            "torso": VP_TORSO_ANIM_DICT,
            "head": CEO_HEAD_ANIM_DICT
        },
        "texture": os.path.join(RESOURCES_DIR, "phase_9", "maps", "cc_t_ene_boss_g.png"),
        "scale": 1.0,
        "name": "CEO",
        "cog": "CEO",
        "suit": "boss",
        "emblem": "emblem_corp"
    }

}

KEYS_LIST = list(COG_DATA.keys())


def create_hpr_sliders(update_hpr_func):
    h_slider = DirectSlider(range=(-180, 180), value=0, pos=(0.8, 0, 0.5), scale=0.5, command=update_hpr_func,
                            extraArgs=["h"])
    p_slider = DirectSlider(range=(-90, 90), value=0, pos=(0.8, 0, 0.4), scale=0.5, command=update_hpr_func,
                            extraArgs=["p"])
    r_slider = DirectSlider(range=(-180, 180), value=0, pos=(0.8, 0, 0.3), scale=0.5, command=update_hpr_func,
                            extraArgs=["r"])

    h_label = OnscreenText(text="Head H", pos=(1.2, 0.5), fg=(0, 0, 1, 1), scale=0.07)
    p_label = OnscreenText(text="Head P", pos=(1.2, 0.4), fg=(1, 0, 0, 1), scale=0.07)
    r_label = OnscreenText(text="Head R", pos=(1.2, 0.3), fg=(0, 1, 0, 1), scale=0.07)

    # Hide the sliders and labels initially
    h_slider.hide()
    p_slider.hide()
    r_slider.hide()
    h_label.hide()
    p_label.hide()
    r_label.hide()

    return (h_slider, p_slider, r_slider, h_label, p_label, r_label)


def create_prop_sliders(update_prop_hpr_func, x=1.0):
    prop_x_slider = DirectSlider(range=(-30, 30), value=0, pos=(x, 0, 0.1), scale=0.6, command=update_prop_hpr_func,
                                 extraArgs=["x"])
    prop_y_slider = DirectSlider(range=(-30, 30), value=0, pos=(x, 0, 0.0), scale=0.6, command=update_prop_hpr_func,
                                 extraArgs=["y"])
    prop_z_slider = DirectSlider(range=(-30, 30), value=0, pos=(x, 0, -0.1), scale=0.6, command=update_prop_hpr_func,
                                 extraArgs=["z"])
    prop_h_slider = DirectSlider(range=(-180, 180), value=0, pos=(x, 0, -0.2), scale=0.6, command=update_prop_hpr_func,
                                 extraArgs=["h"])
    prop_p_slider = DirectSlider(range=(-90, 90), value=0, pos=(x, 0, -0.3), scale=0.6, command=update_prop_hpr_func,
                                 extraArgs=["p"])
    prop_r_slider = DirectSlider(range=(-180, 180), value=0, pos=(x, 0, -0.4), scale=0.6, command=update_prop_hpr_func,
                                 extraArgs=["r"])
    prop_scale_slider = DirectSlider(range=(0.1, 15), value=0, pos=(x, 0, -0.5), scale=0.6,
                                     command=update_prop_hpr_func, extraArgs=["scale"])

    prop_x_label = OnscreenText(text="Prop X", pos=(x + 0.2, 0.1), fg=(1, 0, 0, 1), scale=0.07)
    prop_y_label = OnscreenText(text="Prop Y", pos=(x + 0.2, 0.0), fg=(0, 1, 0, 1), scale=0.07)
    prop_z_label = OnscreenText(text="Prop Z", pos=(x + 0.2, -0.1), fg=(0, 0, 1, 1), scale=0.07)
    prop_h_label = OnscreenText(text="Prop H", pos=(x + 0.2, -0.2), fg=(0, 0, 1, 1), scale=0.07)
    prop_p_label = OnscreenText(text="Prop P", pos=(x + 0.2, -0.3), fg=(1, 0, 0, 1), scale=0.07)
    prop_r_label = OnscreenText(text="Prop R", pos=(x + 0.2, -0.4), fg=(0, 1, 0, 1), scale=0.07)
    prop_scale_label = OnscreenText(text="Prop Scale", pos=(x + 0.2, -0.5), scale=0.07)

    # Hide the sliders and labels initially
    prop_x_slider.hide()
    prop_y_slider.hide()
    prop_z_slider.hide()
    prop_h_slider.hide()
    prop_p_slider.hide()
    prop_r_slider.hide()
    prop_scale_slider.hide()
    prop_x_label.hide()
    prop_y_label.hide()
    prop_z_label.hide()
    prop_h_label.hide()
    prop_p_label.hide()
    prop_r_label.hide()
    prop_scale_label.hide()

    return (prop_x_slider, prop_y_slider, prop_z_slider, prop_h_slider, prop_p_slider, prop_r_slider, prop_scale_slider,
            prop_x_label, prop_y_label, prop_z_label, prop_h_label, prop_p_label, prop_r_label, prop_scale_label)


# Dictionary for each department
SELLBOTS = {}
CASHBOTS = {}
LAWBOTS = {}
BOSSBOTS = {}
BOARDBOTS = {}
MISC = {}

# Dictionary used to map departments
DEPT_MAP = {
    "s": SELLBOTS,
    "m": CASHBOTS,
    "l": LAWBOTS,
    "c": BOSSBOTS,
    "g": BOARDBOTS
}

# Department mapping
for cog, cog_list in COG_DATA.items():
    cog_dept = cog_list.get("dept")
    # Throw miscellaneous cogs into their own category
    if cog_list.get("cog") in ["goon", "deskjockey"]:
        MISC[cog] = cog_list
    # Map the rest to their departments
    elif cog_list.get("dept") in DEPT_MAP:
        DEPT_MAP[cog_dept][cog] = cog_list

# Used for apply_suit_model function
DEPT_SUIT_TEX_MAP = {
    "s": SELLBOT_SUIT,
    "m": CASHBOT_SUIT,
    "l": LAWBOT_SUIT,
    "c": BOSSBOT_SUIT,
    "g": BOARDBOT_SUIT,
}
DEPT_SKELE_SUIT_TEX_MAP = {
    "s": SELLBOT_SKELE_SUIT,
    "m": CASHBOT_SKELE_SUIT,
    "l": LAWBOT_SKELE_SUIT,
    "c": BOSSBOT_SKELE_SUIT,
    "g": BOARDBOT_SKELE_SUIT,
}

EMBLEM_MAP = {
    "Sellbot": "emblem_sales",
    "Cashbot": "emblem_money",
    "Lawbot": "emblem_legal",
    "Bossbot": "emblem_corp",
    "Boardbot": "emblem_board",
    "Health Light": "light",
    "None": "none",
}

HEAD_HPR_DEFAULTS = {
    "x": 0.0,
    "y": 0.0,
    "z": 0.0,
    "h": 0.0,
    "p": 0.0,
    "r": 0.0,
    "scale": 1.0
}
