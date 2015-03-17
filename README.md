InfoBot
=======
InfoBot just needs to be named at the start of a message, and it will reply with a report of all the values that Zulip needs to understand your message. It can be invoked in both public topics and private messages. InfoBot might be useful for other bot developers getting started, and might help pinpoint interesting things about how Zulip functions! InfoBot was started from the source code for Bot-Builder https://github.com/di0spyr0s/Bot-Builder

API
===
InfoBot can only be used by Hacker School Zulip users. All you have to do to use it is say "InfoBot", either in a public topic or in a private message, and it will reply. There is a slight difference in output for public topics and private messages. It has two optional parameters:  
-v, --verbose   (turns on verbose output)  
-nb, --no-box   (stops output from being boxed)