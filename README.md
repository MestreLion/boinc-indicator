BOINC Monitor
=============

App Indicator for monitoring and managing a BOINC.

Also includes python API bindings for the XML RPC_GUI API that the BOINC core client exposes.


The Problem
-----------

Boinc taskbar/panel icon has many issues in Linux:

- For starters, [official docs][1] doesn't even say it *exists*. Only Windows and Mac are mentioned. Same in ["unofficial" docs][2].

- Uses wxTaskBarIcon, which renders as GtkStatusIcon, the old 'notification area' system (also called 'systray'), which has issues in Ubuntu: 11.04 onwards requires [whitelisting the icon][3] to make it work, and for 13.04 onwards such support was [completely removed][4].

- Thus, for many Linux users [BOINC has no taskbar icon][5] at all. [Some think][6] it doesn't even have one, like I did.

- Current system lacks good desktop integration: icons are sub-par, menu layout is not native, and exiting BOINC Manager also shuts down try icon. Also, [closing Manager window][7] has its [own issues][8].


The XML RPC_GUI protocol also has a few drawbacks:

- Lacks proper documentation. "[Look at the source code][9]" is the recommended approach.

- The only API library provided, gui_rpc_client, is C++. No plain C, no Python.

- The command-line utility `boinccmd`, the other high-level interface to boinc client, is easy to use and well documented, but hard and not reliable to use its output to build a GUI manager/monitor on top of it, requiring complex string manipulation and many shell calls.


The Solution
------------

- Ubuntu since 10.04 uses the [Indicator system][10], which works for both Gnome and KDE, and it's now available for many distros. It uses a consistent, well-integrated menu for all its App Indicators.

- An AppIndicator for BOINC can be completely independent of BOINC Manager. You can shut down Manager and still do basic management from Monitor.

- Provide the GUI_RPC API in a fully, easily reusable form. Actually, 2 APIs: one for low-level GUI_RPC, and another, higher level such as `boinccmd` command-line options.

- Everything in Python, to lower the entry barrier and promote third party managers, monitors and GUIs to use a standard library. Python bindings for Gtk libs still [have][11] a [few][12] rough [edges][13], but it's still more widely (and easily) used in Linux than C++.


The Approach
------------

- `gui_rpc_client.py` is a re-write of `gui_rpc_client.{h,cpp}` in Python. Should provide the GUI_RPC API as faithfully as possible, in a Pythonic way, similar to what PyGTK/PyGI/PyGObject/gir bindings do with Gtk/GLib/etc libs. It starts as direct copy-and-paste of the C++ code as comments, and is progressively translated to Python code. C++ structs and enums are converted to classes, `class RpcClient()` being the port of `struct RPC_CLIENT`.

- `client.py` is a conversion of `boinccmd`, not only from C++ to Python, but also from a command-line utility to an API library. Uses `gui_rpc_client.RpcClient` calls to provide an interface that closely matches the command-line options of `boinccmd`, ported as methods of a `BoincClient` class.

- `monitor.py` is the AppIndicator GUI that uses `client.BoincClient` and offers improved icons and better desktop integration. At first, it closely matches the layout and features of `BOINCTaskBar.{h,cpp}`, but will soon incorporate features from BOINC Manager, specially the Activity menu from Advanced view, and later a simplified version of the Simple view

- Since API and App Indicator are distinct, in the future they they can be packaged separately: API as a library package named `python-boinc-gui-rpc` or similar, installed somewhere in `PYTHONPATH`, while the app indicator monitor can be, for example `boinc-monitor` or `boinc-indicator`. Indicator depends on API and recommends `boinc-manager`, and API depends on `boinc-client`.


The Challenges
--------------

Many questions still remain, and help is needed in many areas, not only in programming:

- Indicator (and API) currently has the same limitation as Manager: it can *shutdown* the BOINC core client, but it can not *start* it, since it would require elevated priviledges. `pkexec` can be used to overcome this, and allow a "Start BOINC Client" command via menu.

- Icons are improved, but still subpar. The "suspended" icon is very amateur to say the least (I have *no* skills at all with Gimp), and the "disconnected" was blatantly "stolen" from... the Mac OSX Boinc *Uninstaller*! We need better icons, and more importantly, a good icon design: How to convey messages such as "GPU not Active"? Or Network? Or server Notices? Actually, do we *need* to convey such messages in the icon? Perhaps use Desktop Notifications for some. So, how many states should the icon have? Should they be conveyed as different colors or using mini-"emblems"?

- Also, most desktop design guidelines suggest a monochrome-ish icon design. Both dark and light sets. Colored icons look dated in Unity and Android. So yes, **we desperatly need a good designer**. Actually, *anyone* that can create a consistent set, either colored or light/dark, in scalable format and also properly resized to needed sizes.

- There is no point creating a solid API if there is no documentation. I have no experience in documenting code, or tools to auto-gererate docs from source. Need ideas and implementations (wiki? doxygen? gtk-doc?), and also ways to make it available to users (man page? Yelp? DevHelp?)

- Naming and Packaging: how to package a Python API? How should it be named, in terms of OS package and python package/module hierarchy? And should the indicator monitor should be boinc-indicator or boinc-monitor? Maybe something else?

- It wouldn't hurt to have a simple project page, or a wiki in Github. Anyone familiar with that? Feel free to create it! I already have some screenshots I'd like to post somewhere.

- Most (if not all) of this project could be incorporated in upstream BOINC. How to promote it and make it happen?

Have any comments or suggestions? Don't be shy: [join or open a new issue][14] to discuss any of the above topics and share your ideas!


Requirements
------------

- Pyton (tested in 2.7)
- gir bindings for `GLib`, `Gtk` and `AppIndicator3`

The above are already installed by default in Ubuntu and many Gnome3-based distros

And, of course, the BOINC client.


Running the Indicator
---------------------

Clone the repository and run:

`./boinc-monitor`

A proper installer with `.desktop` launcher will be available soon.


Using the API library
---------------------

Package and modules names are not set in stone yet. Actually, API is still a non-working stub. But, assuming a `boinc` package in `PYTHONPATH`, it will be something like:

For the client API (emulating the options of `boinccmd`):

	from boinc.client import BoincClient
	bc = BoincClient()
	status = bc.get_cc_status()

For the XML GUI_RPC API:

	from boinc.gui_rpc_client import RpcClient
	rpc = RpcClient()
	rpc.init()
	status = rpc.get_status()

The idea is to make the client API somewhat higher-lever and a bit more straightforward than the GUI_RPC, since it automatically deals with deals with `exchange_version()`, `read_gui_rpc_password()` and `authorize()`, but it also may have fewer features. Maybe in the future we realize having 2 layers is pointless, and merge both in a single module that provides both complete feature set and straightforward usage. Only time (or you) will tell.


Written by
----------

Rodigo Silva (MestreLion) <linux@rodrigosilva.com>


Licenses and Copyright
----------------------

Copyright (C) 2013 Rodigo Silva (MestreLion) <linux@rodrigosilva.com>.

License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.

This is free software: you are free to change and redistribute it.

There is NO WARRANTY, to the extent permitted by law.


  [1]: https://boinc.berkeley.edu/wiki/The_BOINC_Manager
  [2]: http://www.boinc-wiki.info/BOINC_Manager
  [3]: http://askubuntu.com/questions/30742
  [4]: http://www.webupd8.org/2013/02/unity-notification-area-systray.html
  [5]: http://boinc.berkeley.edu/dev/forum_thread.php?id=7582
  [6]: http://askubuntu.com/questions/191806
  [7]: https://bugs.launchpad.net/ubuntu/+source/boinc/+bug/926891
  [8]: http://askubuntu.com/questions/191743
  [9]: http://boinc.berkeley.edu/trac/wiki/GuiRpc
  [10]: http://askubuntu.com/questions/14555
  [11]: http://bugs.python.org/issue14138
  [12]: https://bugzilla.gnome.org/show_bug.cgi?id=622084
  [13]: https://bugzilla.gnome.org/show_bug.cgi?id=695683
  [14]: https://github.com/MestreLion/boinc-indicator/issues