/* A generic object system */
function Obj() {};
Obj.prototype.idSeq = 0;
Obj.prototype.create = function () {
  var F = function () {};
  F.prototype = this;
  var res = new F();
  res.id = Obj.idSeq++;
  return res;
};
Obj.prototype.subclassinit = function (name) { this.__name__ = name; }
Obj.prototype.subclass = function () {
  var cls = this.create();
  cls.subclassinit.apply(cls, arguments);
  return cls;
};
Obj.prototype.init = function () {}
Obj.prototype.instantiate = function () {
  var obj = this.create();
  obj.init.apply(obj, arguments);
  return obj;
};
Obj = new Obj();
