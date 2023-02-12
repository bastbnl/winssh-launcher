"""

(c) 2023 by Bas ten Berge. All rights reserved

This program is distributed in the hope that it will be useful, but is provided AS IS with ABSOLUTELY NO WARRANTY;
The entire risk as to the quality and performance of the program is with you. Should the program prove defective,
you assume the cost of all necessary servicing, repair or correction. In no event will any of the developers, or
any other party, be liable to anyone for damages arising out of the use or inability to use the program.
You may copy and distribute copies of the Program, provided that you keep intact all the notices that refer to the
absence of any warranty.

"""
from itertools import filterfalse
from darkdetect import isDark
from multiprocessing import Process
from subprocess import CalledProcessError, CREATE_NEW_CONSOLE, check_call
from tkinter import BOTH, END, SINGLE, X, Button, LabelFrame, Frame, Label, Listbox, Tk, Variable

from .config import NativeSSHLauncherConfiguration
from .const import GRID_PADX as _PADX, \
    GRID_PADY as _PADY, \
    GRID_STICKY_MODE as _STICKY_MODE, \
    GROUP_ALL as _GROUP_ALL, \
    GROUP_LABEL_FOR_ALL as _GROUP_LABEL_FOR_ALL, \
    SECTION_GLOBAL as _SECTION_GLOBAL
from .ssh import start_ssh_session
from .theme import OnThemeChangedMixin, theme_settings


class NativeSSHLauncher(
    OnThemeChangedMixin,
    Tk,
):
    """
    Loads the NativeSSH connections 

    """
    def __init__(self, *args, **kwargs):
        """
        Loads the configuration and validates 

        """
        self._winssh_config = NativeSSHLauncherConfiguration(**kwargs)
        self._winssh_theme_label = 'dark' if isDark() else 'light'
        super().__init__()

        self.config(**theme_settings[self._winssh_theme_label]['form'], )
        self.title(self._winssh_config.title)

        # Resizing the geometry and make sure the app cannot be resized
        self.geometry('800x400')
        self.minsize(800, 400)
        self.maxsize(800, 400)
        self._setup_grid()

        self._add_sessions_groups_frame()
        self._add_sessions_frame()
        self._add_keys_frame()

    def _setup_grid(self, **kwargs):
        """
        Initializes the grid for this page

        """
        # First grid will hold the group container, or a label when the groups are missing
        self.rowconfigure(0, weight=9, )
        self.rowconfigure(1, weight=1, )
        self.columnconfigure(0, weight=1, )
        self.columnconfigure(1, weight=2, )

    def _add_gridded_frame(self, **kwargs):
        """
        Creates a Frame, which uses `grid()` layout and applies config

        """
        to_return_class = Frame
        to_return_kwargs = {}
        label_text = kwargs.get('label', )
        
        if label_text:
            # Label may be very bad to read, so we just create a styled Label and pass that along
            label_widget=Label(
                text=label_text,
            )
            label_widget.configure(
                **theme_settings[self._winssh_theme_label]['label'],
            )
            to_return_kwargs['labelwidget'] = label_widget
            to_return_class = LabelFrame

        to_return = to_return_class(
            master=self,
            **to_return_kwargs,
            **kwargs.get('frame_kwargs', ) or {},
        )
        to_return.grid(
            sticky=_STICKY_MODE,
            **kwargs.get('grid_kwargs', ) or {},
        )
        to_return.configure(
            **theme_settings[self._winssh_theme_label]['controls'],
        )

        return to_return

    def _add_sessions_groups_frame(self, **kwargs):
        """
        Creates a frame containing either a Label, or a list containing the groups

        """
        ssh_sessions_groups_frame = self._add_gridded_frame(
            label='SHOW SESSIONS IN GROUP ...',
            grid_kwargs={
                'column': 0,
                'padx': _PADX,
                'pady': _PADY,
                'row': 0,
            },
        )

        session_group_labels = self._winssh_config.ssh_sessions_groups
        if len(session_group_labels) > 1:
            # We have the __all__ group, which displays any value and which is selected by default
            load_ssh_session_group_list = Listbox(
                ssh_sessions_groups_frame,
                listvariable=Variable(
                    value=[_GROUP_LABEL_FOR_ALL, ] + sorted(filterfalse(lambda x: _GROUP_ALL == x, session_group_labels))
                ),
                selectmode=SINGLE,
                **theme_settings[self._winssh_theme_label]['button'],
            )
            load_ssh_session_group_list.pack(
                padx=5,
                pady=5,
                expand=True,
                fill=BOTH,
            )
            load_ssh_session_group_list.selection_set(0, )
            load_ssh_session_group_list.bind('<<ListboxSelect>>', self._on_session_group_selected)
        else:
            # Must be one, which gets you a proper label
            ssh_session_group_suggestion_label = Label(
                ssh_sessions_groups_frame,
                text='First add `group` to an individual ssh connection',
                **theme_settings[self._winssh_theme_label]['label'],
            )
            ssh_session_group_suggestion_label.pack()

    def _add_sessions_frame(self, **kwargs):
        """
        Adds the session frame

        """
        ssh_sessions_frame = self._add_gridded_frame(
            label='SELECT SSH SESSION...',
            grid_kwargs={
                'column': 1,
                'padx': _PADX,
                'pady': _PADY,
                'row': 0,
            },
        )

        ssh_sessions = self._winssh_config.ssh_sessions
        if ssh_sessions:
            load_ssh_session_list = Listbox(
                ssh_sessions_frame,
                listvariable=Variable(
                    value=ssh_sessions,
                ),
                selectmode=SINGLE,
                **theme_settings[self._winssh_theme_label]['button'],
            )
            load_ssh_session_list.pack(
                expand=True,
                fill=BOTH,
                padx=_PADX,
                pady=_PADY,
            )
            load_ssh_session_list.bind('<<ListboxSelect>>', self._on_session_selected)
            self._winssh_session_list = load_ssh_session_list
        else:
            # We use a different label when SSH is missing
            if self._winssh_config.ssh_filename is None:
                # Indication of invalid configuration, or missing SSH executable
                label_text = f'Make sure the OpenSSH executables are available from {self._winssh_config.ssh_installdir}'
            else:            
                label_text = f"First add sections to your configuration for ssh connections"

            ssh_suggestions_label = Label(
                ssh_sessions_frame,
                text=label_text,
            )
            ssh_suggestions_label.configure(
                **theme_settings[self._winssh_theme_label]['label'],
            )
            ssh_suggestions_label.pack()

    def _add_keys_frame(self, **kwargs):
        """
        Adds the keys frame
        
        """
        ssh_key_frame = self._add_gridded_frame(
            grid_kwargs={
                'row': 1,
                'columnspan': 2,
            },
        )

        if self._winssh_config.has_usable_ssh_keys:
            # TODO: Find a way to see if the keys are already loaded 
            load_ssh_keys_button = Button(
                ssh_key_frame,
                text="LOAD PRIVATE KEYS",
                command=self._on_button_load_keys,
            )
            load_ssh_keys_button.configure(
                **theme_settings[self._winssh_theme_label]['button'],
            )
            load_ssh_keys_button.pack(
                expand=True,
                padx=_PADX,
                pady=_PADY,
                fill=X,
            )
        else:
            # This label text depends on the exact error: no keys or no service
            label_text = f'Quickly load your SSH keys by listing them using ssh.key.pem.filenames in the [{_SECTION_GLOBAL}] section'
            if self._winssh_config.has_ssh_keys:
                label_text = f'You listed your SSH keys. Now make sure the OpenSSH Authentication Agent service is activated'
            
            key_suggestion_label = Label(
                ssh_key_frame,
                text=label_text,
            )
            key_suggestion_label.configure(
                **theme_settings[self._winssh_theme_label]['label'],
            )
            key_suggestion_label.pack()

    def __call__(self, *args, **kwargs):
        """
        Starts the frontend and handles it

        """
        self.mainloop()

    def _on_button_load_keys(self, *args, **kwargs):
        """
        Loads the SSH keys listed in the configuration. This may prompt the user for a passphrase

        """
        for single_ssh_key in self._winssh_config.ssh_keys['pem']:
            # THIS IS FOR WINDOWS 
            try:
                rc = check_call(
                    [
                        self._winssh_config.ssh_add_filename,
                        single_ssh_key,
                    ],
                    creationflags=CREATE_NEW_CONSOLE,
                )
                if 0 == rc:
                    pass
            except CalledProcessError as e:
                # e has the return code, but we don't use it at this time
                pass
        
        # TODO: Howto load PKCS11 keys?
    
    def _on_session_group_selected(self, event_data):
        """
        Called when the session group filter changed
        
        """
        widget = event_data.widget 
        
        if widget:
            selected_group_index = widget.curselection()
            if selected_group_index:
                ssh_sessions = self._winssh_config.ssh_sessions
                selected_group_index = selected_group_index[0]
                if 0 == selected_group_index:
                    selected_ssh_sessions = ssh_sessions
                else:
                    # This selects every group and basically cancels the selection
                    selected_group_label = widget.get(selected_group_index)
                    selected_ssh_sessions = []
                    for single_ssh_session in self._winssh_config.ssh_sessions:
                        if selected_group_label == single_ssh_session.group:
                            selected_ssh_sessions.append(single_ssh_session)
                
                # Repopulate the sessions list. There is always at least one entry since groups are specified on the session
                # level
                self._winssh_session_list.delete(0, END)
                self._winssh_session_list.insert(END, *selected_ssh_sessions)

    def _on_session_selected(self, event_data):
        """
        Called when a session is selected 

        """
        ssh_session = None
        ssh_session_name = event_data.widget.get(event_data.widget.curselection()[0])
        for single_ssh_session in self._winssh_config.ssh_sessions:
            if ssh_session_name == single_ssh_session.label:
                ssh_session = single_ssh_session
                break

        process = Process(
            target=start_ssh_session,
            args=(
                self._winssh_config.ssh_filename,
                f'-p{ssh_session.port}',
                ssh_session.host,
            ),
        )
        process.daemon = True
        process.start()
