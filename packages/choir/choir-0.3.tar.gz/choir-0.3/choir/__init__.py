import requests
BASE = "http://api.choir.io/"
VERSION = "0.3"


EMO_E = ["g", "n", "b"]
EMO_I = [0, 1, 2, 3]


class ChoirError(Exception): pass


class Choir:
    """
        A simple client for Choir.io. 
    """
    def __init__(self, key, sprinkle=None, base=BASE):
        self.base = base + key
        self.sprinkle = sprinkle

    def emote(self, emo, intr, label, text=None, sprinkle=None, tag=None):
        """
            Uses Choir's flexible sound specification. Raises ChoirError in case
            of parameter errors. Returns True of message was succesfully sent,
            False otherwise.
        """
        emo = emo.lower()
        if not emo in EMO_E:
            raise ChoirError("Invalid emo - must be one of %s"%", ".join(EMO_E))
        if not intr in EMO_I:
            raise ChoirError("Invalid intrusiveness - must be one of %s"%", ".join(EMO_I))

        sound = "%s/%s"%(emo, intr)
        if tag:
            sound = sound + "/" + tag
        return self._send(sound, label, text=text, sprinkle=sprinkle)

    def say(self, pack, name, label, text=None, sprinkle=None):
        """
            Uses Choir's direct sound specification. Raises ChoirError in case
            of parameter errors. Returns True of message was succesfully sent,
            False otherwise.
        """
        return self._send("%s/%s"%(pack, name), label, text, sprinkle)

    def _send(self, sound, label, text=None, sprinkle=None):
        data = dict(sound = sound)
        if text:
            data["text"] = text
        if label:
            data["label"] = label
        data["sprinkle"] = sprinkle or self.sprinkle
        try:
            resp = requests.post(self.base, data=data)
        except requests.ConnectionError, v:
            return False
        if resp.status_code != 200:
            return False
        return True
