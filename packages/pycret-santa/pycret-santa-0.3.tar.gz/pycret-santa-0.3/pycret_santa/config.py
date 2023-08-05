
import yaml

from pycret_santa import Separators
from pycret_santa.guests import Guest

class SmtpConfig(object):

  DEFAULT_HOST = "localhost"
  DEFAULT_PORT = 25

  def __init__(self, host=None, port=None, user=None, password=None):
    self.host = host
    self.port = port
    self.user = user
    self.password = password

  def initFromDict(self, params):
    self.host = params.get("host") or self.DEFAULT_HOST
    self.port = params.get("port") or self.DEFAULT_PORT
    self.user = params.get("username") or None


class MailParameters(object):

  DEFAULT_SENDER = "Santa Klaus %ssanta@somebod.com%s" % \
                    (Separators.MAIL_LEFT, Separators.MAIL_RIGHT)
  DEFAULT_SUBJECT = "Secret Santa!"

  def __init__(self, sender=DEFAULT_SENDER, subject=DEFAULT_SUBJECT,
               text=None):
    self.sender = sender
    self.subject = subject
    self.text = text

  def initFromDict(self, params):
    self.sender = Guest.initFromFormattedString(params.get("sender") \
                                                or self.DEFAULT_SENDER)
    self.subject = params.get("subject") or self.DEFAULT_SUBJECT
    self.subject.encode("utf-8")
    self.text = params["text"].encode("utf-8")


class SecretSantaParameters(object):

  def __init__(self, guestList=[], smtpConfig=None, mailParams=None):
    self.guestList = []
    self.smtp = smtpConfig or SmtpConfig()
    self.mail = mailParams or MailParameters()

  def initFromFile(self, filePath):
    with open(filePath, "r") as fd:
      params = yaml.load(fd)
    self.guestList = [Guest.initFromFormattedString(guestString) \
                      for guestString in params["Guests"]]
    self.smtp.initFromDict(params["Smtp"])
    self.mail.initFromDict(params["Mail"])
    self._handleCouples(params["Couples"])
    self._handleNoMatchList(params["No_match"])

  def initFromCommandLine(self):
    # TODO: implement this method...
    raise NotImplementedError("Sorry, this method is not available yet. "
                              "Please use a config file.")

  def _handleCouples(self, couplesList):
    self._updateUnauthorizedMatches(couplesList, Separators.COUPLE)

  def _handleNoMatchList(self, noMatchList):
    self._updateUnauthorizedMatches(noMatchList, Separators.NO_MATCH)

  def _updateUnauthorizedMatches(self, exclusionList, separator):
    for noMatchLine in exclusionList:
      members = noMatchLine.split(separator)
      first = members[0].strip().encode("utf-8")
      second = members[1].strip().encode("utf-8")
      for guest in self.guestList:
        if guest.name == first:
          guest.unauthorizedMatches.add(second)
        if separator == Separators.COUPLE:
          if guest.name == second:
            guest.unauthorizedMatches.add(first)
