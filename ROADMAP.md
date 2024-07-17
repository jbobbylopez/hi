
# 'hi' - The Host Information Tool - A Roadmap #
----
This roadmap is intended to help guide the development of this project.
It will be used to help define future development and to focus on the most
important things.  It will also help me gather my thoughts and prioritize the work.

# Guiding Principles #
Although this tool is fun to use, and fun to develop, in order for this
tool to grow and be successful, some goals and expectations should be
established.

#### Intention ####
- This is not intended to be a full-fledged monitoring tool.
This tool is not intended to replace Nagios, Zabbix, Prometheus, Munin, or
any of the other established tools in this space.  This tool is more
supplemental.  It is intended to help with productivity and visibility from
a personal work-flow perspective.  There may be opportunities to integrate
with some of these more established tools in the future, but currently
there are no plans for that.

#### Goal ####
- The goal of this tool is to provide a pleasant user-experience on the
linux command-line for user-customized notifications and indicators. There
may be some other extra tools and features added along the way, but this
remains the primary goal.

#### Simplicity ####
- Keep it light.  Keep it simple.  This tool should remain focused on
providing clean, clear system checks and reporting information.  This tool
should not evolve into an over-complicated mess.

Simple Progress Tracking:
- 🚧: In Progress
- ✅: Done  / Implemented

#### Status Legend ####
👀 - Todo (What I'm looking at doing next)
🚧 - In Progress
✅ - Completed
⬇️  - De-prioritized

----
# ROADMAP MILESTONES #


## Target Features and Improvements ##
The features and fixes defined in this section are almost positively going
to be implemented.  These are features that seem to provide too much value
to be avoided, and might be fairly simple to implement. These types of
changes may already be in development progress.

#### Design Improvements ####
- Code imporovements - refactoring to increase modularity and maintainability

    - `compile_output_messages()`
        - [✅] Break this out into multiple functions
        - [👀] Default icons ❌ and ✅ shouldn't be used in the code.  Should be
          pulled from config.ini
        - [👀] Backup related concerns should move to separate functions
        - Indicator logic can likely be broken out
    - `display_checks()`
        - [✅] Break this out into multiple functions
        - [✅] Handle table and column creation more dynamically, based on
          config.ini values for number of columns, etc.
    - API friendly data structures
        - Improve the structure of messages so this data can be exposed in
          an API for use in another view, like an HTML report.
    - Do something a bit more constructive with the hi header ("Host
      Information:") line

- Aesthetic Improvements

   - [🚧] Enable customization of output (colors, formatting of tables).  This
      will help prevent the tool's output from becoming too mundane, and
      enable users to refine the tool to show exactly what they want to see.
#### Testing ####
- Improved testing scope, focused on indicators and statuses

#### Logical Separation of Concerns ####
- Externalization of hard-coded configs into config/config.ini



## Likely Features and Improvements ##
Not guaranteed, but likely to be implemented if time permits.

#### Design Improvements ####
- Breaking checks.yml out into multiple files. I imagine that if I'm going to implement
'Dynamic Groups', then I might as well group the checks with filenames representing those groups. 
It would also make managing checks an easier task.
- `compile_output_messages()`
    - `output_messages` should probably become multiple dicts, one per
      group.  In this way each group's messages can be populated
      specifically into it's own output table.



## Backlog Ideas and Improvements ##
These are ideas that seem nice or useful, but may be a bit too ambitions to
take on, may go against the "Guiding Principles" above, or may not actually be that useful.

However I'm still interested in doing them. One day I may just sit down
and hammer out a solution for it, who knows!


#### Design Improvements / User Experience ####
- HTTP Extended Information: I would provide the ability to configure 'hi' to run
a user-space http service that would publish the output in JSON format in a version
controlled API. I could also render a full HTML report that looks similar to the
terminal output, but also expose the extended information such as the 'description:' fields.


#### Scalability and Distributed Deployments ####
- Multi-hi - leveraging an exposed API to be able to configure 'hi' to recognise 
other 'hi' instances, and be able to share information, so that multiple hosts can
be reported on from a single terminal. 


#### User Experience ####
- The 'hi' command-line structure could be crafted to target queries for further
information from target remote hosts in a command-line friendly manner 
(keeping workflow in mind, this shouldn't be cumbersome to use).  
This would also support automation and integration capabilities with other 
tools and pipelines.

- Single-line horizontal graph as check output.  Can a check be a mini progress bar?

#### Security ####
- Making use of ssh keys to execute commands on remote hosts.
- Logging, state change tracking.



# Completed Features and Improvements #
Knocking them down, one at a time..

- [✅] Sub-checks - the ability to check various sub-status using the same check delclaration pattern.

- [✅] Dynamic Groups: Currently the groups are hard-coded (Tools, Data, Mounts, Security, Backup..).
This should be dynamic, and based on a yaml config.

- [✅] Check Description: I want to add a 'info:' field to each check (and sub-check)
to provide details on what the check is doing (or why it's important). These details don't 
need to be part of the default 'hi' tool output, but can be shown as extended information with
a flag on the command-line, or in the HTTP server / API output.

- [✅] Remove the dependency on 'watch' command for continuous monitoring.  The
  GNU 'watch' command that comes with most Linux distributions tends to
  strip ANSI color codes from plain-text output.  Although the 'watch'
  command is very preformant (it's written in C), it still has some
  limitations.  With 'hi', because the tools is leveraging curses output
  based on the Rich module, I need to have a bit more control of the
  output, even when used as a continuous monitor.  And so implementing a
  native watch functionality seems to make the most sense.

  **GOAL:** Enable continously updated output / monitoring as a native part of the
  tool, configured via yaml.
