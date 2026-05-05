import os
import sys
import glob
import fnmatch
import tkinter as tk
from tkinter import ttk, filedialog, PhotoImage
from datetime import datetime
import random
import math
from panda3d.core import (AntialiasAttrib, Loader, TextNode, Mat4,
                          Filename, Texture, loadPrcFile, ClockObject,
                          ColorBlendAttrib, loadPrcFileData, TextureAttrib,
                          TextureStage, TransparencyAttrib, VirtualFileSystem,
                          Multifile, WindowProperties)
from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from direct.task import Task
from direct.interval.IntervalGlobal import Func
from tkinter.colorchooser import askcolor
from platform import system
from os.path import expanduser
from tkinter import messagebox
import json
import builtins
import subprocess
import shutil
import re
import fnmatch

try:
    from PIL import Image
except ImportError:
    print("Pillow is missing! Installing it automatically... hi im pacesetter")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image

# i view da cog
# i am definite and real
# --- Load Config and Resources ---
loadPrcFileData('', 'hardware-animated-vertices #t')
loadPrcFileData('', 'clock-mode limited')
loadPrcFileData('', 'clock-frame-rate 60')
loadPrcFileData('', 'framebuffer-multisample 1')
loadPrcFileData('', 'multisamples 4')
loadPrcFileData('', 'load-display pandagl')

resources = "../resources"
abs_resources_path = os.path.abspath(resources)

if not os.path.exists(abs_resources_path):
    os.makedirs(abs_resources_path)

PREF_FILE = "../load_preferences.prc"
load_mode = None

if os.path.exists(PREF_FILE):
    with open(PREF_FILE, "r") as f:
        load_mode = f.read().strip()
else:
    temp_root = tk.Tk()
    temp_root.withdraw()
    result = messagebox.askyesno(
        title="Hold on a minute pardner",
        message="Would you like to load models directly from the Corporate Clash phase files without extracting them?\n\n• Select 'Yes' to read directly from the game's files (Loads longer, but skips extracting process entirely.).\n• Select 'No' to use the extracted phase files inside your 'resources' directory."
    )
    load_mode = "yes" if result else "no"
    with open(PREF_FILE, "w") as f:
        f.write(load_mode)
    temp_root.destroy()

if load_mode == "yes":
    user_system = system()
    home_dir = expanduser("~")

    DEFAULT_INSTALL_PATHS = {
        "Windows": os.path.join(home_dir, "AppData", "Local", "Corporate Clash", "resources", "default"),
        # add mac ( i do not have a mac) - ferrofluid
    }
    default_path = DEFAULT_INSTALL_PATHS.get(user_system, "")

    PATH_CACHE_FILE = "../CLASH_INSTALL_PATH.txt"
    if os.path.exists(PATH_CACHE_FILE):
        with open(PATH_CACHE_FILE, "r") as f:
            phase_file_dir = f.read().strip()
    else:
        phase_file_dir = default_path

    mf_files = glob.glob(os.path.join(phase_file_dir, "phase_*_maps.mf")) + \
               glob.glob(os.path.join(phase_file_dir, "phase_*_models.mf"))

    if not mf_files:
        temp_root = tk.Tk()
        temp_root.withdraw()
        result = messagebox.askquestion(
            title="Oops",
            message=f"Failed to locate Corporate Clash phase files in:\n{phase_file_dir}\n\nWould you like to select your game folder manually?"
        )
        if result == 'yes':
            phase_file_dir = filedialog.askdirectory(title="Select Corporate Clash Install Folder")
            if phase_file_dir:
                with open(PATH_CACHE_FILE, "w") as f:
                    f.write(phase_file_dir)
                mf_files = glob.glob(os.path.join(phase_file_dir, "*.mf"))
            else:
                print("Operation cancelled. Exiting.")
                sys.exit(0)
        else:
            print("No phase directory selected. Proceeding with extracted resources folder.")
        temp_root.destroy()

    vfs = VirtualFileSystem.getGlobalPtr()
    if mf_files:
        print(f"Loading in {len(mf_files)} .mf files...")
        virtual_mount_point = Filename.fromOsSpecific(abs_resources_path)
        for mf_path in mf_files:
            panda_path = Filename.fromOsSpecific(mf_path)
            vfs.mount(panda_path, virtual_mount_point, VirtualFileSystem.MF_read_only)

    orig_exists = os.path.exists


    def vfs_exists(path):
        if orig_exists(path): return True
        return vfs.exists(Filename.fromOsSpecific(os.path.abspath(path)))


    os.path.exists = vfs_exists

    CACHE_FILENAME = "../cache.json"
    virtual_file_cache = []
    rebuild_cache = True

    if mf_files:
        latest_mf_time = max(os.path.getmtime(f) for f in mf_files)
        if os.path.exists(CACHE_FILENAME) and os.path.getsize(CACHE_FILENAME) > 0:
            try:
                with open(CACHE_FILENAME, 'r') as f:
                    virtual_file_cache = json.load(f)
                if os.path.getmtime(CACHE_FILENAME) > latest_mf_time:
                    rebuild_cache = False
            except json.JSONDecodeError:
                print("Cache file was corrupted. Forcing a rebuild...")
                rebuild_cache = True

        if rebuild_cache:
            TARGET_FOLDERS = (
            "/models/char/", "/models/props/", "/models/char/suits/", "/maps/", "/models/schoolhouse/dummy/")
            virtual_file_cache = []
            for mf_path in mf_files:
                mf = Multifile()
                if mf.openRead(Filename.fromOsSpecific(mf_path)):
                    for i in range(mf.getNumSubfiles()):
                        subfile = mf.getSubfileName(i)
                        if subfile.endswith(".bam") and any(f in subfile for f in TARGET_FOLDERS):
                            p2 = os.path.join(resources, subfile).replace('\\', '/')
                            virtual_file_cache.append((p2, p2.lower()))
            with open(CACHE_FILENAME, 'w') as f:
                json.dump(virtual_file_cache, f)

    orig_iglob = glob.iglob


    def vfs_iglob(pathname, *args, **kwargs):
        results = set()
        pattern = pathname.replace('\\', '/').lower().replace('**', '*')

        regex_pattern = re.compile(fnmatch.translate(pattern))

        for orig_path, lower_path in virtual_file_cache:
            if regex_pattern.match(lower_path):
                if '\\' in pathname:
                    results.add(orig_path.replace('/', '\\'))
                else:
                    results.add(orig_path)

        return iter(results)


    def vfs_glob(pathname, *args, **kwargs):
        return list(vfs_iglob(pathname, *args, **kwargs))


    glob.glob = vfs_glob
    glob.iglob = vfs_iglob

else:
    print("Extracted Mode Active: Skipping Virtual File System and using physical folders.")

import globals

config_path = Filename.fromOsSpecific(globals.CONFIG_DIR)
loadPrcFile(config_path)


class ToolTip:
    def __init__(self, wrapper_widget, target_widget, text):
        self.widget = wrapper_widget
        self.target_widget = target_widget
        self.text = text
        self.tipwindow = None
        self.id = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)

    def enter(self, event=None):
        if 'disabled' in self.target_widget.state():
            self.schedule()
        else:
            self.unschedule()
            self.hidetip()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(300, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x, y, cx, cy = self.widget.bbox("insert") or (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


class ControlPanel(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.master = master
        self.app = app
        self.pack(fill="both", expand=True)
        self.toggles_frame = None
        self.suit_library_frame = None
        self.head_hpr_frame = None
        self.unique_vars = {}

        # State Variables for Checkbuttons
        self.is_shadow_var = tk.BooleanVar(value=self.app.is_shadow)
        self.is_blend_var = tk.BooleanVar(value=self.app.is_blend)
        self.is_body_var = tk.BooleanVar(value=False)
        self.is_autoplay_var = tk.BooleanVar(value=self.app.is_autoplay)
        self.is_background_black_var = tk.BooleanVar(value=self.app.bool)
        self.is_costume_var = tk.BooleanVar(value=False)
        self.is_boogify_var = tk.BooleanVar(value=False)
        self.loop_body_var = tk.BooleanVar(value=True)
        self.loop_head_var = tk.BooleanVar(value=True)
        self.selected_cog_var = tk.StringVar(value=self.app.current_cog)
        self.TIE_OPTIONS = ["(Default)", "Thin Tie", "Wide Tie", "Bowtie", "None"]
        self.tie_options_hidden_var = False

        self.head_hpr_vars = {}
        self.flatten_body_vars = {}
        self.flatten_head_vars = {}
        self.prop1_vars = {}
        self.prop2_vars = {}
        self.custom_model_vars = {}
        self.custom_model_tab_frame = None
        self.prop_notebook = None
        self.bottom_notebook = None
        self.selected_tie_var = tk.StringVar(value="(Default)")

        self.prop1_anim_frame = None
        self.prop2_anim_frame = None
        self.prop1_anim_listbox = None
        self.prop2_anim_listbox = None
        self.prop1_anim_slider = None
        self.prop2_anim_slider = None
        self.prop1_loop_var = tk.BooleanVar(value=True)
        self.prop2_loop_var = tk.BooleanVar(value=True)

        self.master.title("Corporate Clash Cog Viewer Controls")
        self.master.geometry("700x900")

        top_level_notebook = ttk.Notebook(self)
        top_level_notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # --- 1. Cog Tab ---
        cog_tab_frame = ttk.Frame(top_level_notebook)
        top_level_notebook.add(cog_tab_frame, text="Cog")

        # --- 2. Prop Tab ---
        prop_tab_frame = ttk.Frame(top_level_notebook)
        top_level_notebook.add(prop_tab_frame, text="Props")

        # --- 3. environment tab ---
        env_tab_frame = ttk.Frame(top_level_notebook)
        top_level_notebook.add(env_tab_frame, text="Environment")
        self._create_environment_tab(env_tab_frame)

        # --- [POPULATE COG TAB] ---
        # This pane holds (Cog List + Tie List + Anims) AND (Toggles + HPR)
        main_paned_window = ttk.PanedWindow(cog_tab_frame, orient=tk.VERTICAL)
        main_paned_window.pack(fill="both", expand=True)

        # Top Frame: Cogs, Anims
        top_frame = ttk.Frame(main_paned_window)
        main_paned_window.add(top_frame, weight=20)

        # This pane holds the Cog/Body/Head lists side-by-side
        top_paned_window = ttk.PanedWindow(top_frame, orient=tk.HORIZONTAL)
        top_paned_window.pack(fill="both", expand=True)

        # Cog List
        cog_notebook = ttk.Notebook(top_paned_window)
        top_paned_window.add(cog_notebook, weight=1)

        COG_DEPARTMENTS = {
            "Sellbots": globals.SELLBOTS,
            "Cashbots": globals.CASHBOTS,
            "Lawbots": globals.LAWBOTS,
            "Bossbots": globals.BOSSBOTS,
            "Boardbots": globals.BOARDBOTS,
            "Misc": globals.MISC
        }
        self.DEPT_ICONS = {
            "Sellbots": PhotoImage(file="../resources/ICONS/icon_sellbot.png"),
            "Cashbots": PhotoImage(file="../resources/ICONS/icon_cashbot.png"),
            "Lawbots": PhotoImage(file="../resources/ICONS/icon_lawbot.png"),
            "Bossbots": PhotoImage(file="../resources/ICONS/icon_bossbot.png"),
            "Boardbots": PhotoImage(file="../resources/ICONS/icon_boardbot.png"),
            "Misc": PhotoImage(file="../resources/ICONS/icon_misc.png")
        }
        for dept_name, dept_data in COG_DEPARTMENTS.items():
            frame = self._create_scrollable_radio_list(cog_notebook, dept_name, dept_data, self.selected_cog_var,
                                                       self.on_cog_select_radio)
            cog_notebook.add(frame, image=self.DEPT_ICONS[dept_name], compound="none")

        # Body Anim List
        self.body_anim_frame = self._create_listbox_frame(top_paned_window, "Body Animations")
        self.body_anim_listbox = self.body_anim_frame.listbox
        self.body_anim_listbox.bind('<<ListboxSelect>>', self.on_body_anim_select)
        top_paned_window.add(self.body_anim_frame, weight=1)

        # Head Anim List
        self.head_anim_frame = self._create_listbox_frame(top_paned_window, "Head Animations")
        self.head_anim_listbox = self.head_anim_frame.listbox
        self.head_anim_listbox.bind('<<ListboxSelect>>', self.on_head_anim_select)
        top_paned_window.add(self.head_anim_frame, weight=1)

        # Bottom Frame: Sliders and Toggles
        bottom_frame = ttk.Frame(main_paned_window)
        main_paned_window.add(bottom_frame, weight=1)

        self.bottom_notebook = ttk.Notebook(bottom_frame)
        self.bottom_notebook.pack(fill="both", expand=True)

        bottom_notebook = self.bottom_notebook

        # Toggles Tab
        toggles_frame = ttk.Frame(bottom_notebook, padding=10)
        bottom_notebook.add(toggles_frame, text='Main')
        self._create_toggles(toggles_frame)

        # Animation Tab
        anim_sliders_frame = ttk.Frame(bottom_notebook, padding=10)
        bottom_notebook.add(anim_sliders_frame, text='Animation')
        self._create_anim_sliders(anim_sliders_frame)

        # Suit Library Tab
        self.suit_library_frame = ttk.Frame(bottom_notebook, padding=10)
        bottom_notebook.add(self.suit_library_frame, text='Suit Library')
        self._create_suit_library(self.suit_library_frame)

        # Head HPR Tab
        self.head_hpr_frame = ttk.Frame(bottom_notebook, padding=10)
        bottom_notebook.add(self.head_hpr_frame, text='Head HPR')
        self._create_head_hpr_sliders(self.head_hpr_frame)

        # Flatten Tab
        self.flatten_frame = ttk.Frame(bottom_notebook, padding=10)
        bottom_notebook.add(self.flatten_frame, text='Set Scale')
        self._create_flatten_sliders(self.flatten_frame)

        self.color_tab_frame = ttk.Frame(self.bottom_notebook, padding=10)
        self.bottom_notebook.add(self.color_tab_frame, text='Set Color')
        self._create_color_controls(self.color_tab_frame)

        # Accessory Tab
        self.custom_model_tab_frame = ttk.Frame(self.bottom_notebook, padding=10)
        self.bottom_notebook.add(self.custom_model_tab_frame, text='Accessory')
        self.bottom_notebook.hide(self.custom_model_tab_frame)

        prop_paned_window = ttk.PanedWindow(prop_tab_frame, orient=tk.VERTICAL)
        prop_paned_window.pack(fill="both", expand=True)

        prop_list_frame = ttk.Frame(prop_paned_window)
        prop_paned_window.add(prop_list_frame, weight=1)

        middle_paned_window = ttk.PanedWindow(prop_list_frame, orient=tk.HORIZONTAL)
        middle_paned_window.pack(fill="both", expand=True)

        (self.prop1_frame,
         self.prop1_listbox,
         self.prop1_search_entry) = self._create_searchable_listbox_frame(
            middle_paned_window, "Prop 1 (R-Hand)", "Search Prop")
        self.prop1_listbox.bind('<Double-Button-1>', self.on_prop1_select)
        self.prop1_search_entry.bind("<KeyRelease>", self.on_prop1_search)
        middle_paned_window.add(self.prop1_frame, weight=1)

        (self.prop2_frame,
         self.prop2_listbox,
         self.prop2_search_entry) = self._create_searchable_listbox_frame(
            middle_paned_window, "Prop 2 (L-Hand)", "Search Prop")
        self.prop2_listbox.bind('<Double-Button-1>', self.on_prop2_select)
        self.prop2_search_entry.bind("<KeyRelease>", self.on_prop2_search)
        middle_paned_window.add(self.prop2_frame, weight=1)

        self.update_prop_lists()

        prop_controls_frame = ttk.Frame(prop_paned_window)
        prop_paned_window.add(prop_controls_frame, weight=1)

        self.prop_notebook = ttk.Notebook(prop_controls_frame)
        self.prop_notebook.pack(fill="both", expand=True)

        prop1_hpr_frame = ttk.Frame(self.prop_notebook, padding=10)
        self.prop_notebook.add(prop1_hpr_frame, text='Prop 1 HPR')
        self._create_prop_sliders(prop1_hpr_frame, self.app.update_prop_hpr)

        prop2_hpr_frame = ttk.Frame(self.prop_notebook, padding=10)
        self.prop_notebook.add(prop2_hpr_frame, text='Prop 2 HPR')
        self._create_prop_sliders(prop2_hpr_frame, self.app.update_prop2_hpr)

        self.prop1_anim_frame = ttk.Frame(self.prop_notebook, padding=10)
        self.prop_notebook.add(self.prop1_anim_frame, text='Prop 1 Animation')

        (self.prop1_anim_listbox,
         self.prop1_anim_slider) = self._create_anim_controls(
            self.prop1_anim_frame,
            self.app.on_prop1_anim_select,
            self.app.play_prop1_animation,
            self.app.stop_prop1_animation,
            self.app.update_prop1_pose,
            self.prop1_loop_var
        )
        self.prop_notebook.hide(self.prop1_anim_frame)

        self.prop2_anim_frame = ttk.Frame(self.prop_notebook, padding=10)
        self.prop_notebook.add(self.prop2_anim_frame, text='Prop 2 Animation')

        (self.prop2_anim_listbox,
         self.prop2_anim_slider) = self._create_anim_controls(
            self.prop2_anim_frame,
            self.app.on_prop2_anim_select,
            self.app.play_prop2_animation,
            self.app.stop_prop2_animation,
            self.app.update_prop2_pose,
            self.prop2_loop_var
        )
        self.prop_notebook.hide(self.prop2_anim_frame)

        self.is_enraged_var = tk.BooleanVar(value=False)
        self.is_soaked_var = tk.BooleanVar(value=False)
        self.is_stunned_var = tk.BooleanVar(value=False)
        self.is_sued_var = tk.BooleanVar(value=False)
        self.stun_z_offset_var = tk.DoubleVar(value=0.0)
        self.is_zapped_var = tk.BooleanVar(value=False)
        self.is_insured_var = tk.BooleanVar(value=False)
        self.is_chilled_var = tk.BooleanVar(value=False)
        self.is_frozen_var = tk.BooleanVar(value=False)

        self.battle_tab = ttk.Frame(self.bottom_notebook, padding=10)
        self.bottom_notebook.add(self.battle_tab, text='Battle Effects')
        self._create_battle_effects(self.battle_tab)

        self.env_models = {}

        self.update_incompatibilities()

    def _create_environment_tab(self, master):
        btn_frame = ttk.Frame(master)
        btn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(btn_frame, text="Load Environment", command=self.prompt_load_env).pack(side=tk.LEFT, expand=True,
                                                                                          fill="x", padx=2)
        ttk.Button(btn_frame, text="Load Skybox", command=self.prompt_load_skybox).pack(side=tk.LEFT, expand=True,
                                                                                        fill="x", padx=2)
        ttk.Button(btn_frame, text="Add Prop", command=self.prompt_load_env_prop).pack(side=tk.LEFT, expand=True,
                                                                                       fill="x", padx=2)

        paned = ttk.PanedWindow(master, orient=tk.HORIZONTAL)
        paned.pack(fill="both", expand=True, padx=10, pady=5)

        models_frame = ttk.Labelframe(paned, text="Loaded Models")
        paned.add(models_frame, weight=1)

        models_scroll = ttk.Scrollbar(models_frame, orient=tk.VERTICAL)
        self.env_models_listbox = tk.Listbox(models_frame, yscrollcommand=models_scroll.set, exportselection=False)
        models_scroll.config(command=self.env_models_listbox.yview)
        models_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.env_models_listbox.pack(side=tk.LEFT, fill="both", expand=True)
        self.env_models_listbox.bind('<<ListboxSelect>>', self.on_env_model_select)
        self.env_models_listbox.bind('<Button-3>', self.on_env_model_right_click)

        nodes_frame = ttk.Labelframe(paned, text="Model Nodes (GeomNodes)")
        paned.add(nodes_frame, weight=1)

        nodes_scroll = ttk.Scrollbar(nodes_frame, orient=tk.VERTICAL)
        self.env_nodes_listbox = tk.Listbox(nodes_frame, yscrollcommand=nodes_scroll.set, exportselection=False)
        nodes_scroll.config(command=self.env_nodes_listbox.yview)
        nodes_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.env_nodes_listbox.pack(side=tk.LEFT, fill="both", expand=True)

        self.env_nodes_listbox.bind('<<ListboxSelect>>', self.on_env_node_select)
        self.env_nodes_listbox.bind('<Button-3>', self.on_env_node_right_click)

        btn_action_frame = ttk.Frame(master)
        btn_action_frame.pack(fill="x", padx=10, pady=2)
        ttk.Button(btn_action_frame, text="Delete Selected Item", command=self.delete_selected_env_item).pack(
            side=tk.LEFT, fill="x", expand=True, padx=2)
        ttk.Button(btn_action_frame, text="Reset Selected Color", command=self.reset_selected_env_color).pack(
            side=tk.LEFT, fill="x", expand=True, padx=2)

        transform_frame = ttk.Labelframe(master, text="Transform Selection")
        transform_frame.pack(fill="x", padx=10, pady=5)

        self.env_transform_vars = {}
        slider_defs = [
            ("Left/Right", "x", -200, 200, 0.0),
            ("Front/Back", "y", -200, 200, 0.0),
            ("Up/Down", "z", -50, 50, 0.0),
            ("Heading", "h", -360, 360, 0.0),
            ("Pitch", "p", -180, 180, 0.0),
            ("Roll", "r", -360, 360, 0.0),
            ("Scale", "scale", 0.01, 20, 1.0)
        ]

        for label, axis, min_val, max_val, default_val in slider_defs:
            var = tk.DoubleVar(value=default_val)
            self.env_transform_vars[axis] = var

            row = ttk.Frame(transform_frame)
            row.pack(fill="x", expand=True, pady=2)

            ttk.Label(row, text=label, width=10, anchor="w").pack(side=tk.LEFT, padx=(0, 5))
            scale = ttk.Scale(row, from_=min_val, to=max_val, orient=tk.HORIZONTAL, variable=var)
            scale.pack(side=tk.LEFT, fill="x", expand=True, padx=5)
            entry = ttk.Entry(row, textvariable=var, width=7)
            entry.pack(side=tk.LEFT, padx=5)
            ttk.Button(row, text="Reset", width=6, command=lambda v=var, d=default_val: v.set(d)).pack(side=tk.LEFT)

            var.trace_add("write", self._create_env_transform_callback(var, axis))

    def prompt_load_env(self):
        filepath = filedialog.askopenfilename(
            title="Select Environment Model",
            filetypes=[("Panda3D Models", "*.bam *.egg *.egg.pz *.bam.pz")]
        )
        if filepath:
            panda_path = Filename.fromOsSpecific(filepath).getFullpath()
            self.app.load_environment(panda_path)

    def prompt_load_skybox(self):
        filepath = filedialog.askopenfilename(
            title="Select Skybox Model",
            filetypes=[("Panda3D Models", "*.bam *.egg *.egg.pz *.bam.pz")]
        )
        if filepath:
            panda_path = Filename.fromOsSpecific(filepath).getFullpath()
            self.app.load_skybox(panda_path)

    def prompt_load_env_prop(self):
        filepath = filedialog.askopenfilename(
            title="Select Environment Prop",
            filetypes=[("Panda3D Models", "*.bam *.egg *.egg.pz *.bam.pz")]
        )
        if filepath:
            panda_path = Filename.fromOsSpecific(filepath).getFullpath()
            self.app.load_env_prop(panda_path)

    def update_env_model_list(self):
        self.env_models_listbox.delete(0, tk.END)
        self.env_nodes_listbox.delete(0, tk.END)
        for model_key in getattr(self.app, 'env_models', {}).keys():
            self.env_models_listbox.insert(tk.END, model_key)

    def _refresh_env_sliders(self, model_key, node_name=None):
        transform = self.app.get_env_transform(model_key, node_name)
        if not transform:
            return

        self._is_updating_env_sliders = True

        for axis, var in self.env_transform_vars.items():
            if axis in transform:
                var.set(transform[axis])

        self._is_updating_env_sliders = False

    def on_env_model_select(self, event):
        self.env_nodes_listbox.selection_clear(0, tk.END)

        model_key = self._get_selected_from_listbox(event)
        if not model_key: return

        nodes = self.app.get_model_subnodes(model_key)
        self.env_nodes_listbox.delete(0, tk.END)
        for node in nodes:
            self.env_nodes_listbox.insert(tk.END, node)

        self._refresh_env_sliders(model_key, None)

    def on_env_node_select(self, event):
        model_sel = self.env_models_listbox.curselection()
        if not model_sel: return
        model_key = self.env_models_listbox.get(model_sel[0])

        node_name = self._get_selected_from_listbox(event)
        if not node_name: return

        self._refresh_env_sliders(model_key, node_name)

    def _create_env_transform_callback(self, var, axis):
        def trace_callback(*args):
            if getattr(self, '_is_updating_env_sliders', False):
                return

            try:
                model_sel = self.env_models_listbox.curselection()
                if not model_sel: return
                model_key = self.env_models_listbox.get(model_sel[0])

                node_name = None
                node_sel = self.env_nodes_listbox.curselection()
                if node_sel:
                    node_name = self.env_nodes_listbox.get(node_sel[0])

                self.app.update_env_transform(model_key, node_name, axis, var.get())
            except tk.TclError:
                pass

        return trace_callback

    def delete_selected_env_item(self):
        model_sel = self.env_models_listbox.curselection()
        if not model_sel: return
        model_key = self.env_models_listbox.get(model_sel[0])

        node_sel = self.env_nodes_listbox.curselection()
        if node_sel:
            node_name = self.env_nodes_listbox.get(node_sel[0])
            self.app.delete_env_item(model_key, node_name)
            self.env_nodes_listbox.delete(node_sel[0])
        else:
            self.app.delete_env_item(model_key)
            self.env_models_listbox.delete(model_sel[0])
            self.env_nodes_listbox.delete(0, tk.END)

    def on_env_model_right_click(self, event):
        if self.env_models_listbox.size() == 0: return

        index = self.env_models_listbox.nearest(event.y)
        self.env_models_listbox.selection_clear(0, tk.END)
        self.env_models_listbox.selection_set(index)
        self.env_models_listbox.activate(index)

        self.on_env_model_select(event)

        model_key = self.env_models_listbox.get(index)
        color = askcolor(title=f"Colorize {model_key}")[1]

        if color:
            self.app.apply_env_color(model_key, None, color)

    def on_env_node_right_click(self, event):
        if self.env_nodes_listbox.size() == 0: return

        index = self.env_nodes_listbox.nearest(event.y)
        self.env_nodes_listbox.selection_clear(0, tk.END)
        self.env_nodes_listbox.selection_set(index)
        self.env_nodes_listbox.activate(index)

        self.on_env_node_select(event)

        model_sel = self.env_models_listbox.curselection()
        if not model_sel: return
        model_key = self.env_models_listbox.get(model_sel[0])

        node_name = self.env_nodes_listbox.get(index)
        color = askcolor(title=f"Colorize {node_name}")[1]

        if color:
            self.app.apply_env_color(model_key, node_name, color)

    def reset_selected_env_color(self):
        model_sel = self.env_models_listbox.curselection()
        if not model_sel: return
        model_key = self.env_models_listbox.get(model_sel[0])

        node_sel = self.env_nodes_listbox.curselection()
        if node_sel:
            node_name = self.env_nodes_listbox.get(node_sel[0])
            self.app.reset_env_color(model_key, node_name)
        else:
            self.app.reset_env_color(model_key)

    def _create_battle_effects(self, master):

        ttk.Button(master, text="Add Pie Splat",
                   command=self.app.add_pie_splat).pack(fill="x", pady=2)
        ttk.Button(master, text="Clear Pie Splats",
                   command=self.app.clear_pie_splats).pack(fill="x", pady=2)

        ttk.Checkbutton(master, text="Enraged Fire",
                        variable=self.is_enraged_var,
                        command=lambda: self.app.toggle_enrage_fire(self.is_enraged_var.get())).pack(anchor="w", pady=2)

        ttk.Checkbutton(master, text="Soaked",
                        variable=self.is_soaked_var,
                        command=lambda: self.app.toggle_soaked(self.is_soaked_var.get())).pack(anchor="w", pady=2)

        ttk.Checkbutton(master, text="Stunned",
                        variable=self.is_stunned_var,
                        command=lambda: self.app.toggle_stunned(self.is_stunned_var.get())).pack(anchor="w", pady=2)

        ttk.Checkbutton(master, text="Sued",
                        variable=self.is_sued_var,
                        command=lambda: self.app.toggle_sued(self.is_sued_var.get())).pack(anchor="w", pady=2)

        zap_wrapper = ttk.Frame(master)
        zap_wrapper.pack(fill="x", pady=2)
        self.zapped_cb = ttk.Checkbutton(zap_wrapper, text="Zapped",
                                         variable=self.is_zapped_var,
                                         command=lambda: [self.app.toggle_zapped(self.is_zapped_var.get()),
                                                          self.update_incompatibilities()])
        self.zapped_cb.pack(anchor="w")
        ToolTip(zap_wrapper, self.zapped_cb, "Incompatible with Skelecogs.")

        ttk.Checkbutton(master, text="Insured",
                        variable=self.is_insured_var,
                        command=lambda: self.app.toggle_insured(self.is_insured_var.get())).pack(anchor="w", pady=2)

        ttk.Checkbutton(master, text="Chilled",
                        variable=self.is_chilled_var,
                        command=lambda: self.app.toggle_chilled(self.is_chilled_var.get())).pack(anchor="w", pady=2)

        ttk.Checkbutton(master, text="Frozen",
                        variable=self.is_frozen_var,
                        command=lambda: self.app.toggle_frozen(self.is_frozen_var.get())).pack(anchor="w", pady=2)

        ttk.Separator(master, orient=tk.HORIZONTAL).pack(fill='x', pady=5)
        ttk.Label(master, text="Stun/Sued Height Offset").pack(anchor="w")

        slider_frame = ttk.Frame(master)
        slider_frame.pack(fill="x", expand=True, pady=2)

        stun_slider = ttk.Scale(slider_frame, from_=-3.0, to=5.0, orient=tk.HORIZONTAL, variable=self.stun_z_offset_var)
        stun_slider.pack(side=tk.LEFT, fill="x", expand=True, padx=5)

        ttk.Entry(slider_frame, textvariable=self.stun_z_offset_var, width=5).pack(side=tk.LEFT)

        ttk.Button(slider_frame, text="Reset", width=6,
                   command=lambda: self.stun_z_offset_var.set(0.0)).pack(side=tk.LEFT, padx=5)

        self.stun_z_offset_var.trace_add("write", lambda *args: self.app.update_stun_position())

    def _create_listbox_frame(self, master, label_text):
        frame = ttk.Labelframe(master, text=label_text)
        frame.pack(fill="both", expand=True, padx=2, pady=2)

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, exportselection=False)

        scrollbar.config(command=listbox.yview)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.pack(side=tk.LEFT, fill="both", expand=True)

        frame.listbox = listbox
        return frame

    def _create_searchable_listbox_frame(self, master, label_text, placeholder_text="Search..."):
        frame = ttk.Labelframe(master, text=label_text)
        frame.pack(fill="both", expand=True, padx=2, pady=2)

        search_entry = ttk.Entry(frame)
        search_entry.pack(fill="x", padx=5, pady=(5, 2))

        search_entry.insert(0, placeholder_text)
        search_entry.config(foreground='grey')
        search_entry.bind("<FocusIn>",
                          lambda e: self._on_entry_focus_in(search_entry, placeholder_text))
        search_entry.bind("<FocusOut>",
                          lambda e: self._on_entry_focus_out(search_entry, placeholder_text))

        list_container = ttk.Frame(frame)
        list_container.pack(fill="both", expand=True, padx=5, pady=(2, 5))

        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL)
        listbox = tk.Listbox(list_container, yscrollcommand=scrollbar.set, exportselection=False)

        scrollbar.config(command=listbox.yview)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.pack(side=tk.LEFT, fill="both", expand=True)

        return frame, listbox, search_entry

    # SETTING UP TOGGLES
    def _create_toggles(self, master):
        frame = ttk.Frame(master)
        self.toggles_frame = frame
        frame.pack(fill="x", expand=True)

        frame.columnconfigure(0, weight=1)  # Column 1
        frame.columnconfigure(1, weight=1)  # Column 2
        frame.columnconfigure(2, weight=1)  # Column 3
        frame.grid_rowconfigure(6, weight=10000)  # Fixes the buttons next to suit toggles stretching out

        # MAIN TAB COLUMN 1
        suit_frame = ttk.Labelframe(frame, text="Toggles")
        suit_frame.grid(row=0, column=0, rowspan=6, sticky="nsew", padx=5, pady=0)

        # Autoplay Animation Toggle
        ttk.Checkbutton(suit_frame, text="Autoplay Animations", variable=self.is_autoplay_var,
                        command=self.app.autoplay_animations).pack(anchor="w", padx=5)
        # Cog Shadow Toggle
        ttk.Checkbutton(suit_frame, text="Toggle Shadow", variable=self.is_shadow_var,
                        command=self.app.toggle_shadow).pack(anchor="w", padx=5)
        # Cog Body Toggle
        self.body_toggle_btn = ttk.Checkbutton(suit_frame, text="Toggle Body", variable=self.is_body_var,
                                               command=self.app.toggle_body)
        self.body_toggle_btn.pack(anchor="w", padx=5)

        # Standard Toggles
        self.is_executive_var = tk.BooleanVar(value=False)
        self.is_fired_var = tk.BooleanVar(value=False)
        self.is_waiter_var = tk.BooleanVar(value=False)
        self.is_skelecog_var = tk.BooleanVar(value=False)

        self.suit_exec_check = ttk.Checkbutton(suit_frame, text="Make Executive",
                                               variable=self.is_executive_var,
                                               command=lambda: self.app.set_suit_texture("exec"))
        self.suit_exec_check.pack(anchor="w", padx=5)

        self.suit_fired_check = ttk.Checkbutton(suit_frame, text="Make Fired",
                                                variable=self.is_fired_var,
                                                command=lambda: self.app.set_suit_texture("fired"))
        self.suit_fired_check.pack(anchor="w", padx=5)

        self.suit_waiter_check = ttk.Checkbutton(suit_frame, text="Make Waiter",
                                                 variable=self.is_waiter_var,
                                                 command=lambda: self.app.set_suit_texture("waiter"))
        self.suit_waiter_check.pack(anchor="w", padx=5)

        self.skel_wrapper = ttk.Frame(suit_frame)
        self.skel_wrapper.pack(fill="x", pady=0)
        self.skelecog_cb = ttk.Checkbutton(self.skel_wrapper, text="Make Skelecog",
                                           variable=self.is_skelecog_var,
                                           command=lambda: [self.app.toggle_skelecog(self.is_skelecog_var.get()),
                                                            self.update_incompatibilities()])
        self.skelecog_cb.pack(anchor="w", padx=5)
        ToolTip(self.skel_wrapper, self.skelecog_cb, "Incompatible with Zapped.")

        self.suit_costume_check = ttk.Checkbutton(suit_frame, text="Toggle Costume",
                                                  variable=self.is_costume_var,
                                                  command=lambda: self.app.toggle_costume(self.is_costume_var.get()))

        self.suit_is_boogie = ttk.Checkbutton(suit_frame, text="boogie",
                                              variable=self.is_boogify_var,
                                              command=lambda: self.app.toggle_boogie(self.is_boogify_var.get()))

        # UNIQUE TOGGLES START
        self.unique_frame = ttk.Labelframe(frame, text="Unique Toggles")
        self.unique_frame.grid(row=6, column=0, columnspan=3, rowspan=3, sticky="nsew", padx=5, pady=0)
        self.unique_frame.grid_remove()

        self.unique_canvas = tk.Canvas(self.unique_frame, highlightthickness=0, height=120)
        self.unique_scrollbar = ttk.Scrollbar(self.unique_frame, orient="vertical", command=self.unique_canvas.yview)

        self.unique_canvas.pack(side="left", fill="both", expand=True)
        self.unique_scrollbar.pack(side="right", fill="y")

        self.unique_inner_frame = ttk.Frame(self.unique_canvas)
        self.unique_canvas_window = self.unique_canvas.create_window((0, 0), window=self.unique_inner_frame,
                                                                     anchor="nw")

        self.unique_canvas.configure(yscrollcommand=self.unique_scrollbar.set)

        self.unique_inner_frame.bind("<Configure>", lambda e: self.unique_canvas.configure(
            scrollregion=self.unique_canvas.bbox("all")))
        self.unique_canvas.bind("<Configure>",
                                lambda e: self.unique_canvas.itemconfig(self.unique_canvas_window, width=e.width))

        def _on_mousewheel(event):
            self.unique_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.unique_canvas.bind("<Enter>", lambda e: self.unique_canvas.bind_all("<MouseWheel>", _on_mousewheel))
        self.unique_canvas.bind("<Leave>", lambda e: self.unique_canvas.unbind_all("<MouseWheel>"))

        self.unique_config = {
            "ms": [  # Multislacker
                {"type": "check", "label": "TV Static", "var": "ms_toggle_1", "command": self.app.multislacker_toggles},
                {"type": "check", "label": "Static Interval", "var": "ms_toggle_2",
                 "command": self.app.multislacker_toggles}
            ],
            "chainsaw": [  # Chainsaw Consultant
                {"type": "check", "label": "Override", "var": "cs_toggle_1",
                 "command": lambda: self.app.chainsaw_consultant_toggles(1)},
                {"type": "check", "label": "Break Left Bulb", "var": "cs_toggle_2",
                 "command": lambda: self.app.chainsaw_consultant_toggles(2)},
                {"type": "check", "label": "Break Right Bulb", "var": "cs_toggle_3",
                 "command": lambda: self.app.chainsaw_consultant_toggles(3)},
            ],
            "hr": [  # High Roller
                {"type": "check", "label": "Prodigal Suit (Black)", "var": "hr_toggle_1",
                 "command": self.app.high_roller_toggles}
            ],
            "dj": [  # Desk Jockey
                {"type": "check", "label": "Brianbot", "var": "dj_toggle_1", "command": self.app.desk_jockey_toggles},
                {"type": "check", "label": "Executive", "var": "dj_toggle_2", "command": self.app.desk_jockey_toggles}
            ],
            "rm": [  # Rainmaker
                {"type": "combo", "label": "Weather Phase", "var": "rm_weather",
                 "options": ["Inversion", "Heavy Rain", "Oil Rain", "Storm Cell", "Fog"],
                 "command": self.app.update_rainmaker}
            ],
            "ds3": [  # Duck Shuffler
                {"type": "combo", "label": "Left Slot", "var": "ds_slot_l", "options": ["7", "Duck", "Bar", "Cherry"],
                 "command": self.app.update_slots},
                {"type": "combo", "label": "Middle Slot", "var": "ds_slot_m", "options": ["7", "Duck", "Bar", "Cherry"],
                 "command": self.app.update_slots},
                {"type": "combo", "label": "Right Slot", "var": "ds_slot_r", "options": ["7", "Duck", "Bar", "Cherry"],
                 "command": self.app.update_slots},
                {"type": "check", "label": "Spin Slots", "var": "ds_spin", "command": self.app.toggle_spin_slots}
            ],
            "default": []
        }

        # camera fov slider
        self.fov_default = 40
        self.app.camLens.setFov(self.fov_default)
        self.fov_var = tk.DoubleVar(value=self.fov_default)

        fov_frame = ttk.Frame(frame)
        fov_frame.grid(row=9, column=0, columnspan=3, sticky="ew", padx=5, pady=(10, 5))
        fov_frame.columnconfigure(1, weight=1)

        # Label
        ttk.Label(fov_frame, text="FOV", width=12, anchor="w").grid(row=0, column=0, padx=(0, 5))

        # Slider
        self.fov_slider = ttk.Scale(fov_frame, from_=10, to=150, orient="horizontal", variable=self.fov_var)
        self.fov_slider.grid(row=0, column=1, sticky="ew", padx=5)

        # Entry
        self.fov_entry = ttk.Entry(fov_frame, textvariable=self.fov_var, width=7)
        self.fov_entry.grid(row=0, column=2, padx=5)

        # Reset button
        self.fov_reset_btn = ttk.Button(fov_frame, text="Reset", width=6, command=self.reset_fov
                                        )
        self.fov_reset_btn.grid(row=0, column=3, padx=(5, 0))

        self.fov_var.trace_add("write", self.update_fov)

        # rotation slider
        self.rotation_var = tk.DoubleVar(value=180.0)

        rot_frame = ttk.Frame(frame)
        rot_frame.grid(row=10, column=0, columnspan=3, sticky="ew", padx=5, pady=(0, 10))
        rot_frame.columnconfigure(1, weight=1)

        ttk.Label(rot_frame, text="Rotation", width=12, anchor="w").grid(row=0, column=0, padx=(0, 5))

        self.rot_slider = ttk.Scale(rot_frame, from_=-180, to=180, orient="horizontal", variable=self.rotation_var)
        self.rot_slider.grid(row=0, column=1, sticky="ew", padx=5)

        self.rot_entry = ttk.Entry(rot_frame, textvariable=self.rotation_var, width=7)
        self.rot_entry.grid(row=0, column=2, padx=5)

        self.rot_reset_btn = ttk.Button(rot_frame, text="Reset", width=6, command=self.reset_rotation)
        self.rot_reset_btn.grid(row=0, column=3, padx=(5, 0))

        self.rotation_var.trace_add("write", self.update_rotation)

        # Hide all suit toggles by default
        self.suit_exec_check.pack_forget()
        self.suit_fired_check.pack_forget()
        # self.unique_suit_button.pack_forget()
        self.suit_waiter_check.pack_forget()
        self.skel_wrapper.pack_forget()

        # MAIN TAB COLUMN 2
        ttk.Button(frame, text="Toggle Virtualize",
                   command=self.app.toggle_virtualize).grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        ttk.Button(frame, text="Upload Accessory",
                   command=self.app.upload_custom_model).grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        ttk.Button(frame, text="Upload Suit Texture",
                   command=self.app.upload_suit_texture).grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        ttk.Button(frame, text="Upload Head Texture",
                   command=self.app.upload_head_texture).grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        ttk.Button(frame, text="Upload Head Part Texture",
                   command=self.app.upload_additional_head_texture).grid(row=4, column=1, sticky="ew", padx=5, pady=2)

        # MAIN TAB COLUMN 3
        ttk.Button(frame, text="Cycle Health Meter",
                   command=self.app.toggle_skele_meter_color).grid(row=0, column=2, sticky="ew", padx=5, pady=2)
        ttk.Button(frame, text="Reset Camera",
                   command=self.app.reset_camera_pos).grid(row=1, column=2, sticky="ew", padx=5, pady=2)
        ttk.Button(frame, text="Reset Camera Roll",
                   command=self.app.reset_camera_roll).grid(row=2, column=2, sticky="ew", padx=5, pady=2)
        ttk.Button(frame, text="Take Screenshot",
                   command=self.app.take_screenshot).grid(row=3, column=2, sticky="ew", padx=5, pady=2)
        ttk.Button(frame, text="Make GIF",
                   command=self.app.make_gif).grid(row=5, column=2, sticky="ew", padx=5, pady=2)
        ttk.Button(frame, text="Render Frames",
                   command=self.app.take_screenshot_frames).grid(row=4, column=2, sticky="ew", padx=5, pady=2)
        ttk.Button(frame, text="Random Render Button",
                   command=self.app.generate_random_cog_screenshot).grid(row=5, column=1, sticky="ew", padx=5, pady=2)

    # Populate the unique frame
    def fill_unique_frame(self, cog_type):
        for widget in self.unique_inner_frame.winfo_children():
            widget.destroy()

        config = self.unique_config.get(cog_type, self.unique_config["default"])

        for item in config:
            if item["type"] == "check":
                var = tk.BooleanVar(value=False)
                self.unique_vars[item["var"]] = var

                cb = ttk.Checkbutton(
                    self.unique_inner_frame,
                    text=item["label"],
                    variable=var,
                    command=item["command"]
                )
                cb.pack(anchor="w", padx=5, pady=2)

            elif item["type"] == "button":
                btn = ttk.Button(
                    self.unique_inner_frame,
                    text=item["label"],
                    command=item["command"]
                )
                btn.pack(anchor="w", fill="x", padx=5, pady=2)

            elif item["type"] == "combo":
                var = tk.StringVar(value=item["options"][0])
                self.unique_vars[item["var"]] = var

                frame = ttk.Frame(self.unique_inner_frame)
                frame.pack(anchor="w", fill="x", padx=5, pady=2)
                ttk.Label(frame, text=item["label"]).pack(side="left")

                cb = ttk.Combobox(frame, textvariable=var, values=item["options"], state="readonly", width=10)
                cb.pack(side="right")
                cb.bind("<<ComboboxSelected>>", lambda e, cmd=item["command"]: cmd())

    # Update camera FOV
    def update_fov(self, *args):
        try:
            fov = float(self.fov_var.get())
            self.app.camLens.setFov(fov)
        except (tk.TclError, ValueError):
            pass

    def reset_fov(self):
        self.fov_var.set(self.fov_default)

    def update_rotation(self, *args):
        try:
            rot = float(self.rotation_var.get())
            if self.app.actor and not self.app.actor.isEmpty():
                self.app.actor.setH(rot)
        except (tk.TclError, ValueError):
            pass

    def reset_rotation(self):
        self.app.reset_actor_pos()

    def _create_anim_controls(self, master, list_select_cmd, play_cmd, stop_cmd, slider_cmd, loop_var):
        # Anim List
        list_frame = ttk.Labelframe(master, text="Animations")
        list_frame.pack(fill="x", expand=True, padx=5, pady=5)

        list_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        anim_listbox = tk.Listbox(list_frame, yscrollcommand=list_scrollbar.set, exportselection=False, height=5)
        list_scrollbar.config(command=anim_listbox.yview)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        anim_listbox.pack(side=tk.LEFT, fill="both", expand=True)
        anim_listbox.bind('<<ListboxSelect>>', list_select_cmd)

        # Slider and Controls
        slider_frame = ttk.Labelframe(master, text="Controls")
        slider_frame.pack(fill="x", expand=True, padx=5, pady=5)

        ttk.Label(slider_frame, text="Animation Frame").pack(fill="x", expand=True)

        anim_slider = ttk.Scale(slider_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                command=slider_cmd, length=300, name="anim_slider")
        anim_slider.set(0)
        anim_slider.pack(fill="x", expand=True, pady=(0, 10))

        button_frame = ttk.Frame(slider_frame)
        button_frame.pack(fill="x", expand=True)

        ttk.Button(button_frame, text="Play", command=play_cmd).pack(side=tk.LEFT, fill="x", expand=True, padx=2)
        ttk.Button(button_frame, text="Stop", command=stop_cmd).pack(side=tk.LEFT, fill="x", expand=True, padx=2)
        ttk.Checkbutton(button_frame, text="Loop", variable=loop_var).pack(side=tk.LEFT, fill="x", expand=True, padx=5)

        return anim_listbox, anim_slider

    def _create_anim_controls_only(self, master, slider_cmd, play_cmd, stop_cmd, loop_var):
        # Slider and Controls
        slider_frame = ttk.Labelframe(master, text="Controls")
        slider_frame.pack(fill="x", expand=True, padx=5, pady=5)

        ttk.Label(slider_frame, text="Animation Frame").pack(fill="x", expand=True)

        anim_slider = ttk.Scale(slider_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                command=slider_cmd, length=300, name="anim_slider")
        anim_slider.set(0)
        anim_slider.pack(fill="x", expand=True, pady=(0, 10))

        button_frame = ttk.Frame(slider_frame)
        button_frame.pack(fill="x", expand=True)

        ttk.Button(button_frame, text="Play", command=play_cmd).pack(side=tk.LEFT, fill="x", expand=True, padx=2)
        ttk.Button(button_frame, text="Stop", command=stop_cmd).pack(side=tk.LEFT, fill="x", expand=True, padx=2)
        ttk.Checkbutton(button_frame, text="Loop", variable=loop_var).pack(side=tk.LEFT, fill="x", expand=True, padx=5)

        return anim_slider

    def _create_anim_sliders(self, master):
        # Body
        body_frame = ttk.Labelframe(master, text="Body Animation")
        body_frame.pack(fill="x", expand=True, padx=5, pady=5)

        self.body_frame_slider = self._create_anim_controls_only(
            body_frame,
            self.app.update_body_pose,
            self.app.play_body_animation,
            self.app.stop_body_animation,
            self.loop_body_var
        )

        # Head
        head_frame = ttk.Labelframe(master, text="Head Animation")
        head_frame.pack(fill="x", expand=True, padx=5, pady=5)

        self.head_frame_slider = self._create_anim_controls_only(
            head_frame,
            self.app.update_head_pose,
            self.app.play_head_animation,
            self.app.stop_head_animation,
            self.loop_head_var
        )

    def _create_flatten_sliders(self, master):
        default_body = self.app.cog_data.get("scale", 1.0)
        flatten_slider_body_defs = [
            ("Profile (Sx)", "Sx", 0.01, 15, default_body),
            ("Portrait (Sy)", "Sy", 0.01, 15, default_body),
            ("Height (Sz)", "Sz", 0.01, 15, default_body),
        ]
        default_head = self.app.cog_data.get("headSize", 1.0)
        flatten_slider_head_defs = [
            ("Profile (Sx)", "Sx", 0.01, 15, default_head),
            ("Portrait (Sy)", "Sy", 0.01, 15, default_head),
            ("Height (Sz)", "Sz", 0.01, 15, default_head),
        ]

        # Body
        body_frame = ttk.Labelframe(master, text="Cog Scale")
        body_frame.pack(fill="x", expand=True, padx=5, pady=0)

        for label, axis, min_val, max_val, default_val in flatten_slider_body_defs:
            var = tk.DoubleVar(value=default_val)
            self.flatten_body_vars[axis] = var
            # Row frame
            row = ttk.Frame(body_frame)
            row.pack(fill="x", expand=True, pady=2)
            # Label
            ttk.Label(row, text=label, width=11, anchor="w").pack(side=tk.LEFT)
            # Slider
            scale = ttk.Scale(row, from_=min_val, to=max_val, orient=tk.HORIZONTAL, variable=var)
            scale.pack(side=tk.LEFT, fill="x", expand=True, padx=5)
            # Text Entry
            entry = ttk.Entry(row, textvariable=var, width=7)
            entry.pack(side=tk.LEFT, padx=5)
            # Reset Buttons
            reset_btn = ttk.Button(row, text="Reset", width=6,
                                   command=lambda axis=axis, v=var: self.reset_flat_body_axis(axis, v))
            reset_btn.pack(side=tk.LEFT)
            var.trace_add("write", self._create_flatten_trace_callback(var, axis))

        # Head
        head_frame = ttk.Labelframe(master, text="Head Scale")
        head_frame.pack(fill="x", expand=True, padx=5, pady=0)

        for label, axis, min_val, max_val, default_val in flatten_slider_head_defs:
            var = tk.DoubleVar(value=default_val)
            self.flatten_head_vars[axis] = var
            # Row frame
            row = ttk.Frame(head_frame)
            row.pack(fill="x", expand=True, pady=2)
            # Label
            ttk.Label(row, text=label, width=11, anchor="w").pack(side=tk.LEFT)
            # Slider
            slider = ttk.Scale(row, from_=min_val, to=max_val,
                               orient=tk.HORIZONTAL, variable=var)
            slider.pack(side=tk.LEFT, fill="x", expand=True, padx=5)
            # Text Entry
            entry = ttk.Entry(row, textvariable=var, width=7)
            entry.pack(side=tk.LEFT, padx=5)
            # Reset Buttons
            reset_btn = ttk.Button(row, text="Reset", width=6,
                                   command=lambda axis=axis: self.reset_flat_head_axis(axis))
            reset_btn.pack(side=tk.LEFT)
            var.trace_add("write", self._create_flatten_head_trace_callback(var, axis))

        # Reset all scale
        ttk.Separator(master, orient=tk.HORIZONTAL).pack(fill="x", pady=5)
        reset_all_btn = ttk.Button(master, text="Reset All Controls", command=self.reset_flatten)
        reset_all_btn.pack(fill="x", expand=True)

    def _create_color_controls(self, master):  # i color the cog
        entry_frame = ttk.Frame(master)
        entry_frame.pack(fill='x', pady=5)

        ttk.Label(entry_frame, text="Hex (#RRGGBB):").pack(side=tk.LEFT, padx=(0, 5))

        self.hex_color_var = tk.StringVar(value="#FFFFFF")
        self.hex_entry = ttk.Entry(entry_frame, textvariable=self.hex_color_var, width=10)
        self.hex_entry.pack(side=tk.LEFT, padx=5)

        def open_picker():
            color = askcolor(color=self.hex_color_var.get())[1]
            if color:
                self.hex_color_var.set(color)

        picker_btn = ttk.Button(entry_frame, text="Picker", width=6, command=open_picker)
        picker_btn.pack(side=tk.LEFT, padx=5)

        btn_frame = ttk.Frame(master)
        btn_frame.pack(fill='x', pady=5)

        ttk.Button(btn_frame, text="Set Cog ColorScale",
                   command=lambda: self.app.apply_body_colorscale(self.hex_color_var.get())
                   ).pack(fill='x', pady=2)

        ttk.Button(btn_frame, text="Set Head Color",
                   command=lambda: self.app.apply_head_color(self.hex_color_var.get())
                   ).pack(fill='x', pady=2)

        ttk.Button(btn_frame, text="Set Hand Color",
                   command=lambda: self.app.apply_hand_color(self.hex_color_var.get())
                   ).pack(fill='x', pady=2)

        ttk.Button(btn_frame, text="Reset Cog Colors",
                   command=self.app.reset_cog_colors
                   ).pack(fill='x', pady=5)

        ttk.Separator(btn_frame, orient=tk.HORIZONTAL).pack(fill='x', expand=True, pady=5)

        ttk.Button(btn_frame, text="Set Background Color",
                   command=lambda: self.app.apply_background_color(self.hex_color_var.get())
                   ).pack(fill='x', pady=2)

        ttk.Button(btn_frame, text="Reset Background Color",
                   command=self.app.reset_background_color
                   ).pack(fill='x', pady=5)

    def _create_head_hpr_sliders(self, master):
        default = self.app.get_head_hpr_default_values()
        slider_defs = [
            ("Left/Right", "x", -15, 15, default["x"]),
            ("Front/Back", "y", -15, 15, default["y"]),
            ("Up/Down", "z", -15, 15, default["z"]),
            ("Heading", "h", -180, 180, default["h"]),
            ("Pitch", "p", -180, 180, default["p"]),
            ("Roll", "r", -180, 180, default["r"]),
            ("Scale", "scale", 0.0, 15, default["scale"])
        ]

        main_frame = ttk.Frame(master)
        main_frame.pack(fill="x", expand=True)

        for label, axis, min_val, max_val, default_val in slider_defs:
            var = tk.DoubleVar(value=default_val)
            self.head_hpr_vars[axis] = var

            # Row frame
            row = ttk.Frame(main_frame)
            row.pack(fill="x", expand=True, pady=2)

            # Label
            ttk.Label(row, text=label, width=10, anchor="w").pack(side=tk.LEFT, padx=(0, 5))

            # Slider
            scale = ttk.Scale(row, from_=min_val, to=max_val, orient=tk.HORIZONTAL, variable=var)
            scale.pack(side=tk.LEFT, fill="x", expand=True, padx=5)

            # Text Entry
            entry = ttk.Entry(row, textvariable=var, width=7)
            entry.pack(side=tk.LEFT, padx=5)

            # Reset Button
            reset_btn = ttk.Button(row, text="Reset", width=6,
                                   command=lambda axis=axis, v=var: self.reset_head_axis(axis, v))
            reset_btn.pack(side=tk.LEFT)

            var.trace_add("write", self._create_hpr_trace_callback(var, axis))

        # Reset All Button
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill='x', expand=True, pady=5)
        reset_all_btn = ttk.Button(main_frame, text="Reset All Head Controls", command=self.reset_head_hpr)
        reset_all_btn.pack(fill="x", expand=True)

    def update_head_hpr_sliders(self):
        if not hasattr(self.app, "store_head_hpr"):
            return

        for axis, var in self.head_hpr_vars.items():
            if axis in self.app.store_head_hpr:
                var.set(self.app.store_head_hpr[axis])

    def _create_color_frame(self):
        master = self.color_inner_frame
        master.update_idletasks()

    def _create_suit_library(self, master):
        # -------- SUIT TEXTURES --------#
        SUIT_TEXTURES = globals.SUIT_TEXTURES

        suit_notebook = ttk.Notebook(master)
        suit_notebook.grid(row=0, column=0, sticky="nsew")
        suit_categories = ["Standard", "Manager", "Halloween", "Skelecog"]  # Each of the suit categories
        self.selected_suit_tex_var = tk.StringVar()

        # This part fills the categories
        for category in suit_categories:
            category_suit_data = SUIT_TEXTURES.get(category, {})  # Get the data from suit textures dictionary
            tex_frame = self._create_scrollable_radio_list(suit_notebook, f"{category} Suit Textures",
                                                           list(category_suit_data.keys()), self.selected_suit_tex_var,
                                                           self.on_suit_tex_select, 225, 225)
            suit_notebook.add(tex_frame, text=category)

        # -------- SUIT MODELS --------#
        valid_keys = [k for k in globals.SUIT_MODEL_DICT.keys() if k not in ["boss"]]  # fuDGE you bosscog model
        suit_model_names = [(globals.SUIT_MODEL_NAMES[k], k) for k in valid_keys]

        suit_mod_notebook = ttk.Notebook(master)
        suit_mod_notebook.grid(row=0, column=1, sticky="e")
        self.selected_suit_mod_var = tk.StringVar()

        mod_frame = self._create_scrollable_radio_list(suit_mod_notebook, "Suit Models", suit_model_names,
                                                       self.selected_suit_mod_var, self.on_suit_mod_select, 225, 225,
                                                       True)
        suit_mod_notebook.add(mod_frame, text="Suit Models")

        # -------- SUIT EMBLEMS --------#
        self.selected_emblem_var = tk.StringVar()
        emblem_dict = list(globals.EMBLEM_MAP.keys())
        emblem_frame = self._create_radio_list(suit_mod_notebook, "Chest Emblems", emblem_dict,
                                               self.selected_emblem_var, self.on_emblem_select)
        suit_mod_notebook.add(emblem_frame, text="Emblems")

        # ---------- SUIT NECKTIES --------------#
        tie_frame = self._create_radio_list(suit_mod_notebook, "Necktie Models", self.TIE_OPTIONS,
                                            self.selected_tie_var, self.on_tie_select_radio)
        suit_mod_notebook.add(tie_frame, text="Neckties")

    def on_suit_tex_select(self):
        suit_name = self.selected_suit_tex_var.get()
        if suit_name:
            for category in globals.SUIT_TEXTURES:
                if suit_name in globals.SUIT_TEXTURES[category]:
                    texture_path = globals.SUIT_TEXTURES[category].get(suit_name)
                    if texture_path:
                        self.app.apply_suit_texture(texture_path)

    def on_suit_mod_select(self):
        suit_key = self.selected_suit_mod_var.get()
        if suit_key in globals.SUIT_MODEL_DICT:
            self.app.apply_suit_model(suit_key)

    def on_emblem_select(self):
        emblem_key = self.selected_emblem_var.get()
        emblem_name = globals.EMBLEM_MAP.get(emblem_key)
        if emblem_key in globals.EMBLEM_MAP:
            self.app.apply_emblem(emblem_name)
            # Override health meter
            self.app.store_health_meter = False

    def _create_prop_sliders(self, master, update_callback):
        is_prop1 = (update_callback == self.app.update_prop_hpr)
        vars_dict = self.prop1_vars if is_prop1 else self.prop2_vars

        slider_defs = [
            ("Left/Right", "x", -30, 30, 0.0),
            ("Front/Back", "y", -30, 30, 0.0),
            ("Up/Down", "z", -30, 30, 0.0),
            ("Heading", "h", -360, 360, 0.0),
            ("Pitch", "p", -180, 180, 0.0),
            ("Roll", "r", -360, 360, 0.0),
            ("Scale", "scale", 0.1, 15, 1.0),
        ]

        # Frame for all controls
        main_frame = ttk.Frame(master)
        main_frame.pack(fill="x", expand=True)

        for label, axis, min_val, max_val, default_val in slider_defs:
            var = tk.DoubleVar(value=default_val)
            vars_dict[axis] = var

            # Row frame
            row = ttk.Frame(main_frame)
            row.pack(fill="x", expand=True, pady=2)

            # Label
            ttk.Label(row, text=label, width=10, anchor="w").pack(side=tk.LEFT, padx=(0, 5))

            # Slider
            scale = ttk.Scale(row, from_=min_val, to=max_val, orient=tk.HORIZONTAL, variable=var)
            scale.pack(side=tk.LEFT, fill="x", expand=True, padx=5)

            # Text Entry
            entry = ttk.Entry(row, textvariable=var, width=7)
            entry.pack(side=tk.LEFT, padx=5)

            # Reset Button
            reset_btn = ttk.Button(row, text="Reset", width=6,
                                   command=lambda v=var, val=default_val: v.set(val))
            reset_btn.pack(side=tk.LEFT)

            var.trace_add("write", self._create_prop_trace_callback(var, axis, update_callback))

        # Reset All Button
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill='x', expand=True, pady=10)
        reset_all_btn = ttk.Button(main_frame, text="Reset All Prop Controls",
                                   command=lambda d=vars_dict: self.reset_prop_sliders(d))
        reset_all_btn.pack(fill="x", expand=True)

    def _create_scrollable_radio_list(self, master, label_text, items, variable, command, width=200, height=100,
                                      set_text=False):
        frame = ttk.Labelframe(master, text=label_text)

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        canvas = tk.Canvas(frame, yscrollcommand=scrollbar.set, borderwidth=0, highlightthickness=0, width=width,
                           height=height)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=canvas.yview)
        inner_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        if not set_text:
            for item in items:
                ttk.Radiobutton(
                    inner_frame,
                    text=item,
                    variable=variable,
                    value=item,
                    command=command
                ).pack(anchor="nw", fill="x", padx=5, pady=1)
        else:
            for display_text, key in items:
                ttk.Radiobutton(
                    inner_frame,
                    text=display_text,
                    variable=variable,
                    value=key,
                    command=command
                ).pack(anchor="nw", fill="x", padx=5, pady=1)

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        inner_frame.bind("<Configure>", on_frame_configure)

        def _on_mouse_wheel(event):
            if event.num == 5 or event.delta < 0:
                delta = 1
            else:
                delta = -1
            canvas.yview_scroll(delta, "units")

        widgets_to_bind = [canvas, inner_frame] + inner_frame.winfo_children()
        for widget in widgets_to_bind:
            widget.bind("<MouseWheel>", _on_mouse_wheel, add='+')
            widget.bind("<Button-4>", _on_mouse_wheel, add='+')
            widget.bind("<Button-5>", _on_mouse_wheel, add='+')

        return frame

    # Same thing as scrollable_radio_list but not scrollable basically
    def _create_radio_list(self, master, label_text, items, variable, command):
        frame = ttk.Labelframe(master, text=label_text)
        self.radio_list_frame = ttk.Frame(frame)

        for item in items:
            ttk.Radiobutton(
                self.radio_list_frame,
                text=item,
                variable=variable,
                value=item,
                command=command).pack(anchor="nw", fill="x", padx=5, pady=1)

        self.radio_list_frame.pack(fill="both", expand=True)

        return frame

    # Hide tie list
    def hide_tie_list(self):
        self.radio_list_frame.grid_forget()
        self.tie_options_hidden_var = True

    # Show tie list
    def show_tie_list(self):
        self.radio_list_frame.grid(row=0, column=2, rowspan=5, sticky="nsew", padx=5, pady=2)
        self.tie_options_hidden_var = False

    def _on_entry_focus_in(self, entry_widget, placeholder_text):
        if entry_widget.get() == placeholder_text:
            entry_widget.delete(0, tk.END)
            entry_widget.config(foreground='black')

    def _on_entry_focus_out(self, entry_widget, placeholder_text):
        if not entry_widget.get():
            entry_widget.config(foreground='grey')
            entry_widget.insert(0, placeholder_text)

    def filter_listbox(self, listbox_widget, search_term):
        all_props = sorted(list(self.app.available_props.keys()), key=str.lower)

        listbox_widget.delete(0, tk.END)

        if not search_term:
            for prop in all_props:
                listbox_widget.insert(tk.END, prop)
        else:
            for prop in all_props:
                if search_term in prop.lower():
                    listbox_widget.insert(tk.END, prop)

    def on_prop1_search(self, event):
        search_term = self.prop1_search_entry.get().lower()

        if search_term == "search prop":
            search_term = ""

        self.filter_listbox(self.prop1_listbox, search_term)

    def on_prop2_search(self, event):
        search_term = self.prop2_search_entry.get().lower()

        if search_term == "search prop":
            search_term = ""

        self.filter_listbox(self.prop2_listbox, search_term)

    def update_animation_lists(self, body_anims, head_anims):
        self.body_anim_listbox.delete(0, tk.END)
        for anim in body_anims:
            if not anim == "lose" and not anim == "lose_zero":
                self.body_anim_listbox.insert(tk.END, anim)

        self.head_anim_listbox.delete(0, tk.END)

        # Derrick Hand broken skelecog anim fix
        if self.app.current_cog == "Derrick Hand":
            head_anims = (anim for anim in head_anims if "skele" not in anim.lower())

        for anim in head_anims:
            self.head_anim_listbox.insert(tk.END, anim)

    def update_prop_lists(self):
        search_term1 = self.prop1_search_entry.get().lower()
        if search_term1 == "search prop":
            search_term1 = ""

        search_term2 = self.prop2_search_entry.get().lower()
        if search_term2 == "search prop":
            search_term2 = ""

        self.filter_listbox(self.prop1_listbox, search_term1)
        self.filter_listbox(self.prop2_listbox, search_term2)

    def setup_prop_anim_ui(self, listbox, slider, anim_frame, actor):
        anims = actor.getAnimNames()
        listbox.delete(0, tk.END)
        for anim in anims:
            listbox.insert(tk.END, anim)

        try:
            self.prop_notebook.add(anim_frame)  # 'add' also un-hides a hidden tab
        except tk.TclError:
            pass  # Tab already visible

    def hide_prop_anim_ui(self, anim_frame):
        try:
            self.prop_notebook.hide(anim_frame)  # Hide the tab
        except tk.TclError:
            pass  # Tab already hidden

    def update_prop_slider_range(self, slider, num_frames):
        if num_frames <= 1: num_frames = 1
        slider.config(to=num_frames - 1)
        slider.set(0)

    def update_anim_slider_range(self, slider_name, num_frames):
        if num_frames <= 1:
            num_frames = 1

        if slider_name == "body":
            self.body_frame_slider.config(to=num_frames - 1)
            self.body_frame_slider.set(0)
        elif slider_name == "head":
            self.head_frame_slider.config(to=num_frames - 1)
            self.head_frame_slider.set(0)

    def _create_hpr_trace_callback(self, var, axis):
        def trace_callback(*args):
            try:
                value = var.get()
                self.app.update_head_hpr(axis, value)
            except tk.TclError:
                pass

        return trace_callback

    def _create_flatten_trace_callback(self, var, axis):
        def trace_callback(*args):
            try:
                value = var.get()
                self.app.update_flatten_body(axis, value)
            except tk.TclError:
                pass

        return trace_callback

    def _create_flatten_head_trace_callback(self, var, axis):
        def trace_callback(*args):
            try:
                value = var.get()
                self.app.update_flatten_head(axis, value)
            except tk.TclError:
                pass

        return trace_callback

    def _create_prop_trace_callback(self, var, axis, update_func):
        def trace_callback(*args):
            try:
                update_func(axis, var.get())
            except tk.TclError:
                pass

        return trace_callback

    def reset_head_axis(self, axis, var):
        default_val = self.app.get_head_hpr_default_values()[axis]
        var.set(default_val)
        if hasattr(self.app, "store_head_hpr"):
            self.app.store_head_hpr[axis] = default_val

        self.app.update_head_hpr(axis, default_val)

    def reset_head_hpr(self):
        default = self.app.get_head_hpr_default_values()
        for axis, var in self.head_hpr_vars.items():
            var.set(default[axis])

        self.app.store_head_hpr = globals.HEAD_HPR_DEFAULTS.copy()

    def reset_flat_body_axis(self, axis, var):
        default_val = self.app.cog_data.get("scale", 1.0)
        var.set(default_val)

        self.app.update_flatten_body(axis, default_val)

    def reset_flat_head_axis(self, axis):
        default = self.app.cog_data.get("headSize", 1.0)
        self.flatten_head_vars[axis].set(default)
        self.app.update_flatten_head(axis, default)

    def reset_flatten(self):
        default_body = self.app.cog_data.get("scale", 1.0)
        default_head = self.app.cog_data.get("headSize", 1.0)
        # Reset Flatten Body
        for axis, var in self.flatten_body_vars.items():
            var.set(default_body)
            self.app.update_flatten_body(axis, default_body)
        # Reset Flatten Head
        for axis, var in self.flatten_head_vars.items():
            var.set(default_head)
            self.app.update_flatten_head(axis, default_head)

    def reset_prop_sliders(self, vars_dict):
        for axis, var in vars_dict.items():
            if axis == "scale":
                var.set(1.0)
            else:
                var.set(0.0)

    def setup_custom_model_tab(self):
        self._create_prop_sliders(self.custom_model_tab_frame, self.app.update_custom_model_hpr)

    def show_custom_model_tab(self, show=True):
        if show:
            try:
                self.bottom_notebook.add(self.custom_model_tab_frame, text='Accessory HPR')
            except tk.TclError:
                pass
        else:
            try:
                self.bottom_notebook.hide(self.custom_model_tab_frame)
            except tk.TclError:
                pass

    def show_suit_library(self, show=True):
        if show:
            try:
                self.bottom_notebook.add(self.suit_library_frame, text='Suit Library')
            except tk.TclError:
                pass
        else:
            try:
                self.bottom_notebook.hide(self.suit_library_frame)
            except tk.TclError:
                pass

    def on_cog_select_radio(self):
        cog_name = self.selected_cog_var.get()
        if cog_name:
            self.app.load_cog(cog_name)

    def _get_selected_from_listbox(self, event):
        widget = event.widget
        selection = widget.curselection()
        if selection:
            index = selection[0]
            return widget.get(index)
        return None

    def on_tie_select_radio(self):
        tie_name = self.selected_tie_var.get()
        self.app.store_necktie = tie_name
        if tie_name:
            self.app.set_necktie(tie_name)

    def on_body_anim_select(self, event):
        anim_name = self._get_selected_from_listbox(event)
        if anim_name:
            self.app.set_animation(anim_name)
            self.app.check_body_autoplay()

    def on_head_anim_select(self, event):
        anim_name = self._get_selected_from_listbox(event)
        if anim_name:
            self.app.set_head_animation(anim_name)
            self.app.check_head_autoplay()

    def on_prop1_select(self, event):
        prop_name = self._get_selected_from_listbox(event)
        if prop_name:
            self.app.set_prop(prop_name)

    def on_prop2_select(self, event):
        prop_name = self._get_selected_from_listbox(event)
        if prop_name:
            self.app.set_prop2(prop_name)

    def show_body_toggle(self, show=True):
        if show:
            self.body_toggle_btn.pack(anchor="w", padx=5)
        else:
            self.body_toggle_btn.pack_forget()

    def update_incompatibilities(self):
        if not hasattr(self, 'zapped_cb') or not hasattr(self, 'skelecog_cb'):
            return

        active_suit = getattr(self.app, 'suit_type', '')
        is_skel_mod = self.selected_suit_mod_var.get() in ["as", "bs", "cs"] or active_suit in ["as", "bs", "cs"]

        is_made_skel = self.is_skelecog_var.get()
        is_zapped = getattr(self, 'is_zapped_var', None) and self.is_zapped_var.get()

        if is_skel_mod or is_made_skel:
            if is_zapped:
                self.is_zapped_var.set(False)
                self.app.toggle_zapped(False)
            self.zapped_cb.state(['disabled'])
        else:
            self.zapped_cb.state(['!disabled'])

        is_zapped_recheck = getattr(self, 'is_zapped_var', None) and self.is_zapped_var.get()

        if is_zapped_recheck:
            if is_made_skel:
                self.is_skelecog_var.set(False)
                self.app.toggle_skelecog(False)
            self.skelecog_cb.state(['disabled'])
        else:
            self.skelecog_cb.state(['!disabled'])


class CogViewer(ShowBase):
    def __init__(self):
        loadPrcFileData("", "want-tk #t")
        ShowBase.__init__(self)
        self.base = base
        self.render = render
        self.clock = ClockObject.getGlobalClock()

        props = WindowProperties()
        props.setTitle('Corporate Clash Cog Viewer')
        props.setIconFilename("../resources/ICONS/gearIcon.ico")
        self.win.requestProperties(props)

        def cool_slash(data):
            if isinstance(data, str):
                return data.replace('\\', '/')
            elif isinstance(data, dict):
                return {k: cool_slash(v) for k, v in data.items()}
            elif isinstance(data, (list, tuple)):
                return type(data)([cool_slash(i) for i in data])
            return data

        orig_load_model = builtins.loader.loadModel

        def safe_load_model(modelPath, *args, **kwargs):
            return orig_load_model(
                cool_slash(modelPath),
                *cool_slash(args),
                **cool_slash(kwargs)
            )

        builtins.loader.loadModel = safe_load_model

        orig_load_texture = builtins.loader.loadTexture

        def safe_load_texture(texturePath, *args, **kwargs):
            return orig_load_texture(
                cool_slash(texturePath),
                *cool_slash(args),
                **cool_slash(kwargs)
            )

        builtins.loader.loadTexture = safe_load_texture

        orig_actor_init = Actor.__init__

        def safe_actor_init(self_actor, models=None, anims=None, *args, **kwargs):
            safe_models = cool_slash(models)
            safe_anims = cool_slash(anims)
            orig_actor_init(self_actor, safe_models, safe_anims, *args, **kwargs)

        Actor.__init__ = safe_actor_init

        self.screenshot_path = globals.SCREENSHOT_DIR
        self.frame_index = 0
        self.available_props = globals.PROPS_DICT
        self.bool = False
        self.actor = None
        self.available_animations = []
        self.available_head_animations = []
        self.is_autoplay = True  # Used for autoplay animation toggle
        self.is_shadow = True  # Used for toggle shadow
        self.is_posed = False
        self.is_blend = True
        self.is_costume_active = False  # Used for toggle costume
        self.is_body = True  # Used for toggle body
        self.current_animation = "zero"
        self.current_head_animation = "zero"
        self.previous_prop1 = "zero"
        self.prop_item1 = "zero"
        self.previous_prop2 = "zero"
        self.prop_item2 = "zero"
        self.last_pose_frame = 0
        self.cog_list = list(globals.COG_DATA)
        self.current_cog_index = 0
        self.current_cog = self.cog_list[self.current_cog_index]
        self.cog_data = globals.COG_DATA[self.current_cog]
        self.custom_model = None
        self.suit_is_executive = False
        self.suit_is_fired = False
        self.prop_item1_actor = None
        self.prop_item2_actor = None
        self.splat_stages = []
        self.suit_type = None
        self.background_color = (105 / 255, 105 / 255, 105 / 255)
        self.zapped_head = None
        self.skelecog = None
        self.skelecog_skull = None

        self.control_panel = ControlPanel(self.base.tkRoot, self)
        self.control_panel.setup_custom_model_tab()
        self.shadow = loader.loadModel(globals.SHADOW_MODEL)
        self.shadow.setScale(globals.SHADOW_SCALE)
        self.shadow.setColor(globals.SHADOW_COLOR)

        # have to do this for the environment model
        self.shadow.setTransparency(TransparencyAttrib.MAlpha, 1)
        self.shadow.setDepthWrite(False, 1)
        self.shadow.setDepthTest(True, 1)
        self.shadow.setDepthOffset(3, 1)
        self.shadow.setBin("fixed", 100, 1)

        vfs = VirtualFileSystem.getGlobalPtr()
        resource_path = Filename.fromOsSpecific(globals.RESOURCES_DIR)
        vfs.mount(resource_path, ".", VirtualFileSystem.MFReadOnly)

        self.skele_i = 0
        self.skele_meter_color = 0
        self.skele_color_index = 0
        self.flatten_switch = 0
        self.it = 0
        self.it2 = 0
        self.it_l = 0
        self.it_m = 0
        self.it_r = 0

        self.current_cog_index = 0
        self.current_cog = self.cog_list[self.current_cog_index]
        self.build_cog()

        self.reset_actor_pos()
        self.reset_camera_pos()

        self.accept("r", self.reset_camera_roll)
        self.accept("f9", self.take_screenshot)
        self.accept("f10", self.take_screenshot_frames)
        self.accept("control-z", self.reset_camera_pos)

        # Store a bunch of data
        self.store_head_texture = None
        self.store_suit_texture = None
        self.store_skelecog_texture = None
        self.store_health_meter = False
        self.store_emblem = "emblem_sales"
        self.store_necktie = "(Default)"
        self.store_costume = None
        self.store_virtualize = False
        self.store_head_hpr = globals.HEAD_HPR_DEFAULTS.copy()
        self.store_is_skelecog = False
        self.store_skelecog_skull = None
        self.store_skel_head_name = None
        self.store_skel_head_tex = None
        # Stored unique toggles
        self.store_unique_suit_toggle = False
        self.store_cycle_slot_l = False
        self.store_cycle_slot_m = False
        self.store_cycle_slot_r = False
        self.store_ms_toggle_1 = False
        self.store_cs_toggle_1 = False
        self.store_cs_toggle_2 = False
        # Stored Body anims
        self.store_body_anim = None
        self.store_body_frame = 0
        self.store_body_loop = False
        self.store_body_adjusted = False
        self.store_body_playing = False
        # Stored Head anims
        self.store_head_anim = None
        self.store_head_frame = 0
        self.store_head_loop = False
        self.store_head_adjusted = False
        self.store_head_playing = False
        # Stored Scale vals
        self.store_flatten_body = {
            "Sx": self.cog_data.get("scale", 1.0),
            "Sy": self.cog_data.get("scale", 1.0),
            "Sz": self.cog_data.get("scale", 1.0),
        }
        self.store_flatten_head = {
            "Sx": self.cog_data.get("headSize", 1.0),
            "Sy": self.cog_data.get("headSize", 1.0),
            "Sz": self.cog_data.get("headSize", 1.0),
        }
        # Stored Colors
        self.store_body_hex_color = None
        self.store_body_color = False
        self.store_head_hex_color = None
        self.store_head_color = False
        self.store_hand_hex_color = None
        self.store_hand_color = False
        # Stored Props
        self.current_prop1 = "zero"
        self.current_prop2 = "zero"
        self.store_prop1 = "zero"
        self.store_prop2 = "zero"
        self.store_prop1_hpr = globals.HEAD_HPR_DEFAULTS.copy()
        self.store_prop2_hpr = globals.HEAD_HPR_DEFAULTS.copy()
        self.store_custom_model = None
        self.store_custom_model_hpr = globals.HEAD_HPR_DEFAULTS.copy()

        particle_path = os.path.join(globals.RESOURCES_DIR, "phase_3.5", "models", "props", "suit-particles.bam")
        if os.path.exists(particle_path):
            self.fire_particle_base = loader.loadModel(particle_path).find("**/fire")
        else:
            self.fire_particle_base = None
            print("Warning: suit-particles.bam not found!")

        self.active_fires = []

        if os.path.exists(particle_path):
            self.drop_particle_base = loader.loadModel(particle_path).find("**/raindrop")
        else:
            self.drop_particle_base = None

        self.is_chilled = False
        self.is_frozen = False

        self.active_drops = []
        self.snow_active = False
        self.active_snows = []
        self.active_icecube = None

        icecube_path = os.path.join(globals.RESOURCES_DIR, "phase_4", "models", "accessories", "bosses",
                                    "hat_icecube.bam")
        if os.path.exists(icecube_path):
            self.icecube_model = loader.loadModel(icecube_path)
            self.icecube_model.setTransparency(TransparencyAttrib.MAlpha)
            self.icecube_model.setColorScale(1.0, 1.0, 1.0, 1.0)
        else:
            self.icecube_model = None

        snowflake_path = os.path.join(globals.RESOURCES_DIR, "phase_8", "models", "props", "snowflake_particle.bam")
        if os.path.exists(snowflake_path):
            self.snow_particle_base = loader.loadModel(snowflake_path)
            self.snow_particle_base.setColorScale(1.0, 1.0, 1.0, 1.0)
        else:
            self.snow_particle_base = None

        stun_mod = os.path.join(globals.RESOURCES_DIR, "phase_5", "models", "effects", "stun-mod.bam")
        stun_chan = os.path.join(globals.RESOURCES_DIR, "phase_5", "models", "effects", "stun-chan.bam")
        if os.path.exists(stun_mod) and os.path.exists(stun_chan):
            self.stun_effect = Actor(stun_mod, {"stun": stun_chan})
            self.sued_effect = Actor(stun_mod, {"stun": stun_chan})

            sued_tex_path = os.path.join(globals.RESOURCES_DIR, "phase_5", "maps", "battle",
                                         "ttcc_fx_battleParticles_palette_2.jpg")
            sued_alpha_path = os.path.join(globals.RESOURCES_DIR, "phase_5", "maps", "battle",
                                           "ttcc_fx_battleParticles_palette_2_a.rgb")

            if os.path.exists(sued_tex_path):
                if sued_tex_path.endswith(".jpg") and os.path.exists(sued_alpha_path):
                    sued_tex = loader.loadTexture(sued_tex_path, sued_alpha_path)
                else:
                    sued_tex = loader.loadTexture(sued_tex_path)

                self.sued_effect.setTexture(sued_tex, 1)

                self.sued_effect.setTransparency(1)



        else:
            self.stun_effect = None
            self.sued_effect = None

        self.base.enableParticles()
        self.render.setAntialias(AntialiasAttrib.MMultisample)

    def load_cog(self, cog_name):
        self.current_cog = cog_name
        self.build_cog()

        try:
            self.control_panel.selected_cog_var.set(cog_name)
        except Exception as e:
            print(f"Could not update cog selection: {e}")

        self.refresh_battle_effects()
        if hasattr(self, 'control_panel') and hasattr(self.control_panel, 'update_incompatibilities'):
            self.control_panel.update_incompatibilities()

    def switch_toggle(self, this_var, other_var, other_func):
        if this_var.get() and other_var.get():
            other_var.set(False)
            other_func(False)

    def set_POSHPR(self, target, axis, value):
        is_skel = target in [getattr(self, 'zapped_head', None), getattr(self, 'skelecog_skull', None)]
        if is_skel:
            base_val = globals.HEAD_HPR_DEFAULTS.get(axis, 0.0 if axis != "scale" else 1.0)

            if axis == "scale":
                if base_val != 0:
                    value = value / base_val
            else:
                value = value - base_val

        POSHPR_DICT = {
            "x": target.setX,
            "y": target.setY,
            "z": target.setZ,
            "h": target.setH,
            "p": target.setP,
            "r": target.setR,
            "scale": target.setScale
        }
        pos = POSHPR_DICT.get(axis)
        if pos:
            pos(value)

    def set_depth(self, target, axis, value):
        is_skel = target in [getattr(self, 'zapped_head', None), getattr(self, 'skelecog_skull', None)]
        if is_skel and hasattr(self, 'base_head_scale') and self.base_head_scale != 0:
            value = value / self.base_head_scale

        if hasattr(self, "store_flatten_body") and not is_skel:
            if target == self.actor:
                self.store_flatten_body[axis] = value
            else:
                self.store_flatten_head[axis] = value

        SCALE_DICT = {
            "Sx": target.setSx,
            "Sy": target.setSy,
            "Sz": target.setSz,
        }
        func = SCALE_DICT.get(axis)
        if func:
            func(value)

    def update_head_hpr(self, axis, value):
        self.store_head_hpr[axis] = value

        if hasattr(self, 'head') and not self.head.isEmpty():
            self.set_POSHPR(self.head, axis, value)

        if hasattr(self, 'skelecog_skull') and self.skelecog_skull and not self.skelecog_skull.isEmpty():
            self.set_POSHPR(self.skelecog_skull, axis, value)

        if hasattr(self, 'zapped_head') and self.zapped_head and not self.zapped_head.isEmpty():
            self.set_POSHPR(self.zapped_head, axis, value)

    def update_flatten_body(self, axis, value):
        if not hasattr(self, 'actor') or self.actor is None:
            return
        self.set_depth(self.actor, axis, value)
        self.update_stun_position()

    def update_flatten_head(self, axis, value):
        if hasattr(self, "store_flatten_head"):
            self.store_flatten_head[axis] = value

        if hasattr(self, "head") and not self.head.isEmpty():
            self.set_depth(self.head, axis, value)

        if hasattr(self, 'skelecog_skull') and self.skelecog_skull and not self.skelecog_skull.isEmpty():
            self.set_depth(self.skelecog_skull, axis, value)

        if hasattr(self, 'zapped_head') and self.zapped_head and not self.zapped_head.isEmpty():
            self.set_depth(self.zapped_head, axis, value)

        self.update_stun_position()

    def _get_selected_from_listbox(self, event):
        widget = event.widget
        selection = widget.curselection()
        if selection:
            index = selection[0]
            return widget.get(index)
        return None

    def update_prop_hpr(self, axis, value):
        item_to_move = self.prop_item1_actor if self.prop_item1_actor else self.prop_item1

        if item_to_move != "zero" and not item_to_move.isEmpty():
            self.set_POSHPR(item_to_move, axis, value)
            self.store_prop1_hpr[axis] = value

    def update_prop2_hpr(self, axis, value):
        item_to_move = self.prop_item2_actor if self.prop_item2_actor else self.prop_item2

        if item_to_move != "zero" and not item_to_move.isEmpty():
            self.set_POSHPR(item_to_move, axis, value)
            self.store_prop2_hpr[axis] = value

    def set_prop(self, prop, check_prop=True):
        if self.prop_item1_actor:
            self.prop_item1_actor.cleanup()
            self.prop_item1_actor.removeNode()
            self.prop_item1_actor = None
        if self.prop_item1 != "zero" and not self.prop_item1.isEmpty():
            self.prop_item1.removeNode()
            self.prop_item1 = "zero"
        self.control_panel.hide_prop_anim_ui(self.control_panel.prop1_anim_frame)

        if check_prop:
            if self.current_prop1 == prop:
                # Clicked same prop, toggle off
                self.current_prop1 = "zero"
                self.store_prop1 = "zero"
                return

        self.current_prop1 = prop
        self.store_prop1 = prop
        prop_data = globals.PROPS_DICT[prop]

        if prop_data.get("anims"):
            # It's an animated prop
            self.prop_item1_actor = Actor(prop_data["model"], prop_data["anims"])
            if self.cog_data.get("cog_type") == "boss":
                self.prop_item1_actor.reparentTo(self.boss_parts["torso"].find('**/joint17'))
            else:
                self.prop_item1_actor.reparentTo(self.actor.find('**/joint_Rhold'))
            self.control_panel.setup_prop_anim_ui(
                self.control_panel.prop1_anim_listbox,
                self.control_panel.prop1_anim_slider,
                self.control_panel.prop1_anim_frame,
                self.prop_item1_actor
            )
        else:
            # It's a static prop
            self.prop_item1 = loader.loadModel(prop_data["model"])
            if self.cog_data.get("cog_type") == "boss":
                self.prop_item1.reparentTo(self.boss_parts["torso"].find('**/joint17'))
            else:
                self.prop_item1.reparentTo(self.actor.find('**/joint_Rhold'))

        if prop == "flintbass":  # i hate this prop
            try:
                texture_path = os.path.join(globals.RESOURCES_DIR, "phase_12", "maps", "flintbass.png")
                tex_node = self.prop_item1_actor if self.prop_item1_actor else self.prop_item1
                if os.path.isfile(texture_path):
                    prop_texture = loader.loadTexture(texture_path)
                    tex_node.setTexture(prop_texture, 1)
                else:
                    print(f"Warning: Looked for {texture_path} but didn't find it.")
            except Exception as e:
                print(f"Error applying flintbass texture: {e}")
        if check_prop:
            self.control_panel.reset_prop_sliders(self.control_panel.prop1_vars)

    def set_prop2(self, prop2, check_prop=True):
        if self.prop_item2_actor:
            self.prop_item2_actor.cleanup()
            self.prop_item2_actor.removeNode()
            self.prop_item2_actor = None
        if self.prop_item2 != "zero" and not self.prop_item2.isEmpty():
            self.prop_item2.removeNode()
            self.prop_item2 = "zero"
        self.control_panel.hide_prop_anim_ui(self.control_panel.prop2_anim_frame)

        if check_prop:
            if self.current_prop2 == prop2:
                self.current_prop2 = "zero"
                self.store_prop2 = "zero"
                return

        self.current_prop2 = prop2
        self.store_prop2 = prop2
        prop_data = globals.PROPS_DICT[prop2]

        if prop_data.get("anims"):
            # It's an animated prop
            self.prop_item2_actor = Actor(prop_data["model"], prop_data["anims"])
            if self.cog_data.get("cog_type") == "boss":
                self.prop_item2_actor.reparentTo(self.boss_parts["torso"].find('**/joint17'))
            else:
                self.prop_item2_actor.reparentTo(self.actor.find('**/joint_Lhold'))
            self.control_panel.setup_prop_anim_ui(
                self.control_panel.prop2_anim_listbox,
                self.control_panel.prop2_anim_slider,
                self.control_panel.prop2_anim_frame,
                self.prop_item2_actor
            )
        else:
            # It's a static prop
            self.prop_item2 = loader.loadModel(prop_data["model"])
            if self.cog_data.get("cog_type") == "boss":
                self.prop_item2.reparentTo(self.boss_parts["torso"].find('**/joint17'))
            else:
                self.prop_item2.reparentTo(self.actor.find('**/joint_Lhold'))

        if prop2 == "flintbass":
            try:
                texture_path = os.path.join(globals.RESOURCES_DIR, "phase_12", "maps", "flintbass.png")
                tex_node = self.prop_item2_actor if self.prop_item2_actor else self.prop_item2
                if os.path.isfile(texture_path):
                    prop_texture = loader.loadTexture(texture_path)
                    tex_node.setTexture(prop_texture, 1)
                else:
                    print(f"Warning: Looked for {texture_path} but didn't find it.")
            except Exception as e:
                print(f"Error applying flintbass texture: {e}")
        if check_prop:
            self.control_panel.reset_prop_sliders(self.control_panel.prop2_vars)

    def add_pie_splat(self):
        cog_data = globals.COG_DATA[self.current_cog]
        if not self.actor: return

        vfs = VirtualFileSystem.getGlobalPtr()
        possible_splats = []

        phases_to_check = []
        for i in range(3, 15):
            phases_to_check.append(f"phase_{i}")
            phases_to_check.append(f"phase_{i}.5")

        for phase in phases_to_check:
            search_dir = Filename.fromOsSpecific(os.path.join(globals.RESOURCES_DIR, phase, "maps"))

            if vfs.exists(search_dir):
                file_list = vfs.scanDirectory(search_dir)
                if file_list:
                    for v_file in file_list:
                        fname = v_file.getFilename().getBasename().lower()
                        if "splat" in fname and fname.endswith(('.png', '.jpg')):
                            if "grayscale" not in fname and "fruit" not in fname:
                                possible_splats.append(v_file.getFilename())

        pie_tex = loader.loadTexture(random.choice(possible_splats))
        pie_tex.setWrapU(Texture.WMBorderColor)
        pie_tex.setWrapV(Texture.WMBorderColor)
        pie_tex.setBorderColor((0, 0, 0, 0))

        stage_name = f"splatStage_{len(self.splat_stages)}"
        decal_stage = TextureStage(stage_name)
        decal_stage.setMode(TextureStage.MDecal)
        decal_stage.setSort(10 + len(self.splat_stages))

        scale_x, scale_y = random.uniform(0.75, 0.5), random.uniform(0.75, 0.5)
        offset_x, offset_y = random.uniform(0.0, 0.50), random.uniform(0.0, 0.25)

        is_zapped = getattr(self, 'is_zapped', False)
        is_skel = hasattr(self, 'control_panel') and self.control_panel.is_skelecog_var.get()

        if is_zapped and hasattr(self, 'zapped_skelecog') and self.zapped_skelecog:
            target_body = self.zapped_skelecog.find('**/body')
            target_head = getattr(self, 'zapped_head', self.head)
        elif is_skel and hasattr(self, 'skelecog') and self.skelecog:
            target_body = self.skelecog.find('**/body')
            target_head = getattr(self, 'skelecog_skull', self.head)
        elif cog_data.get("suit") in ["boss", "bossCog"]:
            target_body = self.boss_parts.get("torso", self.actor.find('**/body'))
            target_head = self.head
        else:
            target_body = self.actor.find('**/body')
            target_head = self.head

        splat_applied = False

        if target_body and not target_body.isEmpty():
            target_body.setTexture(decal_stage, pie_tex, 1)
            target_body.setTexScale(decal_stage, scale_x, scale_y)
            target_body.setTexOffset(decal_stage, offset_x, offset_y)
            splat_applied = True

        if target_head and not target_head.isEmpty():
            target_head.setTexture(decal_stage, pie_tex, 1)
            target_head.setTexScale(decal_stage, scale_x, scale_y)
            target_head.setTexOffset(decal_stage, offset_x, offset_y)
            splat_applied = True

        if splat_applied:
            self.splat_stages.append(decal_stage)

    def clear_pie_splats(self):
        if not self.actor: return

        bodies = [
            self.actor.find('**/body'),
            self.boss_parts.get("torso") if hasattr(self, 'boss_parts') else None,
            self.skelecog.find('**/body') if hasattr(self, 'skelecog') and self.skelecog else None,
            self.zapped_skelecog.find('**/body') if hasattr(self, 'zapped_skelecog') and self.zapped_skelecog else None
        ]
        heads = [
            self.head if hasattr(self, 'head') else None,
            self.skelecog_skull if hasattr(self, 'skelecog_skull') else None,
            self.zapped_head if hasattr(self, 'zapped_head') else None
        ]

        for stage in self.splat_stages:
            for b in bodies:
                if b and not b.isEmpty(): b.clearTexture(stage)
            for h in heads:
                if h and not h.isEmpty(): h.clearTexture(stage)

        self.splat_stages = []

    def set_head_animation(self, animation):
        self.current_head_animation = animation
        active_head = self.get_active_head()

        if isinstance(active_head, Actor):
            active_head.loop(animation)

        self.is_posed = False

        if self.current_head_animation != self.store_head_anim:
            self.store_head_frame = 0
            self.store_head_adjusted = False

        try:
            if isinstance(active_head, Actor):
                num_frames = active_head.getNumFrames(self.current_head_animation)
            else:
                num_frames = 0
            self.control_panel.update_anim_slider_range("head", num_frames)
            self.store_head_anim = self.current_head_animation
        except:
            self.control_panel.update_anim_slider_range("head", 0)
            self.store_head_anim = None

    def set_animation(self, animation):
        self.current_animation = animation
        self.actor.loop(animation)

        if hasattr(self, 'skelecog') and self.skelecog:
            self.skelecog.loop(animation)
        if hasattr(self, 'zapped_skelecog') and self.zapped_skelecog:
            self.zapped_skelecog.loop(animation)
        if hasattr(self, 'hw_body_actor') and self.hw_body_actor:
            self.hw_body_actor.loop(animation)

        self.is_posed = False

        if self.current_animation != self.store_body_anim:
            self.store_body_frame = 0
            self.store_body_adjusted = False

        try:
            num_frames = self.actor.getNumFrames(self.current_animation)
            self.control_panel.update_anim_slider_range("body", num_frames)
            self.store_body_anim = self.current_animation
        except:
            self.control_panel.update_anim_slider_range("body", 0)
            self.store_body_anim = None

    def check_body_autoplay(self):
        if self.control_panel.is_autoplay_var.get():  # Autoplay on
            self.play_body_animation()
        else:  # Autoplay off
            self.stop_body_animation()

    def check_head_autoplay(self):
        if self.control_panel.is_autoplay_var.get():  # Autoplay on
            self.play_head_animation()
        else:  # Autoplay off
            self.stop_head_animation()

    def take_screenshot(self):
        cog_data = globals.COG_DATA[self.current_cog]
        path = globals.SCREENSHOT_DIR
        if not os.path.exists(path):
            os.makedirs(path)
        now = datetime.now()
        date_string = now.strftime("%d-%m-%Y-%H-%M-%S")
        screenshot_name = os.path.join(path, "ss-{}-{}.png".format(cog_data["cog"], date_string))
        self.setBackgroundColor(0, 0, 0)
        self.graphicsEngine.renderFrame()
        self.graphicsEngine.renderFrame()
        self.base.screenshot(screenshot_name, False)
        self.setBackgroundColor(self.background_color)
        self.auto_trim_screenshot(screenshot_name)

    def toggle_background(self):
        self.bool = self.control_panel.is_background_black_var.get()
        if self.bool:
            self.setBackgroundColor(0, 0, 0)
        else:
            self.setBackgroundColor(105 / 255, 105 / 255, 105 / 255)

    def enable_mouse_cam(self):
        mat = Mat4(camera.getMat())
        mat.invertInPlace()
        base.mouseInterfaceNode.setMat(mat)
        base.enableMouse()

    def disable_mouse_cam(self):
        base.disableMouse()

    def reset_camera_roll(self):
        self.disable_mouse_cam()
        camera.setR(0)
        self.enable_mouse_cam()

    def reset_actor_pos(self):
        if self.actor:
            if self.cog_data.get("cog_type") == "boss":
                new_h = 0
            else:
                new_h = 180
            self.actor.setH(new_h)

            if hasattr(self, 'control_panel') and hasattr(self.control_panel, 'rotation_var'):
                self.control_panel.rotation_var.set(new_h)

    def reset_camera_pos(self):
        self.disable_mouse_cam()
        base.camera.setPosHpr(*globals.DEFAULT_CAMERA_POS, 0, 0, 0)
        self.enable_mouse_cam()

    def play_body_animation(self):
        if self.current_animation != "zero":
            self.is_posed = False
            self.store_body_adjusted = False
            self.store_body_playing = True
            self.store_body_frame = 0

            if self.cog_data.get("cog_type") == "boss" and hasattr(self, "boss_parts"):
                for part_name, part_actor in self.boss_parts.items():
                    if part_name == "head": continue
                    if isinstance(part_actor, Actor):
                        if self.control_panel.loop_body_var.get():
                            part_actor.loop(self.current_animation)
                        else:
                            part_actor.play(self.current_animation)

            elif self.actor:
                if self.control_panel.loop_body_var.get():
                    self.actor.loop(self.current_animation)
                    if hasattr(self, 'skelecog') and self.skelecog:
                        self.skelecog.loop(self.current_animation)
                    if hasattr(self, 'zapped_skelecog') and self.zapped_skelecog:
                        self.zapped_skelecog.loop(self.current_animation)
                    if hasattr(self, 'hw_body_actor') and self.hw_body_actor:
                        self.hw_body_actor.loop(self.current_animation)
                else:
                    self.actor.play(self.current_animation)
                    if hasattr(self, 'skelecog') and self.skelecog:
                        self.skelecog.play(self.current_animation)
                    if hasattr(self, 'zapped_skelecog') and self.zapped_skelecog:
                        self.zapped_skelecog.play(self.current_animation)
                    if hasattr(self, 'hw_body_actor') and self.hw_body_actor:
                        self.hw_body_actor.play(self.current_animation)

    def stop_body_animation(self):
        if self.current_animation != "zero":
            self.is_posed = True
            self.store_body_adjusted = True
            self.store_body_playing = False
            self.store_body_frame = 0

            if self.cog_data.get("cog_type") == "boss" and hasattr(self, "boss_parts"):
                for part_name, part_actor in self.boss_parts.items():
                    if part_name == "head": continue
                    if isinstance(part_actor, Actor):
                        part_actor.pose(self.current_animation, 0)

            elif self.actor:
                self.actor.pose(self.current_animation, 0)
                if hasattr(self, 'skelecog') and self.skelecog:
                    self.skelecog.pose(self.current_animation, 0)
                if hasattr(self, 'zapped_skelecog') and self.zapped_skelecog:
                    self.zapped_skelecog.pose(self.current_animation, 0)
                if hasattr(self, 'hw_body_actor') and self.hw_body_actor:
                    self.hw_body_actor.pose(self.current_animation, 0)

            self.control_panel.body_frame_slider.set(0)

    def play_head_animation(self):
        active_head = self.get_active_head()
        if active_head and isinstance(active_head, Actor) and self.current_head_animation != "zero":
            self.is_posed = False
            self.store_head_adjusted = False
            self.store_head_playing = True
            self.store_head_frame = 0

            if self.control_panel.loop_head_var.get():
                active_head.loop(self.current_head_animation)
            else:
                active_head.play(self.current_head_animation)

    def stop_head_animation(self):
        active_head = self.get_active_head()
        if active_head and isinstance(active_head, Actor) and self.current_head_animation != "zero":
            self.is_posed = True
            self.store_head_adjusted = True
            self.store_head_playing = False
            self.store_head_frame = 0

            active_head.pose(self.current_head_animation, 0)
            self.control_panel.head_frame_slider.set(0)

    def on_prop1_anim_select(self, event):
        anim_name = self._get_selected_from_listbox(event)
        if anim_name and self.prop_item1_actor:
            self.prop_item1_actor.stop()
            num_frames = self.prop_item1_actor.getNumFrames(anim_name)
            self.control_panel.update_prop_slider_range(self.control_panel.prop1_anim_slider, num_frames)

            if self.control_panel.is_autoplay_var.get():
                self.play_prop1_animation(anim_name)
            else:
                self.prop_item1_actor.pose(anim_name, 0)

    def play_prop1_animation(self, anim_name=None):
        if not self.prop_item1_actor: return
        if not anim_name:
            anim_name = self.prop_item1_actor.getCurrentAnim()
        if not anim_name: return

        if self.control_panel.prop1_loop_var.get():
            self.prop_item1_actor.loop(anim_name)
        else:
            self.prop_item1_actor.play(anim_name)
        self.prop_item1_actor.setBlend(frameBlend=True)
        self.prop_item1_actor.setTwoSided(True)

    def stop_prop1_animation(self):
        if self.prop_item1_actor and self.prop_item1_actor.getCurrentAnim():
            anim_name = self.prop_item1_actor.getCurrentAnim()
            self.prop_item1_actor.pose(anim_name, 0)
            self.control_panel.prop1_anim_slider.set(0)

    def update_prop1_pose(self, frame_value):
        if self.prop_item1_actor and self.prop_item1_actor.getCurrentAnim():
            frame = int(round(float(frame_value)))
            self.prop_item1_actor.pose(self.prop_item1_actor.getCurrentAnim(), frame)

    def on_prop2_anim_select(self, event):
        anim_name = self._get_selected_from_listbox(event)
        if anim_name and self.prop_item2_actor:
            self.prop_item2_actor.stop()
            num_frames = self.prop_item2_actor.getNumFrames(anim_name)
            self.control_panel.update_prop_slider_range(self.control_panel.prop2_anim_slider, num_frames)

            if self.control_panel.is_autoplay_var.get():
                self.play_prop2_animation(anim_name)
            else:
                self.prop_item2_actor.pose(anim_name, 0)

    def play_prop2_animation(self, anim_name=None):
        if not self.prop_item2_actor: return
        if not anim_name:
            anim_name = self.prop_item2_actor.getCurrentAnim()
        if not anim_name: return

        if self.control_panel.prop2_loop_var.get():
            self.prop_item2_actor.loop(anim_name)
        else:
            self.prop_item2_actor.play(anim_name)
        self.prop_item2_actor.setBlend(frameBlend=True)
        self.prop_item2_actor.setTwoSided(True)

    def stop_prop2_animation(self):
        if self.prop_item2_actor and self.prop_item2_actor.getCurrentAnim():
            anim_name = self.prop_item2_actor.getCurrentAnim()
            self.prop_item2_actor.pose(anim_name, 0)
            self.control_panel.prop2_anim_slider.set(0)

    def update_prop2_pose(self, frame_value):
        if self.prop_item2_actor and self.prop_item2_actor.getCurrentAnim():
            frame = int(round(float(frame_value)))
            self.prop_item2_actor.pose(self.prop_item2_actor.getCurrentAnim(), frame)

    def toggle_blend(self):
        self.is_blend = not self.is_blend
        self.control_panel.is_blend_var.set(self.is_blend)
        if self.actor:
            self.actor.setBlend(frameBlend=True)
        if hasattr(self, 'head') and self.head:
            self.head.setBlend(frameBlend=True)

    def build_cog(self, suit_type=None, refresh_cog=True):
        pos = (0, 0, 0)
        hpr = (180, 0, 0)

        self.skele_meter_color = 0
        self.flatten_switch = 0

        self.current_head_animation = "zero"
        self.current_animation = "zero"
        self.is_posed = False
        self.control_panel.show_suit_library(True)
        self.control_panel.show_body_toggle(True)

        if not self.actor == None:
            pos = self.actor.getPos()
            current_hpr = self.actor.getHpr()

            prev_is_boss = False
            if self.cog_data:
                prev_is_boss = self.cog_data.get("cog_type") == "boss"

            if prev_is_boss:
                hpr = globals.DEFAULT_HPR
            else:
                hpr = current_hpr

            self.actor.cleanup()
            self.actor.removeNode()

            if hasattr(self, 'hw_body_actor') and self.hw_body_actor:
                self.taskMgr.remove("UpdateHWBodyTask")
                self.hw_body_actor.cleanup()
                self.hw_body_actor.removeNode()
                self.hw_body_actor = None

        if hasattr(self, 'boss_parts'):  # Cleanup old boss parts
            for part in self.boss_parts.values():
                if isinstance(part, Actor): part.cleanup()
                part.removeNode()
        self.boss_parts = {}  # Reset

        head_path = ""
        head_animations = {}

        cog_data = globals.COG_DATA[self.current_cog]
        self.cog_data = cog_data
        dept = cog_data["dept"]

        self.clear_pie_splats()

        if suit_type == None:
            suit_type = self.cog_data["suit"]

        if "legacy" in suit_type:
            self.build_legacy(cog_data, suit_type)
            self.suit_type = suit_type

            self.control_panel.is_shadow_var.set(True)
            self.is_shadow = True
            self.shadow.show()
            self.is_costume_active = False
            self.control_panel.is_body_var.set(True)
            self.is_body = True

            # Hide irrelevant toggles
            self.control_panel.suit_exec_check.pack_forget()
            self.control_panel.suit_fired_check.pack_forget()
            self.control_panel.hide_tie_list()

            if refresh_cog:
                self.reset_stored_vals()
            return

        if cog_data.get("cog_type") == "boss":
            self.build_boss_cog(cog_data)
            return

        self.build_body(suit_type)

        ##### SET SUIT/NECKTIE TEXTURE ########################################
        tx_suit = loader.loadTexture(cog_data["suitTex"])
        if suit_type in ["erfit"] or cog_data['name'] in ["ttcc_ene_counterfit"]:
            self.actor.find('**/body').setTexture(tx_suit, 1)
        else:
            self.actor.find('**/body').setTexture(tx_suit, 1)
            self.actor.find('**/necktie-s').setTexture(tx_suit, 1)
            self.actor.find('**/necktie-w').setTexture(tx_suit, 1)
            self.actor.find('**/bowtie').setTexture(tx_suit, 1)

        # Fix for Bellringer & Insider, set their hand textures
        if suit_type == "bc":
            self.actor.find('**/hands').setTexture(tx_suit, 1)

        if (suit_type == "mph"):
            tx_body = loader.loadTexture(globals.MP_BODY)
            self.actor.find('**/bowtie').setTexture(tx_body, 1)
            self.actor.find('**/highroller_body').setTexture(tx_body, 1)

        # Call build_necktie function
        if suit_type not in globals.NO_NECKTIE_SUITS:
            self.build_necktie()
        else:
            self.control_panel.hide_tie_list()
            if suit_type not in ["erfit"]:
                self.actor.find('**/necktie-s').hide()  # Hide Sellbot necktie
                self.actor.find('**/necktie-w').hide()  # Hide Cash/Boss/Board necktie
                self.actor.find('**/bowtie').hide()  # Hide Law bowtie

        self.head = loader.loadModel(cog_data["head"])

        if suit_type not in ["bossCog"]:
            already_skel = suit_type in ["as", "bs", "cs"]

            if not already_skel:
                if "hands" in cog_data:
                    hands_np = self.actor.find('**/hands')
                    if not hands_np.isEmpty():
                        hands_np.setColor(cog_data["hands"])

                medallion = cog_data.get("emblem", "emblem_corp")
                chest_null = self.actor.find("**/joint_attachMeter")
                if not chest_null.isEmpty():
                    self.iconbase = loader.loadModel(globals.COG_ICONS_BASE)
                    self.iconbase.reparentTo(chest_null)
                    chest_null.setH(0)
                    self.iconbase.setPosHprScale(*globals.COG_ICON_HPR)

                    for emb in ['emblem_hp', 'glow', 'emblem_sales', 'emblem_money', 'emblem_legal', 'emblem_corp',
                                'emblem_board']:
                        target = self.iconbase.find(f'**/{emb}')
                        if not target.isEmpty():
                            target.hide()

                    target_med = self.iconbase.find(f'**/{medallion}')
                    if not target_med.isEmpty():
                        target_med.show()

                    if suit_type in ["a", "af", "cch", "mph", "hr"]:
                        self.iconbase.setY(-0.10)
                    elif suit_type in ["c"]:
                        self.iconbase.setY(0.10)
                    elif suit_type in ["cf"]:
                        self.iconbase.setY(0.02);
                        self.iconbase.setZ(0.23);
                        self.iconbase.setP(2.5)
                    elif suit_type in ["erfit"]:
                        self.iconbase.setPosHprScale(0.00, 0.04, 0.00, 180.00, 349.70, 0.00, 1.00, 1.00, 1.00)
                    else:
                        self.iconbase.setY(0.00)

                    if suit_type == "hr": self.iconbase.hide()
            else:
                self.health_meter = self.actor.find("**/emblem_healthmeter")
                self.meter_glow = self.actor.find('**/glow')

        # Set up head animations

        cog_name = cog_data["name"]

        head_anim_dict, head_anims = globals.HEAD_ANIMATION_PATH(cog_name)
        head_path = cog_data["head"]

        self.available_head_animations = head_anims
        head_animations = head_anim_dict

        if len(head_anims) > 1:
            self.head = Actor(head_path, head_animations)
        else:
            self.head = loader.loadModel(head_path)

        self.head.reparentTo(self.actor.find('**/joint_head'))

        # Head resize for specific cogs
        if "headSize" in cog_data:
            self.head.setScale(cog_data["headSize"])

        if cog_data["name"] in ["ttcc_ene_prethinker"]:
            self.head.find('**/brain').setScale(0.95)

        # Move down treekiller's head
        if "headPos" in cog_data:
            self.head.setZ(cog_data["headPos"])
            if "headPosY" in cog_data:
                self.head.setY(cog_data["headPosY"])
            if "headPosP" in cog_data:
                self.head.setP(cog_data["headPosP"])
            if "headPosH" in cog_data:
                self.head.setH(cog_data["headPosH"])

        # Satellite Investor Colors
        if "bodyColor" in cog_data:
            self.actor.find('**/body').setColor(cog_data["bodyColor"])
            self.head.setColor(cog_data["bodyColor"])

        # Skelecog Head Texture
        if "headTex" in cog_data:
            head_texture = loader.loadTexture(cog_data["headTex"])
            self.head.setTexture(head_texture, 1)

        # Chainsaw and Scapegoat Fix
        if cog_data["name"] in ["ttcc_ene_chainsaw", "ttcc_ene_scapegoat"]:
            self.actor.setTwoSided(True)

        # Conveyancer Belt Fix
        if "belt" in cog_data:
            belt = loader.loadModel(cog_data["belt"])
            belt.reparentTo(self.head)

        self.actor.setScale(cog_data["scale"])

        self.actor.setPos(pos)
        self.actor.setHpr(hpr)

        if hasattr(self, 'control_panel') and hasattr(self.control_panel, 'rotation_var'):
            self.control_panel.rotation_var.set(hpr[0])

        self.actor.reparentTo(render)
        self.actor.setBlend(frameBlend=True)
        if hasattr(self.head, "getAnimNames"):
            self.head.setBlend(frameBlend=True)
        # self.actor.find("**/joint_attachMeter").setHpr(*globals.COG_ICON_HPR)

        self.suit_type = suit_type

        self.control_panel.update_animation_lists(
            self.available_animations,
            self.available_head_animations
        )

        # Reset Toggles
        self.control_panel.update_anim_slider_range("body", 0)
        self.control_panel.update_anim_slider_range("head", 0)

        self.control_panel.is_shadow_var.set(True)
        self.is_shadow = True
        self.shadow.show()
        self.is_costume_active = False
        self.control_panel.is_body_var.set(True)
        self.control_panel.is_costume_var.set(False)
        self.control_panel.is_executive_var.set(False)
        self.control_panel.is_fired_var.set(False)
        self.control_panel.is_waiter_var.set(False)
        self.control_panel.is_skelecog_var.set(False)
        self.is_body = True

        if refresh_cog and not getattr(self, 'is_swapping_body', False):
            self.is_costume_active = False
            self.control_panel.is_costume_var.set(False)
            self.control_panel.is_executive_var.set(False)
            self.control_panel.is_fired_var.set(False)
            self.control_panel.is_waiter_var.set(False)
            self.control_panel.is_skelecog_var.set(False)
            if hasattr(self.control_panel, 'is_zapped_var'):
                self.control_panel.is_zapped_var.set(False)

            if hasattr(self.control_panel, 'selected_suit_mod_var'):
                self.control_panel.selected_suit_mod_var.set("")

            self.store_skelecog_skull = None
            self.store_skel_head_name = None

        suitToggle = self.cog_data.get("suitToggle")
        dept = self.cog_data.get("dept")

        # Hide main panel toggles
        self.control_panel.suit_exec_check.pack_forget()
        self.control_panel.suit_fired_check.pack_forget()
        self.control_panel.suit_waiter_check.pack_forget()
        self.control_panel.skel_wrapper.pack_forget()
        self.control_panel.unique_frame.grid_remove()  # Hide specific manager toggles

        if hasattr(self.control_panel, 'suit_costume_check'):
            self.control_panel.suit_costume_check.pack_forget()
            self.control_panel.suit_is_boogie.pack_forget()

        if suitToggle in ["y", "s", "u"]:
            # Show standard toggles
            self.control_panel.suit_exec_check.pack(anchor="w", padx=5)
            self.control_panel.suit_fired_check.pack(anchor="w", padx=5)
            # Show waiter check *only* for Bossbots
            if dept == "c":
                self.control_panel.suit_waiter_check.pack(anchor="w", padx=5)

        # Show the unique manager toggles for those specific cogs
        if suitToggle in ["hr", "rm", "dj", "u", "chainsaw", "ms", "ds3"]:
            self.control_panel.unique_frame.config(text=f"{self.current_cog}")
            self.control_panel.unique_frame.grid()

            self.control_panel.fill_unique_frame(suitToggle)

        if self.suit_type not in ["as", "bs", "cs", "boss"]:
            self.control_panel.skel_wrapper.pack(fill="x", pady=0)

        if self.cog_data and self.cog_data.get("hasHalloween"):
            self.control_panel.suit_costume_check.pack(anchor="w", padx=5, pady=2)

        if self.custom_model and not self.custom_model.isEmpty():
            self.custom_model.removeNode()
            self.custom_model = None
        self.control_panel.show_custom_model_tab(False)

        self.control_panel.selected_tie_var.set("(Default)")

        # Used to refresh the store variables used for apply suit model function
        if refresh_cog:
            self.reset_stored_vals()

        # Stupid suit library model fix for when chainsaw has bulb broken
        if self.store_cs_toggle_2:
            self.head.find('**/bulbLeft').hide()

    def build_legacy(self, cog_data, suit_type):  # for skelecogs (unimplmented forever)
        model_key = suit_type
        body_path = globals.SUIT_MODEL_DICT.get(model_key)
        cog_name = self.cog_data["name"]

        if suit_type.endswith("_b"):
            anim_key = "b"
        elif suit_type.endswith("_c"):
            anim_key = "c"
        else:
            anim_key = "a"

        anims = {}

        if anim_key == "a":
            anims = globals.SUIT_A_ANIMATION_DICT
            self.available_animations = globals.SUIT_A_ANIMATIONS
        elif anim_key == "b":
            anims = globals.SUIT_B_ANIMATION_DICT
            self.available_animations = globals.SUIT_B_ANIMATIONS
        else:
            anims = globals.SUIT_C_ANIMATION_DICT
            self.available_animations = globals.SUIT_C_ANIMATIONS

        self.actor = Actor(body_path, anims)
        self.actor.reparentTo(self.render)
        self.actor.setPos(0, 0, 0)
        self.actor.setH(180)
        self.actor.setBlend(frameBlend=True)
        self.actor.setTwoSided(True)

        TEXTURE_MAP = {
            "cogRobots_palette_3cmla_1.jpg": "phase_5/maps/cogRobots_palette_3cmla_1.png",
            "cogRobots_palette_1lmla_1.jpg": "phase_5/maps/cogRobots_palette_1lmla_1.png",
            "phase_5_palette_4amla_1.jpg": "phase_5/maps/phase_5_palette_4amla_1.png",
            "cogB_tie_instrumentB.jpg": "phase_5/maps/cogB_tie_instrumentB.png",
            "cogRobots_palette_4amla_1.jpg": "phase_5/maps/cogRobots_palette_4amla_1.png",
            "cogRobots_palette_2tmla_1.jpg": "phase_5/maps/cogRobots_palette_2tmla_1.png",
            "phase_5_palette_1lmla_1.jpg": "phase_5/maps/phase_5_palette_1lmla_1.png"
        }

        for part in self.actor.findAllMatches("**/+GeomNode"):
            node = part.node()
            for i in range(node.getNumGeoms()):
                state = node.getGeomState(i)
                tex_attrib = state.getAttrib(TextureAttrib)

                if tex_attrib:
                    for stage in tex_attrib.getOnStages():
                        tex = tex_attrib.getOnTexture(stage)

                        if tex:
                            current_name = tex.getFilename().getBasename()

                            if current_name in TEXTURE_MAP:
                                new_path = TEXTURE_MAP[current_name]
                                new_path = os.path.join(globals.RESOURCES_DIR, new_path).replace("\\", "/")

                                if os.path.exists(new_path):
                                    new_tex = loader.loadTexture(new_path)
                                    # new_tex.setMinfilter(Texture.FTLinearMipmapLinear)
                                    # new_tex.setMagfilter(Texture.FTLinear)
                                    new_attrib = tex_attrib.addOnStage(stage, new_tex)
                                    new_state = state.setAttrib(new_attrib)

                                    node.setGeomState(i, new_state)

        scale = cog_data.get("scale", 1.0)
        self.actor.setScale(scale)

        parts = self.actor.findAllMatches('**/pPlane*')
        for part in parts:
            part.setTwoSided(True)

        dept = cog_data.get("dept")
        tie = self.actor.find('**/tie')
        tie.setColor(1, 1, 1, 1)
        if not tie.isEmpty():
            tie_map = {
                'c': 'phase_5/maps/cog_robot_tie_boss.png',
                's': 'phase_5/maps/cog_robot_tie_sales.png',
                'l': 'phase_5/maps/cog_robot_tie_legal.png',
                'm': 'phase_5/maps/cog_robot_tie_money.png',
                'g': 'phase_5/maps/cog_robot_tie_board.png'
            }
            tex_path = os.path.join(globals.RESOURCES_DIR, tie_map.get(dept, 'c'))
            tex_path = tex_path.replace("\\", "/")

            try:
                if cog_name in ["wsi"]:
                    tieTex = loader.loadTexture("phase_5/maps/cog_robot_tie_legal_exec.png")
                elif cog_name in ["dola"]:
                    tieTex = loader.loadTexture("phase_5/maps/cog_robot_tie_sales_exec.png")
                elif cog_name in ["dopr"]:
                    tieTex = loader.loadTexture("phase_5/maps/cog_robot_tie_board_exec.png")
                else:
                    tieTex = loader.loadTexture(tex_path)
                tie.setTexture(tieTex, 1)
            except:
                print("wherer tie")

        self.head = self.actor.find("**/joint_head")

        self.available_head_animations = []
        self.control_panel.update_animation_lists(self.available_animations, [])

        self.shadow.reparentTo(self.actor.find('**/joint_shadow'))

        if "bodyColor" in cog_data:
            self.actor.setColor(cog_data["bodyColor"])

        chest_null = self.actor.find("**/joint_attachMeter")
        gear = loader.loadModel('phase_5/models/gui/skele_gear.bam')
        gear.reparentTo(self.actor.find("**/joint_attachMeter"))
        gear.setColor(1, 1, 1, 1)
        chest_null.clearColor()

        if not chest_null.isEmpty():
            self.iconbase = loader.loadModel(globals.COG_ICONS_BASE)
            self.iconbase.reparentTo(chest_null)
            if suit_type.endswith("_b"):
                self.iconbase.setPosHprScale(0.00, 0.00, 0.70, 180.00, 0.00, 0.00, 1.00, 1.00, 1.00)
                gear.setPosHprScale(0.00, 0.00, 0.71, 180.00, 0.00, 0.00, 0.96, 0.96, 0.96)
            elif suit_type.endswith("_c"):
                self.iconbase.setPosHprScale(0.00, -0.40, 0.49, 180.00, 0.00, 0.00, 1.00, 1.00, 1.00)
                gear.setPosHprScale(0.00, -0.40, 0.49, 180.00, 0.00, 0.00, 0.96, 0.96, 0.96)
            else:
                self.iconbase.setPosHprScale(0.00, -0.40, 0.49, 180.00, 345.00, 0.00, 1.00, 1.00, 1.00)
                gear.setPosHprScale(0.00, -0.36, 0.51, 180.00, 345.00, 0.00, 0.96, 0.96, 0.96)
            self.iconbase.setColor(1, 1, 1, 1)
            for node in self.iconbase.getChildren():
                node.hide()

            emblem = cog_data.get("emblem", "emblem_corp")
            target_emblem = self.iconbase.find(f'**/{emblem}')
            if not target_emblem.isEmpty():
                target_emblem.show()

    def build_body(self, suit_type):
        body_path = ""
        body_animations = {}

        body_path = globals.SUIT_MODEL_DICT.get(suit_type, None)

        if body_path is None:
            print(f"Warning: Suit type '{suit_type}' not recognized.")

        if (suit_type in ["a", "af", "hr", "as", "mph", "cch", "erfit"]):
            body_animations = globals.SUIT_A_ANIMATION_DICT
            self.available_animations = globals.SUIT_A_ANIMATIONS
        elif (suit_type in ["b", "bf", "bc", "ps", "rm", "bs"]):
            body_animations = globals.SUIT_B_ANIMATION_DICT
            self.available_animations = globals.SUIT_B_ANIMATIONS
        elif (suit_type in ["c", "cf", "cs"]):
            body_animations = globals.SUIT_C_ANIMATION_DICT
            self.available_animations = globals.SUIT_C_ANIMATIONS
        elif (suit_type in ["bossCog"]):
            body_animations = globals.BOSS_COG_ANIMATION_DICT
            self.available_animations = globals.BOSS_COG_ANIMATIONS

        self.actor = Actor(body_path, body_animations)
        shadow_joint = self.actor.find('**/joint_shadow')
        if not shadow_joint.isEmpty():
            self.shadow.reparentTo(shadow_joint)
        else:
            pass

    def build_necktie(self):
        cog_data = self.cog_data
        self.control_panel.show_tie_list()

        # We hide the neckties by default, then re-enable them for departments
        self.actor.find('**/necktie-s').hide()  # Sellbot
        self.actor.find('**/necktie-w').hide()  # Cashbot, Bossbot, Boardbot
        self.actor.find('**/bowtie').hide()  # Lawbot

        if cog_data["cog"] not in globals.NO_NECKTIE_COGS:
            necktie_map = globals.NECKTIE_MAP
            necktie = necktie_map.get(cog_data["cog"]) or necktie_map.get(
                cog_data["dept"])  # Search by cog name or department
            self.actor.find(necktie).show()  # Find the appropriate necktie and unhide it

    def set_suit_texture(self, trigger=None):
        if not self.cog_data: return

        is_exec = self.control_panel.is_executive_var.get()
        is_fired = self.control_panel.is_fired_var.get()
        is_waiter = self.control_panel.is_waiter_var.get()

        is_toggled_skel = hasattr(self, 'control_panel') and self.control_panel.is_skelecog_var.get()
        already_skel = self.suit_type in ["as", "bs", "cs"]
        is_skelecog = is_toggled_skel or already_skel

        not_erfit = self.suit_type != "erfit"

        if trigger == "fired" and is_fired:
            self.control_panel.is_executive_var.set(False)
            self.control_panel.is_waiter_var.set(False)
            is_exec = False
            is_waiter = False

        elif trigger == "exec" and is_exec:
            self.control_panel.is_fired_var.set(False)
            is_fired = False

        elif trigger == "waiter" and is_waiter:
            self.control_panel.is_fired_var.set(False)
            is_fired = False

        if not is_skelecog and not_erfit:
            if is_waiter:
                self.set_necktie("Bowtie")
            else:
                if hasattr(self, 'control_panel'):
                    self.control_panel.on_tie_select_radio()

        cog_name = self.cog_data["name"]
        dept = self.cog_data["dept"]
        paths = globals.SUIT_TEXTURE_PATH

        orig_suit = self.cog_data.get("suit", "")
        was_originally_skel = orig_suit in ["as", "bs", "cs"]

        if already_skel:
            base_tex_key = dept + "s"
        elif cog_name in paths and not was_originally_skel:
            base_tex_key = cog_name
        else:
            base_tex_key = dept

        tex_list = paths.get(base_tex_key)
        if not tex_list: return

        tex_index = 0
        if is_fired:
            tex_index = -1
        elif is_waiter and base_tex_key in ["c", "cs"] and len(tex_list) > 3:
            tex_index = 3 if is_exec else 2
        elif is_exec and len(tex_list) > 1:
            tex_index = 1

        tex_to_apply = tex_list[tex_index]

        if tex_index == 0 and not already_skel:
            if "suitTex" in self.cog_data and not was_originally_skel:
                tex_to_apply = self.cog_data["suitTex"]

        tx_suit = loader.loadTexture(tex_to_apply)

        if not already_skel:
            self.actor.find('**/body').setTexture(tx_suit, 1)
            if (not self.actor.find('**/hands').isEmpty()):
                self.actor.find('**/hands').setTexture(tx_suit, 1)
            if not_erfit:
                for tie in ['**/necktie-s', '**/necktie-w', '**/bowtie']:
                    np = self.actor.find(tie)
                    if not np.isEmpty(): np.setTexture(tx_suit, 1)
            self.store_suit_texture = tex_to_apply

        skel_tex_key = dept + "s"
        skel_tex_list = paths.get(skel_tex_key)
        if skel_tex_list:
            if is_waiter:
                skel_tex_path = f"{globals.RESOURCES_DIR}/phase_5/maps/ttcc_ene_skelecog_waiter.png"
            elif is_fired:
                skel_tex_path = skel_tex_list[-1]
            elif is_exec and len(skel_tex_list) > 1:
                skel_tex_path = skel_tex_list[1]
            else:
                if was_originally_skel and "suitTex" in self.cog_data:
                    skel_tex_path = self.cog_data["suitTex"]
                else:
                    skel_tex_path = skel_tex_list[0]

            skel_tx_suit = loader.loadTexture(skel_tex_path)
            self.store_skelecog_texture = skel_tex_path
            self.store_skel_head_tex = skel_tx_suit

            selected_mod = None
            if hasattr(self, 'control_panel') and self.control_panel.selected_suit_mod_var.get():
                selected_mod = self.control_panel.selected_suit_mod_var.get()

            is_override = selected_mod and selected_mod not in ["as", "bs", "cs"]

            skelecog_body_tex = tx_suit if is_override else skel_tx_suit
            zapped_body_tex = skel_tx_suit

            if already_skel:
                for part in ['body', 'necktie-s', 'necktie-w', 'bowtie']:
                    np = self.actor.find(f'**/{part}')
                    if not np.isEmpty(): np.setTexture(skel_tx_suit, 1)
                if hasattr(self, 'apply_skelecog_hand_color'):
                    self.apply_skelecog_hand_color(self.actor)
                orig_suit = self.cog_data.get("suit", "")
                if orig_suit in ["as", "bs", "cs"]:
                    if hasattr(self, 'head') and self.head:
                        self.head.setTexture(skel_tx_suit, 1)

            if hasattr(self, 'zapped_skelecog') and self.zapped_skelecog:
                for part in ['body', 'necktie-s', 'necktie-w', 'bowtie']:
                    np = self.zapped_skelecog.find(f'**/{part}')
                    if not np.isEmpty(): np.setTexture(zapped_body_tex, 1)
                if hasattr(self, 'apply_skelecog_hand_color'):
                    self.apply_skelecog_hand_color(self.zapped_skelecog)

            if hasattr(self, 'skelecog') and self.skelecog:
                for part in ['body', 'necktie-s', 'necktie-w', 'bowtie']:
                    np = self.skelecog.find(f'**/{part}')
                    if not np.isEmpty(): np.setTexture(skelecog_body_tex, 1)
                if hasattr(self, 'apply_skelecog_hand_color'):
                    self.apply_skelecog_hand_color(self.skelecog)

            for head_attr in ['zapped_head', 'skelecog_skull']:
                head_node = getattr(self, head_attr, None)
                if head_node and not head_node.isEmpty():
                    head_node.setTexture(skel_tx_suit, 1)

        if self.cog_data.get("suitToggle", "") in ["s"]:
            if hasattr(self, 'head') and self.head:
                self.head.setTexture(tx_suit, 1)
                self.store_head_texture = tex_to_apply

        elif cog_name in ["cc_a_ene_bagholder", "cc_a_ene_insider", "cc_a_ene_headhoncho"]:
            head_tex_list = globals.HEAD_TEXTURE_PATH.get(base_tex_key)
            if head_tex_list:
                head_tex = head_tex_list[0]
                if is_fired:
                    head_tex = head_tex_list[-1]
                elif is_exec:
                    head_tex = head_tex_list[1]
                self.head.setTexture(loader.loadTexture(head_tex), 1)
                self.store_head_texture = head_tex

    def u_toggle_setup(self, i, head=None):
        if not head:
            head = self.head
        head_paths = globals.HEAD_TEXTURE_PATH.get(self.cog_data["name"])
        tx_head = loader.loadTexture(head_paths[i])
        head.setTexture(tx_head, 1)
        self.store_head_texture = head_paths[i]

    def multislacker_toggles(self, *args):
        is_static = self.control_panel.unique_vars["ms_toggle_1"].get()
        is_interval = self.control_panel.unique_vars.get("ms_toggle_2", tk.BooleanVar(value=False)).get()

        self.store_ms_toggle_1 = is_static
        self.store_ms_toggle_2 = is_interval

        if is_interval:
            if not self.taskMgr.hasTaskNamed("MultislackerStaticTask"):
                self.ms_static_state = 1 if is_static else 0
                self.taskMgr.doMethodLater(2.0, self.ms_static_interval_task, "MultislackerStaticTask")
        else:
            if self.taskMgr.hasTaskNamed("MultislackerStaticTask"):
                self.taskMgr.remove("MultislackerStaticTask")
            self.u_toggle_setup(1 if is_static else 0)

    def ms_static_interval_task(self, task):
        self.ms_static_state = 1 if self.ms_static_state == 0 else 0
        self.u_toggle_setup(self.ms_static_state)

        if "ms_toggle_1" in self.control_panel.unique_vars:
            self.control_panel.unique_vars["ms_toggle_1"].set(self.ms_static_state == 1)
            self.store_ms_toggle_1 = (self.ms_static_state == 1)

        return task.again

    def duck_shuffler_toggles(self):
        self.cycle_slot_l()
        self.cycle_slot_m()
        self.cycle_slot_r()

    def high_roller_toggles(self):
        i = 1 if self.control_panel.unique_vars["hr_toggle_1"].get() else 0

        suit_paths = globals.SUIT_TEXTURE_PATH.get("hr")
        body_paths = globals.HEAD_TEXTURE_PATH.get("hr")

        tx_suit = loader.loadTexture(suit_paths[i])
        tx_body = loader.loadTexture(body_paths[i])

        self.actor.find('**/body').setTexture(tx_suit, 1)
        if self.suit_type in ["hr"]:
            self.actor.find('**/highroller_body').setTexture(tx_body, 1)

        self.store_suit_texture = suit_paths[i]
        self.store_hr_toggle_1 = (i == 1)

    def update_rainmaker(self):
        offsets = {
            "Inversion": 0.0,
            "Heavy Rain": 0.2,
            "Oil Rain": 0.4,
            "Storm Cell": 0.6,
            "Fog": 0.8
        }

        if hasattr(self, 'head') and self.head:
            weather = self.control_panel.unique_vars["rm_weather"].get()

            self.store_rm_weather = weather

            for Hair in self.head.findAllTextureStages("*hair"):
                self.head.setTexOffset(Hair, 0, offsets.get(weather, 0.0))

    def chainsaw_consultant_toggles(self, toggle_id):
        lookup_var = self.control_panel.unique_vars[f"cs_toggle_{toggle_id}"]
        var_state = lookup_var.get()
        if toggle_id == 1:
            self.u_toggle_setup(int(var_state))
            self.store_cs_toggle_1 = var_state
            cc_head_list = [self.zapped_head, self.skelecog_skull]
            for head in cc_head_list:
                if head:
                    self.u_toggle_setup(int(var_state), head)
        if toggle_id == 2:
            bulb = self.head.find('**/bulbLeft')
            if not bulb.isEmpty():
                if var_state:
                    bulb.hide()
                else:
                    bulb.show()
            self.store_cs_toggle_2 = var_state
        if toggle_id == 3:
            bulb = self.head.find('**/bulbRight')
            if not bulb.isEmpty():
                if var_state:
                    bulb.hide()
                else:
                    bulb.show()
            self.store_cs_toggle_3 = var_state

    def desk_jockey_toggles(self):
        is_brian = self.control_panel.unique_vars["dj_toggle_1"].get()
        is_exec = self.control_panel.unique_vars["dj_toggle_2"].get()

        # Brianbot Exe = 2, Brianbot = 1, Normal = 0
        if is_brian and is_exec:
            i = 2
        elif is_brian:
            i = 1
        else:
            i = 0

        suit_paths = globals.SUIT_TEXTURE_PATH.get("dj")
        tx_suit = loader.loadTexture(suit_paths[i])

        self.actor.find('**/body').setTexture(tx_suit, 1)
        self.actor.find('**/bowtie').setTexture(tx_suit, 1)

        self.store_suit_texture = suit_paths[i]
        self.store_dj_toggle_1 = is_brian
        self.store_dj_toggle_2 = is_exec

    def toggle_unique_suit(self, iterate=True):
        if not self.cog_data: return

        self.store_unique_suit_toggle = True
        cog_name = self.cog_data["name"]
        suitToggle = self.cog_data.get("suitToggle")

        # Chainsaw Consultant
        if suitToggle == "chainsaw":
            suit_paths = globals.SUIT_TEXTURE_PATH.get(cog_name)
            head_paths = globals.HEAD_TEXTURE_PATH.get(cog_name)
            if iterate:
                self.it = (self.it + 1) % len(suit_paths)
            tx_suit = loader.loadTexture(suit_paths[self.it])
            tx_head = loader.loadTexture(head_paths[self.it])
            self.actor.find('**/body').setTexture(tx_suit, 1)
            self.actor.find('**/necktie-w').setTexture(tx_suit, 1)
            self.head.setTexture(tx_head, 1)
            if self.it > 1:
                self.head.find('**/bulbLeft').hide()
            else:
                self.head.find('**/bulbLeft').show()

        # Multislacker
        elif suitToggle == "ms":
            suit_paths = globals.SUIT_TEXTURE_PATH.get(cog_name)
            head_paths = globals.HEAD_TEXTURE_PATH.get(cog_name)
            if iterate:
                self.it = (self.it + 1) % len(suit_paths)
            tx_head = loader.loadTexture(head_paths[self.it])
            self.head.setTexture(tx_head, 1)
            self.store_head_texture = head_paths[self.it]

        # High Roller
        elif suitToggle == "hr":
            suit_paths = globals.SUIT_TEXTURE_PATH.get("hr")
            body_paths = globals.HEAD_TEXTURE_PATH.get("hr")
            if iterate:
                self.it = (self.it + 1) % len(suit_paths)
            tx_suit = loader.loadTexture(suit_paths[self.it])
            tx_body = loader.loadTexture(body_paths[self.it])
            self.actor.find('**/body').setTexture(tx_suit, 1)
            # check if the suit has the high roller model
            if self.suit_type in ["hr"]:
                self.actor.find('**/highroller_body').setTexture(tx_body, 1)
            self.store_suit_texture = suit_paths[self.it]

        # Rainmaker
        elif suitToggle == "rm":
            for Hair in self.head.findAllTextureStages("*hair"):
                if iterate:
                    self.it2 += 0.2
                if self.it2 == 1: self.it2 = 0
                self.head.setTexOffset(Hair, 0, self.it2)

        # Desk Jockey
        elif suitToggle == "dj":
            suit_paths = globals.SUIT_TEXTURE_PATH.get("dj")
            self.it = (self.it + 1) % len(suit_paths)
            tx_suit = loader.loadTexture(suit_paths[self.it])
            self.actor.find('**/body').setTexture(tx_suit, 1)
            self.actor.find('**/bowtie').setTexture(tx_suit, 1)
            self.store_suit_texture = suit_paths[self.it]

    def cycle_slot_l(self, iterate=True):
        if not self.head or self.head.isEmpty(): return
        self.store_cycle_slot_l = True
        slotL = self.head.find('**/slotL')
        if not slotL.isEmpty():
            if iterate:
                self.it_l = (self.it_l + 0.25) % 1.0
            slotL.setTexOffset(TextureStage.getDefault(), 0, self.it_l)

    def cycle_slot_m(self, iterate=True):
        if not self.head or self.head.isEmpty(): return
        self.store_cycle_slot_m = True
        slotM = self.head.find('**/slotMid')
        if not slotM.isEmpty():
            if iterate:
                self.it_m = (self.it_m + 0.25) % 1.0
            slotM.setTexOffset(TextureStage.getDefault(), 0, self.it_m)

    def cycle_slot_r(self, iterate=True):
        if not self.head or self.head.isEmpty(): return
        self.store_cycle_slot_r = True
        slotR = self.head.find('**/slotR')
        if not slotR.isEmpty():
            if iterate:
                self.it_r = (self.it_r + 0.25) % 1.0
            slotR.setTexOffset(TextureStage.getDefault(), 0, self.it_r)

    def set_necktie(self, override=None):
        if self.suit_type in ["erfit"]:
            return

        cog_data = self.cog_data

        for tie_name in ['necktie-s', 'necktie-w', 'bowtie']:
            tie_node = self.actor.find(f'**/{tie_name}')
            if not tie_node.isEmpty(): tie_node.hide()

        for skel_attr in ['skelecog', 'zapped_skelecog', 'hw_body_actor']:
            skel_node = getattr(self, skel_attr, None)
            if skel_node and not skel_node.isEmpty():
                skel_node.find('**/necktie-s').hide()
                skel_node.find('**/necktie-w').hide()
                skel_node.find('**/bowtie').hide()

        tie_to_show = None
        if override and override != "(Default)":
            tie_override = {
                "Thin Tie": "**/necktie-s",
                "Wide Tie": "**/necktie-w",
                "Bowtie": "**/bowtie",
            }
            if override == "None":
                return
            tie_to_show = tie_override.get(override)
        else:
            if getattr(self, 'is_costume_active', False) and cog_data["cog"] == "chainsawconsultant":
                return

            if cog_data["cog"] in globals.NO_NECKTIE_COGS:
                return
            else:
                necktie_map = globals.NECKTIE_MAP
                tie_to_show = necktie_map.get(cog_data["cog"]) or necktie_map.get(cog_data["dept"])

        if tie_to_show:
            is_standalone_active = hasattr(self, 'control_panel') and hasattr(self.control_panel,
                                                                              'is_skelecog_var') and self.control_panel.is_skelecog_var.get()

            is_costume_overlay = hasattr(self, 'hw_body_actor') and self.hw_body_actor

            if not is_standalone_active and not is_costume_overlay:
                if self.suit_type not in globals.NO_NECKTIE_SUITS:
                    self.actor.find(tie_to_show).show()

            for skel_attr in ['skelecog', 'zapped_skelecog', 'hw_body_actor']:
                skel_node = getattr(self, skel_attr, None)
                if skel_node and not skel_node.isEmpty():
                    skel_node.find(tie_to_show).show()

    def _swap_head_model(self, new_model_path):
        if not new_model_path:
            return None

        vfs = VirtualFileSystem.getGlobalPtr()
        panda_path = Filename.fromOsSpecific(new_model_path)
        panda_path.makeTrueCase()

        if not (os.path.isfile(new_model_path) or vfs.exists(panda_path)):
            print(f"Warning: Could not find head model in OS or VFS: {new_model_path}")
            return None

        new_head = None
        anim_dict = {}

        if isinstance(self.head, Actor):
            if hasattr(self.head, "_anim_dict"):
                anim_dict = self.head._anim_dict
            elif hasattr(self.head, "getAnimNames"):
                anim_names = self.head.getAnimNames()
                for anim in anim_names:
                    anim_dict[anim] = self.head.getAnimFilename(anim)
            else:
                anim_dict = getattr(globals, "HEAD_ANIM_DICT", {}).get(self.current_cog, {})

        try:
            if anim_dict:
                new_head = Actor(panda_path, anim_dict)
            else:
                new_head = loader.loadModel(panda_path)
        except Exception as e:
            new_head = loader.loadModel(panda_path)

        if not new_head or new_head.isEmpty():
            print(f"Warning: Failed to load head model from {panda_path}")
            return None

        joint = self.actor.find('**/joint_head')
        if not joint.isEmpty():
            new_head.reparentTo(joint)
        else:
            new_head.reparentTo(self.actor)

        if hasattr(self, "head") and self.head is not None and not self.head.isEmpty():
            new_head.setPos(self.head.getPos())
            new_head.setHpr(self.head.getHpr())
            new_head.setScale(self.head.getScale())

        return new_head

    def texture_part_check(self, part_list, actor, texture):
        for part in part_list:
            np = actor.find(f'**/{part}')
            if not np.isEmpty():
                np.setTexture(texture, 1)

    def toggle_costume(self, active, check_stored=True):  # Toggle halloween costumes for managers
        cog_data = globals.COG_DATA.get(self.current_cog, None)
        if not cog_data: return

        cog_name = cog_data["name"]
        suit_type = cog_data.get("suit", "a")
        cog_id = cog_data.get("cog", "")

        def get_valid_texture_path(tex_value):
            if not tex_value: return None
            if isinstance(tex_value, (list, tuple)): tex_value = tex_value[0]
            if isinstance(tex_value, (str, bytes, os.PathLike)) and os.path.exists(tex_value): return tex_value
            return None

        hw_head_model_path = cog_data.get("headModel_HW")
        hw_body_model_path = cog_data.get("bodyModel_HW")
        if active:
            self.is_costume_active = True

            self.switch_toggle(self.control_panel.is_costume_var, self.control_panel.is_skelecog_var,
                               self.toggle_skelecog)

            if cog_id == "majorplayer" and hasattr(self, 'control_panel'):
                self.control_panel.suit_is_boogie.pack(anchor="w", padx=5, pady=2)

            vfs = VirtualFileSystem.getGlobalPtr()
            panda_hw_path = Filename.fromOsSpecific(hw_head_model_path) if hw_head_model_path else Filename("")

            if hw_head_model_path and (os.path.isfile(hw_head_model_path) or vfs.exists(panda_hw_path)):
                if check_stored:
                    self.set_stored_vals()

                new_head = self._swap_head_model(hw_head_model_path)
                if new_head is not None:
                    if hasattr(self, 'head') and self.head is not None:
                        self.head.detachNode()
                    self.head = new_head

                if check_stored:
                    self.update_cog_attributes(None, True)

            use_hw_body = False
            if hw_body_model_path and os.path.exists(hw_body_model_path):
                if self.suit_type == cog_data.get("suit", "a"):
                    use_hw_body = True

            if use_hw_body:
                if self.actor:
                    for part in ['body', 'hands', 'necktie-s', 'necktie-w', 'bowtie']:
                        np = self.actor.find(f'**/{part}')
                        if not np.isEmpty(): np.hide()
                    chest = self.actor.find("**/joint_attachMeter")
                    if not chest.isEmpty(): chest.hide()

                if suit_type in ["a", "af", "hr", "as", "mph", "cch", "erfit"]:
                    anims = globals.SUIT_A_ANIMATION_DICT
                elif suit_type in ["b", "bf", "bc", "ps", "rm", "bs"]:
                    anims = globals.SUIT_B_ANIMATION_DICT
                elif suit_type in ["c", "cf", "cs"]:
                    anims = globals.SUIT_C_ANIMATION_DICT
                else:
                    anims = {}

                self.hw_body_actor = Actor(hw_body_model_path, anims)
                self.hw_body_actor.reparentTo(self.actor)
                self.hw_body_actor.setBlend(frameBlend=True)

                if hasattr(self, 'head') and self.head and not self.head.isEmpty():
                    hw_head_joint = self.hw_body_actor.find('**/joint_head')
                    if not hw_head_joint.isEmpty(): self.head.reparentTo(hw_head_joint)

                if hasattr(self, 'prop_item1') and self.prop_item1 != "zero":
                    self.prop_item1.reparentTo(self.hw_body_actor.find('**/joint_Rhold'))
                if hasattr(self, 'prop_item1_actor') and self.prop_item1_actor:
                    self.prop_item1_actor.reparentTo(self.hw_body_actor.find('**/joint_Rhold'))

                if hasattr(self, 'prop_item2') and self.prop_item2 != "zero":
                    self.prop_item2.reparentTo(self.hw_body_actor.find('**/joint_Lhold'))
                if hasattr(self, 'prop_item2_actor') and self.prop_item2_actor:
                    self.prop_item2_actor.reparentTo(self.hw_body_actor.find('**/joint_Lhold'))

                if hasattr(self, 'iconbase') and self.iconbase:
                    hw_chest = self.hw_body_actor.find("**/joint_attachMeter")
                    if not hw_chest.isEmpty(): self.iconbase.reparentTo(hw_chest)

                self.sync_overlay_animation(self.hw_body_actor)
            else:
                if hasattr(self, 'hw_body_actor') and self.hw_body_actor:
                    if hasattr(self, 'head') and self.head and not self.head.isEmpty():
                        self.head.reparentTo(self.actor.find('**/joint_head'))
                    if hasattr(self, 'prop_item1') and self.prop_item1 != "zero":
                        self.prop_item1.reparentTo(self.actor.find('**/joint_Rhold'))
                    if hasattr(self, 'prop_item1_actor') and self.prop_item1_actor:
                        self.prop_item1_actor.reparentTo(self.actor.find('**/joint_Rhold'))
                    if hasattr(self, 'prop_item2') and self.prop_item2 != "zero":
                        self.prop_item2.reparentTo(self.actor.find('**/joint_Lhold'))
                    if hasattr(self, 'prop_item2_actor') and self.prop_item2_actor:
                        self.prop_item2_actor.reparentTo(self.actor.find('**/joint_Lhold'))
                    if hasattr(self, 'iconbase') and self.iconbase:
                        chest = self.actor.find("**/joint_attachMeter")
                        if not chest.isEmpty(): self.iconbase.reparentTo(chest)

                    self.hw_body_actor.cleanup()
                    self.hw_body_actor.removeNode()

                self.hw_body_actor = None

                if self.actor and getattr(self, 'is_body', True):
                    for part in ['body', 'hands']:
                        np = self.actor.find(f'**/{part}')
                        if not np.isEmpty(): np.show()
                    chest = self.actor.find("**/joint_attachMeter")
                    if not chest.isEmpty(): chest.show()

            target_actor = self.hw_body_actor if hasattr(self, 'hw_body_actor') and self.hw_body_actor else self.actor

            if cog_id == "majorplayer":
                is_boogie = hasattr(self, 'control_panel') and self.control_panel.is_boogify_var.get()

                if is_boogie:
                    hw_suit_tex = loader.loadTexture(get_valid_texture_path(cog_data.get("suitTex_HW")))
                    tx_body_hw = loader.loadTexture(get_valid_texture_path(cog_data.get("bodyTex_HW")))
                    hw_head_tex = loader.loadTexture(get_valid_texture_path(cog_data.get("headTex_HW")))

                    self.texture_part_check(['necktie-s', 'necktie-w', 'bowtie', 'highroller_body'], target_actor,
                                            tx_body_hw)
                    target_actor.find('**/body').setTexture(hw_suit_tex, 1)

                    self.head.setTexture(hw_head_tex, 1)
                    teeth = self.head.find('**/he_teeths')
                    if not teeth.isEmpty(): teeth.hide()

                else:
                    normal_suit_tex = loader.loadTexture(get_valid_texture_path(cog_data.get("suitTex")))
                    tx_body_normal = getattr(globals, "MP_BODY", get_valid_texture_path(cog_data.get("suitTex")))
                    if isinstance(tx_body_normal, str): tx_body_normal = loader.loadTexture(tx_body_normal)

                    self.texture_part_check(['necktie-s', 'necktie-w', 'bowtie', 'highroller_body'], target_actor,
                                            tx_body_normal)
                    target_actor.find('**/body').setTexture(normal_suit_tex, 1)

                    self.head.clearTexture()
                    teeth = self.head.find('**/he_teeths')
                    if not teeth.isEmpty(): teeth.show()

            else:
                head_tex_path = get_valid_texture_path(cog_data.get("headTex_HW"))
                if head_tex_path:
                    hw_head_tex = loader.loadTexture(head_tex_path)
                    if "ttcc_ene_rainmaker" in cog_name:
                        rainHW = loader.loadTexture(cog_data.get("headTex_HW"))
                        rainHair = loader.loadTexture(cog_data.get("hairTex_HW"))
                        geomNode = self.head.find("**/head").node()

                        state0 = geomNode.getGeomState(0)
                        tex_attr0 = state0.getAttrib(TextureAttrib)
                        if tex_attr0:
                            for stage in tex_attr0.getOnStages():
                                if stage.getName() == "ttcc_ene_rainmaker_hair":
                                    new_state = state0.setAttrib(tex_attr0.addOnStage(stage, rainHair))
                                    geomNode.setGeomState(0, new_state)
                        state1 = geomNode.getGeomState(1)
                        tex_attr1 = state1.getAttrib(TextureAttrib)
                        if tex_attr1:
                            for stage in tex_attr1.getOnStages():
                                if stage.getName() == "rainmaker":
                                    new_state = state1.setAttrib(tex_attr1.addOnStage(stage, rainHW))
                                    geomNode.setGeomState(1, new_state)
                    else:
                        self.head.setTexture(hw_head_tex, 1)

                    if "ttcc_ene_duckshuffler" in cog_name:
                        slot_tex = loader.loadTexture(cog_data["slotTex"])
                        for part in ['slotL', 'slotMid', 'slotR']:
                            np = self.head.find(f'**/{part}')
                            if not np.isEmpty(): np.setTexture(slot_tex, 1)
                    elif "ttcc_ene_prethinker" in cog_name:
                        glass = loader.loadTexture(cog_data["glassTex"])
                        self.head.find('**/brain').setTexture(hw_head_tex, 1)
                        self.head.find('**/glass').setTexture(glass, 1)
                        self.head.find('**/head').setTexture(hw_head_tex, 1)

                suit_tex_path = get_valid_texture_path(cog_data.get("suitTex_HW"))
                if suit_tex_path:
                    hw_suit_tex = loader.loadTexture(suit_tex_path)
                    for part in ['body', 'necktie-s', 'necktie-w', 'bowtie']:
                        np = target_actor.find(f'**/{part}')
                        if not np.isEmpty(): np.setTexture(hw_suit_tex, 1)

            if self.suit_type not in ["as", "bs", "cs", "boss"]:
                if "handsHW" in cog_data:
                    hands = target_actor.find('**/hands')
                    if not hands.isEmpty(): hands.setColor(cog_data["handsHW"])

            tie_to_set = "(Default)"
            if cog_id == "majorplayer":
                tie_to_set = "Bowtie"
            elif hasattr(self, 'control_panel'):
                tie_to_set = self.control_panel.selected_tie_var.get()
            self.set_necktie(tie_to_set)

        # disable costume
        else:
            self.is_costume_active = False

            if cog_id == "majorplayer" and hasattr(self, 'control_panel'):
                self.control_panel.suit_is_boogie.pack_forget()
                self.control_panel.is_boogify_var.set(False)

            vfs = VirtualFileSystem.getGlobalPtr()
            panda_hw_path = Filename.fromOsSpecific(hw_head_model_path) if hw_head_model_path else Filename("")

            if hw_head_model_path and (os.path.isfile(hw_head_model_path) or vfs.exists(panda_hw_path)):
                self.set_stored_vals()

                new_head = self._swap_head_model(cog_data.get("head"))
                if new_head is not None:
                    if hasattr(self, 'head') and self.head is not None:
                        self.head.detachNode()
                    self.head = new_head

                self.update_cog_attributes(None, True)

            if "ttcc_ene_rainmaker" in cog_name:
                rainHW = loader.loadTexture(cog_data.get("headTex1"))
                rainHair = loader.loadTexture(cog_data.get("hairTex"))
                geomNode = self.head.find("**/head").node()

                state0 = geomNode.getGeomState(0)
                tex_attr0 = state0.getAttrib(TextureAttrib)
                if tex_attr0:
                    for stage in tex_attr0.getOnStages():
                        if stage.getName() == "ttcc_ene_rainmaker_hair":
                            new_state = state0.setAttrib(tex_attr0.addOnStage(stage, rainHair))
                            geomNode.setGeomState(0, new_state)
                state1 = geomNode.getGeomState(1)
                tex_attr1 = state1.getAttrib(TextureAttrib)
                if tex_attr1:
                    for stage in tex_attr1.getOnStages():
                        if stage.getName() == "rainmaker":
                            new_state = state1.setAttrib(tex_attr1.addOnStage(stage, rainHW))
                            geomNode.setGeomState(1, new_state)
            else:
                self.head.clearTexture()

            if "ttcc_ene_duckshuffler" in cog_name:
                for part in ['slotL', 'slotMid', 'slotR']:
                    np = self.head.find(f'**/{part}')
                    if not np.isEmpty(): np.clearTexture()
            elif cog_id == "majorplayer":
                teeth = self.head.find('**/he_teeths')
                if not teeth.isEmpty(): teeth.show()
            elif "ttcc_ene_prethinker" in cog_name:
                self.head.find('**/brain').clearTexture()
                self.head.find('**/glass').clearTexture()
                self.head.find('**/head').clearTexture()

            suit_tex_path = get_valid_texture_path(cog_data.get("suitTex"))
            if suit_tex_path:
                normal_suit_tex = loader.loadTexture(suit_tex_path)
                for part in ['body', 'necktie-s', 'necktie-w', 'bowtie']:
                    np = self.actor.find(f'**/{part}')
                    if not np.isEmpty(): np.setTexture(normal_suit_tex, 1)

            if (self.suit_type not in ["as", "bs", "cs", "bossCog"]):
                if "hands" in cog_data:
                    self.actor.find('**/hands').setColor(cog_data["hands"])

            if hasattr(self, 'hw_body_actor') and self.hw_body_actor:
                if hasattr(self, 'head') and self.head and not self.head.isEmpty():
                    self.head.reparentTo(self.actor.find('**/joint_head'))

                if hasattr(self, 'prop_item1') and self.prop_item1 != "zero":
                    self.prop_item1.reparentTo(self.actor.find('**/joint_Rhold'))
                if hasattr(self, 'prop_item1_actor') and self.prop_item1_actor:
                    self.prop_item1_actor.reparentTo(self.actor.find('**/joint_Rhold'))

                if hasattr(self, 'prop_item2') and self.prop_item2 != "zero":
                    self.prop_item2.reparentTo(self.actor.find('**/joint_Lhold'))
                if hasattr(self, 'prop_item2_actor') and self.prop_item2_actor:
                    self.prop_item2_actor.reparentTo(self.actor.find('**/joint_Lhold'))

                if hasattr(self, 'iconbase') and self.iconbase:
                    chest = self.actor.find("**/joint_attachMeter")
                    if not chest.isEmpty(): self.iconbase.reparentTo(chest)

                self.hw_body_actor.cleanup()
                self.hw_body_actor.removeNode()
                self.hw_body_actor = None

                if getattr(self, 'is_body', True):
                    for part in ['body', 'hands']:
                        np = self.actor.find(f'**/{part}')
                        if not np.isEmpty(): np.show()

                    tie_to_set = "(Default)"
                    if hasattr(self, 'control_panel'):
                        tie_to_set = self.control_panel.selected_tie_var.get()
                    self.set_necktie(tie_to_set)

                    chest = self.actor.find("**/joint_attachMeter")
                    if not chest.isEmpty(): chest.show()

        if self.control_panel.is_zapped_var.get():
            self.darken_cog()
        elif cog_id in ["majorplayer", "chainsawconsultant"]:
            self.darken_cog(False)

    def toggle_boogie(self, active, store_tex=True):
        if getattr(self, 'is_costume_active', False):
            cog_data = globals.COG_DATA.get(self.current_cog, None)
            if not cog_data or cog_data.get("cog") != "majorplayer":
                return

            target_actor = self.hw_body_actor if hasattr(self, 'hw_body_actor') and self.hw_body_actor else self.actor

            def get_valid_texture_path(tex_value):
                if not tex_value: return None
                if isinstance(tex_value, (list, tuple)): tex_value = tex_value[0]
                if isinstance(tex_value, (str, bytes, os.PathLike)) and os.path.exists(tex_value): return tex_value
                return None

            if active:
                hw_suit_tex = loader.loadTexture(get_valid_texture_path(cog_data.get("suitTex_HW")))
                tx_body_hw = loader.loadTexture(get_valid_texture_path(cog_data.get("bodyTex_HW")))
                hw_head_tex = loader.loadTexture(get_valid_texture_path(cog_data.get("headTex_HW")))

                self.texture_part_check(['necktie-s', 'necktie-w', 'bowtie', 'highroller_body'], target_actor,
                                        tx_body_hw)
                target_actor.find('**/body').setTexture(hw_suit_tex, 1)

                if hasattr(self, 'head') and self.head:
                    self.head.setTexture(hw_head_tex, 1)
                    teeth = self.head.find('**/he_teeths')
                    if not teeth.isEmpty(): teeth.hide()
                # store texture for suit library
                if store_tex:
                    self.store_suit_texture = get_valid_texture_path(cog_data.get("suitTex_HW"))
            else:
                normal_suit_tex = loader.loadTexture(get_valid_texture_path(cog_data.get("suitTex")))
                tx_body_normal = getattr(globals, "MP_BODY", get_valid_texture_path(cog_data.get("suitTex")))
                if isinstance(tx_body_normal, str): tx_body_normal = loader.loadTexture(tx_body_normal)

                self.texture_part_check(['necktie-s', 'necktie-w', 'bowtie', 'highroller_body'], target_actor,
                                        tx_body_normal)
                target_actor.find('**/body').setTexture(normal_suit_tex, 1)

                if hasattr(self, 'head') and self.head:
                    self.head.clearTexture()
                    teeth = self.head.find('**/he_teeths')
                    if not teeth.isEmpty(): teeth.show()

        if getattr(self, 'is_zapped', False):
            self.toggle_zapped(False)
            self.toggle_zapped(True)

    def toggle_body(self):
        is_skel = hasattr(self, 'control_panel') and self.control_panel.is_skelecog_var.get()
        target_actor = self.skelecog if (is_skel and hasattr(self, 'skelecog') and self.skelecog) else self.actor

        hands = target_actor.find('**/hands')
        hr_body = target_actor.find('**/highroller_body')

        if self.is_body:
            target_actor.find('**/body').hide()
            target_actor.find("**/joint_attachMeter").hide()
            if self.cog_data["cog"] not in ["counterfit", "VP", "CFO", "CLO", "CEO"]:
                target_actor.find('**/necktie-s').hide()
                target_actor.find('**/necktie-w').hide()
                target_actor.find('**/bowtie').hide()

            self.shadow.hide()
            self.control_panel.is_shadow_var.set(False)
            self.is_shadow = False

            if not hands.isEmpty():
                hands.hide()
                if not hr_body.isEmpty(): hr_body.hide()
            else:
                target_actor.find("**/emblem_healthmeter").hide()
                target_actor.find('**/glow').hide()

            self.is_body = False
            self.control_panel.is_body_var.set(self.is_body)
            self.control_panel.is_background_black_var.set(self.bool)
            self.control_panel.is_executive_var.set(False)
            self.control_panel.is_fired_var.set(False)

            if self.prop_item1_actor: self.prop_item1_actor.cleanup()
            if self.prop_item2_actor: self.prop_item2_actor.cleanup()
            if self.prop_item1 != "zero": self.prop_item1.removeNode()
            if self.prop_item2 != "zero": self.prop_item2.removeNode()
            self.prop_item1_actor = None
            self.prop_item2_actor = None
            self.prop_item1, self.prop_item2, self.current_prop1, self.current_prop2 = "zero", "zero", "zero", "zero"
            self.control_panel.hide_prop_anim_ui(self.control_panel.prop1_anim_frame)
            self.control_panel.hide_prop_anim_ui(self.control_panel.prop2_anim_frame)

        else:
            target_actor.find('**/body').show()
            target_actor.find("**/joint_attachMeter").show()

            self.shadow.show()
            self.control_panel.is_shadow_var.set(True)
            self.is_shadow = True

            if not hands.isEmpty():
                hands.show()
                if not hr_body.isEmpty(): hr_body.show()
            else:
                target_actor.find("**/emblem_healthmeter").show()
                target_actor.find('**/glow').show()

            tie_to_set = self.control_panel.selected_tie_var.get()
            self.set_necktie(tie_to_set)
            self.is_body = True
            self.load_stored_props()

    def toggle_shadow(self):
        self.is_shadow = not self.is_shadow
        self.control_panel.is_shadow_var.set(self.is_shadow)
        if self.is_shadow:
            self.shadow.show()
        else:
            self.shadow.hide()

    def hex_to_p3d_color(self, hex_code):
        try:
            hex_code = hex_code.lstrip('#')
            if len(hex_code) != 6:
                print(f"Invalid Hex Code: {hex_code}")
                return None
            r, g, b = tuple(int(hex_code[i:i + 2], 16) for i in (0, 2, 4))
            return (r / 255.0, g / 255.0, b / 255.0, 1.0)
        except ValueError:
            print("Invalid Hex input")
            return None

    def apply_body_colorscale(self, hex_code):
        color = self.hex_to_p3d_color(hex_code)
        if not color: return

        if self.actor and not self.boss_parts:
            self.actor.setColorScale(color)

        if hasattr(self, 'boss_parts') and self.boss_parts:
            for part_name, part_node in self.boss_parts.items():
                if part_node and not part_node.isEmpty():
                    part_node.setColorScale(color)
        self.store_body_hex_color = hex_code
        self.store_body_color = True

    def apply_skelecog_hand_color(self, target_actor):
        if not target_actor: return
        hands = target_actor.find('**/hands')

        if not hands.isEmpty():
            is_exec = hasattr(self, 'control_panel') and self.control_panel.is_executive_var.get()

            if not is_exec:
                hands.setColor(126 / 255.0, 126 / 255.0, 125 / 255.0, 1.0)
            else:
                dept = self.cog_data.get("dept", "s")
                if dept == "s":
                    hands.setColor(122 / 255.0, 90 / 255.0, 125 / 255.0, 1.0)
                elif dept == "m":
                    hands.setColor(85 / 255.0, 103 / 255.0, 82 / 255.0, 1.0)
                elif dept == "l":
                    hands.setColor(85 / 255.0, 103 / 255.0, 125 / 255.0, 1.0)
                elif dept == "c":
                    hands.setColor(133 / 255.0, 112 / 255.0, 86 / 255.0, 1.0)
                elif dept == "g":
                    hands.setColor(72 / 255.0, 94 / 255.0, 93 / 255.0, 1.0)
                else:
                    hands.setColor(126 / 255.0, 126 / 255.0, 125 / 255.0, 1.0)

    def apply_head_color(self, hex_code):
        color = self.hex_to_p3d_color(hex_code)
        if not color: return

        if self.head:
            self.head.setColor(color)
        self.store_head_hex_color = hex_code
        self.store_head_color = True

    def apply_hand_color(self, hex_code):
        color = self.hex_to_p3d_color(hex_code)
        if not color: return

        if self.actor:
            hands = self.actor.find('**/hands')
            if not hands.isEmpty():
                hands.setColor(color)
            else:
                print("Hands node not found (Is this a Skelecog or a boss cog?)")
        self.store_hand_hex_color = hex_code
        self.store_hand_color = True

    def reset_cog_colors(self):
        if self.actor:
            self.actor.clearColorScale()
            hands = self.actor.find('**/hands')
            if not hands.isEmpty():
                hands.clearColor()
                if self.cog_data and "hands" in self.cog_data:
                    hands.setColor(self.cog_data["hands"])
        if self.head:
            self.head.clearColor()

        if hasattr(self, 'boss_parts') and self.boss_parts:
            for part_node in self.boss_parts.values():
                if part_node and not part_node.isEmpty():
                    part_node.clearColorScale()
        self.store_hand_color = False
        self.store_head_color = False
        self.store_body_color = False
        print("Colors reset.")

    def apply_background_color(self, hex_code):
        color = self.hex_to_p3d_color(hex_code)
        if not color: return
        self.background_color = color
        self.setBackgroundColor(color)

    def reset_background_color(self):
        self.background_color = (105 / 255, 105 / 255, 105 / 255)
        self.setBackgroundColor(self.background_color)

    def autoplay_animations(self):
        self.is_autoplay = self.control_panel.is_autoplay_var.get()

    def build_boss_cog(self, cog_data):
        self.control_panel.hide_tie_list()  # Hides necktie options on toggles
        self.control_panel.show_suit_library(False)  # hides suit library
        self.control_panel.show_body_toggle(False)  # hides toggle body

        parts = cog_data["parts"]
        anims = cog_data.get("anims", {})
        cog_name = cog_data["name"]

        if "legs" in parts:
            root_part_name = "legs"
        elif "body" in parts:
            root_part_name = "body"
        else:
            root_part_name = "torso"  # Fallback

        root_path = parts[root_part_name]
        root_anims = anims.get(root_part_name, {})

        self.actor = Actor(root_path, root_anims)
        self.actor.reparentTo(self.render)
        self.actor.setPos(0, 0, 0)
        # self.actor.setHpr(0, 0, 0)
        self.boss_parts[root_part_name] = self.actor
        self.actor.setBlend(frameBlend=True)
        self.actor.setTwoSided(True)

        for part_name, part_path in parts.items():
            if part_name == root_part_name: continue

            part_anims = anims.get(part_name, {})
            if part_anims:
                part_node = Actor(part_path, part_anims)
            else:
                part_node = loader.loadModel(part_path)

            if part_name == "torso" or part_name == "body":
                part_node.reparentTo(self.actor.find("**/joint_pelvis"))

            elif part_name == "head":
                parent = None
                if "torso" in self.boss_parts:
                    parent = self.boss_parts["torso"]
                elif "body" in self.boss_parts:
                    parent = self.boss_parts["body"]
                else:
                    parent = self.actor

                joint = parent.find("**/joint34")
                if joint.isEmpty(): joint = parent.find("**/def_head")
                if joint.isEmpty(): joint = parent.find("**/joint_head")

                if not joint.isEmpty():
                    part_node.reparentTo(joint)
                else:
                    print(f"Warning: Could not find head joint on {parent.getName()}")

                self.head = part_node

            elif part_name == "treads":
                part_node.reparentTo(self.actor.find("**/joint_axle"))

            self.boss_parts[part_name] = part_node

        if "texture" in cog_data:
            tex = loader.loadTexture(cog_data["texture"])
            if "torso" in self.boss_parts:
                self.boss_parts["torso"].find('**/Object').setTexture(tex, 1)
            elif "body" in self.boss_parts:
                self.boss_parts["body"].find('**/Object').setTexture(tex, 1)

        anim_list_key = "torso" if "torso" in anims else "body"
        self.boss_parts["legs"].find('**/mesh_doorFront').reparentTo(self.boss_parts["legs"].find('**/joint_doorFront'))
        self.boss_parts["legs"].find('**/mesh_doorRear').reparentTo(self.boss_parts["legs"].find('**/joint_doorRear'))
        # self.boss_parts["legs"].find('**/joint_doorFront').setHpr(0,0, 80)
        # self.boss_parts["legs"].find('**/joint_doorRear').setHpr(0,0, -80)
        self.boss_parts["legs"].find('**/mesh_doorFront').setPosHprScale(-1.36, 0.00, -6.30, 90.00, 281.31, 0.00, 1.00,
                                                                         1.00, 1.00)
        self.boss_parts["legs"].find('**/mesh_doorRear').setPosHprScale(0.34, 0.00, -6.47, 90.00, 87.00, 0.00, 1.00,
                                                                        1.00, 1.00)

        meter_parent = None
        if "torso" in self.boss_parts:
            meter_parent = self.boss_parts["torso"]
        elif "body" in self.boss_parts:
            meter_parent = self.boss_parts["body"]
        else:
            meter_parent = self.actor

        meter_joint = meter_parent.find('**/joint_lifeMeter')

        medallionColors = {'c': (0.863, 0.776, 0.769, 1.0),
                           's': (0.843, 0.745, 0.745, 1.0),
                           'l': (0.749, 0.776, 0.824, 1.0),
                           'm': (0.749, 0.769, 0.749, 1.0)}
        icon_path = os.path.join(globals.RESOURCES_DIR, "phase_3", "models", "gui", "cog_icons.bam")
        if os.path.exists(icon_path) and not meter_joint.isEmpty():
            dept = cog_data.get('dept', 'c')
            icon_map = {'s': 'SalesIcon', 'm': 'MoneyIcon', 'l': 'LegalIcon', 'c': 'CorpIcon', 'g': 'CorpIcon'}
            node_name = icon_map.get(dept, 'CorpIcon')

            icon_model = loader.loadModel(icon_path)
            icon_node = icon_model.find('**/' + node_name)

            if not icon_node.isEmpty():
                self.boss_icon = icon_node.copyTo(meter_joint)
                if cog_data['name'] in ["CLO"]:
                    self.boss_icon.setPosHprScale(0.00, 0.90, 0.00, 0.00, -20.00, 0.00, 2.00, 2.00, 2.00)
                else:
                    self.boss_icon.setPosHprScale(0.00, -0.15, 0.00, 0.00, -20.00, 0.00, 2.00, 2.00, 2.00)
                self.boss_icon.setColor(medallionColors[dept])

        gui_path = os.path.join(globals.RESOURCES_DIR, "phase_3.5", "models", "gui", "matching_game_gui.bam")
        glow_path = os.path.join(globals.RESOURCES_DIR, "phase_3.5", "models", "props", "glow.bam")

        if os.path.exists(gui_path) and os.path.exists(glow_path) and not meter_joint.isEmpty():
            model = loader.loadModel(gui_path)
            button = model.find('**/minnieCircle')

            if not button.isEmpty():
                self.health_meter = button.copyTo(meter_joint)

                self.health_meter.setScale(6.2)
                self.health_meter.setP(-20)
                if cog_data['name'] in ["CLO"]:
                    self.health_meter.setY(0.90)
                else:
                    self.health_meter.setY(-0.20)
                self.health_meter.setColor(globals.SKELECOG_METER_COLORS[0])

                glow = loader.loadModel(glow_path)
                glow.reparentTo(self.health_meter)
                glow.setScale(0.28)
                glow.setPos(-0.005, 0.01, 0.015)
                glow.setColor(globals.SKELECOG_METER_COLORS[0])

                self.meter_glow = glow
                self.health_meter.hide()
                self.meter_glow.hide()

        anim_list_key = "torso" if "torso" in anims else "body"
        self.available_animations = list(anims.get(anim_list_key, {}).keys())
        self.available_head_animations = list(anims.get("head", {}).keys())
        self.control_panel.update_animation_lists(self.available_animations, self.available_head_animations)

        self.suit_type = "boss"
        self.skele_i = 0

        if self.available_animations:
            target_anim = "Ff_neutral"

            if target_anim in self.available_animations:
                first_anim = target_anim
            else:
                self.available_animations.sort()
                first_anim = self.available_animations[0]

            self.actor.pose(first_anim, 0)

            if "torso" in self.boss_parts:
                self.boss_parts["torso"].pose(first_anim, 0)
            elif "body" in self.boss_parts:
                self.boss_parts["body"].pose(first_anim, 0)

            self.actor.update()

        self.control_panel.suit_exec_check.pack_forget()
        self.control_panel.suit_fired_check.pack_forget()
        self.is_costume_active = False
        self.control_panel.is_costume_var.set(False)
        self.control_panel.is_executive_var.set(False)
        self.control_panel.is_fired_var.set(False)
        self.control_panel.is_waiter_var.set(False)
        if hasattr(self.control_panel, 'suit_costume_check'):
            self.control_panel.suit_costume_check.pack_forget()
            self.control_panel.suit_is_boogie.pack_forget()

    def toggle_virtualize(self):
        self.store_virtualize = True
        if not hasattr(self, 'skele_color_index'):
            self.skele_color_index = 0

        self.skele_color_index = (self.skele_color_index + 1) % len(globals.SKELECOG_METER_COLORS)

        if self.skele_color_index == 0:
            self.actor.clearColorScale()
            self.actor.clearAttrib(ColorBlendAttrib.getClassType())
            self.actor.setDepthWrite(True)
            self.actor.setBin('default', 0)
        else:
            new_color = globals.SKELECOG_METER_COLORS[self.skele_color_index]
            self.actor.setColorScale(new_color)
            self.actor.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
            self.actor.setDepthWrite(False)
            self.actor.setBin('fixed', 1)

    def on_tie_select(self, event=None):
        selection = self.control_panel.tie_listbox.curselection()
        if selection:
            selected_tie = self.control_panel.tie_listbox.get(selection[0])
            self.set_necktie(selected_tie)

    def toggle_skele_meter_color(self):
        cog_data = globals.COG_DATA[self.current_cog]
        self.skele_meter_color = globals.SKELECOG_METER_COLORS[self.skele_i]

        already_skel = self.suit_type in ["as", "bs", "cs"]
        if already_skel:
            if hasattr(self, 'health_meter') and getattr(self, 'health_meter') and not self.health_meter.isEmpty():
                self.health_meter.setColor(self.skele_meter_color)
            if hasattr(self, 'meter_glow') and getattr(self, 'meter_glow') and not self.meter_glow.isEmpty():
                self.meter_glow.setColor(self.skele_meter_color)

        if hasattr(self, 'iconbase') and getattr(self, 'iconbase'):
            emblem_hp = self.iconbase.find('**/emblem_hp')
            glow = self.iconbase.find('**/glow')

            if cog_data['name'] in ["VP", "CFO", "CLO"]:
                if self.skele_i < 6:
                    if hasattr(self, 'health_meter') and self.health_meter and not self.health_meter.isEmpty():
                        self.health_meter.show()
                        self.health_meter.setColor(self.skele_meter_color)
                    if hasattr(self, 'meter_glow') and self.meter_glow and not self.meter_glow.isEmpty():
                        self.meter_glow.show()
                        self.meter_glow.setColor(self.skele_meter_color)
                    self.boss_icon.hide()
                elif self.skele_i == 6:
                    if hasattr(self, 'health_meter') and self.health_meter and not self.health_meter.isEmpty():
                        self.health_meter.hide()
                    if hasattr(self, 'meter_glow') and self.meter_glow and not self.meter_glow.isEmpty():
                        self.meter_glow.hide()
                    self.boss_icon.show()

            elif cog_data['name'] in ["CEO"]:
                if self.skele_i < 6:
                    if hasattr(self, 'health_meter') and self.health_meter and not self.health_meter.isEmpty():
                        self.health_meter.show()
                        self.health_meter.setColor(self.skele_meter_color)
                        self.head.find('**/ceo_sclera').setColor(0, 0, 0, 1.0)
                        self.head.find('**/ceo_eyes').setColor(self.skele_meter_color)
                    if hasattr(self, 'meter_glow') and self.meter_glow and not self.meter_glow.isEmpty():
                        self.meter_glow.show()
                        self.meter_glow.setColor(self.skele_meter_color)
                    self.boss_icon.hide()
                elif self.skele_i == 6:
                    if hasattr(self, 'health_meter') and self.health_meter and not self.health_meter.isEmpty():
                        self.health_meter.hide()
                        self.head.find('**/ceo_sclera').clearColor()
                        self.head.find('**/ceo_eyes').clearColor()
                    if hasattr(self, 'meter_glow') and self.meter_glow and not self.meter_glow.isEmpty():
                        self.meter_glow.hide()
                        self.boss_icon.show()

            elif self.skele_i < 6:
                emblem_hp.show()
                glow.show()
                emblem_hp.setColor(self.skele_meter_color)
                glow.setColor(self.skele_meter_color)
                if self.store_emblem not in ["light", "none"]:
                    self.iconbase.find(f'**/{self.store_emblem}').hide()

            elif self.skele_i == 6:
                emblem_hp.setColor(self.skele_meter_color)
                glow.setColor(self.skele_meter_color)
                if self.store_emblem != "light":
                    emblem_hp.hide()
                    glow.hide()
                    self.apply_emblem(self.store_emblem)

        for attr in ['skel_iconbase', 'zap_iconbase']:
            icon_node = getattr(self, attr, None)
            if icon_node and not icon_node.isEmpty():
                hp = icon_node.find('**/emblem_hp')
                gl = icon_node.find('**/glow')
                if self.skele_i < 6:
                    hp.show()
                    gl.show()
                    hp.setColor(self.skele_meter_color)
                    gl.setColor(self.skele_meter_color)
                    if getattr(self, 'store_emblem', None) not in ["light", "none"]:
                        target = icon_node.find(f'**/{self.store_emblem}')
                        if not target.isEmpty(): target.hide()
                elif self.skele_i == 6:
                    hp.setColor(self.skele_meter_color)
                    gl.setColor(self.skele_meter_color)
                    if getattr(self, 'store_emblem', None) != "light":
                        hp.hide()
                        gl.hide()
                        if self.store_emblem not in ["light", "none"]:
                            target = icon_node.find(f'**/{self.store_emblem}')
                            if not target.isEmpty(): target.show()

        self.skele_i += 1
        self.skele_i %= 7
        self.store_health_meter = True

    def upload_texture(self, part, target):
        root = tk.Tk()
        root.withdraw()

        file_path = filedialog.askopenfilename(
            title=f"Select {part} Texture",
            filetypes=[
                ("Image Files", "*.png *.jpg *.jpeg *.bmp *.tga"),
                ("All Files", "*.*")
            ]
        )

        if not file_path:
            print("Texture upload canceled.")
            return

        try:
            panda_path = Filename.fromOsSpecific(file_path)
            panda_path.makeTrueCase()

            new_tex = loader.loadTexture(panda_path)
            if not new_tex:
                print("Error: Failed to load texture.")
                return

            for node in target:
                node.setTexture(new_tex, 1)

            print(f"Applied new suit texture: {file_path}")

            if part == "Suit":
                if self.suit_type not in ["as", "bs", "cs"]:
                    self.store_suit_texture = panda_path
                else:
                    self.store_skelecog_texture = panda_path
            elif part == "Head":
                self.store_head_texture = panda_path

        except Exception as e:
            print(f"Failed to apply texture: {e}")

    def upload_suit_texture(self):
        suit_part = "Suit"
        if self.cog_data["cog"] in ["VP", "CFO", "CLO", "CEO"]:
            suit_target = [
                self.actor.find('**/Object')
            ]
        elif self.suit_type not in ["as", "bs", "cs"]:
            suit_target = [
                self.actor.find('**/body'),
                self.actor.find('**/necktie-s'),
                self.actor.find('**/necktie-w'),
                self.actor.find('**/bowtie'),
                self.actor.find('**/hands')
            ]
        else:
            suit_target = [
                self.actor.find('**/body'),
                self.actor.find('**/necktie-s'),
                self.actor.find('**/necktie-w'),
                self.actor.find('**/bowtie')
            ]
        self.upload_texture(suit_part, suit_target)

    def upload_head_texture(self):
        cog_data = globals.COG_DATA.get(self.current_cog, None)
        cog_name = cog_data["name"]
        if "ttcc_ene_rainmaker" in cog_name:
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.askopenfilename(
                title="Select Head Texture",
                filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.tga"), ("All Files", "*.*")]
            )

            if not file_path:
                print("Upload canceld")
                return
            try:
                panda_path = Filename.fromOsSpecific(file_path)
                panda_path.makeTrueCase()
                new_tex = loader.loadTexture(panda_path)

                if not new_tex:
                    print("faile to load teture")
                    return
                if self.head:
                    geomNode = self.head.find('**/head').node()
                    state1 = geomNode.getGeomState(1)
                    tex_attr1 = state1.getAttrib(TextureAttrib)

                    if tex_attr1:
                        for stage in tex_attr1.getOnStages():
                            if stage.getName() == "rainmaker":
                                new_state = state1.setAttrib(tex_attr1.addOnStage(stage, new_tex))
                                geomNode.setGeomState(1, new_state)
            except Exception as e:
                print("what")
            return

        elif "ttcc_ene_counterfit" in cog_name:
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.askopenfilename(
                title="Select Head Texture",
                filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.tga"), ("All Files", "*.*")]
            )

            if not file_path:
                print("Upload canceld")
                return
            try:
                panda_path = Filename.fromOsSpecific(file_path)
                panda_path.makeTrueCase()
                new_tex = loader.loadTexture(panda_path)

                if not new_tex:
                    print("faile to load teture")
                    return

                if self.head:
                    gn_path = self.head.find("**/+GeomNode")

                    if not gn_path.isEmpty():
                        geomNode = gn_path.node()

                        for i in range(geomNode.getNumGeoms()):
                            state = geomNode.getGeomState(i)
                            tex_attr = state.getAttrib(TextureAttrib)

                            if tex_attr:
                                for stage in tex_attr.getOnStages():
                                    current_tex = tex_attr.getOnTexture(stage)
                                    if current_tex and "ttcc_ene_counterfit" in current_tex.getFilename().getBasename():
                                        new_state = state.setAttrib(tex_attr.addOnStage(stage, new_tex))
                                        geomNode.setGeomState(i, new_state)

            except Exception as e:
                print("what")
            return
        elif "ttcc_ene_firestarter" in cog_name:
            head_part = "Head"
            head_target = [
                self.head.find('**/Fire_Starter.001')
            ]
        else:
            head_part = "Head"
            head_target = [
                self.head
            ]
        self.upload_texture(head_part, head_target)

    def upload_additional_head_texture(self):
        cog_data = globals.COG_DATA.get(self.current_cog, None)
        cog_name = cog_data["name"]
        if "ttcc_ene_rainmaker" in cog_name:
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.askopenfilename(
                title="Select Hair Texture",
                filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.tga"), ("All Files", "*.*")]
            )

            if not file_path:
                print("Upload canceled.")
                return

            try:
                panda_path = Filename.fromOsSpecific(file_path)
                panda_path.makeTrueCase()
                new_tex = loader.loadTexture(panda_path)

                if not new_tex:
                    print("Failed to load texture.")
                    return

                if self.head:
                    geomNode = self.head.find("**/head").node()

                    state0 = geomNode.getGeomState(0)
                    tex_attr0 = state0.getAttrib(TextureAttrib)

                    if tex_attr0:
                        for stage in tex_attr0.getOnStages():
                            if stage.getName() == "ttcc_ene_rainmaker_hair":
                                new_state = state0.setAttrib(tex_attr0.addOnStage(stage, new_tex))
                                geomNode.setGeomState(0, new_state)
                                print(f"Applied Rainmaker Hair Texture: {file_path}")

            except Exception as e:
                print(f"Error applying Rainmaker hair: {e}")

            return
        target = []
        if "ttcc_ene_firestarter" in cog_name:
            if self.head:
                fire = self.head.find('**/fire_seq')
                if not fire.isEmpty():
                    target.append(fire)

        self.upload_texture("Additional Head", target)

    # Used for Suit Library
    def apply_suit_texture(self, texture_path):
        if self.actor:
            is_toggled_skel = hasattr(self, 'control_panel') and self.control_panel.is_skelecog_var.get()
            already_skel = self.suit_type in ["as", "bs", "cs"]

            tex_str = str(texture_path).lower()
            is_skel_tex = "skelecog" in tex_str or "skel" in tex_str or "as_" in tex_str or "bs_" in tex_str or "cs_" in tex_str

            if is_skel_tex or already_skel:
                self.store_skelecog_texture = texture_path
                self.store_skel_head_tex = loader.loadTexture(texture_path)
            else:
                self.store_suit_texture = texture_path

            texture = loader.loadTexture(texture_path)

            if not already_skel and not is_skel_tex:
                if self.suit_type not in ["erfit", "boss"]:
                    suit_nodes = [self.actor.find('**/body'), self.actor.find('**/necktie-s'),
                                  self.actor.find('**/necktie-w'), self.actor.find('**/bowtie')]
                else:
                    suit_nodes = [self.actor.find('**/body')]
                for node in suit_nodes:
                    if not node.isEmpty(): node.setTexture(texture, 1)

            elif already_skel:
                for part in ['body', 'necktie-s', 'necktie-w', 'bowtie']:
                    np = self.actor.find(f'**/{part}')
                    if not np.isEmpty(): np.setTexture(texture, 1)
                if hasattr(self, 'apply_skelecog_hand_color'):
                    self.apply_skelecog_hand_color(self.actor)
                orig_suit = self.cog_data.get("suit", "")
                if orig_suit in ["as", "bs", "cs"]:
                    if hasattr(self, 'head') and self.head:
                        self.head.setTexture(texture, 1)

            if is_toggled_skel:
                selected_mod = None
                if hasattr(self, 'control_panel') and self.control_panel.selected_suit_mod_var.get():
                    selected_mod = self.control_panel.selected_suit_mod_var.get()
                is_override = selected_mod and selected_mod not in ["as", "bs", "cs"]

                if is_override:
                    overlay_tex = loader.loadTexture(self.store_suit_texture) if self.store_suit_texture else texture
                else:
                    overlay_tex = loader.loadTexture(
                        self.store_skelecog_texture) if self.store_skelecog_texture else texture

                for skel_attr in ['zapped_skelecog', 'skelecog']:
                    skel_node = getattr(self, skel_attr, None)
                    if skel_node and not skel_node.isEmpty():
                        for part in ['body', 'necktie-s', 'necktie-w', 'bowtie']:
                            np = skel_node.find(f'**/{part}')
                            if not np.isEmpty(): np.setTexture(overlay_tex, 1)
                        if hasattr(self, 'apply_skelecog_hand_color'):
                            self.apply_skelecog_hand_color(skel_node)

                if is_skel_tex:
                    cog_id = self.cog_data.get("cog", "").lower().replace(" ", "")
                    for head_attr in ['zapped_head', 'skelecog_skull']:
                        head_node = getattr(self, head_attr, None)
                        if head_node and not head_node.isEmpty():
                            if cog_id not in ["derrickhand", "clubpresident", "chainsawconsultant"]:
                                head_node.setTexture(texture, 1)

    def set_stored_vals(self):
        self.store_costume = self.is_costume_active
        self.store_body_loop = self.control_panel.loop_body_var.get()
        self.store_head_frame = self.control_panel.head_frame_slider.get()
        self.store_head_loop = self.control_panel.loop_head_var.get()

    def apply_suit_model(self, suit_model_key):
        self.is_swapping_body = True

        was_skel = False
        was_exec = False
        was_fired = False
        was_zapped = False

        if hasattr(self, 'control_panel'):
            was_skel = self.control_panel.is_skelecog_var.get()
            was_exec = self.control_panel.is_executive_var.get()
            was_fired = self.control_panel.is_fired_var.get()

            if was_skel: self.toggle_skelecog(False)

            if getattr(self.control_panel, 'is_zapped_var', None) and self.control_panel.is_zapped_var.get():
                self.toggle_zapped(False)
                self.control_panel.is_zapped_var.set(False)

            battle_vars = [
                ('is_enraged_var', self.toggle_enrage_fire),
                ('is_soaked_var', self.toggle_soaked),
                ('is_stunned_var', self.toggle_stunned),
                ('is_sued_var', self.toggle_sued),
                ('is_insured_var', self.toggle_insured),
                ('is_chilled_var', self.toggle_chilled),
                ('is_frozen_var', self.toggle_frozen)
            ]

            for var_name, toggle_func in battle_vars:
                if hasattr(self.control_panel, var_name):
                    var_obj = getattr(self.control_panel, var_name)
                    if var_obj.get():
                        toggle_func(False)
                        var_obj.set(False)

            self.clear_pie_splats()

        if self.actor:
            self.set_stored_vals()
            self.build_cog(suit_model_key, False)

            if hasattr(self, 'control_panel'):
                if was_exec: self.control_panel.is_executive_var.set(True)
                if was_fired: self.control_panel.is_fired_var.set(True)
                if was_skel: self.control_panel.is_skelecog_var.set(True)

            self.update_cog_attributes(suit_model_key)

            if hasattr(self, 'control_panel'):
                self.set_suit_texture()
                if was_exec:
                    self.set_suit_texture("exec")
                elif was_fired:
                    self.set_suit_texture("fired")

                if was_skel:
                    self.toggle_skelecog(True)

                if was_zapped:
                    self.toggle_zapped(True)
                    self.control_panel.is_zapped_var.set(True)

                self.control_panel.update_incompatibilities()

        self.is_swapping_body = False

    def reset_stored_vals(self):
        # Reset the stored values
        self.store_suit_texture = None
        self.store_skelecog_texture = None
        self.store_head_texture = None
        self.store_necktie = "(Default)"
        self.it, self.it2, self.it_l, self.it_m, self.it_r = 0, 0, 0, 0, 0
        self.skele_i = 0
        self.skele_color_index = 0
        self.store_virtualize = False
        self.store_health_meter = False
        self.store_emblem = globals.COG_DATA[self.current_cog]["emblem"]
        self.store_head_hpr = globals.HEAD_HPR_DEFAULTS.copy()
        self.control_panel.reset_head_hpr()
        self.control_panel.is_boogify_var.set(False)
        self.store_is_skelecog = False
        self.store_skelecog_skull = None
        self.store_skel_head_name = None
        self.store_skel_head_tex = None
        # Stored unique toggles
        self.store_unique_suit_toggle = False
        self.store_ds_slot_l = "Duck"
        self.store_ds_slot_m = "Duck"
        self.store_ds_slot_r = "Duck"
        self.store_ds_spin = False
        self.store_ms_toggle_1 = False
        self.store_cs_toggle_1 = False
        self.store_cs_toggle_2 = False
        self.store_hr_toggle_1 = False
        self.store_dj_toggle_1 = False
        self.store_dj_toggle_2 = False
        self.store_rm_weather = "Inversion"
        self.store_cs_toggle_3 = False
        self.store_ms_toggle_2 = False
        # Body anim
        self.store_body_anim = None
        self.store_body_frame = 0
        self.store_body_adjusted = False
        self.store_body_playing = False
        # Head anim
        self.store_head_anim = None
        self.store_head_frame = 0
        self.store_head_adjusted = False
        self.store_head_playing = False
        # Scale
        self.control_panel.reset_flatten()
        self.store_flatten_body = {
            "Sx": self.cog_data.get("scale", 1.0),
            "Sy": self.cog_data.get("scale", 1.0),
            "Sz": self.cog_data.get("scale", 1.0),
        }
        self.store_flatten_head = {
            "Sx": self.cog_data.get("headSize", 1.0),
            "Sy": self.cog_data.get("headSize", 1.0),
            "Sz": self.cog_data.get("headSize", 1.0),
        }
        # Stored Colors
        self.store_body_hex_color = None
        self.store_body_color = False
        self.store_head_hex_color = None
        self.store_head_color = False
        self.store_hand_hex_color = None
        self.store_hand_color = False
        # Stored Props
        self.current_prop1 = "zero"
        self.current_prop2 = "zero"
        self.store_prop1 = "zero"
        self.store_prop2 = "zero"
        self.store_prop1_hpr = globals.HEAD_HPR_DEFAULTS.copy()
        self.store_prop2_hpr = globals.HEAD_HPR_DEFAULTS.copy()
        self.store_custom_model = None
        self.store_custom_model_hpr = globals.HEAD_HPR_DEFAULTS.copy()

        if hasattr(self, 'store_original_head_anims'):
            del self.store_original_head_anims
        if hasattr(self, 'store_original_head_anims_skel'):
            del self.store_original_head_anims_skel
        if hasattr(self, 'head') and self.head and not self.head.isEmpty():
            self.base_head_scale = self.head.getSx()
        else:
            self.base_head_scale = 1.0

    def update_cog_attributes(self, suit_model_key=None, costume_check=False):
        autoplay = self.control_panel.is_autoplay_var.get()

        if self.store_is_skelecog:
            self.control_panel.is_skelecog_var.set(True)
            self.toggle_skelecog(True, suit_model_key)

            if self.store_suit_texture is None:
                tex = loader.loadTexture(self.cog_data["suitTex"])
                for part in ['body', 'hands', 'necktie-s', 'necktie-w', 'bowtie']:
                    np = self.skelecog.find(f'**/{part}')
                    if not np.isEmpty():
                        np.setTexture(tex, 1)
            if self.store_skel_head_tex:
                self.skelecog_skull.setTexture(self.store_skel_head_tex, 1)
            else:
                tex = loader.loadTexture(globals.SKELE_UNEMPLOYED_SUIT)
                self.skelecog_skull.setTexture(tex, 1)

        if self.store_necktie != "(Default)":
            self.set_necktie(self.store_necktie)
            self.control_panel.selected_tie_var.set(self.store_necktie)

        if self.store_costume and not costume_check:
            self.toggle_costume(True)
            self.control_panel.is_costume_var.set(True)
            # Check if dave's boogie texture is active
            is_boogie = hasattr(self, 'control_panel') and self.control_panel.is_boogify_var.get()
            if is_boogie:
                self.toggle_boogie(self.control_panel.is_boogify_var.get(), False)

        if self.store_head_texture is not None:
            head_tex = loader.loadTexture(self.store_head_texture)
            self.head.setTexture(head_tex, 1)

        is_toggled_skel = hasattr(self, 'control_panel') and self.control_panel.is_skelecog_var.get()
        is_natural_skel = self.suit_type in ["as", "bs", "cs"]
        orig_suit = self.cog_data.get("suit", "")
        was_originally_skel = orig_suit in ["as", "bs", "cs"]

        if not is_natural_skel:
            if self.store_suit_texture:
                self.apply_suit_texture(self.store_suit_texture)
            else:
                cog_name = self.cog_data.get("name", "")
                dept = self.cog_data.get("dept", "s")
                paths = globals.SUIT_TEXTURE_PATH

                if "suitTex" in self.cog_data and not was_originally_skel:
                    self.apply_suit_texture(self.cog_data["suitTex"])
                elif cog_name in paths and not was_originally_skel:
                    self.apply_suit_texture(paths[cog_name][0])
                else:
                    self.apply_suit_texture(globals.DEPT_SUIT_TEX_MAP.get(dept))

        if is_toggled_skel or is_natural_skel:
            if self.store_skelecog_texture:
                self.apply_suit_texture(self.store_skelecog_texture)
            else:
                dept = self.cog_data.get("dept", "s")
                skel_tex_key = dept + "s"
                paths = globals.SUIT_TEXTURE_PATH

                if was_originally_skel and "suitTex" in self.cog_data:
                    self.apply_suit_texture(self.cog_data["suitTex"])
                elif skel_tex_key in paths:
                    self.apply_suit_texture(paths[skel_tex_key][0])
                else:
                    self.apply_suit_texture(globals.DEPT_SKELE_SUIT_TEX_MAP.get(dept))

        if self.store_virtualize:
            self.skele_color_index = (self.skele_color_index - 1) % len(globals.SKELECOG_METER_COLORS)
            self.toggle_virtualize()

        if self.store_emblem is not None:
            self.apply_emblem(self.store_emblem)

        if self.store_health_meter:
            self.skele_i -= 1
            self.skele_i %= 7
            self.toggle_skele_meter_color()

        if self.store_body_anim is not None:
            self.set_animation(self.store_body_anim)
            self.control_panel.loop_body_var.set(self.store_body_loop)
            self.control_panel.body_frame_slider.set(self.store_body_frame)
            self.actor.pose(self.store_body_anim, self.store_body_frame)

            if not self.store_body_adjusted:
                if not autoplay and self.store_body_playing:
                    self.play_body_animation()
                else:
                    self.check_body_autoplay()

        if self.store_head_anim is not None:
            active_head = self.get_active_head()

            if active_head and hasattr(active_head, 'pose'):
                self.set_head_animation(self.store_head_anim)
                self.control_panel.loop_head_var.set(self.store_head_loop)
                self.control_panel.head_frame_slider.set(self.store_head_frame)
                active_head.pose(self.store_head_anim, self.store_head_frame)

                if not self.store_head_adjusted:
                    if not autoplay and self.store_head_playing:
                        self.play_head_animation()
                    else:
                        self.check_head_autoplay()

        for axis, value in self.store_head_hpr.items():
            self.update_head_hpr(axis, value)
        self.control_panel.update_head_hpr_sliders()

        for axis, value in self.store_flatten_body.items():
            self.update_flatten_body(axis, value)
        for axis, value in self.store_flatten_head.items():
            self.update_flatten_head(axis, value)

        if self.store_body_color:
            self.apply_body_colorscale(self.store_body_hex_color)
        if self.store_head_color:
            self.apply_head_color(self.store_head_hex_color)
        if self.store_hand_color:
            self.apply_hand_color(self.store_hand_hex_color)

        if self.store_unique_suit_toggle:
            self.toggle_unique_suit(False)
        if self.store_ms_toggle_1:
            self.control_panel.unique_vars["ms_toggle_1"].set(True)
        if getattr(self, 'store_hr_toggle_1', False) and "hr_toggle_1" in self.control_panel.unique_vars:
            self.control_panel.unique_vars["hr_toggle_1"].set(True)
        if getattr(self, 'store_dj_toggle_1', False) and "dj_toggle_1" in self.control_panel.unique_vars:
            self.control_panel.unique_vars["dj_toggle_1"].set(True)
        if getattr(self, 'store_dj_toggle_2', False) and "dj_toggle_2" in self.control_panel.unique_vars:
            self.control_panel.unique_vars["dj_toggle_2"].set(True)
        if getattr(self, 'store_ms_toggle_2', False) and "ms_toggle_2" in self.control_panel.unique_vars:
            self.control_panel.unique_vars["ms_toggle_2"].set(True)
            self.multislacker_toggles()
        if self.store_cs_toggle_1:
            self.control_panel.unique_vars["cs_toggle_1"].set(True)
            self.chainsaw_consultant_toggles(1)
        if self.store_cs_toggle_2:
            self.control_panel.unique_vars["cs_toggle_2"].set(True)
            self.chainsaw_consultant_toggles(2)
        if getattr(self, 'store_cs_toggle_3', False) and "cs_toggle_3" in self.control_panel.unique_vars:
            self.control_panel.unique_vars["cs_toggle_3"].set(True)
            self.chainsaw_consultant_toggles(3)

        if "ds_slot_l" in self.control_panel.unique_vars:
            self.control_panel.unique_vars["ds_slot_l"].set(getattr(self, 'store_ds_slot_l', "Duck"))
            self.control_panel.unique_vars["ds_slot_m"].set(getattr(self, 'store_ds_slot_m', "Duck"))
            self.control_panel.unique_vars["ds_slot_r"].set(getattr(self, 'store_ds_slot_r', "Duck"))

            spin_state = getattr(self, 'store_ds_spin', False)
            self.control_panel.unique_vars["ds_spin"].set(spin_state)

            if spin_state:
                self.toggle_spin_slots()
            else:
                self.update_slots()

        if "rm_weather" in self.control_panel.unique_vars:
            self.control_panel.unique_vars["rm_weather"].set(getattr(self, 'store_rm_weather', "Inversion"))
            self.update_rainmaker()

        if self.store_custom_model is not None:
            self.custom_model = loader.loadModel(self.store_custom_model)
            self.load_custom_model()

        for axis, value in self.store_custom_model_hpr.items():
            self.update_custom_model_hpr(axis, value)

        self.load_stored_props()

        self.refresh_battle_effects()
        # statu effects stuff
        if hasattr(self, 'control_panel') and hasattr(self.control_panel, 'is_stunned_var'):
            if self.control_panel.is_enraged_var.get():
                self.toggle_enrage_fire(False)
                self.toggle_enrage_fire(True)

            if self.control_panel.is_soaked_var.get():
                self.toggle_soaked(False)
                self.toggle_soaked(True)

            if self.control_panel.is_stunned_var.get():
                self.toggle_stunned(False)
                self.toggle_stunned(True)

    def load_stored_props(self):
        # Prop 1
        if self.store_prop1 != "zero":  # Load prop 1
            self.set_prop(self.store_prop1, False)

        for axis, value in self.store_prop1_hpr.items():  # Update HPR
            self.update_prop_hpr(axis, value)

        # Prop 2
        if self.store_prop2 != "zero":  # Load prop 2
            self.set_prop2(self.store_prop2, False)

        for axis, value in self.store_prop2_hpr.items():  # Update HPR
            self.update_prop2_hpr(axis, value)

    def apply_emblem(self, emblem_name):
        if self.actor:
            self.store_emblem = emblem_name
            emblem_map = globals.EMBLEM_MAP

            targets = []
            if hasattr(self, 'iconbase') and self.iconbase: targets.append(self.iconbase)
            if hasattr(self, 'skel_iconbase') and self.skel_iconbase: targets.append(self.skel_iconbase)
            if hasattr(self, 'zap_iconbase') and self.zap_iconbase: targets.append(self.zap_iconbase)

            for target in targets:
                target.show()
                for emblem in list(emblem_map)[:-2]:
                    current_emblem = globals.EMBLEM_MAP.get(emblem)
                    target.find(f'**/{current_emblem}').hide()

                if emblem_name not in ["light", "none"]:
                    target.find('**/emblem_hp').hide()
                    target.find('**/glow').hide()
                    target.find(f'**/{emblem_name}').show()
                elif emblem_name == "light":
                    target.find('**/emblem_hp').show()
                    target.find('**/glow').show()
                else:
                    target.find('**/emblem_hp').hide()
                    target.find('**/glow').hide()
                    target.hide()

            if emblem_name == "none":
                if self.actor.find('**/emblem_healthmeter'):
                    self.actor.find('**/emblem_healthmeter').hide()
                    self.actor.find('**/glow').hide()
            else:
                if self.actor.find('**/emblem_healthmeter'):
                    self.actor.find('**/emblem_healthmeter').show()
                    self.actor.find('**/glow').show()

    def update_custom_model_hpr(self, axis, value):
        if self.custom_model and not self.custom_model.isEmpty():
            self.set_POSHPR(self.custom_model, axis, value)
            self.store_custom_model_hpr[axis] = value

    def upload_custom_model(self):
        if not self.actor or self.actor.isEmpty():
            print("Please load a Cog before adding a custom model.")
            return

        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title="Select Custom .bam Model",
            filetypes=[("Panda3D Models", "*.bam"), ("All Files", "*.*")]
        )
        if not file_path:
            print("Custom model upload canceled.")
            return

        try:
            panda_path = Filename.fromOsSpecific(file_path)
            panda_path.makeTrueCase()

            if self.custom_model and not self.custom_model.isEmpty():
                self.custom_model.removeNode()
                self.custom_model = None
                self.store_custom_model = None

            self.custom_model = loader.loadModel(panda_path)
            self.store_custom_model = panda_path
            if not self.custom_model:
                print(f"Error: Failed to load model {panda_path}")
                return

            self.load_custom_model()
            self.control_panel.reset_prop_sliders(self.control_panel.custom_model_vars)
            for axis, value in globals.HEAD_HPR_DEFAULTS.items():
                self.update_custom_model_hpr(axis, value)

            print(f"Loaded custom model: {file_path}")

        except Exception as e:
            print(f"Failed to load custom model: {e}")

    def load_custom_model(self):
        head_joint = self.actor.find('**/joint_head')
        if not head_joint.isEmpty():
            self.custom_model.reparentTo(head_joint)
        else:
            self.custom_model.reparentTo(self.actor)

        self.control_panel.show_custom_model_tab(True)

    def update_frame(self, task):
        if not self.actor or self.current_animation == "zero":
            print("can not take screenshot frames: mo animation selected")
            if self.bool:
                self.setBackgroundColor(0, 0, 0)
            else:
                self.setBackgroundColor(self.background_color)
            return task.done

        total_frames = self.actor.getNumFrames(self.current_animation)

        active_head = self.get_active_head()

        has_head_anim = False
        total_head_frames = 0
        if active_head and isinstance(active_head, Actor) and self.current_head_animation != "zero":
            try:
                total_head_frames = active_head.getNumFrames(self.current_head_animation)
                has_head_anim = True
            except:
                has_head_anim = False

        if self.frame_index < total_frames:
            self.actor.stop()
            if hasattr(self, 'skelecog') and self.skelecog: self.skelecog.stop()
            if hasattr(self, 'zapped_skelecog') and self.zapped_skelecog: self.zapped_skelecog.stop()
            if hasattr(self, 'hw_body_actor') and self.hw_body_actor: self.hw_body_actor.stop()
            if hasattr(self, 'prop_item1_actor') and self.prop_item1_actor: self.prop_item1_actor.stop()
            if hasattr(self, 'prop_item2_actor') and self.prop_item2_actor: self.prop_item2_actor.stop()

            if has_head_anim and hasattr(active_head, 'stop'):
                active_head.stop()

            self.actor.pose(self.current_animation, self.frame_index)
            if hasattr(self, 'skelecog') and self.skelecog: self.skelecog.pose(self.current_animation, self.frame_index)
            if hasattr(self, 'zapped_skelecog') and self.zapped_skelecog: self.zapped_skelecog.pose(
                self.current_animation, self.frame_index)
            if hasattr(self, 'hw_body_actor') and self.hw_body_actor: self.hw_body_actor.pose(self.current_animation,
                                                                                              self.frame_index)

            if hasattr(self, 'boss_parts') and self.boss_parts:
                for part_name, part_actor in self.boss_parts.items():
                    if part_name == "head": continue
                    if isinstance(part_actor, Actor):
                        part_actor.pose(self.current_animation, self.frame_index)

            if hasattr(self, 'prop_item1_actor') and self.prop_item1_actor and self.prop_item1_actor.getCurrentAnim():
                p1_anim = self.prop_item1_actor.getCurrentAnim()
                self.prop_item1_actor.pose(p1_anim, self.frame_index % self.prop_item1_actor.getNumFrames(p1_anim))

            if hasattr(self, 'prop_item2_actor') and self.prop_item2_actor and self.prop_item2_actor.getCurrentAnim():
                p2_anim = self.prop_item2_actor.getCurrentAnim()
                self.prop_item2_actor.pose(p2_anim, self.frame_index % self.prop_item2_actor.getNumFrames(p2_anim))

            if has_head_anim:
                head_frame = 0
                if total_head_frames > 0:
                    head_frame = self.frame_index % total_head_frames
                active_head.pose(self.current_head_animation, head_frame)

            self.graphicsEngine.renderFrame()
            screenshot_name = os.path.join(self.frame_folder_path, f"{self.frame_index:03d}.png")
            self.screenshot(screenshot_name, False)

            self.frame_index += 1
            return task.cont
        else:
            print(
                f"finished taking {total_frames} screenshots! im pacesetter hey they are saved in {self.frame_folder_path}")
            if self.bool:
                self.setBackgroundColor(0, 0, 0)
            else:
                self.setBackgroundColor(self.background_color)

            self.play_body_animation()
            if has_head_anim:
                self.play_head_animation()
            return task.done

    def make_gif(self):
        if not self.actor or self.current_animation == "zero":
            print("can not take screenshot frames: mo animation selected")
            return

        self.frame_index = 0
        cog_data = globals.COG_DATA[self.current_cog]
        current_anim = getattr(self, 'current_animation', 'anim')
        date_string = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
        self.temp_frame_path = os.path.join(globals.SCREENSHOT_DIR,
                                            f"temp_{cog_data['cog']}_{current_anim}_{date_string}")

        if not os.path.exists(self.temp_frame_path):
            os.makedirs(self.temp_frame_path)

        if hasattr(self, 'play_body_animation'):
            self.stop_body_animation()
        if hasattr(self, 'head') and self.head and self.current_head_animation != "zero":
            self.stop_head_animation()

        self.setBackgroundColor(0, 0, 0)

        self.restore_shadow = False
        if hasattr(self, 'control_panel') and getattr(self.control_panel, 'is_shadow_var', None):
            if self.control_panel.is_shadow_var.get():
                self.restore_shadow = True
                self.control_panel.is_shadow_var.set(False)
                if hasattr(self, 'toggle_shadow'):
                    self.toggle_shadow()

        self.taskMgr.add(self.update_frame_gif, "UpdateFrameGifTask")

    def update_frame_gif(self, task):
        if not self.actor or self.current_animation == "zero":
            print("can not take screenshot frames: mo animation selected")
            if self.bool:
                self.setBackgroundColor(0, 0, 0)
            else:
                self.setBackgroundColor(self.background_color)
            return task.done

        total_frames = self.actor.getNumFrames(self.current_animation)

        active_head = self.get_active_head()

        has_head_anim = False
        total_head_frames = 0
        if active_head and isinstance(active_head, Actor) and self.current_head_animation != "zero":
            try:
                total_head_frames = active_head.getNumFrames(self.current_head_animation)
                has_head_anim = True
            except:
                has_head_anim = False

        if self.frame_index < total_frames:
            self.actor.stop()
            if hasattr(self, 'skelecog') and self.skelecog: self.skelecog.stop()
            if hasattr(self, 'zapped_skelecog') and self.zapped_skelecog: self.zapped_skelecog.stop()
            if hasattr(self, 'hw_body_actor') and self.hw_body_actor: self.hw_body_actor.stop()
            if hasattr(self, 'prop_item1_actor') and self.prop_item1_actor: self.prop_item1_actor.stop()
            if hasattr(self, 'prop_item2_actor') and self.prop_item2_actor: self.prop_item2_actor.stop()

            if has_head_anim and hasattr(active_head, 'stop'):
                active_head.stop()

            self.actor.pose(self.current_animation, self.frame_index)
            if hasattr(self, 'skelecog') and self.skelecog: self.skelecog.pose(self.current_animation, self.frame_index)
            if hasattr(self, 'zapped_skelecog') and self.zapped_skelecog: self.zapped_skelecog.pose(
                self.current_animation, self.frame_index)
            if hasattr(self, 'hw_body_actor') and self.hw_body_actor: self.hw_body_actor.pose(self.current_animation,
                                                                                              self.frame_index)

            if hasattr(self, 'boss_parts') and self.boss_parts:
                for part_name, part_actor in self.boss_parts.items():
                    if part_name == "head": continue
                    if isinstance(part_actor, Actor):
                        part_actor.pose(self.current_animation, self.frame_index)

            if hasattr(self, 'prop_item1_actor') and self.prop_item1_actor and self.prop_item1_actor.getCurrentAnim():
                p1_anim = self.prop_item1_actor.getCurrentAnim()
                self.prop_item1_actor.pose(p1_anim, self.frame_index % self.prop_item1_actor.getNumFrames(p1_anim))

            if hasattr(self, 'prop_item2_actor') and self.prop_item2_actor and self.prop_item2_actor.getCurrentAnim():
                p2_anim = self.prop_item2_actor.getCurrentAnim()
                self.prop_item2_actor.pose(p2_anim, self.frame_index % self.prop_item2_actor.getNumFrames(p2_anim))

            if has_head_anim:
                head_frame = 0
                if total_head_frames > 0:
                    head_frame = self.frame_index % total_head_frames
                active_head.pose(self.current_head_animation, head_frame)

            self.graphicsEngine.renderFrame()
            screenshot_name = os.path.join(self.temp_frame_path, f"{self.frame_index:03d}.png")
            self.screenshot(screenshot_name, False)

            self.frame_index += 1
            return task.cont
        else:
            print(f"finished taking {total_frames} screenshots. hi im pacesetter and im compiling your gif")
            cog_data = globals.COG_DATA[self.current_cog]
            current_anim = getattr(self, 'current_animation', 'anim')
            date_string = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
            filename = f"{cog_data['cog']}{current_anim}-{date_string}.gif"
            gif_filename = os.path.join(globals.SCREENSHOT_DIR, filename)

            self.compile_gif_and_cleanup(self.temp_frame_path, gif_filename, fps=24)

            if self.bool:
                self.setBackgroundColor(0, 0, 0)
            else:
                self.setBackgroundColor(self.background_color)

            if getattr(self, 'restore_shadow', False):
                if hasattr(self, 'control_panel') and getattr(self.control_panel, 'is_shadow_var', None):
                    self.control_panel.is_shadow_var.set(True)
                    if hasattr(self, 'toggle_shadow'):
                        self.toggle_shadow()

            self.play_body_animation()
            if has_head_anim:
                self.play_head_animation()
            return task.done

    def start_screenshots(self, task):
        self.frame_index = 0
        self.setBackgroundColor(0, 0, 0)

        if self.actor:
            self.actor.stop()
        if hasattr(self, 'head') and self.head and hasattr(self.head, 'stop'):
            self.head.stop()

        self.taskMgr.add(self.update_frame, "TakeScreenshotsTask")
        return task.done

    def take_screenshot_frames(self):
        if not self.actor or self.current_animation == "zero":
            print("can not take screenshot frames: mo animation selected")
            return

        self.frame_index = 0
        cog_data = globals.COG_DATA[self.current_cog]
        current_anim = getattr(self, 'current_animation', 'anim')
        date_string = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
        self.frame_folder_path = os.path.join(globals.SCREENSHOT_DIR, f"{cog_data['cog']}_{current_anim}_{date_string}")

        if not os.path.exists(self.frame_folder_path):
            os.makedirs(self.frame_folder_path)

        if hasattr(self, 'play_body_animation'):
            self.stop_body_animation()
        if hasattr(self, 'head') and self.head and self.current_head_animation != "zero":
            self.stop_head_animation()

        self.setBackgroundColor(0, 0, 0)

        self.taskMgr.add(self.update_frame, "UpdateFrameTask")

    def update_body_pose(self, frame_value):
        if self.current_animation != "zero":
            frame = int(round(float(frame_value)))
            if frame != 0:
                self.store_body_frame = frame
                self.store_body_adjusted = True
                self.store_body_playing = False

            if self.cog_data.get("cog_type") == "boss" and hasattr(self, "boss_parts"):
                for part_name, part_actor in self.boss_parts.items():
                    if part_name == "head": continue
                    if isinstance(part_actor, Actor):
                        part_actor.pose(self.current_animation, frame)

            elif self.actor:
                self.actor.pose(self.current_animation, frame)
                if hasattr(self, 'skelecog') and self.skelecog:
                    self.skelecog.pose(self.current_animation, frame)
                if hasattr(self, 'zapped_skelecog') and self.zapped_skelecog:
                    self.zapped_skelecog.pose(self.current_animation, frame)
                if hasattr(self, 'hw_body_actor') and self.hw_body_actor:
                    self.hw_body_actor.pose(self.current_animation, frame)

    def update_head_pose(self, frame_value):
        active_head = self.get_active_head()
        if self.current_head_animation != "zero" and active_head and isinstance(active_head, Actor):
            frame = int(round(float(frame_value)))
            if frame != 0:
                self.store_head_frame = frame
                self.store_head_adjusted = True
                self.store_head_playing = False
            active_head.pose(self.current_head_animation, frame)

    def get_head_hpr_default_values(self):
        defaults = {
            "x": 0.0,
            "y": 0.0,
            "z": 0.0,
            "h": 0.0,
            "p": 0.0,
            "r": 0.0,
            "scale": 1.0
        }
        cog = globals.COG_DATA.get(self.current_cog, {})

        head_pos_map = {
            "headPos": "z",
            "headPosY": "y",
            "headPosH": "h",
            "headPosP": "p",
            "headSize": "scale"
        }
        for pos_key, pos_type in head_pos_map.items():
            value = cog.get(pos_key)
            if value is not None:
                defaults[pos_type] = value

        globals.HEAD_HPR_DEFAULTS = defaults.copy()

        return defaults

    def toggle_enrage_fire(self, active):
        if not self.fire_particle_base:
            print("Fire particle not loaded.")
            return

        if active:
            self.taskMgr.add(self.spawn_fire_task, "SpawnFireTask")
            self.taskMgr.add(self.update_fire_task, "UpdateFireTask")
        else:
            self.taskMgr.remove("SpawnFireTask")
            self.taskMgr.remove("UpdateFireTask")
            for fire_data in self.active_fires:
                fire_data["node"].removeNode()
            self.active_fires.clear()

    def spawn_fire_task(self, task):
        if not self.actor:
            return task.cont

        fire_np = self.fire_particle_base.copyTo(self.render)

        base_pos = self.actor.getPos(self.render)
        offset_x = random.uniform(-0.5, 0.5)
        offset_y = random.uniform(-0.5, 0.5)
        fire_np.setPos(base_pos.getX() + offset_x, base_pos.getY() + offset_y, base_pos.getZ())

        fire_np.setBillboardPointEye()

        scale_height = random.uniform(0.4, 0.6)
        fire_np.setSx(scale_height * 0.55)
        fire_np.setSz(scale_height)

        # fire color, unsure if it needs to be adjusted?
        fire_np.setColorScale(1.0, 0.3, 0.3, 1.0)
        fire_np.setTransparency(1)

        angle = random.uniform(0, 2 * math.pi)
        spread_speed = random.uniform(0.1, 1.0)

        vel_x = math.cos(angle) * spread_speed
        vel_y = math.sin(angle) * spread_speed
        vel_z = random.uniform(1.5, 2.5)

        self.active_fires.append({
            "node": fire_np,
            "life": 1.0,
            "vel_x": vel_x,
            "vel_y": vel_y,
            "vel_z": vel_z
        })

        task.delayTime = random.uniform(0.05, 0.15)
        return task.again

    def update_fire_task(self, task):
        dt = globalClock.getDt()
        alive_fires = []

        for fire_data in self.active_fires:
            node = fire_data["node"]
            fire_data["life"] -= dt * 0.30

            if fire_data["life"] <= 0:
                node.removeNode()
            else:
                new_x = node.getX() + (fire_data["vel_x"] * dt)
                new_y = node.getY() + (fire_data["vel_y"] * dt)
                new_z = node.getZ() + (fire_data["vel_z"] * dt)

                node.setPos(new_x, new_y, new_z)

                node.setAlphaScale(fire_data["life"])
                alive_fires.append(fire_data)

        self.active_fires = alive_fires
        return task.cont

    def toggle_soaked(self, active):
        if active:
            if self.actor:
                self.actor.setColorScale(0.65, 0.65, 0.95, 1.0)

            if self.drop_particle_base:
                self.taskMgr.add(self.spawn_drop_task, "SpawnDropTask")
                self.taskMgr.add(self.update_drop_task, "UpdateDropTask")
        else:
            if self.actor:
                self.actor.clearColorScale()
                if self.store_body_color:
                    self.apply_body_colorscale(self.store_body_hex_color)
                if self.store_head_color:
                    self.apply_head_color(self.store_head_hex_color)

            self.taskMgr.remove("SpawnDropTask")
            self.taskMgr.remove("UpdateDropTask")
            for drop_data in self.active_drops:
                drop_data["node"].removeNode()
            self.active_drops.clear()

    def spawn_drop_task(self, task):
        if not self.actor or not self.drop_particle_base:
            return task.cont

        drop_np = self.drop_particle_base.copyTo(self.render)

        bounds = self.actor.getTightBounds(self.render)

        if bounds:
            min_bounds, max_bounds = bounds

            target_x = random.uniform(min_bounds.getX(), max_bounds.getX())
            target_y = random.uniform(min_bounds.getY(), max_bounds.getY())

            min_z = min_bounds.getZ()
            max_z = max_bounds.getZ()
            target_z = random.uniform(min_z + ((max_z - min_z) * 0.20), max_z)

        else:
            base_pos = self.actor.getPos(self.render)
            target_x = base_pos.getX() + random.uniform(-1.5, 1.5)
            target_y = base_pos.getY() + random.uniform(-1.5, 1.5)
            target_z = base_pos.getZ() + random.uniform(2.0, 4.0)

        drop_np.setPos(target_x, target_y, target_z)

        drop_np.setBillboardPointEye()
        drop_np.setScale(random.uniform(0.3, 0.3))
        drop_np.setTransparency(1)

        vel_z = random.uniform(-5.0, -3.0)

        self.active_drops.append({
            "node": drop_np,
            "life": 1.0,
            "vel_z": vel_z
        })

        task.delayTime = random.uniform(0.1, 0.3)
        return task.again

    def update_drop_task(self, task):
        dt = globalClock.getDt()
        alive_drops = []

        for drop_data in self.active_drops:
            node = drop_data["node"]
            drop_data["life"] -= dt * 1.1

            if drop_data["life"] <= 0:
                node.removeNode()
            else:
                new_z = node.getZ() + (drop_data["vel_z"] * dt)
                node.setZ(new_z)
                node.setAlphaScale(drop_data["life"])
                alive_drops.append(drop_data)

        self.active_drops = alive_drops
        return task.cont

    def update_stun_position(self):
        if not hasattr(self, 'head') or self.head.isEmpty():
            return

        stun_attached = hasattr(self, 'stun_effect') and self.stun_effect and self.stun_effect.getParent() == self.head
        sued_attached = hasattr(self, 'sued_effect') and self.sued_effect and self.sued_effect.getParent() == self.head

        if stun_attached: self.stun_effect.detachNode()
        if sued_attached: self.sued_effect.detachNode()

        bounds = self.head.getTightBounds(self.head)

        if bounds:
            highest_local_z = bounds[1].getZ()

            manual_offset = 0.0
            if hasattr(self, 'control_panel') and hasattr(self.control_panel, 'stun_z_offset_var'):
                try:
                    manual_offset = self.control_panel.stun_z_offset_var.get()
                except tk.TclError:
                    pass

            target_z = highest_local_z - 0.05 + manual_offset
            flatten_head = getattr(self, 'store_flatten_head', {})
            head_sx = flatten_head.get("Sx", 1.0)
            head_sy = flatten_head.get("Sy", 1.0)
            head_sz = flatten_head.get("Sz", 1.0)

            target_scale = (1.0 / (head_sx if head_sx != 0 else 0.01),
                            1.0 / (head_sy if head_sy != 0 else 0.01),
                            1.0 / (head_sz if head_sz != 0 else 0.01))

            if stun_attached:
                self.stun_effect.reparentTo(self.head)
                self.stun_effect.setPos(0, 0, target_z)
                self.stun_effect.setHpr(0, 0, 0)
                self.stun_effect.setScale(*target_scale)

            if sued_attached:
                self.sued_effect.reparentTo(self.head)
                self.sued_effect.setPos(0, 0, target_z)
                self.sued_effect.setHpr(0, 0, 0)
                self.sued_effect.setScale(*target_scale)

            if self.suit_type in ["bossCog", "boss"]:
                self.stun_effect.setPosHprScale(7.00, 0.00, 0.00, 0.00, 0.00, 90.00, 3.00, 3.00,
                                                3.00)  # (4.780, -0.165, -0.165, 0.00, 0.00, 90.00, 3.00, 3.00, 3.00)
                self.sued_effect.setPosHprScale(7.00, 0.00, 0.00, 0.00, 0.00, 90.00, 3.00, 3.00, 3.00)

    def toggle_stunned(self, active):
        if active:
            if hasattr(self, 'head') and not self.head.isEmpty():
                self.stun_effect.reparentTo(self.head)

                color_path = os.path.join(globals.RESOURCES_DIR, "phase_5", "maps", "battle",
                                          "ttcc_fx_battleParticles_palette_1.jpg")
                alpha_path = os.path.join(globals.RESOURCES_DIR, "phase_5", "maps", "battle",
                                          "ttcc_fx_battleParticles_palette_1_a.rgb")

                if os.path.exists(color_path) and os.path.exists(alpha_path):
                    stun_tex = loader.loadTexture(color_path, alpha_path)
                else:
                    stun_tex = loader.loadTexture('phase_5/maps/battle/ttcc_fx_battleParticles_palette_1.jpg')

                self.update_stun_position()

                self.stun_effect.setTexture(stun_tex, 1)
                self.stun_effect.setTransparency(1)

                self.stun_effect.loop("stun")
                self.stun_effect.setBlend(frameBlend=True)
        else:
            self.stun_effect.stop()
            self.stun_effect.detachNode()

    def toggle_sued(self, active):
        if active:
            if hasattr(self, 'head') and not self.head.isEmpty():
                self.sued_effect.reparentTo(self.head)
                self.update_stun_position()
                self.sued_effect.loop("stun")
                self.sued_effect.setBlend(frameBlend=True)
        else:
            self.sued_effect.stop()
            self.sued_effect.detachNode()

    def refresh_battle_effects(self):
        if hasattr(self, 'control_panel'):
            if hasattr(self.control_panel, 'is_enraged_var') and self.control_panel.is_enraged_var.get():
                self.toggle_enrage_fire(False)
                self.toggle_enrage_fire(True)

            if hasattr(self.control_panel, 'is_soaked_var') and self.control_panel.is_soaked_var.get():
                self.toggle_soaked(False)
                self.toggle_soaked(True)

            if hasattr(self.control_panel, 'is_stunned_var') and self.control_panel.is_stunned_var.get():
                self.toggle_stunned(False)
                self.toggle_stunned(True)

            if hasattr(self.control_panel, 'is_sued_var') and self.control_panel.is_sued_var.get():
                self.toggle_sued(False)
                self.toggle_sued(True)

            if hasattr(self.control_panel, 'is_zapped_var') and self.control_panel.is_zapped_var.get():
                self.toggle_zapped(False)
                self.toggle_zapped(True)

            if hasattr(self.control_panel, 'is_insured_var') and self.control_panel.is_insured_var.get():
                self.toggle_insured(False)
                self.toggle_insured(True)

            if hasattr(self.control_panel, 'is_chilled_var') and self.control_panel.is_chilled_var.get():
                self.toggle_chilled(False)
                self.toggle_chilled(True)

            if hasattr(self.control_panel, 'is_frozen_var') and self.control_panel.is_frozen_var.get():
                self.toggle_frozen(False)
                self.toggle_frozen(True)

    def get_active_head(self):
        if hasattr(self, 'control_panel'):
            if hasattr(self.control_panel, 'is_zapped_var') and self.control_panel.is_zapped_var.get():
                if hasattr(self, 'zapped_head') and self.zapped_head:
                    return self.zapped_head
            if hasattr(self.control_panel, 'is_skelecog_var') and self.control_panel.is_skelecog_var.get():
                if hasattr(self, 'skelecog_skull') and self.skelecog_skull:
                    return self.skelecog_skull
        return self.head if hasattr(self, 'head') else None

    def darken_cog(self, active=True):  # for zap
        is_made_skelecog = hasattr(self, 'control_panel') and self.control_panel.is_skelecog_var.get()
        # darken Cog
        if active:
            if self.suit_type in ["as", "bs", "cs"] or is_made_skelecog:
                target_actor = self.skelecog if is_made_skelecog else self.actor
                if target_actor:
                    for part in ['body', 'hands', 'necktie-s', 'necktie-w', 'bowtie']:
                        np = target_actor.find(f'**/{part}')
                        if not np.isEmpty():
                            np.setColorScale(1.0, 1.0, 0.0, 1.0)

                    chest = target_actor.find("**/joint_attachMeter")
                    if not chest.isEmpty(): chest.hide()

                target_head = self.skelecog_skull if is_made_skelecog else self.head
                if hasattr(self, 'head') and self.head:
                    self.head.setColorScale(1.0, 1.0, 0.0, 1.0)
                if target_head and target_head != self.head:
                    target_head.setColorScale(1.0, 1.0, 0.0, 1.0)
                return

            target_actor = self.hw_body_actor if hasattr(self, 'hw_body_actor') and self.hw_body_actor else self.actor

            if target_actor:
                for part in ['body', 'hands', 'necktie-s', 'necktie-w', 'bowtie', 'highroller_body']:
                    np = target_actor.find(f'**/{part}')
                    if not np.isEmpty():
                        np.setColorScale(0, 0, 0, 1.0)
                        np.setDepthWrite(False)

                chest = target_actor.find("**/joint_attachMeter")
                if not chest.isEmpty():
                    chest.hide()

            if hasattr(self, 'head') and self.head:
                self.head.setColorScale(0, 0, 0, 1.0)
                self.head.setDepthWrite(False)

        # disable darken
        else:
            target_actor = self.hw_body_actor if hasattr(self, 'hw_body_actor') and self.hw_body_actor else self.actor
            if target_actor:
                for part in ['body', 'hands', 'necktie-s', 'necktie-w', 'bowtie', 'highroller_body']:
                    np = target_actor.find(f'**/{part}')
                    if not np.isEmpty():
                        np.clearColorScale()
                        np.clearDepthWrite()

                chest = target_actor.find("**/joint_attachMeter")
                if not chest.isEmpty() and getattr(self, 'is_body', True):
                    chest.show()
            if hasattr(self, 'head') and self.head:
                self.head.clearColorScale()
                self.head.clearDepthWrite()
                if getattr(self, 'store_head_color', False):
                    self.apply_head_color(self.store_head_hex_color)

            if self.suit_type in ["as", "bs", "cs"] or is_made_skelecog:
                target_actor = self.skelecog if is_made_skelecog else self.actor
                if target_actor:
                    for part in ['body', 'hands', 'necktie-s', 'necktie-w', 'bowtie']:
                        np = target_actor.find(f'**/{part}')
                        if not np.isEmpty(): np.clearColorScale()

                target_head = self.skelecog_skull if is_made_skelecog else self.head
                if hasattr(self, 'head') and self.head:
                    self.head.clearColorScale()
                if target_head and target_head != self.head:
                    target_head.clearColorScale()
                return

            if getattr(self, 'store_body_color', False):
                self.apply_body_colorscale(self.store_body_hex_color)
            if getattr(self, 'store_hand_color', False):
                self.apply_hand_color(self.store_hand_hex_color)

    def toggle_zapped(self, active, stored_suit_path=None):
        if active:
            if hasattr(self, 'zapped_skelecog') and self.zapped_skelecog:
                self.zapped_skelecog.cleanup()
                self.zapped_skelecog.removeNode()
                self.zapped_skelecog = None
            if hasattr(self, 'zapped_head') and self.zapped_head:
                if hasattr(self.zapped_head, 'cleanup'): self.zapped_head.cleanup()
                self.zapped_head.removeNode()
                self.zapped_head = None

            self.switch_toggle(self.control_panel.is_zapped_var, self.control_panel.is_skelecog_var,
                               self.toggle_skelecog)
            self.is_zapped = True

            if self.suit_type in ["bossCog", "boss"]: return

            cog_id = self.cog_data.get("cog", "").lower().replace(" ", "")
            self.darken_cog()

            suit = self.suit_type
            skel_suit = "as"
            skel_head_model = globals.SUIT_A_SKELECOG_HEAD
            skel_head_name = "suitA_skeleton_skull"

            if suit in ["b", "bf", "bc", "ps", "rm", "bs"]:
                skel_suit = "bs"
                skel_head_model = globals.SUIT_B_SKELECOG_HEAD
                skel_head_name = "suitB_skeleton_skull"
            elif suit in ["c", "cf", "cs"]:
                skel_suit = "cs"
                skel_head_model = globals.SUIT_C_SKELECOG_HEAD
                skel_head_name = "suitC_skeleton_skull"

            selected_mod = None
            if hasattr(self, 'control_panel') and self.control_panel.selected_suit_mod_var.get():
                selected_mod = self.control_panel.selected_suit_mod_var.get()
            skel_suits = ["as", "bs", "cs"]
            if selected_mod and selected_mod in skel_suits:
                skel_suit = selected_mod

            manager_list = cog_id in [
                "factoryforeman", "mintsupervisor", "headattorney", "clubpresident",
                "derrickman", "laa", "prr", "derrickhand", "dold", "dopa", "duckshuffler",
                "deepdiver", "gatekeeper", "bellringer", "mouthpiece", "firestarter",
                "treekiller", "featherbedder", "prethinker", "rainmaker", "witchhunter",
                "multislacker", "majorplayer", "plutocrat", "chainsawconsultant", "pacesetter",
                "litigator", "stenographer", "scapegoat", "casemanager", "counterclaim",
                "counterfit", "highroller", "reddheirwing"
            ]

            body_path = globals.SUIT_MODEL_DICT.get(skel_suit)
            if skel_suit == "as":
                anims = globals.SUIT_A_ANIMATION_DICT
            elif skel_suit == "bs":
                anims = globals.SUIT_B_ANIMATION_DICT
            elif skel_suit == "cs":
                anims = globals.SUIT_C_ANIMATION_DICT
            else:
                anims = {}

            self.zapped_skelecog = Actor(body_path, anims)
            self.zapped_skelecog.reparentTo(self.actor)
            self.zapped_skelecog.setBlend(frameBlend=True)

            dept = self.cog_data.get("dept", "s")
            is_exec = hasattr(self, 'control_panel') and self.control_panel.is_executive_var.get()

            if hasattr(self, 'store_skelecog_texture') and self.store_skelecog_texture:
                tex_path = self.store_skelecog_texture
            else:
                skel_tex_key = dept + "s"
                skel_tex_list = globals.SUIT_TEXTURE_PATH.get(skel_tex_key)
                if skel_tex_list:
                    if (is_exec or manager_list) and len(skel_tex_list) > 1:
                        tex_path = skel_tex_list[1]
                    else:
                        orig_suit = self.cog_data.get("suit", "")
                        if orig_suit in ["as", "bs", "cs"] and "suitTex" in self.cog_data:
                            tex_path = self.cog_data["suitTex"]
                        else:
                            tex_path = skel_tex_list[0]
                else:
                    tex_path = globals.DEPT_SKELE_SUIT_TEX_MAP.get(dept, globals.SELLBOT_SKELE_SUIT)

            tex = loader.loadTexture(tex_path)

            for part in ['body', 'necktie-s', 'necktie-w', 'bowtie']:
                self.zapped_skelecog.findAllMatches(f'**/{part}').setTexture(tex, 1)

            if hasattr(self, 'apply_skelecog_hand_color'):
                self.apply_skelecog_hand_color(self.zapped_skelecog)

            if cog_id == "derrickhand":
                skel_head_model = f"{globals.RESOURCES_DIR}/phase_12/models/char/suits/ttcc_ene_derrickhand_skele-zero.bam"
                skel_head_name = "ttcc_ene_derrickhand_skele"
            elif cog_id == "clubpresident":
                skel_head_model = f"{globals.RESOURCES_DIR}/phase_12/models/char/suits/ttcc_ene_clubpresident-zero.bam"
                skel_head_name = "ttcc_ene_clubpresident"
            elif cog_id == "chainsawconsultant":
                skel_head_model = f"{globals.RESOURCES_DIR}/phase_12/models/char/suits/ttcc_ene_chainsaw-zero.bam"
                skel_head_name = "ttcc_ene_chainsaw"

            if getattr(self, 'store_skelecog_skull', None) is not None:
                skel_head_model = self.store_skelecog_skull
            if getattr(self, 'store_skel_head_name', None) is not None:
                skel_head_name = self.store_skel_head_name

            if getattr(self, 'store_skelecog_skull', None) is None:
                self.store_skelecog_skull = skel_head_model
                self.store_skel_head_name = skel_head_name

            skel_head_anim_dict, skel_head_anims = globals.HEAD_ANIMATION_PATH(skel_head_name)

            if len(skel_head_anims) > 1:
                self.zapped_head = Actor(skel_head_model, skel_head_anim_dict)
                self.zapped_head.setBlend(frameBlend=True)
            else:
                self.zapped_head = loader.loadModel(skel_head_model)

            self.zapped_head.reparentTo(self.zapped_skelecog.find('**/joint_head'))

            if cog_id not in ["derrickhand", "clubpresident"]:
                self.zapped_head.setTexture(tex, 1)

            for axis, value in self.store_head_hpr.items():
                self.set_POSHPR(self.zapped_head, axis, value)
            for axis, value in self.store_flatten_head.items():
                self.set_depth(self.zapped_head, axis, value)

            self.store_original_head_anims = self.available_head_animations
            self.available_head_animations = skel_head_anims

            if hasattr(self, 'control_panel'):
                self.control_panel.update_animation_lists(self.available_animations, self.available_head_animations)
                self.control_panel.update_anim_slider_range("head", 0)

            if self.current_head_animation in skel_head_anims and isinstance(self.zapped_head, Actor):
                self.zapped_head.loop(self.current_head_animation)
            else:
                self.current_head_animation = "zero"
                if isinstance(self.zapped_head, Actor) and "zero" in skel_head_anims:
                    self.zapped_head.loop("zero")

            zap_chest = self.zapped_skelecog.find("**/joint_attachMeter")
            if not zap_chest.isEmpty():
                if skel_suit in ["as", "bs", "cs"]:
                    zap_chest.hide()
                else:
                    zap_chest.show()
                    self.zap_iconbase = loader.loadModel(globals.COG_ICONS_BASE)
                    self.zap_iconbase.reparentTo(zap_chest)
                    self.zap_iconbase.setPosHprScale(*globals.COG_ICON_HPR)
                    zap_chest.setH(0)

                    for emb in ['emblem_hp', 'glow', 'emblem_sales', 'emblem_money', 'emblem_legal', 'emblem_corp',
                                'emblem_board']:
                        self.zap_iconbase.findAllMatches(f'**/{emb}').hide()

                    if getattr(self, 'store_emblem', None) and self.store_emblem not in ["light", "none"]:
                        self.zap_iconbase.findAllMatches(f'**/{self.store_emblem}').show()
                    elif getattr(self, 'store_emblem', None) == "light":
                        hp = self.zap_iconbase.findAllMatches('**/emblem_hp')
                        glow = self.zap_iconbase.findAllMatches('**/glow')
                        hp.show();
                        hp.setColor(self.skele_meter_color)
                        glow.show();
                        glow.setColor(self.skele_meter_color)

                    if skel_suit in ["a", "af", "cch", "mph", "hr"]:
                        self.zap_iconbase.setY(-0.10)
                    elif skel_suit in ["c"]:
                        self.zap_iconbase.setY(0.10)
                    elif skel_suit in ["cf"]:
                        self.zap_iconbase.setY(0.02);
                        self.zap_iconbase.setZ(0.23);
                        self.zap_iconbase.setP(2.5)

            self.zapped_skelecog.find('**/glow').hide()

            for tie in ['necktie-s', 'necktie-w', 'bowtie']:
                self.zapped_skelecog.findAllMatches(f'**/{tie}').hide()

            for tie_name in ['necktie-s', 'necktie-w', 'bowtie']:
                main_tie = self.actor.find(f'**/{tie_name}')
                if not main_tie.isEmpty() and not main_tie.isHidden():
                    self.zapped_skelecog.findAllMatches(f'**/{tie_name}').show()

            self.zapped_skelecog.setBin("fixed", 40)
            self.sync_overlay_animation(self.zapped_skelecog)

            if skel_head_name:
                cog_data = globals.COG_DATA.get(self.current_cog, None)
                if cog_id == "chainsawconsultant": self.setup_chainsaw_skelecog_head(self.zapped_head)
                headPosMap = {
                    "headPos": self.zapped_head.setZ,
                    "headPosY": self.zapped_head.setY,
                    "headPosP": self.zapped_head.setP,
                    "headPosH": self.zapped_head.setH
                }
                if cog_id == "clubpresident":
                    for part, setPart in headPosMap.items():
                        if part in cog_data: setPart(cog_data[part])

        else:
            self.is_zapped = False

            if hasattr(self, 'zapped_skelecog') and self.zapped_skelecog:
                self.zapped_skelecog.cleanup()
                self.zapped_skelecog.removeNode()
                self.zapped_skelecog = None
            if hasattr(self, 'zapped_head') and self.zapped_head:
                if hasattr(self.zapped_head, 'cleanup'): self.zapped_head.cleanup()
                self.zapped_head.removeNode()
                self.zapped_head = None

            self.darken_cog(False)

            if hasattr(self, 'store_original_head_anims'):
                self.available_head_animations = self.store_original_head_anims
                if hasattr(self, 'control_panel'):
                    self.control_panel.update_animation_lists(self.available_animations, self.available_head_animations)
                    self.control_panel.update_anim_slider_range("head", 0)
                self.current_head_animation = "zero"

    def toggle_insured(self, active):
        if active:
            if not hasattr(self, 'insured_effect') or not self.insured_effect:
                from direct.particles.ParticleEffect import ParticleEffect
                from direct.particles.Particles import Particles
                from panda3d.physics import (BaseParticleRenderer, BaseParticleEmitter,
                                             SparkleParticleRenderer)
                from panda3d.core import Vec3, Vec4, Point3

                self.insured_effect = ParticleEffect()
                p0 = Particles('insured_sparkles')

                p0.setFactory("PointParticleFactory")
                p0.factory.setLifespanBase(0.7)
                p0.factory.setLifespanSpread(0.2)
                p0.factory.setMassBase(1.0)
                p0.factory.setTerminalVelocityBase(400.0)

                p0.setRenderer("SparkleParticleRenderer")
                p0.renderer.setAlphaMode(BaseParticleRenderer.PRALPHANONE)
                p0.renderer.setUserAlpha(1.0)

                p0.renderer.setCenterColor(Vec4(0, 255 / 255.0, 0, 1.0))
                p0.renderer.setEdgeColor(Vec4(0, 255 / 255.0, 0, 1.0))

                p0.renderer.setBirthRadius(0.15)
                p0.renderer.setDeathRadius(0.05)
                p0.renderer.setLifeScale(SparkleParticleRenderer.SPSCALE)

                p0.setEmitter("SphereVolumeEmitter")
                p0.emitter.setEmissionType(BaseParticleEmitter.ETRADIATE)
                p0.emitter.setRadius(2.0)
                p0.emitter.setAmplitude(0.2)
                p0.emitter.setAmplitudeSpread(0.1)
                p0.emitter.setOffsetForce(Vec3(0.0, 0.0, 0.5))
                p0.emitter.setRadiateOrigin(Point3(0.0, 0.0, 0.0))

                p0.setPoolSize(40)
                p0.setBirthRate(0.20)
                p0.setLitterSize(2)
                p0.setLitterSpread(1)
                p0.setLocalVelocityFlag(1)

                self.insured_effect.addParticles(p0)

            if self.actor:
                self.insured_effect.start(self.actor)
                self.insured_effect.setPos(0, 0, 1.0)
                self.insured_effect.setDepthWrite(False)
        else:
            if hasattr(self, 'insured_effect') and self.insured_effect:
                self.insured_effect.cleanup()
                self.insured_effect = None

    def setup_chainsaw_skelecog_head(self, head):
        head.setScale(self.cog_data["headSize"])
        print(self.cog_data["headSize"])
        if self.store_cs_toggle_1:
            cc_head_tex = loader.loadTexture(
                os.path.join(globals.RESOURCES_DIR, "phase_12", "maps", "ttcc_ene_chainsaw_b.png"))
        else:
            cc_head_tex = loader.loadTexture(
                os.path.join(globals.RESOURCES_DIR, "phase_12", "maps", "ttcc_ene_chainsaw.png"))
        head.setTexture(cc_head_tex, 1)
        cc_part_list = ["Hat", "bulbRight", "bulbLeft", "bulbLeft-filament", "bulbRight-filament"]
        for part in cc_part_list:
            find_part = head.find(f'**/{part}')
            if not find_part.isEmpty():
                find_part.hide()

    def toggle_skelecog(self, active, stored_suit_path=None):
        if active:
            self.store_is_skelecog = True

            if hasattr(self, 'skelecog') and self.skelecog:
                self.skelecog.cleanup()
                self.skelecog.removeNode()
                self.skelecog = None
            if hasattr(self, 'skelecog_skull') and self.skelecog_skull:
                if hasattr(self.skelecog_skull, 'cleanup'): self.skelecog_skull.cleanup()
                self.skelecog_skull.removeNode()
                self.skelecog_skull = None

            self.switch_toggle(self.control_panel.is_skelecog_var, self.control_panel.is_costume_var,
                               self.toggle_costume)
            self.switch_toggle(self.control_panel.is_skelecog_var, self.control_panel.is_zapped_var, self.toggle_zapped)
            self.toggle_zapped(False)

            if self.suit_type in ["bossCog", "boss"]: return

            self.active_main_ties = []
            if self.actor:
                for tie_name in ['necktie-s', 'necktie-w', 'bowtie']:
                    main_tie = self.actor.find(f'**/{tie_name}')
                    if not main_tie.isEmpty() and not main_tie.isHidden():
                        self.active_main_ties.append(tie_name)

            if self.actor:
                for part in ['body', 'hands', 'necktie-s', 'necktie-w', 'bowtie', 'highroller_body']:
                    self.actor.findAllMatches(f'**/{part}').hide()

                chest = self.actor.find("**/joint_attachMeter")
                if not chest.isEmpty(): chest.hide()

            if hasattr(self, 'head') and self.head:
                self.head.hide()

            suit = self.suit_type
            skel_suit = "as"
            skel_head_model = globals.SUIT_A_SKELECOG_HEAD
            skel_head_name = "suitA_skeleton_skull"

            if suit in ["b", "bf", "bc", "ps", "rm", "bs"]:
                skel_suit = "bs"
                skel_head_model = globals.SUIT_B_SKELECOG_HEAD
                skel_head_name = "suitB_skeleton_skull"
            elif suit in ["c", "cf", "cs"]:
                skel_suit = "cs"
                skel_head_model = globals.SUIT_C_SKELECOG_HEAD
                skel_head_name = "suitC_skeleton_skull"

            selected_mod = None
            if hasattr(self, 'control_panel') and self.control_panel.selected_suit_mod_var.get():
                selected_mod = self.control_panel.selected_suit_mod_var.get()
            if selected_mod:
                skel_suit = selected_mod

            cog_id = self.cog_data.get("cog", "").lower().replace(" ", "")
            manager_list = cog_id in [
                "factoryforeman", "mintsupervisor", "headattorney", "clubpresident",
                "derrickman", "laa", "prr", "derrickhand", "dold", "dopa", "duckshuffler",
                "deepdiver", "gatekeeper", "bellringer", "mouthpiece", "firestarter",
                "treekiller", "featherbedder", "prethinker", "rainmaker", "witchhunter",
                "multislacker", "majorplayer", "plutocrat", "chainsawconsultant", "pacesetter",
                "litigator", "stenographer", "scapegoat", "casemanager", "counterclaim",
                "counterfit", "highroller", "reddheirwing"
            ]

            if cog_id == "derrickhand":
                skel_head_model = "phase_12/models/char/suits/ttcc_ene_derrickhand_skele-zero.bam"
                skel_head_name = "ttcc_ene_derrickhand_skele"
            elif cog_id == "clubpresident":
                skel_head_model = "phase_12/models/char/suits/ttcc_ene_autocaddie-zero.bam"
            elif cog_id == "chainsawconsultant":
                skel_head_model = "phase_12/models/char/suits/ttcc_ene_chainsaw-zero.bam"
                skel_head_name = "ttcc_ene_chainsaw"

            if stored_suit_path is not None:
                skel_suit = stored_suit_path

            body_path = globals.SUIT_MODEL_DICT.get(skel_suit)

            if skel_suit in globals.SUIT_A_MODEL_KEYS:
                anims = globals.SUIT_A_ANIMATION_DICT
            elif skel_suit in globals.SUIT_B_MODEL_KEYS:
                anims = globals.SUIT_B_ANIMATION_DICT
            elif skel_suit in globals.SUIT_C_MODEL_KEYS:
                anims = globals.SUIT_C_ANIMATION_DICT
            else:
                anims = {}

            self.skelecog = Actor(body_path, anims)
            self.skelecog.reparentTo(self.actor)
            self.skelecog.setBlend(frameBlend=True)

            dept = self.cog_data.get("dept", "s")
            is_exec = hasattr(self, 'control_panel') and self.control_panel.is_executive_var.get()
            is_fired = hasattr(self, 'control_panel') and self.control_panel.is_fired_var.get()

            if hasattr(self, 'store_skelecog_texture') and self.store_skelecog_texture:
                tex_path = self.store_skelecog_texture
            else:
                skel_tex_key = dept + "s"
                skel_tex_list = globals.SUIT_TEXTURE_PATH.get(skel_tex_key)
                if skel_tex_list:
                    if is_fired:
                        tex_path = skel_tex_list[-1]
                    elif (is_exec or manager_list) and len(skel_tex_list) > 1:
                        tex_path = skel_tex_list[1]
                    else:
                        orig_suit = self.cog_data.get("suit", "")
                        if orig_suit in ["as", "bs", "cs"] and "suitTex" in self.cog_data:
                            tex_path = self.cog_data["suitTex"]
                        else:
                            tex_path = skel_tex_list[0]
                else:
                    tex_path = globals.DEPT_SKELE_SUIT_TEX_MAP.get(dept, globals.SELLBOT_SKELE_SUIT)

            tex = loader.loadTexture(tex_path)
            actual_tex = tex
            if selected_mod and selected_mod not in ["as", "bs", "cs"]:
                if getattr(self, 'store_suit_texture', None):
                    actual_tex = loader.loadTexture(self.store_suit_texture)

            for part in ['body', 'necktie-s', 'necktie-w', 'bowtie']:
                self.skelecog.findAllMatches(f'**/{part}').setTexture(actual_tex, 1)

            if hasattr(self, 'apply_skelecog_hand_color'):
                self.apply_skelecog_hand_color(self.skelecog)

            if getattr(self, 'store_skelecog_skull', None) is not None:
                skel_head_model = self.store_skelecog_skull
            if getattr(self, 'store_skel_head_name', None) is not None:
                skel_head_name = self.store_skel_head_name

            if getattr(self, 'store_skelecog_skull', None) is None:
                self.store_skelecog_skull = skel_head_model
                self.store_skel_head_name = skel_head_name

            skel_head_anim_dict, skel_head_anims = globals.HEAD_ANIMATION_PATH(skel_head_name)

            if skel_head_anims:
                self.skelecog_skull = Actor(skel_head_model, skel_head_anim_dict)
            else:
                self.skelecog_skull = loader.loadModel(skel_head_model)

            self.skelecog_skull.reparentTo(self.skelecog.find('**/joint_head'))

            if cog_id not in ["derrickhand", "clubpresident", "chainsawconsultant"]:
                self.skelecog_skull.setTexture(tex, 1)

            for axis, value in self.store_head_hpr.items(): self.set_POSHPR(self.skelecog_skull, axis, value)
            for axis, value in self.store_flatten_head.items(): self.set_depth(self.skelecog_skull, axis, value)

            self.store_original_head_anims_skel = self.available_head_animations
            self.available_head_animations = skel_head_anims

            if cog_id == "chainsawconsultant": self.setup_chainsaw_skelecog_head(self.skelecog_skull)

            if hasattr(self, 'control_panel'):
                self.control_panel.update_animation_lists(self.available_animations, self.available_head_animations)
                self.control_panel.update_anim_slider_range("head", 0)

            if self.current_head_animation in skel_head_anims and isinstance(self.skelecog_skull, Actor):
                self.skelecog_skull.loop(self.current_head_animation)
            else:
                self.current_head_animation = "zero"
                if isinstance(self.skelecog_skull, Actor) and "zero" in skel_head_anims:
                    self.skelecog_skull.loop("zero")

            zap_chest = self.skelecog.find("**/joint_attachMeter")
            if not zap_chest.isEmpty():
                if skel_suit in ["as", "bs", "cs"]:
                    zap_chest.hide()
                else:
                    zap_chest.show()
                    self.skel_iconbase = loader.loadModel(globals.COG_ICONS_BASE)
                    self.skel_iconbase.reparentTo(zap_chest)
                    self.skel_iconbase.setPosHprScale(*globals.COG_ICON_HPR)
                    zap_chest.setH(0)

                    for emb in ['emblem_hp', 'glow', 'emblem_sales', 'emblem_money', 'emblem_legal', 'emblem_corp',
                                'emblem_board']:
                        self.skel_iconbase.findAllMatches(f'**/{emb}').hide()

                    if getattr(self, 'store_emblem', None) and self.store_emblem not in ["light", "none"]:
                        self.skel_iconbase.findAllMatches(f'**/{self.store_emblem}').show()
                    elif getattr(self, 'store_emblem', None) == "light":
                        hp = self.skel_iconbase.findAllMatches('**/emblem_hp')
                        glow = self.skel_iconbase.findAllMatches('**/glow')
                        hp.show();
                        hp.setColor(self.skele_meter_color)
                        glow.show();
                        glow.setColor(self.skele_meter_color)

                    if skel_suit in ["a", "af", "cch", "mph", "hr"]:
                        self.skel_iconbase.setY(-0.10)
                    elif skel_suit in ["c"]:
                        self.skel_iconbase.setY(0.10)
                    elif skel_suit in ["cf"]:
                        self.skel_iconbase.setY(0.02);
                        self.skel_iconbase.setZ(0.23);
                        self.skel_iconbase.setP(2.5)
                    elif skel_suit in ["erfit"]:
                        self.skel_iconbase.setPosHprScale(0.00, 0.04, 0.00, 180.00, 349.70, 0.00, 1.00, 1.00, 1.00)

            for tie in ['necktie-s', 'necktie-w', 'bowtie']:
                self.skelecog.findAllMatches(f'**/{tie}').hide()

            for tie_name in self.active_main_ties:
                self.skelecog.findAllMatches(f'**/{tie_name}').show()

            self.sync_overlay_animation(self.skelecog)

        else:
            self.store_is_skelecog = False
            if hasattr(self, 'skelecog') and self.skelecog:
                self.skelecog.cleanup()
                self.skelecog.removeNode()
                self.skelecog = None
            if hasattr(self, 'skelecog_skull') and self.skelecog_skull:
                if hasattr(self.skelecog_skull, 'cleanup'): self.skelecog_skull.cleanup()
                self.skelecog_skull.removeNode()
                self.skelecog_skull = None

            if self.actor and getattr(self, 'is_body', True):
                for part in ['body', 'hands', 'necktie-s', 'necktie-w', 'bowtie', 'highroller_body']:
                    self.actor.findAllMatches(f'**/{part}').show()

                tie_to_set = "(Default)"
                if hasattr(self, 'control_panel'): tie_to_set = self.control_panel.selected_tie_var.get()
                self.set_necktie(tie_to_set)

                chest = self.actor.find("**/joint_attachMeter")
                if not chest.isEmpty(): chest.show()

            if hasattr(self, 'head') and self.head: self.head.show()

            if hasattr(self, 'store_original_head_anims_skel'):
                self.available_head_animations = self.store_original_head_anims_skel
                if hasattr(self, 'control_panel'):
                    self.control_panel.update_animation_lists(self.available_animations, self.available_head_animations)
                    self.control_panel.update_anim_slider_range("head", 0)

                if hasattr(self.head, 'getAnimNames') and self.current_head_animation in self.head.getAnimNames():
                    self.head.loop(self.current_head_animation)
                else:
                    self.current_head_animation = "zero"

    def load_environment(self, model_path):
        if not hasattr(self, 'env_models'):
            self.env_models = {}

        if 'Environment' in self.env_models:
            self.env_models['Environment'].removeNode()

        try:
            env = loader.loadModel(model_path)
            env.reparentTo(render)

            self.env_models['Environment'] = env

            if hasattr(self, 'control_panel'):
                self.control_panel.update_env_model_list()

            print(f"Successfully loaded environment: {model_path}")
        except Exception as e:
            print(f"Failed to load environment: {e}")

    def load_skybox(self, skybox_path):
        if not hasattr(self, 'env_models'):
            self.env_models = {}

        if 'Skybox' in self.env_models:
            self.env_models['Skybox'].removeNode()

        try:
            sky = loader.loadModel(skybox_path)
            sky.reparentTo(render)

            self.env_models['Skybox'] = sky

            if hasattr(self, 'control_panel'):
                self.control_panel.update_env_model_list()

            print(f"Successfully loaded skybox: {skybox_path}")
        except Exception as e:
            print(f"Failed to load skybox: {e}")

    def load_env_prop(self, prop_path):
        if not hasattr(self, 'env_models'):
            self.env_models = {}

        try:
            prop = loader.loadModel(prop_path)
            prop.reparentTo(render)

            base_name = os.path.basename(prop_path)
            unique_name = base_name
            count = 1
            while unique_name in self.env_models:
                unique_name = f"{base_name} ({count})"
                count += 1

            self.env_models[unique_name] = prop

            if hasattr(self, 'control_panel'):
                self.control_panel.update_env_model_list()

            print(f"Successfully loaded env prop: {prop_path}")
        except Exception as e:
            print(f"Failed to load env prop: {e}")

    def get_model_subnodes(self, model_key):
        if not hasattr(self, 'env_models') or model_key not in self.env_models:
            return []

        model = self.env_models[model_key]
        nodes = model.findAllMatches('**/?*')

        node_names = list(set([np.getName() for np in nodes if np.getName()]))
        return sorted(node_names)

    def delete_env_item(self, model_key, node_name=None):
        if not hasattr(self, 'env_models') or model_key not in self.env_models:
            return

        model = self.env_models[model_key]

        if node_name:
            target = model.find(f'**/{node_name}')
            if not target.isEmpty():
                target.removeNode()
        else:
            model.removeNode()
            del self.env_models[model_key]

    def update_env_transform(self, model_key, node_name, axis, value):
        if not hasattr(self, 'env_models') or model_key not in self.env_models:
            return

        target = self.env_models[model_key]

        if node_name:
            sub_target = target.find(f'**/{node_name}')
            if not sub_target.isEmpty():
                target = sub_target
            else:
                return

        self.set_POSHPR(target, axis, value)

    def get_env_transform(self, model_key, node_name=None):
        if not hasattr(self, 'env_models') or model_key not in self.env_models:
            return None

        target = self.env_models[model_key]

        if node_name:
            sub_target = target.find(f'**/{node_name}')
            if not sub_target.isEmpty():
                target = sub_target
            else:
                return None

        return {
            "x": round(target.getX(), 3),
            "y": round(target.getY(), 3),
            "z": round(target.getZ(), 3),
            "h": round(target.getH(), 3),
            "p": round(target.getP(), 3),
            "r": round(target.getR(), 3),
            "scale": round(target.getSx(), 3)
        }

    def apply_env_color(self, model_key, node_name, hex_code):
        if not hasattr(self, 'env_models') or model_key not in self.env_models:
            return

        color = self.hex_to_p3d_color(hex_code)
        if not color: return

        target = self.env_models[model_key]

        if node_name:
            sub_target = target.find(f'**/{node_name}')
            if not sub_target.isEmpty():
                target = sub_target
            else:
                return

        target.setColorScale(color)

    def reset_env_color(self, model_key, node_name=None):
        if not hasattr(self, 'env_models') or model_key not in self.env_models:
            return

        target = self.env_models[model_key]

        if node_name:
            sub_target = target.find(f'**/{node_name}')
            if not sub_target.isEmpty():
                target = sub_target
            else:
                return

        target.clearColorScale()

    def sync_overlay_animation(self, overlay_actor):
        if not overlay_actor or not self.actor: return

        anim = getattr(self, 'current_animation', "zero")
        if anim != "zero":
            curr_frame = self.actor.getCurrentFrame(anim)
            if curr_frame is None: curr_frame = 0

            is_playing = getattr(self, 'store_body_playing', True)

            if not is_playing:
                overlay_actor.pose(anim, curr_frame)
            else:
                if hasattr(self, 'control_panel') and self.control_panel.loop_body_var.get():
                    overlay_actor.pose(anim, curr_frame)
                    overlay_actor.loop(anim, restart=0)
                else:
                    overlay_actor.play(anim, fromFrame=curr_frame)

    def auto_trim_screenshot(self, filepath):  # auto trims the cog render screenshot
        try:
            from PIL import Image
            from panda3d.core import Filename

            if isinstance(filepath, Filename):
                os_filepath = filepath.toOsSpecific()
            else:
                os_filepath = Filename.fromOsSpecific(filepath).toOsSpecific()

            img = Image.open(os_filepath)

            if img.mode == 'RGBA':
                bbox = img.getchannel('A').getbbox()
            else:
                bbox = img.getbbox()

            if bbox:
                pad = 0
                padded_bbox = (
                    max(0, bbox[0] - pad),
                    max(0, bbox[1] - pad),
                    min(img.width, bbox[2] + pad),
                    min(img.height, bbox[3] + pad)
                )
                cropped_img = img.crop(padded_bbox)
                cropped_img.save(os_filepath)
            else:
                print("Image is completely empty; nothing to trim.")

        except Exception as e:
            print(f"Failed to auto-trim screenshot: {e}")

    def compile_gif_and_cleanup(self, temp_folder, output_filename,
                                fps=24):  # automatically compiles all of the rendered frames and turns it into a gif
        try:
            if not os.path.exists(temp_folder):
                print("Temp folder missing! Cannot build GIF.")
                return

            frame_files = [os.path.join(temp_folder, f) for f in os.listdir(temp_folder) if f.endswith('.png')]
            frame_files.sort()

            if not frame_files:
                print("No screenshot frames found!")
                return

            images = []
            min_x, min_y, max_x, max_y = 99999, 99999, 0, 0

            for f in frame_files:
                img = Image.open(f)
                if img.mode == 'RGBA':
                    bbox = img.getchannel('A').getbbox()
                else:
                    bbox = img.getbbox()

                if bbox:
                    min_x = min(min_x, bbox[0])
                    min_y = min(min_y, bbox[1])
                    max_x = max(max_x, bbox[2])
                    max_y = max(max_y, bbox[3])
                images.append(img)

            if min_x != 99999:
                pad = 10
                global_bbox = (
                    max(0, min_x - pad),
                    max(0, min_y - pad),
                    min(images[0].width, max_x + pad),
                    min(images[0].height, max_y + pad)
                )
                cropped_images = [img.crop(global_bbox) for img in images]
            else:
                cropped_images = images

            duration = int(1000 / fps)
            cropped_images[0].save(
                output_filename,
                save_all=True,
                append_images=cropped_images[1:],
                duration=duration,
                loop=0,
                disposal=2
            )
            print(f"Successfully generated GIF: {output_filename}")

            for img in images:
                img.close()
            shutil.rmtree(temp_folder)

        except Exception as e:
            print(f"Failed to generate GIF: {e}")

    def update_slots(self, spin_offset=0.0):
        offsets = {
            "7": 0.0,
            "Duck": 0.25,
            "Bar": 0.5,
            "Cherry": 0.75
        }

        if hasattr(self, 'head') and self.head:
            l_val = self.control_panel.unique_vars["ds_slot_l"].get()
            m_val = self.control_panel.unique_vars["ds_slot_m"].get()
            r_val = self.control_panel.unique_vars["ds_slot_r"].get()

            self.store_ds_slot_l = l_val
            self.store_ds_slot_m = m_val
            self.store_ds_slot_r = r_val

            ts = TextureStage.getDefault()

            for part, val in [('slotL', l_val), ('slotMid', m_val), ('slotR', r_val)]:
                np = self.head.find(f'**/{part}')
                if not np.isEmpty():
                    base_offset = offsets.get(val, 0.0)
                    np.setTexOffset(ts, 0, base_offset + spin_offset)

    def toggle_spin_slots(self):
        is_spinning = self.control_panel.unique_vars["ds_spin"].get()
        self.store_ds_spin = is_spinning

        self.taskMgr.remove("SpinSlotsTask")

        if is_spinning:
            self.slot_v_offset = getattr(self, 'slot_v_offset', 0.0)
            self.taskMgr.add(self.spin_slots_task, "SpinSlotsTask")
        else:
            self.update_slots()

    def spin_slots_task(self, task):
        if not hasattr(self, 'head') or not self.head:
            return task.done

        self.slot_v_offset += 0.05
        if self.slot_v_offset > 1.0:
            self.slot_v_offset -= 1.0

        self.update_slots(spin_offset=self.slot_v_offset)

        return task.cont

    def toggle_chilled(self, active):
        self.is_chilled = active

        self._update_ice_tint()
        self.update_snow_state()

    def toggle_frozen(self, active):
        self.is_frozen = active

        self._update_ice_tint()

        if active:
            if getattr(self, 'icecube_model', None):
                self.active_icecube = self.icecube_model.copyTo(self.render)
                self.taskMgr.add(self.update_icecube_task, "UpdateIcecubeTask")
        else:
            if getattr(self, 'active_icecube', None):
                self.active_icecube.removeNode()
                self.active_icecube = None

            self.taskMgr.remove("UpdateIcecubeTask")

        self.update_snow_state()

    def update_icecube_task(self, task):
        if not getattr(self, 'active_icecube', None) or not self.actor:
            return task.done

        bounds = self.actor.getTightBounds(self.render)
        if bounds:
            min_b, max_b = bounds
            size = max_b - min_b

            center_x = (max_b.getX() + min_b.getX()) / 2.0
            center_y = (max_b.getY() + min_b.getY()) / 2.0
            bottom_z = min_b.getZ() - 0.15

            self.active_icecube.setPos(center_x, center_y, bottom_z)

            scale_x = size.getX() * 0.15
            scale_y = size.getY() * 0.14
            scale_z = size.getZ() * 0.15

            self.active_icecube.setScale(scale_x, scale_y, scale_z)
            self.active_icecube.setH(180)

        return task.cont

    def update_snow_state(self):
        wants_snow = self.is_frozen or self.is_chilled
        if wants_snow and not self.snow_active:
            self.taskMgr.add(self.spawn_snow_task, "SpawnSnowTask")
            self.taskMgr.add(self.update_snow_task, "UpdateSnowTask")
            self.snow_active = True
        elif not wants_snow and getattr(self, 'snow_active', False):
            self.taskMgr.remove("SpawnSnowTask")
            self.taskMgr.remove("UpdateSnowTask")
            for snow_data in self.active_snows:
                snow_data["node"].removeNode()
            self.active_snows.clear()
            self.snow_active = False

    def spawn_snow_task(self, task):
        if not self.actor or not getattr(self, 'snow_particle_base', None):
            return task.cont

        snow_np = self.snow_particle_base.copyTo(self.render)
        bounds = self.actor.getTightBounds(self.render)

        if bounds:
            min_b, max_b = bounds
            target_x = random.uniform(min_b.getX(), max_b.getX())
            target_y = random.uniform(min_b.getY(), max_b.getY())
            target_z = random.uniform(min_b.getZ(), max_b.getZ())
        else:
            base_pos = self.actor.getPos(self.render)
            target_x = base_pos.getX() + random.uniform(-0.5, 0.5)
            target_y = base_pos.getY() + random.uniform(-0.5, 0.5)
            target_z = base_pos.getZ() + random.uniform(0.0, 4.0)

        snow_np.setPos(target_x, target_y, target_z)
        snow_np.setBillboardPointEye()
        snow_np.setScale(random.uniform(0.04, 0.08))
        snow_np.setTransparency(1)

        vel_x = random.uniform(-0.2, 0.2)
        vel_y = random.uniform(-0.2, 0.2)
        vel_z = random.uniform(-0.2, 0.2)

        self.active_snows.append({
            "node": snow_np,
            "life": 1.0,
            "vel_x": vel_x,
            "vel_y": vel_y,
            "vel_z": vel_z
        })

        task.delayTime = random.uniform(0.05, 0.15)
        return task.again

    def update_snow_task(self, task):
        dt = globalClock.getDt()
        alive_snows = []

        for snow_data in self.active_snows:
            node = snow_data["node"]

            snow_data["life"] -= dt * 0.4

            if snow_data["life"] <= 0:
                node.removeNode()
            else:
                new_x = node.getX() + (snow_data["vel_x"] * dt)
                new_y = node.getY() + (snow_data["vel_y"] * dt)
                new_z = node.getZ() + (snow_data["vel_z"] * dt)

                node.setPos(new_x, new_y, new_z)
                node.setAlphaScale(snow_data["life"])
                alive_snows.append(snow_data)

        self.active_snows = alive_snows
        return task.cont

    def _update_ice_tint(self):
        color = (145 / 255.0, 184 / 255.0, 197 / 255.0, 1.0)

        is_toggled_skel = hasattr(self, 'control_panel') and getattr(self.control_panel, 'is_skelecog_var',
                                                                     None) and self.control_panel.is_skelecog_var.get()
        is_already_skelecog = getattr(self, 'suit_type', '') in ["as", "bs", "cs"]

        if self.actor:
            self.actor.clearColorScale()
            for light in self.actor.findAllMatches('**/joint_attachMeter'):
                light.clearColorScale()

        if getattr(self, 'cog_data', {}).get("cog_type") == "boss" and hasattr(self, "boss_parts"):
            for part_name, part_actor in self.boss_parts.items():
                if part_actor and not part_actor.isEmpty():
                    part_actor.clearColorScale()
                    for light in part_actor.findAllMatches('**/joint_attachMeter'):
                        light.clearColorScale()
        else:
            if is_toggled_skel and getattr(self, 'skelecog', None) is not None:
                self.skelecog.clearColorScale()
                target_head = getattr(self, 'skelecog_skull', None)
                if target_head is not None and not target_head.isEmpty():
                    target_head.clearColorScale()
            elif is_already_skelecog and getattr(self, 'actor', None) is not None:
                if hasattr(self, 'head') and self.head and not self.head.isEmpty():
                    self.head.clearColorScale()
            elif getattr(self, 'actor', None) is not None:
                for part in ['body', 'necktie-s', 'necktie-w', 'bowtie', 'highroller_body']:
                    np = self.actor.find(f'**/{part}')
                    if not np.isEmpty():
                        np.clearColorScale()

        if self.is_frozen:
            if self.actor:
                self.actor.setColorScale(*color)
                if is_already_skelecog and hasattr(self, 'head') and self.head and not self.head.isEmpty():
                    self.head.setColorScale(*color)

        elif self.is_chilled:
            if getattr(self, 'cog_data', {}).get("cog_type") == "boss" and hasattr(self, "boss_parts"):
                for part_name, part_actor in self.boss_parts.items():
                    if part_actor and not part_actor.isEmpty():
                        part_actor.setColorScale(*color)
                        for light in part_actor.findAllMatches('**/joint_attachMeter'):
                            light.setColorScale(1, 1, 1, 1, 1)
            else:
                if is_toggled_skel and getattr(self, 'skelecog', None) is not None:
                    self.skelecog.setColorScale(*color)
                    for light in self.skelecog.findAllMatches('**/joint_attachMeter'):
                        light.setColorScale(1, 1, 1, 1, 1)

                elif is_already_skelecog and getattr(self, 'actor', None) is not None:
                    self.actor.setColorScale(*color)
                    for light in self.actor.findAllMatches('**/joint_attachMeter'):
                        light.setColorScale(1, 1, 1, 1, 1)

                elif getattr(self, 'actor', None) is not None:
                    for part in ['body', 'necktie-s', 'necktie-w', 'bowtie', 'highroller_body']:
                        np = self.actor.find(f'**/{part}')
                        if not np.isEmpty():
                            np.setColorScale(*color)

                    if getattr(self, 'store_head_color', False):
                        self.apply_head_color(self.store_head_hex_color)

        else:
            if getattr(self, 'store_body_color', False):
                self.apply_body_colorscale(self.store_body_hex_color)
            if getattr(self, 'store_head_color', False):
                self.apply_head_color(self.store_head_hex_color)

    def generate_random_cog_screenshot(self):
        stash_node = self.render.attachNewNode("stash")
        stash_node.hide()

        actor_parent = None
        if getattr(self, 'actor', None) and not self.actor.isEmpty():
            actor_parent = self.actor.getParent()
            self.actor.reparentTo(stash_node)

        boss_parents = {}
        if hasattr(self, 'boss_parts'):
            for name, part in self.boss_parts.items():
                if part and not part.isEmpty() and part.getParent() == self.render:
                    boss_parents[name] = part.getParent()
                    part.reparentTo(stash_node)

        cogs = [c for c in self.cog_list if
                globals.COG_DATA[c].get("cog_type") != "boss" and "legacy" not in globals.COG_DATA[c].get("suit", "")]
        random_cog = random.choice(cogs)
        cog_data = globals.COG_DATA[random_cog]
        original_suit_type = cog_data["suit"]
        dept = cog_data.get("dept", "s")
        cog_id = cog_data.get("cog", "").lower().replace(" ", "")

        suitToggle = cog_data.get("suitToggle", "y")
        can_exec = suitToggle in ["y", "s", "u"]
        can_skel = original_suit_type not in ["as", "bs", "cs", "boss", "bossCog"]

        skel_chance = 0.05  # too much skelecogs before had to done it down
        exec_chance = 0.05

        is_skel = (random.random() < skel_chance) if can_skel else False
        is_exec = (random.random() < exec_chance) if can_exec else False

        if is_skel:
            if original_suit_type in ["a", "af", "hr", "mph", "cch", "erfit"]:
                suit_type = "as"
            elif original_suit_type in ["b", "bf", "bc", "ps", "rm"]:
                suit_type = "bs"
            elif original_suit_type in ["c", "cf"]:
                suit_type = "cs"
            else:
                suit_type = original_suit_type
        else:
            suit_type = original_suit_type

        temp_root = self.render.attachNewNode("temp_random_cog")

        body_path = globals.SUIT_MODEL_DICT.get(suit_type)
        if suit_type in ["a", "af", "hr", "as", "mph", "cch", "erfit"]:
            anims = globals.SUIT_A_ANIMATION_DICT
        elif suit_type in ["b", "bf", "bc", "ps", "rm", "bs"]:
            anims = globals.SUIT_B_ANIMATION_DICT
        elif suit_type in ["c", "cf", "cs"]:
            anims = globals.SUIT_C_ANIMATION_DICT
        else:
            anims = {}

        temp_actor = Actor(body_path, anims)
        temp_actor.reparentTo(temp_root)

        if getattr(self, 'actor', None) and not self.actor.isEmpty():
            temp_actor.setPos(self.actor.getPos())
            temp_actor.setHpr(self.actor.getHpr())
        else:
            temp_actor.setH(180)

        temp_actor.setScale(cog_data.get("scale", 1.0))
        temp_actor.setBlend(frameBlend=True)
        temp_actor.setTwoSided(True)

        tex_path = cog_data.get("suitTex")

        if is_exec:
            if "exeTex" in cog_data:
                tex_path = cog_data["exeTex"]
            elif tex_path:
                base, ext = os.path.splitext(tex_path)
                exe_tex_path = f"{base}_e{ext}"
                if os.path.exists(exe_tex_path):
                    tex_path = exe_tex_path
                else:
                    is_exec = False

        if is_skel:
            skel_tex_list = globals.SUIT_TEXTURE_PATH.get(dept + "s")
            if skel_tex_list:
                tex_index = 1 if is_exec and len(skel_tex_list) > 1 else 0
                tex_path = skel_tex_list[tex_index]
            else:
                tex_path = globals.DEPT_SKELE_SUIT_TEX_MAP.get(dept, globals.SELLBOT_SKELE_SUIT)

        tx_suit = loader.loadTexture(tex_path)
        temp_actor.find('**/body').setTexture(tx_suit, 1)

        if original_suit_type not in ["erfit"]:
            for tie in ['**/necktie-s', '**/necktie-w', '**/bowtie']:
                tie_np = temp_actor.find(tie)
                if not tie_np.isEmpty():
                    tie_np.setTexture(tx_suit, 1)
                    tie_np.hide()

        if cog_data.get("cog") not in globals.NO_NECKTIE_COGS:
            tie_name = globals.NECKTIE_MAP.get(cog_data.get("cog")) or globals.NECKTIE_MAP.get(dept)
            if tie_name:
                tie_np = temp_actor.find(tie_name)
                if not tie_np.isEmpty(): tie_np.show()

        if original_suit_type not in ["as", "bs", "cs", "bossCog"] and "hands" in cog_data:
            hands = temp_actor.find('**/hands')
            if not hands.isEmpty():
                hands.setColor(cog_data["hands"])

        if original_suit_type == "bc":
            hands = temp_actor.find('**/hands')
            if not hands.isEmpty():
                hands.setTexture(tx_suit, 1)

        chest_null = temp_actor.find("**/joint_attachMeter")

        if suit_type in ["as", "bs", "cs"]:
            if not chest_null.isEmpty(): chest_null.hide()
            health_meter = temp_actor.find("**/emblem_healthmeter")
            if not health_meter.isEmpty(): health_meter.show()
            meter_glow = temp_actor.find('**/glow')
            if not meter_glow.isEmpty(): meter_glow.show()

        elif not chest_null.isEmpty() and "emblem" in cog_data:
            iconbase = loader.loadModel(globals.COG_ICONS_BASE)
            iconbase.reparentTo(chest_null)
            chest_null.setH(0)
            iconbase.setPosHprScale(*globals.COG_ICON_HPR)

            for emb in ['emblem_hp', 'glow', 'emblem_sales', 'emblem_money', 'emblem_legal', 'emblem_corp',
                        'emblem_board']:
                target = iconbase.find(f'**/{emb}')
                if not target.isEmpty(): target.hide()

            target_emblem = iconbase.find(f'**/{cog_data["emblem"]}')
            if not target_emblem.isEmpty(): target_emblem.show()

            if original_suit_type in ["a", "af", "cch", "mph", "hr"]:
                iconbase.setY(-0.10)
            elif original_suit_type in ["c"]:
                iconbase.setY(0.10)
            elif original_suit_type in ["cf"]:
                iconbase.setY(0.02);
                iconbase.setZ(0.23);
                iconbase.setP(2.5)
            elif original_suit_type in ["erfit"]:
                iconbase.setPosHprScale(0.00, 0.04, 0.00, 180.00, 349.70, 0.00, 1.00, 1.00, 1.00)
            else:
                iconbase.setY(0.00)

            if original_suit_type == "hr":
                iconbase.hide()

        head_anims = []
        if is_skel:
            skel_head_name = ""
            if suit_type == "as":
                skel_head_model = globals.SUIT_A_SKELECOG_HEAD; skel_head_name = "suitA_skeleton_skull"
            elif suit_type == "bs":
                skel_head_model = globals.SUIT_B_SKELECOG_HEAD; skel_head_name = "suitB_skeleton_skull"
            elif suit_type == "cs":
                skel_head_model = globals.SUIT_C_SKELECOG_HEAD; skel_head_name = "suitC_skeleton_skull"

            if cog_id == "derrickhand":
                skel_head_model = f"{globals.RESOURCES_DIR}/phase_12/models/char/suits/ttcc_ene_derrickhand_skele-zero.bam"
                skel_head_name = "ttcc_ene_derrickhand_skele"
            elif cog_id == "clubpresident":
                skel_head_model = f"{globals.RESOURCES_DIR}/phase_12/models/char/suits/ttcc_ene_clubpresident-zero.bam"
                skel_head_name = "ttcc_ene_clubpresident"
            elif cog_id == "chainsawconsultant":
                skel_head_model = f"{globals.RESOURCES_DIR}/phase_12/models/char/suits/ttcc_ene_chainsaw-zero.bam"
                skel_head_name = "ttcc_ene_chainsaw"

            try:
                head_anim_dict, head_anims = globals.HEAD_ANIMATION_PATH(skel_head_name)
            except:
                head_anim_dict, head_anims = {}, []

            if len(head_anims) > 1:
                temp_head = Actor(skel_head_model, head_anim_dict)
                temp_head.setBlend(frameBlend=True)
            else:
                temp_head = loader.loadModel(skel_head_model)

            if cog_id not in ["derrickhand", "clubpresident", "chainsawconsultant"]:
                temp_head.setTexture(tx_suit, 1)

            if cog_id == "chainsawconsultant":
                if is_exec:
                    cc_head_tex = loader.loadTexture(
                        os.path.join(globals.RESOURCES_DIR, "phase_12", "maps", "ttcc_ene_chainsaw_b.png"))
                else:
                    cc_head_tex = loader.loadTexture(
                        os.path.join(globals.RESOURCES_DIR, "phase_12", "maps", "ttcc_ene_chainsaw.png"))
                temp_head.setTexture(cc_head_tex, 1)
                for part in ["Hat", "bulbRight", "bulbLeft", "bulbLeft-filament", "bulbRight-filament"]:
                    np = temp_head.find(f'**/{part}')
                    if not np.isEmpty(): np.hide()

        else:
            head_anim_dict, head_anims = globals.HEAD_ANIMATION_PATH(cog_data["name"])
            if len(head_anims) > 1:
                temp_head = Actor(cog_data["head"], head_anim_dict)
                temp_head.setBlend(frameBlend=True)
            else:
                temp_head = loader.loadModel(cog_data["head"])

            if "headTex" in cog_data:
                head_tex_path = cog_data["headTex"]
                if is_exec:
                    base, ext = os.path.splitext(head_tex_path)
                    exe_head_path = f"{base}_e{ext}"
                    if os.path.exists(exe_head_path):
                        head_tex_path = exe_head_path

                head_texture = loader.loadTexture(head_tex_path)
                temp_head.setTexture(head_texture, 1)

            if "bodyColor" in cog_data:
                temp_actor.find('**/body').setColor(cog_data["bodyColor"])
                temp_head.setColor(cog_data["bodyColor"])

        if "headPos" in cog_data:
            temp_head.setZ(cog_data["headPos"])
            if "headPosY" in cog_data:
                temp_head.setY(cog_data["headPosY"])
            if "headPosP" in cog_data:
                temp_head.setP(cog_data["headPosP"])
            if "headPosH" in cog_data:
                temp_head.setH(cog_data["headPosH"])

        if "belt" in cog_data:
            belt = loader.loadModel(cog_data["belt"])
            belt.reparentTo(temp_head)

        if (not temp_head.find('**/brain').isEmpty()):
            temp_head.find('**/brain').setScale(0.95)

        head_joint = temp_actor.find('**/joint_head')
        if not head_joint.isEmpty(): temp_head.reparentTo(head_joint)
        if "headSize" in cog_data: temp_head.setScale(cog_data["headSize"])

        banned_keywords = ["lose", "skeleton-lose"]

        if anims:
            safe_anims = [a for a in anims.keys() if not any(ban in a.lower() for ban in banned_keywords)]

            if safe_anims:
                rand_anim = random.choice(safe_anims)
                num_frames = temp_actor.getNumFrames(rand_anim)

                if num_frames is not None and num_frames > 0:
                    rand_frame = random.randint(0, num_frames - 1)
                    temp_actor.pose(rand_anim, rand_frame)

        if len(head_anims) > 1:
            safe_head_anims = [a for a in head_anims if not any(ban in a.lower() for ban in banned_keywords)]

            if safe_head_anims:
                rand_head_anim = random.choice(safe_head_anims)
                num_h_frames = temp_head.getNumFrames(rand_head_anim)

                if num_h_frames is not None and num_h_frames > 0:
                    rand_h_frame = random.randint(0, num_h_frames - 1)
                    temp_head.pose(rand_head_anim, rand_h_frame)

        orig_cam_pos = self.camera.getPos()
        orig_cam_hpr = self.camera.getHpr()

        self.graphicsEngine.renderFrame()

        bounds = temp_root.getTightBounds()
        if bounds:
            min_b, max_b = bounds
            center = (min_b + max_b) / 2.0
            dimensions = max_b - min_b

            fov_h, fov_v = self.camLens.getFov()

            pad = 1.15

            if fov_h > 0 and fov_v > 0:
                dist_h = (dimensions.getX() / 2.0) / math.tan(math.radians(fov_h / 2.0)) * pad
                dist_v = (dimensions.getZ() / 2.0) / math.tan(math.radians(fov_v / 2.0)) * pad

                distance = max(dist_h, dist_v, 2.0)

                self.camera.setPos(center.getX(), center.getY() - distance, center.getZ())
                self.camera.setHpr(0, 0, 0)

        self.setBackgroundColor(0, 0, 0)
        self.graphicsEngine.renderFrame()
        self.graphicsEngine.renderFrame()

        path = globals.SCREENSHOT_DIR
        if not os.path.exists(path): os.makedirs(path)
        date_string = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")

        random_cog_name = cog_data.get("cog", "UnknownCog").replace(" ", "")
        screenshot_name = os.path.join(path, f"{random_cog_name}-{date_string}.png")

        self.base.screenshot(screenshot_name, False)
        self.auto_trim_screenshot(screenshot_name)

        if self.bool:
            self.setBackgroundColor(0, 0, 0)
        else:
            self.setBackgroundColor(self.background_color)

        self.camera.setPos(orig_cam_pos)
        self.camera.setHpr(orig_cam_hpr)

        if isinstance(temp_head, Actor): temp_head.cleanup()
        temp_actor.cleanup()
        temp_root.removeNode()

        if actor_parent and getattr(self, 'actor', None) and not self.actor.isEmpty():
            self.actor.reparentTo(actor_parent)

        for name, part in boss_parents.items():
            if getattr(self, 'boss_parts', {}).get(name) and not self.boss_parts[name].isEmpty():
                self.boss_parts[name].reparentTo(part)

        stash_node.removeNode()


if __name__ == "__main__":
    app = CogViewer()
    try:
        import pyi_splash

        pyi_splash.close()
    except ImportError:
        pass

    app.run()
