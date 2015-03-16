import zulip
import json, requests, os, textwrap


class InfoBot():

    def __init__(self, zulip_username, zulip_api_key, key_word, subscribed_streams=[]):
        """
        InfoBot takes a zulip username and api key, a word or phrase to respond to,
        and a list of the zulip streams it should be active in.
        """
        self.username = zulip_username
        self.api_key = zulip_api_key
        self.key_word = key_word.lower()

        self.subscribed_streams = subscribed_streams
        self.client = zulip.Client(zulip_username, zulip_api_key)
        self.subscriptions = self.subscribe_to_streams()

        self.output_order = [
            "content", "recipient_id", "type", "display_recipient",
            "subject", "subject_links", "id", "timestamp", "content_type",
            "sender_full_name", "sender_short_name", "sender_id",
            "sender_email", "sender_domain", "client",
            "gravatar_hash", "avatar_url"]

    @property
    def streams(self):
        """Standardizes a list of streams in the form [{'name': stream}]"""
        if not self.subscribed_streams:
            streams = [{"name": stream["name"]} for stream in self.get_all_zulip_streams()]
            return streams
        else: 
            streams = [{"name": stream} for stream in self.subscribed_streams]
            return streams


    def get_all_zulip_streams(self):
        """Call Zulip API to get a list of all streams"""

        response = requests.get("https://api.zulip.com/v1/streams", auth=(self.username, self.api_key))
        if response.status_code == 200:
            return response.json()["streams"]
        elif response.status_code == 401:
            raise RuntimeError("check your auth")
        else:
            raise RuntimeError(":( we failed to GET streams.\n(%s)" % response)


    def subscribe_to_streams(self):
        """Subscribes to zulip streams"""
        self.client.add_subscriptions(self.streams)


    def respond(self, msg):
        """
        If key_word is the start of msg, it parses the message and options,
        then calls send_message()
        """

        content = msg["content"].lower()

        # makes sure InfoBot was the first word
        if content.find(self.key_word) == 0:

            verbose = "-v" in content or "--verbose" in content
            box = "-nb" not in content and "--no-box" not in content
            msg["content"] = self.parse_message(msg, verbose, box)
            self.send_message(msg)
               

    def send_message(self, msg):
        """Sends a message to zulip stream"""

        self.client.send_message({
            "type": "stream",
            "subject": msg["subject"],
            "to": msg["display_recipient"],
            "content": msg["content"]
            })


    def parse_message(self, msg, verbose, box):
        """
        Parses a given message to identify each value
        output can be verbose or not, by setting verbose to true or false
        verbose parsing gives hand written explanations for each value,
        and non-verbose parsing just gives a formatted display of values
        output can be captured in a box or not, by setting box to true or false
        """

        parsing = u""

        if not verbose:
            for key in self.output_order:
                parsing += "%s%s\n" % ("\t{:<20}".format(key), msg[key])
            if not box:
                parsing = parsing.replace("\t", "")
            parsing += "(Want verbose output? Say `InfoBot -v` or `InfoBot --verbose`!"
        else:
            # content ("hello") and recipient identifier
            parsing += ("A message with content `\"%s\"` was sent to recipient_id `%s`.\n\n\n"
                        % (msg["content"], msg["recipient_id"]))
            # destination type, stream:topic [subject links]
            parsing += ("The destination was of type `\"%s\"` and sent to "
                        "display_recipient (or `%s`) `\"%s\"`, at subject "
                        "(or topic) `\"%s\"`, along with subject_links `%s`.\n\n\n"
                        % (msg["type"], msg["type"], msg["display_recipient"],
                            msg["subject"], msg["subject_links"]))
            # message id, timestamp, and content type
            parsing += ("The message has an id of `%s`, sent at timestamp `%s`, "
                        "and has the content_type `\"%s\"`.\n\n\n"
                        % (msg["id"], msg["timestamp"], msg["content_type"]))
            # sender full name, short name, id, and email
            parsing += ("The message came from sender_full_name `\"%s\"`, known "
                        "also as sender_short_name `\"%s\"` who has a sender_id "
                        "of `%s`, and a sender_email of `\"%s\"`.\n\n\n"
                        % (msg["sender_full_name"], msg["sender_short_name"],
                            msg["sender_id"], msg["sender_email"]))
            # sender domain, client
            parsing += ("The sender_domain is `\"%s\"`, using client `\"%s\"`.\n\n\n"
                        % (msg["sender_domain"], msg["client"]))
            # gravatar hash and avatar url
            parsing += ("The gravatar_hash of the sender's avatar is `%s`, "
                        "and their avatar_url is `%s`.\n\n\n"
                        % (msg["gravatar_hash"], msg["avatar_url"]))
            
            parsing = parsing.replace("\"", "") if box else parsing.replace("`", "")
            parsing += "\n(Don't want verbose output? Say just `InfoBot`!"
            
        parsing += "\nYou can also turn off box printing with `-nb` or `--no-box`!)"
        return parsing


    def main(self):
        """Blocking call that runs forever. Calls self.respond() on every message received."""
        self.client.call_on_each_message(lambda msg: self.respond(msg))


zulip_username = os.environ["ZULIP_USR"]
zulip_api_key = os.environ["ZULIP_API"]
key_word = "InfoBot"
subscribed_streams = []

bot = InfoBot(zulip_username, zulip_api_key, key_word, subscribed_streams)
bot.main()