# This file is auto-generated from regression.idl(0.5.2-68-g68e898d) with jenerator version 0.5.2-45-gc4cfc98/master
# *** DO NOT EDIT ***


import msgpackrpc
import jubatus.common
from .types import *
from jubatus.common.types import *

class Regression(jubatus.common.ClientBase):
  def __init__(self, host, port, name, timeout=10):
    super(Regression, self).__init__(host, port, name, timeout)

  def train(self, train_data):
    return self.jubatus_client.call("train", [train_data], TInt(True, 4),
        [TList(TUserDef(ScoredDatum))])

  def estimate(self, estimate_data):
    return self.jubatus_client.call("estimate", [estimate_data], TList(TFloat(
        )), [TList(TDatum())])

  def clear(self):
    return self.jubatus_client.call("clear", [], TBool(), [])
