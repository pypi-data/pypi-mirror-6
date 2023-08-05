# This file is auto-generated from classifier.idl(0.4.5-347-g86989a6) with jenerator version 0.4.5-611-gb9472a4/master
# *** DO NOT EDIT ***


import msgpackrpc
import jubatus.common
from types import *
from jubatus.common.types import *

class Classifier(jubatus.common.ClientBase):
  def __init__(self, host, port, name, timeout=10):
    super(Classifier, self).__init__(host, port, name, timeout)

  def train(self, data):
    return self.jubatus_client.call("train", [data], TInt(True, 4), [TList(
        TUserDef(LabeledDatum))])

  def classify(self, data):
    return self.jubatus_client.call("classify", [data], TList(TList(TUserDef(
        EstimateResult))), [TList(TDatum())])

  def clear(self):
    return self.jubatus_client.call("clear", [], TBool(), [])
