#!/bin/env python3

class TextEnd():
  def __repr__(self): return "TextEnd";
  def __str__ (self): return "TextEnd";
class ParseUtil():
  def __init__(self, text):
    self.text  = text;
    self.tlen  = len(text);
    self.index = 0;
    self.stack = [0];
  def read(self, count=1):
    if self.index+count>self.tlen:
      return TextEnd;
    self.index     += count;
    self.stack[-1] += count;
    return self.text[self.index-count:self.index];
  def push(self):
    self.stack.append(0);
  def pop (self, success=True):
    if success:
      self.stack[-2] += self.stack[-1];
    else:
      self.index     -= self.stack[-1];
    del self.stack[-1];

class NotMatch(Exception): None;
def ParseFunc(func):
  def ret_func(putil, *args, **kwargs):
    putil.push();
    try: result = func(putil, *args, **kwargs);
    except NotMatch: putil.pop(False); raise;
    putil.pop(True);
    return result;
  ret_func.func = func;
  return ret_func;
def DefineFunc(pfunc):
  def ret_func(*args, **kwargs):
    def ret_func2(putil): return pfunc(putil, *args, **kwargs);
    ret_func2.args   = args;
    ret_func2.kwargs = kwargs;
    return ret_func2;
  ret_func.pfunc = pfunc;
  return ret_func;

@DefineFunc
@ParseFunc
def achar(putil, chars):
  ch = putil.read();
  if ch == TextEnd or not ch in chars:
    raise NotMatch(str(ch));
  return ch;
@DefineFunc
@ParseFunc
def astr(putil, string):
  s  = putil.read(len(string));
  if s == TextEnd or not s == string:
    raise NotMatch(str(s));
  return s;
@DefineFunc
@ParseFunc
def txtend(putil):
  ch = putil.read();
  if ch != TextEnd: raise NotMatch(str(ch));
  return TextEnd;

@DefineFunc
@ParseFunc
def pseq(putil, *pfuncs): # <a><b>
  result = [];
  for pfunc in pfuncs:
    result.append(pfunc(putil));
  return result;
@DefineFunc
@ParseFunc
def psel(putil, *pfuncs): # <a>|<b>
  for pfunc in pfuncs:
    try: return pfunc(putil);
    except NotMatch as nme: nm = nme;
  raise nm;
@DefineFunc
@ParseFunc
def popt(putil, apfunc): # [a]
  try: return apfunc(putil);
  except NotMatch: return None;
@DefineFunc
@ParseFunc
def prpt(putil, apfunc): # {a}
  repeats = [];
  try:
    while True: repeats.append(apfunc(putil));
  except NotMatch: return repeats;

# definition
digits = achar('01234567890');
unsign = pseq(digits, prpt(digits));
signed = pseq(popt(achar('-')), unsign);
opt2 = achar('*/');
opt1 = achar('-+');
opr2 = lambda putl: pseq(opr , prpt(pseq(opt2, opr )))(putl);
opr1 = lambda putl: pseq(opr2, prpt(pseq(opt1, opr2)))(putl);
expr = opr1;
opr  = psel(signed, pseq(achar('('), expr, achar(')')));
syntax = pseq(expr, txtend());
# simplify
def s_syntax(syn):
  return s_expr(syn[0]);
def s_expr(expr):
  return s_opr1(expr);
def s_opt1(opt1): return opt1;
def s_opr1(opr1):
  result = [None, None];
  result[0] = s_opr2(opr1[0]);
  result[1] = [
    [s_opt1(opt1), s_opr2(opr2)] for opt1, opr2 in opr1[1]
  ];
  return result;
def s_opt2(opt2): return opt2;
def s_opr2(opr2):
  result = [None, None];
  result[0] = s_opr(opr2[0]);
  result[1] = [
    [s_opt2(opt2), s_opr(opr)]   for opt2, opr  in opr2[1]
  ];
  return result;
def s_opr(opr):
  if opr[0] == '(':
    return s_expr(opr[1]);
  else:
    return s_signed(opr);
def s_signed(signed):
  sign     = [-1,1][signed[0]==None];
  unsigned = s_unsigned(signed[1]);
  return sign*unsigned;
def s_unsigned(unsigned):
  number   = unsigned[0] + ''.join(unsigned[1]);
  return int(number);
# evaluation
def e_syntax(syn):
  return e_expr(syn);
def e_expr(expr):
  return e_opr1(expr);
def e_opr1(opr1):
  value = e_opr2(opr1[0]);
  for opt1, opr2 in opr1[1]:
    val = e_opr2(opr2);
    if opt1 == '-':
      value -= val;
    else:
      value += val;
  return value;
def e_opr2(opr2):
  value = e_opr(opr2[0]);
  for opt2, opr  in opr2[1]:
    val = e_opr(opr);
    if opt2 == '*':
      value *= val;
    else:
      value /= val;
  return value;
def e_opr(opr):
  if type(opr)!=list:
    return opr;
  else:
    return e_expr(opr);
# example
def Parse(sb):
  p = ParseUtil(sb);
  r = syntax(p);
  s = s_syntax(r);
  e = e_syntax(s);
  return e;
