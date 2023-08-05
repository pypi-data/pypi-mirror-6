A basic Python command line time tracker, inspired by a post on Hacker News by James Britt (https://news.ycombinator.com/item?id=6897425).

#Basics

To install:

`pip install timetracker`

To run:

`timetracker`

It's recommended that you alias it to `@`, for easier use:

`alias @=timetracker`

#Using timetracker

Just invoke timetracker followed with a string of whatever you're working on:

`@ repaired the flux capacitor`

If invoked without arguments, it will prompt you to type a note.

timetracker will save your note, timestamped, into a .log file stored as follows:

`$ROOT/YYYY/MM/dd.log`

By default, $ROOT will be a `timetracker` directory in your home folder.
You can change that by editing the config file `~/.config/timetracker/timetracker.conf`; it look as follows:

````
root = '~/location/to/other/folder'
time_format = '%H:%M'
`````

`root` is where the logs will be stored; `time_format` indicates how dates will be structured in the log files.

#Tips

You can integrate it in your workflow in a nice way; for example, by writing a script that will invoke it every hour, or every time you do a `git commit`, etc.
A good way to not forget about it is to have your terminal greeting remind you to use it!

The program is fairly smart with appending to existing files etc., so you can configure it to write to your Dropbox folder (or whatever other data backup system you use) - in that way, you can keep track of your notes across computers :)
