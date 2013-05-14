#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# gui_rpc_client.py - GUI_RPC API for BOINC core client
#
#    Copyright (C) 2013 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. See <http://www.gnu.org/licenses/gpl.html>

# Based on lib/gui_rpc_client*.{h,cpp}


from xml.etree import ElementTree
import StringIO
import socket

# #
# // This file contains:
# // 1) functions to clear and parse the various structs
# // 2) actual GUI RPCs
#
# // The core client expects all data to be formatted in the "C" locale,
# // so each GUI RPC should get the current locale, then switch to the
# // "C" locale before formatting messages or parsing results.
# // After all work is completed, revert back to the original locale.
# //
# // Template:
# //
# // int RPC_CLIENT::template_function( args ) {
# //     int retval;
# //     SET_LOCALE sl;
# //     char buf[256];
# //     RPC rpc(this);
# //
# //     <do something useful>
# //
# //     return retval;
# // }
# //
# // NOTE: Failing to revert back to the original locale will cause
# //   formatting failures for any software that has been localized or
# //   displays localized data.
#
#
# #if defined(_WIN32) && !defined(__STDWX_H__) && !defined(_BOINC_WIN_) && !defined(_AFX_STDAFX_H_)
# #include "boinc_win.h"
# #endif
#
# #ifdef _WIN32
# #include "../version.h"
# #else
# #include "config.h"
# #endif

''' Version number relates to the BOINC version this API was based on '''

''' Major part of BOINC version number '''
BOINC_MAJOR_VERSION = 7

''' Minor part of BOINC version number '''
BOINC_MINOR_VERSION = 0

''' Release part of BOINC version number '''
BOINC_RELEASE = 65


# #include "str_util.h"
# #include "util.h"
# #include "error_numbers.h"
# #include "miofile.h"
# #include "md5_file.h"
# #include "network.h"


# #include "common_defs.h"
# #ifndef _COMMON_DEFS_
# #define _COMMON_DEFS_

# // #defines or enums that are shared by more than one BOINC component
# // (e.g. client, server, Manager, etc.)
GUI_RPC_PASSWD_FILE = "/etc/boinc-client/gui_rpc_auth.cfg"
GUI_RPC_PORT        = 31416

# // values of "network status"
NETWORK_STATUS_ONLINE          = 0
NETWORK_STATUS_WANT_CONNECTION = 1
NETWORK_STATUS_WANT_DISCONNECT = 2
NETWORK_STATUS_LOOKUP_PENDING  = 3

# struct TIME_STATS {
class TimeStats(object):
    pass
# // we maintain an exponentially weighted average of these quantities:
#     double now;
#         // the client's time of day
#     double on_frac;
#         // the fraction of total time this host runs the client
#     double connected_frac;
#         // of the time this host runs the client,
#         // the fraction it is connected to the Internet,
#         // or -1 if not known
#     double cpu_and_network_available_frac;
#         // of the time this host runs the client,
#         // the fraction it is connected to the Internet
#         // AND network usage is allowed (by prefs and user toggle)
#         // AND CPU usage is allowed
#     double active_frac;
#         // of the time this host runs the client,
#         // the fraction it is enabled to use CPU
#         // (as determined by preferences, manual suspend/resume, etc.)
#     double gpu_active_frac;
#         // same, GPU
#     double client_start_time;
#     double previous_uptime;
#         // duration of previous session
#
#     void write(MIOFILE&);
#     int parse(XML_PARSER&);
#     void print();
# };

# struct VERSION_INFO {
class VersionInfo(object):

    def __init__(self):
        self.major     = 0
        self.minor     = 0
        self.release   = 0
        self.prerelase = False

    #int parse(MIOFILE&);
    def parse(self, input):
        pass

    #void write(MIOFILE&);
    def write(self, output):
        pass

    #bool greater_than(VERSION_INFO&);
    def greater_than(self, vi):
        if (self.major > vi.major): return True;
        if (self.major < vi.major): return False;
        if (self.minor > vi.minor): return True;
        if (self.minor < vi.minor): return False;
        if (self.release > vi.release): return True;
        return False;

    def __str__(self):
        return "%d.%d.%d" % (self.major, self.minor, self.release)

# #endif common_defs.h

# #include "diagnostics.h"


# #include "parse.h"
# struct XML_PARSER {
class XmlParser(object):
    #XML_PARSER::XML_PARSER(MIOFILE* _f)
    def __init__(self, _f):
        #MIOFILE* f;
        self.f = _f

    #void init(MIOFILE* mf)
    def init(self, mf):
        self.f = mf


# #include "gui_rpc_client.h"
# #ifndef _GUI_RPC_CLIENT_H_
# #define _GUI_RPC_CLIENT_H_
# #include "cc_config.h"
# #include "filesys.h"
# #include "hostinfo.h"
# #ifndef _HOSTINFO_
# #define _HOSTINFO_
#
# // Description of a host's hardware and software.
# // This is used a few places:
# // - it's part of the client's state file, client_state.xml
# // - it's passed in the reply to the get_host_info GUI RPC
# // - it's included in scheduler RPC requests
# //
# // Other host-specific info is kept in
# // TIME_STATS (on/connected/active fractions)
# // NET_STATS (average network bandwidths)
#
# #include "miofile.h"
# #include "coproc.h"
#
# // if you add fields, update clear_host_info()
#
# class HOST_INFO {
class HostInfo(object):
    pass
# public:
#     int timezone;                 // local STANDARD time - UTC time (in seconds)
#     char domain_name[256];
#     char serialnum[256];
#     char ip_addr[256];
#     char host_cpid[64];
#
#     int p_ncpus;
#     char p_vendor[256];
#     char p_model[256];
#     char p_features[1024];
#     double p_fpops;
#     double p_iops;
#     double p_membw;
#     double p_calculated;          // when benchmarks were last run, or zero
#     bool p_vm_extensions_disabled;
#
#     double m_nbytes;              // Total amount of memory in bytes
#     double m_cache;
#     double m_swap;                // Total amount of swap space in bytes
#
#     double d_total;               // Total amount of disk in bytes
#     double d_free;                // Total amount of free disk in bytes
#
#     char os_name[256];
#     char os_version[256];
#
#     // the following is non-empty if VBox is installed
#     //
#     char virtualbox_version[256];
#
#     COPROCS coprocs;
#
# #ifdef ANDROID
#     int battery_charge_pct;
#     int battery_state;
#     double battery_temperature_celsius;
#     void get_battery_status();
# #endif
#
#     HOST_INFO();
#     int parse(XML_PARSER&, bool benchmarks_only = false);
#     int write(MIOFILE&, bool include_net_info, bool include_coprocs);
#     int parse_cpu_benchmarks(FILE*);
#     int write_cpu_benchmarks(FILE*);
#     void print();
#
#     bool host_is_running_on_batteries();
# #ifdef __APPLE__
#     bool users_idle(bool check_all_logins, double idle_time_to_run, double *actual_idle_time=NULL);
# #else
#     bool users_idle(bool check_all_logins, double idle_time_to_run);
# #endif
# #ifdef ANDROID
#     bool host_wifi_online();
# #endif
#     int get_host_info();
#     int get_host_battery_charge();
#     int get_host_battery_state();
#     int get_local_network_info();
#     int get_virtualbox_version();
#     void clear_host_info();
#     void make_random_string(const char* salt, char* out);
#     void generate_host_cpid();
# };
#
# #ifdef __APPLE__
# #ifdef __cplusplus
# extern "C" {
# #endif
#
# #include <IOKit/hidsystem/IOHIDLib.h>
# #include <IOKit/hidsystem/IOHIDParameter.h>
# #include <IOKit/hidsystem/event_status_driver.h>
#
# bool isDualGPUMacBook();
#
# // Apple has removed NxIdleTime() beginning with OS 10.6, so we must try
# // loading it at run time to avoid a link error.  For details, please see
# // the comments in the __APPLE__ version of HOST_INFO::users_idle() in
# // client/hostinfo_unix.cpp.
# typedef double (*nxIdleTimeProc)(NXEventHandle handle);
# #ifdef __cplusplus
# }    // extern "C"
# #endif
#
# extern NXEventHandle gEventHandle;
# #endif
#
# #endif

# #include "miofile.h"
# #include "network.h"
# #include "notice.h"
# #include "prefs.h"
# // global prefs are maintained as follows:
# // 1) a "global_prefs.xml" file, which stores the "network" prefs;
# //      it's maintained by communication with scheduling servers
# //      or project managers
# // 2) a "global_prefs_override.xml" file, which can be edited manually
# //      or via a GUI.
# //      For the prefs that it specifies, it overrides the network prefs.
#
# // A struct with one bool per pref.
# // This is passed in GUI RPCs (get/set_global_prefs_override_struct)
# // to indicate which prefs are (or should be) specified in the override file
# //
# struct GLOBAL_PREFS_MASK {
#     bool confirm_before_connecting;
#     bool cpu_scheduling_period_minutes;
#     bool cpu_usage_limit;
#     bool daily_xfer_limit_mb;
#     bool daily_xfer_period_days;
#     bool disk_interval;
#     bool disk_max_used_gb;
#     bool disk_max_used_pct;
#     bool disk_min_free_gb;
#     bool dont_verify_images;
#     bool end_hour;
#     bool hangup_if_dialed;
#     bool idle_time_to_run;
#     bool leave_apps_in_memory;
#     bool max_bytes_sec_down;
#     bool max_bytes_sec_up;
#     bool max_ncpus;
#     bool max_ncpus_pct;
#     bool net_end_hour;
#     bool net_start_hour;
#     bool network_wifi_only;
#     bool ram_max_used_busy_frac;
#     bool ram_max_used_idle_frac;
#     bool run_if_user_active;
#     bool run_gpu_if_user_active;
#     bool run_on_batteries;
#     bool start_hour;
#     bool suspend_cpu_usage;
#     bool suspend_if_no_recent_input;
#     bool vm_max_used_frac;
#     bool work_buf_additional_days;
#     bool work_buf_min_days;
#
#     GLOBAL_PREFS_MASK();
#     void clear();
#     bool are_prefs_set();
#     bool are_simple_prefs_set();
#     void set_all();
# };
#
#
# // 0..24
# // run always if start==end or start==0, end=24
# // don't run at all if start=24, end=0
# //
# struct TIME_SPAN {
#     bool present;
#     double start_hour;
#     double end_hour;
#
#     enum TimeMode {
#         Always = 7000,
#         Never,
#         Between
#     };
#     TIME_SPAN() : start_hour(0), end_hour(0) {}
#     TIME_SPAN(double start, double end) : start_hour(start), end_hour(end) {}
#
#     bool suspended(double hour) const;
#     TimeMode mode() const;
# };
#
#
# struct WEEK_PREFS {
#     TIME_SPAN days[7];
#
#     void clear() {
#         memset(this, 0, sizeof(WEEK_PREFS));
#     }
#     WEEK_PREFS() {
#         clear();
#     }
#
#     void set(int day, double start, double end);
#     void set(int day, TIME_SPAN* time);
#     void unset(int day);
#
# protected:
#     void copy(const WEEK_PREFS& original);
# };
#
#
# struct TIME_PREFS : public TIME_SPAN {
#     WEEK_PREFS week;
#
#     TIME_PREFS() {}
#     TIME_PREFS(double start, double end) {
#         start_hour = start;
#         end_hour = end;
#     }
#
#     void clear();
#     bool suspended(double t);
#
# };
#
#
# struct GLOBAL_PREFS {
class GlobalPrefs(object):
    pass
#     double mod_time;
#
#     bool confirm_before_connecting;
#     double cpu_scheduling_period_minutes;
#         // length of a time slice.
#         // scheduling happens more often.
#     TIME_PREFS cpu_times;
#     double cpu_usage_limit;
#     double daily_xfer_limit_mb;
#     int daily_xfer_period_days;
#     double disk_interval;
#     double disk_max_used_gb;
#     double disk_max_used_pct;
#     double disk_min_free_gb;
#     bool dont_verify_images;
#     bool hangup_if_dialed;
#     double idle_time_to_run;
#     bool leave_apps_in_memory;
#     double max_bytes_sec_down;
#     double max_bytes_sec_up;
#     int max_ncpus;
#     double max_ncpus_pct;
#     TIME_PREFS net_times;
#     bool network_wifi_only;
#         // introduced with Android. Do network communication only when on Wifi,
#         // not on public cell networks.
#         // CAUTION: this only applies to file transfers.
#         // scheduler RPCs are made regardless of this preference.
#     double ram_max_used_busy_frac;
#     double ram_max_used_idle_frac;
#     bool run_gpu_if_user_active;
#     bool run_if_user_active;
#     bool run_on_batteries;
#         // poorly named; what it really means is:
#         // if false, suspend while on batteries
#     double suspend_cpu_usage;
#     double suspend_if_no_recent_input;
#     double vm_max_used_frac;
#     double work_buf_additional_days;
#     double work_buf_min_days;
#
#     char source_project[256];
#     char source_scheduler[256];
#     bool host_specific;
#         // an account manager can set this; if set, don't propagate
#     bool override_file_present;
#
#     GLOBAL_PREFS();
#     void defaults();
#     void init();
#     void clear_bools();
#     int parse(XML_PARSER&, const char* venue, bool& found_venue, GLOBAL_PREFS_MASK& mask);
#     int parse_day(XML_PARSER&);
#     int parse_override(XML_PARSER&, const char* venue, bool& found_venue, GLOBAL_PREFS_MASK& mask);
#     int parse_file(const char* filename, const char* venue, bool& found_venue);
#     int write(MIOFILE&);
#     int write_subset(MIOFILE&, GLOBAL_PREFS_MASK&);
#     void write_day_prefs(MIOFILE&);
#     inline double cpu_scheduling_period() {
#         return cpu_scheduling_period_minutes*60;
#     }
# };
#
# struct GUI_URL {
#     std::string name;
#     std::string description;
#     std::string url;
#
#     int parse(XML_PARSER&);
#     void print();
# };
#
# // statistics at a specific day
# //
# struct DAILY_STATS {
#     double user_total_credit;
#     double user_expavg_credit;
#     double host_total_credit;
#     double host_expavg_credit;
#     double day;
#
#     int parse(XML_PARSER&);
# };
#
#
# struct PROJECT_LIST_ENTRY {
#     std::string name;
#     std::string url;
#     std::string general_area;
#     std::string specific_area;
#     std::string description;
#     std::string home;       // sponsoring organization
#     std::string image;      // URL of logo
#     std::vector<std::string> platforms;
#         // platforms supported by project, or empty
#
#     PROJECT_LIST_ENTRY();
#     ~PROJECT_LIST_ENTRY();
#
#     int parse(XML_PARSER&);
#     void clear();
# };
#
# struct AM_LIST_ENTRY {
#     std::string name;
#     std::string url;
#     std::string description;
#     std::string image;
#
#     AM_LIST_ENTRY();
#     ~AM_LIST_ENTRY();
#
#     int parse(XML_PARSER&);
#     void clear();
# };
#
# struct ALL_PROJECTS_LIST {
#     std::vector<PROJECT_LIST_ENTRY*> projects;
#     std::vector<AM_LIST_ENTRY*> account_managers;
#
#     ALL_PROJECTS_LIST();
#     ~ALL_PROJECTS_LIST();
#
#     void clear();
#     void alpha_sort();
# };
#
# struct RSC_DESC {
#     double backoff_time;
#     double backoff_interval;
#     bool no_rsc_ams;
#     bool no_rsc_apps;
#     bool no_rsc_pref;
#     bool no_rsc_config;
#
#     void clear();
# };
#
# struct PROJECT {
class Project(object):
    pass
#     char master_url[256];
#     double resource_share;
#     std::string project_name;
#     std::string user_name;
#     std::string team_name;
#     int hostid;
#     std::vector<GUI_URL> gui_urls;
#     double user_total_credit;
#     double user_expavg_credit;
#     double host_total_credit;      // as reported by server
#     double host_expavg_credit;     // as reported by server
#     double disk_usage;
#     int nrpc_failures;          // # of consecutive times we've failed to
#                                 // contact all scheduling servers
#     int master_fetch_failures;
#     double min_rpc_time;           // earliest time to contact any server
#     double download_backoff;
#     double upload_backoff;
#
#     RSC_DESC rsc_desc_cpu;
#     RSC_DESC rsc_desc_nvidia;
#     RSC_DESC rsc_desc_ati;
#     RSC_DESC rsc_desc_intel_gpu;
#
#     double sched_priority;
#
#     double duration_correction_factor;
#
#     bool anonymous_platform;
#     bool master_url_fetch_pending; // need to fetch and parse the master URL
#     int sched_rpc_pending;      // need to contact scheduling server
#         // encodes the reason for the request
#     bool non_cpu_intensive;
#     bool suspended_via_gui;
#     bool dont_request_more_work;
#     bool scheduler_rpc_in_progress;
#     bool attached_via_acct_mgr;
#     bool detach_when_done;
#     bool ended;
#     bool trickle_up_pending;
#     double project_files_downloaded_time;
#         // when the last project file download was finished
#         // (i.e. the time when ALL project files were finished downloading)
#     double last_rpc_time;
#         // when the last successful scheduler RPC finished
#     std::vector<DAILY_STATS> statistics; // credit data over the last x days
#     char venue[256];
#
#     // NOTE: if you add any data items above,
#     // update parse(), and clear() to include them!!
#
#     PROJECT();
#     ~PROJECT();
#
#     int parse(XML_PARSER&);
#     void print();
#     void print_disk_usage();
#     void clear();
#     void get_name(std::string&);
#
#     // temp - keep track of whether or not this record needs to be deleted
#     bool flag_for_delete;
# };
#
# struct APP {
class App(object):
    pass
#     char name[256];
#     char user_friendly_name[256];
#     PROJECT* project;
#
#     APP();
#     ~APP();
#
#     int parse(XML_PARSER&);
#     void print();
#     void clear();
# };
#
# struct APP_VERSION {
class AppVersion(object):
    pass
#     char app_name[256];
#     int version_num;
#     char platform[64];
#     char plan_class[64];
#     double avg_ncpus;
#     int gpu_type;
#         // PROC_TYPE_xx
#     double gpu_usage;
#     double natis;
#     double gpu_ram;
#     double flops;
#     APP* app;
#     PROJECT* project;
#
#     APP_VERSION();
#     ~APP_VERSION();
#
#     int parse(XML_PARSER&);
#     int parse_coproc(XML_PARSER&);
#     void print();
#     void clear();
# };
#
# struct WORKUNIT {
#     char name[256];
#     char app_name[256];
#     int version_num;    // backwards compat
#     double rsc_fpops_est;
#     double rsc_fpops_bound;
#     double rsc_memory_bound;
#     double rsc_disk_bound;
#     PROJECT* project;
#     APP* app;
#
#     WORKUNIT();
#     ~WORKUNIT();
#
#     int parse(XML_PARSER&);
#     void print();
#     void clear();
# };
#
# struct RESULT {
class Result(object):
    pass
#     char name[256];
#     char wu_name[256];
#     char project_url[256];
#     int version_num;
#     char plan_class[64];
#     double report_deadline;
#     double received_time;
#     bool ready_to_report;
#     bool got_server_ack;
#     double final_cpu_time;
#     double final_elapsed_time;
#     int state;
#     int scheduler_state;
#     int exit_status;
#     int signal;
#     //std::string stderr_out;
#     bool suspended_via_gui;
#     bool project_suspended_via_gui;
#     bool coproc_missing;
#     bool scheduler_wait;
#     char scheduler_wait_reason[256];
#     bool network_wait;
#
#     // the following defined if active
#     bool active_task;
#     int active_task_state;
#     int app_version_num;
#     int slot;
#     int pid;
#     double checkpoint_cpu_time;
#     double current_cpu_time;
#     double fraction_done;
#     double elapsed_time;
#     double swap_size;
#     double working_set_size_smoothed;
#     double estimated_cpu_time_remaining;
#         // actually, estimated elapsed time remaining
#     bool too_large;
#     bool needs_shmem;
#     bool edf_scheduled;
#     char graphics_exec_path[MAXPATHLEN];
#     char web_graphics_url[256];
#     char remote_desktop_addr[256];
#     char slot_path[MAXPATHLEN];
#         // only present if graphics_exec_path is
#     char resources[256];
#
#     APP* app;
#     WORKUNIT* wup;
#     PROJECT* project;
#     APP_VERSION* avp;
#
#     RESULT();
#     ~RESULT();
#
#     int parse(XML_PARSER&);
#     void print();
#     void clear();
# };
#
# struct FILE_TRANSFER {
#     std::string name;
#     std::string project_url;
#     std::string project_name;
#     double nbytes;              // total # of bytes to be transferred
#     bool uploaded;
#     bool is_upload;
#     bool generated_locally;     // deprecated; for compatibility w/ old clients
#     bool sticky;
#     bool pers_xfer_active;
#     bool xfer_active;
#     int num_retries;
#     double first_request_time;
#     double next_request_time;
#     int status;
#     double time_so_far;
#     double bytes_xferred;
#     double file_offset;
#     double xfer_speed;
#     std::string hostname;
#     double project_backoff;
#     PROJECT* project;
#
#     FILE_TRANSFER();
#     ~FILE_TRANSFER();
#
#     int parse(XML_PARSER&);
#     void print();
#     void clear();
# };
#
# struct MESSAGE {
class Message(object):
    pass
#     std::string project;
#     int priority;
#     int seqno;
#     int timestamp;
#     std::string body;
#
#     MESSAGE();
#     ~MESSAGE();
#
#     int parse(XML_PARSER&);
#     void print();
#     void clear();
# };
#
# // should match up with PROXY_INFO in proxy_info.h
# //
# struct GR_PROXY_INFO {
#     bool use_http_proxy;
#     bool use_http_authentication;
#     std::string http_server_name;
#     int http_server_port;
#     std::string http_user_name;
#     std::string http_user_passwd;
#
#     bool use_socks_proxy;
#     std::string socks_server_name;
#     int socks_server_port;
#     std::string socks5_user_name;
#     std::string socks5_user_passwd;
#
#     std::string noproxy_hosts;
#
#     GR_PROXY_INFO();
#     ~GR_PROXY_INFO();
#
#     int parse(XML_PARSER&);
#     void print();
#     void clear();
# };
#
# // Represents the entire client state.
# // Call get_state() infrequently.
# //
# struct CC_STATE {
class CcState(object):
    def __init__(self):
        #std::vector<PROJECT*> projects;
        self.projects = []
        #std::vector<APP*> apps;
        self.apps = []
        #std::vector<APP_VERSION*> app_versions;
        self.app_versions = []
        #std::vector<WORKUNIT*> wus;
        self.wus = []
        #std::vector<RESULT*> results;
        self.results = []
        #std::vector<std::string> platforms;
        self.platforms = []
        #// platforms supported by client

        #GLOBAL_PREFS global_prefs;  // working prefs, i.e. network + override
        self.global_prefs = GlobalPrefs()
        #VERSION_INFO version_info;  // populated only if talking to pre-5.6 client
        self.version_info = VersionInfo()
        #bool executing_as_daemon;   // true if client is running as a service / daemon
        self.executing_as_daemon = False
        #HOST_INFO host_info;
        self.host_info = HostInfo()
        #TIME_STATS time_stats;
        self.time_stats = TimeStats()
        #bool have_nvidia;           // deprecated; include for compat (set by <have_cuda/>)
        self.have_nvidia = False
        #bool have_ati;              // deprecated; include for compat
        self.have_ati = False

        self.clear()
#
#     PROJECT* lookup_project(const char* url);
#     APP* lookup_app(PROJECT*, const char* name);
#     APP_VERSION* lookup_app_version(PROJECT*, APP*, int, char* plan_class);
#     APP_VERSION* lookup_app_version_old(PROJECT*, APP*, int);
#     WORKUNIT* lookup_wu(PROJECT*, const char* name);
#     RESULT* lookup_result(PROJECT*, const char* name);
#     RESULT* lookup_result(const char* url, const char* name);
#
#     void print();


    #void clear();
    def clear(self):
        pass


    #int parse(XML_PARSER&);
    def parse(self, xp):
        return xp.f
#
# struct PROJECTS {
#     std::vector<PROJECT*> projects;
#
#     PROJECTS(){}
#     ~PROJECTS();
#
#     void print();
#     void clear();
# };
#
# struct DISK_USAGE {
#     std::vector<PROJECT*> projects;
#     double d_total;
#     double d_free;
#     double d_boinc;     // amount used by BOINC itself, not projects
#     double d_allowed;   // amount BOINC is allowed to use, total
#
#     DISK_USAGE(){clear();}
#     ~DISK_USAGE();
#
#     void print();
#     void clear();
# };
#
# struct RESULTS {
#     std::vector<RESULT*> results;
#
#     RESULTS(){}
#     ~RESULTS();
#
#     void print();
#     void clear();
# };
#
# struct FILE_TRANSFERS {
#     std::vector<FILE_TRANSFER*> file_transfers;
#
#     FILE_TRANSFERS();
#     ~FILE_TRANSFERS();
#
#     void print();
#     void clear();
# };
#
# struct MESSAGES {
#     std::vector<MESSAGE*> messages;
#
#     MESSAGES();
#     ~MESSAGES();
#
#     void print();
#     void clear();
# };
#
# struct NOTICES {
#     bool complete;
#     bool received;
#         // whether vector contains all notices, or just new ones
#     std::vector<NOTICE*> notices;
#
#     NOTICES();
#     ~NOTICES();
#
#     void print();
#     void clear();
# };
#
# struct ACCT_MGR_INFO {
#     std::string acct_mgr_name;
#     std::string acct_mgr_url;
#     bool have_credentials;
#     bool cookie_required;
#     std::string cookie_failure_url;
#
#     ACCT_MGR_INFO();
#     ~ACCT_MGR_INFO(){}
#
#     int parse(XML_PARSER&);
#     void clear();
# };
#
# struct PROJECT_ATTACH_REPLY {
#     int error_num;
#     std::vector<std::string>messages;
#
#     PROJECT_ATTACH_REPLY();
#     ~PROJECT_ATTACH_REPLY(){}
#
#     int parse(XML_PARSER&);
#     void clear();
# };
#
# struct ACCT_MGR_RPC_REPLY {
#     int error_num;
#     std::vector<std::string>messages;
#
#     ACCT_MGR_RPC_REPLY();
#     ~ACCT_MGR_RPC_REPLY(){}
#
#     int parse(XML_PARSER&);
#     void clear();
# };
#
# struct PROJECT_INIT_STATUS {
#     std::string url;
#     std::string name;
#     std::string team_name;
#     bool has_account_key;
#
#     PROJECT_INIT_STATUS();
#     ~PROJECT_INIT_STATUS(){}
#
#     int parse(XML_PARSER&);
#     void clear();
# };
#
# struct PROJECT_CONFIG {
#     int error_num;
#     std::string name;
#     std::string master_url;
#     int local_revision;     // SVN changeset# of server software
#     int min_passwd_length;
#     bool account_manager;
#     bool uses_username;     // true for WCG
#     bool account_creation_disabled;
#     bool client_account_creation_disabled;  // must create account on web
#     bool sched_stopped;         // scheduler disabled
#     bool web_stopped;           // DB-driven web functions disabled
#     int min_client_version;
#     std::string error_msg;
#     std::string terms_of_use;
#         // if present, show this text in an "accept terms of use?" dialog
#         // before allowing attachment to continue.
#     std::vector<std::string> platforms;
#         // platforms supported by project, or empty
#
#     PROJECT_CONFIG();
#     ~PROJECT_CONFIG();
#
#     int parse(XML_PARSER&);
#     void clear();
#     void print();
# };
#
# struct ACCOUNT_IN {
#     std::string url;
#     std::string email_addr;
#         // the account identifier (email address or user name)
#     std::string user_name;
#     std::string passwd;
#     std::string team_name;
#
#     ACCOUNT_IN();
#     ~ACCOUNT_IN();
#
#     void clear();
# };
#
# struct ACCOUNT_OUT {
#     int error_num;
#     std::string error_msg;
#     std::string authenticator;
#
#     ACCOUNT_OUT();
#     ~ACCOUNT_OUT();
#
#     int parse(XML_PARSER&);
#     void clear();
#     void print();
# };


#struct CC_STATUS {
class CcStatus(object):
    def __init__(self):
        self.clear()


    #void clear();
    def clear(self):
        self.network_status         = -1    #// values: NETWORK_STATUS_*
        self.ams_password_error     = False
        self.manager_must_quit      = False
        self.task_suspend_reason    = -1    #// bitmap, see common_defs.h
        self.task_mode              = -1    #// always/auto/never; see common_defs.h
        self.task_mode_perm         = -1    #// same, but permanent version
        self.task_mode_delay        =  0.0  #// time until perm becomes actual
        self.network_suspend_reason = -1
        self.network_mode           = -1
        self.network_mode_perm      = -1
        self.network_mode_delay     =  0.0
        self.gpu_suspend_reason     = -1
        self.gpu_mode               = -1
        self.gpu_mode_perm          = -1
        self.gpu_mode_delay         =  0.0
        self.disallow_attach        = False
        self.simple_gui_only        = False


    #int parse(XML_PARSER&);
    #int CC_STATUS::parse(XML_PARSER& xp) {
    def parse(self, xp):
        #PS: As per original code, parse() is able to read the broken XML, so we
        #    can't simply use ElementTree in the whole file. We gotta loop it
        #    line-by-line and parse each fragment. Lame
        for buf in xp.f:
            if '</cc_status>' in buf:
                return

            e = ElementTree.fromstring(buf)
            try:
                if   e.tag == 'network_status':         self.network_status         = int  (e.text)
                elif e.tag == 'ams_password_error':     self.ams_password_error     = bool (e.text)
                elif e.tag == 'manager_must_quit':      self.manager_must_quit      = bool (e.text)
                elif e.tag == 'task_suspend_reason':    self.task_suspend_reason    = int  (e.text)
                elif e.tag == 'task_mode':              self.task_mode              = int  (e.text)
                elif e.tag == 'task_mode_perm':         self.task_mode_perm         = int  (e.text)
                elif e.tag == 'task_mode_delay':        self.task_mode_delay        = float(e.text)
                elif e.tag == 'gpu_suspend_reason':     self.gpu_suspend_reason     = int  (e.text)
                elif e.tag == 'gpu_mode':               self.gpu_mode               = int  (e.text)
                elif e.tag == 'gpu_mode_perm':          self.gpu_mode_perm          = int  (e.text)
                elif e.tag == 'gpu_mode_delay':         self.gpu_mode_delay         = float(e.text)
                elif e.tag == 'network_suspend_reason': self.network_suspend_reason = int  (e.text)
                elif e.tag == 'network_mode':           self.network_mode           = int  (e.text)
                elif e.tag == 'network_mode_perm':      self.network_mode_perm      = int  (e.text)
                elif e.tag == 'network_mode_delay':     self.network_mode_delay     = float(e.text)
                elif e.tag == 'disallow_attach':        self.disallow_attach        = bool (e.text)
                elif e.tag == 'simple_gui_only':        self.simple_gui_only        = bool (e.text)
            except ValueError:
                pass

        raise BoincException("ERR_XML_PARSE")


    #void print();
# };


#
# struct SIMPLE_GUI_INFO {
#     std::vector<PROJECT*> projects;
#     std::vector<RESULT*> results;
#     void print();
# };
#
# struct DAILY_XFER {
#     int when;
#     double up;
#     double down;
#
#     int parse(XML_PARSER&);
# };
#
# struct DAILY_XFER_HISTORY {
#     std::vector <DAILY_XFER> daily_xfers;
#     int parse(XML_PARSER&);
#     void print();
# };


# struct RPC_CLIENT {
class RpcClient(object):

    def __init__(self):
#     int sock;
        self.sock = -1

#     double timeout;
        self.timeout = 30

#     double start_time;
#     bool retry;
#     sockaddr_storage addr;
        self.addr = None


    #int send_request(const char*);
    def send_request(self, p):
        ''' Send a XML request to socket, properly enclosed in GUI RPC format
        '''
        buf = \
            "<boinc_gui_rpc_request>\n"\
            "%s"\
            "</boinc_gui_rpc_request>\n\003"\
             % (p)

        try:
            self.sock.sendall(buf)
        except (socket.error, socket.herror, socket.gaierror, socket.timeout):
            #DIFF: throws original exception instead of "ERR_WRITE"
            raise


    #// get reply from server.  Caller must free buf
    #//
    #int get_reply(char*&);
    #DIFF: instead of int get_reply(char*&), char* get_reply(void)
    def get_reply(self):
        ''' Read reply from socket and return result as string
        '''
        mf = ""
        end = '\003'
        while True:
            buf = self.sock.recv(8192)
            if not buf:
                raise BoincException("ERR_READ")
            n = buf.find(end)
            if not n == -1: break
            mf += buf

        return mf + buf[:n]


    #int get_ip_addr(const char* host, int port);
    def get_ip_addr(self, host, port):
        ''' Set self.addr to a (5-tuple) suitable for socket connection
        '''
        #DIFF: allows port as string such as 'http'
        self.addr = socket.getaddrinfo(host or None,
                                       port or GUI_RPC_PORT,
                                       socket.AF_INET,
                                       socket.SOCK_STREAM,
                                       socket.IPPROTO_TCP)[0]

    #int init(const char* host, int port=0);
    def init(self, host, port=0):
        ''' Connect to (host, port) and set self.sock to the socket object
        '''
        self.get_ip_addr(host, port)
        socket.setdefaulttimeout(30)
        self.sock = socket.socket(*self.addr[:3])
        self.sock.connect(self.addr[-1])

        #PS: The above is soooo primitive. A much simpler and powerful version:
        #self.sock = socket.create_connection((host or None, port or GUI_RPC_PORT), 30)
        # Advantages: uses IPv6+IPv4, and tries every address returned by getaddrinfo()


#     int init_asynch(
#         const char* host, double timeout, bool retry, int port=GUI_RPC_PORT
#     );
#         // timeout == how long to wait until give up
#         //    If the caller (i.e. BOINC Manager) just launched the core client,
#         //    this should be large enough to allow the process to
#         //    run and open its listening socket (e.g. 60 sec)
#         //    If connecting to a remote client, it should be large enough
#         //    for the user to deal with a "personal firewall" popup
#         //    (e.g. 60 sec)
#         // retry: if true, keep retrying until succeed or timeout.
#         //    Use this if just launched the core client.
#     int init_poll();


    # // if any RPC returns ERR_READ or ERR_WRITE,
    # // call this and then call init() again.
    # //
    #void close();
    def close(self):
        if self.sock > -1:
            self.sock.close()
            self.sock = -1;


    #int authorize(const char* passwd);
    def authorize(self, passwd):
        pass


    #int exchange_versions(VERSION_INFO&);
    def exchange_versions(self):
        ''' Send API version info and return a VersionInfo object from client
        '''
        rpc = Rpc(self)
        server = VersionInfo()

        buf = \
            "<exchange_versions>\n"\
            "   <major>%d</major>\n"\
            "   <minor>%d</minor>\n"\
            "   <release>%d</release>\n"\
            "</exchange_versions>\n" % (
            BOINC_MAJOR_VERSION,
            BOINC_MINOR_VERSION,
            BOINC_RELEASE)

        rpc.do_rpc(buf)
        for buf in ElementTree.parse(rpc.fin).iter():
            try:
                if   buf.tag == 'major'  : server.major   = int(buf.text)
                elif buf.tag == 'minor'  : server.minor   = int(buf.text)
                elif buf.tag == 'release': server.release = int(buf.text)
            except ValueError:
                pass  # error in int() conversion

        return server


    #int get_state(CC_STATE&);
    def get_state(self):
        ''' Return a CcState object with entire client state info
        '''
        rpc = Rpc(self)
        rpc.do_rpc("<get_state/>\n")
        state = CcState()
        return state.parse(rpc.xp);


    #int get_cc_status(CC_STATUS&);
    #int RPC_CLIENT::get_cc_status(CC_STATUS& status) {
    def get_cc_status(self):
        status = CcStatus()
        rpc = Rpc(self)
        rpc.do_rpc("<get_cc_status/>\n")

        #PS: this loop is just to position rpc.fin after '<cc_status>'
        #    so status.parse() is not even called if tag does not exist.
        #    As a side effect, it also pass a broken XML file to it:(
        for buf in rpc.fin:
            if '<cc_status>' in buf:
                status.parse(rpc.xp)
                break

        return status


#     int get_results(RESULTS&, bool active_only = false);
#     int get_file_transfers(FILE_TRANSFERS&);
#     int get_simple_gui_info(SIMPLE_GUI_INFO&);
#     int get_project_status(PROJECTS&);
#     int get_all_projects_list(ALL_PROJECTS_LIST&);
#     int get_disk_usage(DISK_USAGE&);
#     int project_op(PROJECT&, const char* op);
#     int set_run_mode(int mode, double duration);
#         // if duration is zero, change is permanent.
#         // otherwise, after duration expires,
#         // restore last permanent mode
#     int set_gpu_mode(int mode, double duration);
#     int set_network_mode(int mode, double duration);
#     int get_screensaver_tasks(int& suspend_reason, RESULTS&);
#     int run_benchmarks();
#     int set_proxy_settings(GR_PROXY_INFO&);
#     int get_proxy_settings(GR_PROXY_INFO&);
#     int get_messages(int seqno, MESSAGES&, bool translatable=false);
#     int get_message_count(int& seqno);
#     int get_notices(int seqno, NOTICES&);
#     int get_notices_public(int seqno, NOTICES&);
#     int file_transfer_op(FILE_TRANSFER&, const char*);
#     int result_op(RESULT&, const char*);
#     int get_host_info(HOST_INFO&);
#     int quit();
#     int acct_mgr_info(ACCT_MGR_INFO&);
#     const char* mode_name(int mode);
#     int get_statistics(PROJECTS&);
#     int network_available();
#     int get_project_init_status(PROJECT_INIT_STATUS& pis);
#
#     // the following are asynch operations.
#     // Make the first call to start the op,
#     // call the second one periodically until it returns zero.
#     // TODO: do project update
#     //
#     int get_project_config(std::string url);
#     int get_project_config_poll(PROJECT_CONFIG&);
#     int lookup_account(ACCOUNT_IN&);
#     int lookup_account_poll(ACCOUNT_OUT&);
#     int create_account(ACCOUNT_IN&);
#     int create_account_poll(ACCOUNT_OUT&);
#     int project_attach(
#         const char* url, const char* auth, const char* project_name
#     );
#     int project_attach_from_file();
#     int project_attach_poll(PROJECT_ATTACH_REPLY&);
#     int acct_mgr_rpc(
#         const char* url, const char* name, const char* passwd,
#         bool use_config_file=false
#     );
#     int acct_mgr_rpc_poll(ACCT_MGR_RPC_REPLY&);
#
#     int get_newer_version(std::string&, std::string&);
#     int read_global_prefs_override();
#     int read_cc_config();


#     int get_global_prefs_file(std::string&);
#     int get_global_prefs_working(std::string&);
#     int get_global_prefs_working_struct(GLOBAL_PREFS&, GLOBAL_PREFS_MASK&);
#     int get_global_prefs_override(std::string&);
#     int set_global_prefs_override(std::string&);
#     int get_global_prefs_override_struct(GLOBAL_PREFS&, GLOBAL_PREFS_MASK&);
#     int set_global_prefs_override_struct(GLOBAL_PREFS&, GLOBAL_PREFS_MASK&);
#     int get_cc_config(CONFIG& config, LOG_FLAGS& log_flags);
#     int set_cc_config(CONFIG& config, LOG_FLAGS& log_flags);
#     int get_daily_xfer_history(DAILY_XFER_HISTORY&);
# };
class BoincException(Exception): pass

# struct RPC {
class Rpc(object):
    #RPC(RPC_CLIENT*);
    def __init__(self, rpc_client):
        ''' set self.rpc_client as the given object. It could be understood as
            the "caller" (or owner, parent) object, the one it uses methods
            like send_request() and get_reply()
        '''
#     char* mbuf;
        self.mbuf = ""
#     MIOFILE fin;
        self.fin  = StringIO.StringIO()
#     XML_PARSER xp;
        self.xp   = XmlParser(self.fin)
#     RPC_CLIENT* rpc_client;
        self.rpc_client = rpc_client


    #int do_rpc(const char*);
    def do_rpc(self, req):
        ''' Send request and store reply in self.mbuf (string) and
            self.fin (file-like). Uses the caller's ( or "owner", or "parent")
            own send_request() and get_reply() methods
        '''
        if self.rpc_client.sock == -1:
            raise BoincException("ERR_CONNECT")

        self.rpc_client.send_request(req)
        self.mbuf = self.rpc_client.get_reply()
        self.fin.write(self.mbuf)
        self.fin.seek(0)

#     int parse_reply();
# };
#
# // We recommend using the XCode project under OS 10.5 to compile
# // the BOINC library, but some projects still use config & make,
# // so the following compatibility code avoids compiler errors when
# // building libboinc.a using config & make on system OS 10.3.9 or
# // with the OS 10.3.9 SDK (but using config & make is not recommended.)
# //
# #if defined(__APPLE__) && (MAC_OS_X_VERSION_MIN_REQUIRED < MAC_OS_X_VERSION_10_4) && (!defined(BUILDING_MANAGER))
# #define NO_PER_THREAD_LOCALE 1
# #endif
#
# // uselocal() API should be available on UNIX, Fedora & Ubuntu.
# // For any platforms which do not support setting locale on a
# // per-thread basis, add code here similar to the following sample:
# //#if defined(__UNIVAC__)
# //#define NO_PER_THREAD_LOCALE 1
# //#endif
# #if defined(__HAIKU__)
# #define NO_PER_THREAD_LOCALE 1
# #endif
#
#
# #ifdef NO_PER_THREAD_LOCALE
#     // Use this code for any platforms which do not support
#     // setting locale on a per-thread basis (see comment above)
#  struct SET_LOCALE {
#     std::string locale;
#     inline SET_LOCALE() {
#         locale = setlocale(LC_ALL, NULL);
#         setlocale(LC_ALL, "C");
#     }
#     inline ~SET_LOCALE() {
#         setlocale(LC_ALL, locale.c_str());
#     }
# };
#
# #elif defined(__APPLE__) && (MAC_OS_X_VERSION_MIN_REQUIRED < MAC_OS_X_VERSION_10_4)
# // uselocale() is not available in OS 10.3.9 so use weak linking
# #include <xlocale.h>
# extern int        freelocale(locale_t) __attribute__((weak_import));
# extern locale_t    newlocale(int, __const char *, locale_t) __attribute__((weak_import));
# extern locale_t    uselocale(locale_t) __attribute__((weak_import));
#
# struct SET_LOCALE {
#     locale_t old_locale, RPC_locale;
#     std::string locale;
#     inline SET_LOCALE() {
#         if (uselocale == NULL) {
#             locale = setlocale(LC_ALL, NULL);
#             setlocale(LC_ALL, "C");
#         }
#     }
#     inline ~SET_LOCALE() {
#         if (uselocale == NULL) {
#             setlocale(LC_ALL, locale.c_str());
#         }
#     }
# };
#
# #else
#
# struct SET_LOCALE {
#     // Don't need to juggle locales if we have per-thread locale
#     inline SET_LOCALE() {
#     }
#     inline ~SET_LOCALE() {
#     }
# };
# #endif
#
# extern int read_gui_rpc_password(char*);
# If there's a password file, read it
def read_gui_rpc_password():
    ''' Read password string from hardcoded GUI_RPC_PASSWD_FILE file, trim the
        last CR (ir any), and return it
    '''
    try:
        with open(GUI_RPC_PASSWD_FILE, 'r') as f:
            buf = f.read()
    except IOError:
        # Permission denied or File not found.
        buf = ""

    # trim CR
    if buf.endswith('\n'):
        buf = buf[:-1]

    return buf
#
# #endif /* _GUI_RPC_CLIENT_H_ */


# Unit tests
if __name__ == "__main__":
    print "read_gui_rpc_password(): '%s'" % read_gui_rpc_password()
    rpc = RpcClient()

    rpc.get_ip_addr('', 0)
    print "get_ip_addr('', 0):", rpc.addr
    rpc.get_ip_addr('boinc.berkeley.edu', 0)
    print "get_ip_addr('boinc.berkeley.edu', 0):", rpc.addr
    rpc.get_ip_addr('boinc.berkeley.edu', 80)
    print "get_ip_addr('boinc.berkeley.edu', 80):", rpc.addr

    rpc.init('boinc.berkeley.edu', 80)
    print "init('boinc.berkeley.edu', 80):", rpc.sock
    rpc.init('')
    print "init(''):", rpc.sock

    version = rpc.exchange_versions()
    print "version: %d.%d.%d" % (version.major, version.minor, version.release)

    status = rpc.get_cc_status()
    print "get_cc_status:"
    for item in status.__dict__:
        print '\t%s\t%s' % (item, getattr(status, item))

    state = rpc.get_state()
    print "get_state:"
    for line in state:
        print '\t%s' % line.rstrip()
