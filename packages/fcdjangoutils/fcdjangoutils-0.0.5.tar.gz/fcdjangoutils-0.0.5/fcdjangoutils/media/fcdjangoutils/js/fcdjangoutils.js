var fcdjangoutils = {
  itemIdx : 0
};

String.prototype.format = function() {
  var res = "";
  var aIdx = 0;
  var idx = 0;
  var input = String(this);  // make sure we are operating on a string ('this' is an 'object' in IE)

  while (idx < input.length) {
    switch (input.charAt(idx)) {
    case '%':
      switch (input.charAt(idx + 1)) {
      case '%':
        res += '%';
        idx += 2;
        break;
      case 's':
        res += (new String(arguments[aIdx++])).toString();
        idx += 2;
        break;

      case '(':
        var end = input.indexOf(')', idx);
        if (end == -1)
          throw "Invalid format string";

        var name = input.substr(idx + 2, end - idx - 2);
        idx = end + 1;
        switch (input.charAt(idx)) {
        case 's':
          res += (new String(arguments[0][name])).toString();
          idx++;
          break;

        default:
          throw "Unsupported format option: '" + input.charAt(idx) + "'";

        }
        break;
      default:
        throw "Unsupported format option: '" + input.charAt(idx + 1) + "'";
      }
      break;

    default:
      res += input.charAt(idx);
      idx++;
      break;
    }
  }

  return res;
};

Date.prototype.getWeek = function() {
  var onejan = new Date(this.getFullYear(), 0, 1);
  return Math.ceil((((this - onejan) / 86400000) + onejan.getDay() + 1) / 7);
};

fcdjangoutils.formatTimeField = function(value) {
  var tm = fcdjangoutils.parseTimeField(value);
  return tm[0] + ":" + (tm[1] < 10 ? '0' : '') + tm[1];
};

fcdjangoutils.join = function(str, arr) {
  return _.reduce(_.rest(arr), function(prev, val) {
    return prev + str + val;
  }, _.first(arr));

};

fcdjangoutils.message = function(msg, id, style, fadeOut) {
  style = style || 'message';
  var lst = $('#messages');
  var line = $('<li>').text(msg).addClass(style);
  if (id) {
    $('#' + id, lst).detach();
    line.attr('id', id);
  }
  lst.append(line);

  if (fadeOut) {
    setTimeout(function() {
      line.fadeOut();
    }, 5000);
  }
};

fcdjangoutils.error = function(msg, id) {
  fcdjangoutils.message(msg, id, 'error');
};

fcdjangoutils.warning = function(msg, id) {
  fcdjangoutils.message(msg, id, 'warning');
};

fcdjangoutils.fromIsoDate = function(txt) {
  var darr = txt.split("-");
  if (darr.length != 3)
    return null;
  // Input is iso date, but javascript expects
  // month component in range 0..11,
  // so we subtract one from the month
  darr[1] -= 1;
  return new Date(Date.UTC.apply(null, darr));
};

fcdjangoutils.toIsoDate = function(date) {
  var month = date.getMonth() + 1;
  var day = date.getDate();
  return "" + date.getFullYear() + "-" + ((month < 10 ? '0' : '') + month) + "-" + ((day < 10 ? '0' : '') + day);
};

/**
 * Get the number of hours, minutes and seconds from a number just consisting of
 * seconds.
 */
fcdjangoutils.parseTimeField = function(totalSeconds) {
  var tm = parseInt(totalSeconds, 10);
  var hours = Math.floor(tm / 3600);
  var minutes = Math.floor((tm % 3600) / 60);
  var seconds = Math.floor(tm % 60);
  return [ hours, minutes, seconds ];
};

/**
 * Mangles a valid form name attribute into something that can be used as a dom
 * id by replacing all unholy characters with underscores.
 */
fcdjangoutils.nameToId = function(name) {
  return name.replace(/[^a-zA-Z0-9_]/g, '_');
};

/*
 * Make sure the application works even if console debugging is used without an
 * active Firebug.
 */
if(typeof(console) == 'undefined') {
  var console = {};
  console.log = console.error = console.info = console.debug = console.warn =
    console.trace = console.dir = console.dirxml = console.group =
    console.groupEnd = console.time = console.timeEnd = console.assert =
    console.profile = function() {};
};

$.extend($.validator.messages, {
  required : gettext("This field is required."),
  remote : gettext("Please fix this field."),
  email : gettext("Please enter a valid email address."),
  url : gettext("Please enter a valid URL."),
  date : gettext("Please enter a valid date."),
  dateISO : gettext("Please enter a valid date (ISO)."),
  number : gettext("Please enter a valid number."),
  digits : gettext("Please enter only digits."),
  creditcard : gettext("Please enter a valid credit card number."),
  equalTo : gettext("Please enter the same value again."),
  accept : gettext("Please enter a value with a valid extension."),
  maxlength : $.validator.format(gettext("Please enter no more than {0} characters.")),
  minlength : $.validator.format(gettext("Please enter at least {0} characters.")),
  rangelength : $.validator.format(gettext("Please enter a value between {0} and {1} characters long.")),
  range : $.validator.format(gettext("Please enter a value between {0} and {1}.")),
  max : $.validator.format(gettext("Please enter a value less than or equal to {0}.")),
  min : $.validator.format(gettext("Please enter a value greater than or equal to {0}."))
});

/* Create a number type that accepts both ',' and '.' as a decimal separator. */
$.validator.addMethod("uninumber", function(value, element) {
  return this.optional(element) || /^-?(?:\d+|\d{1,3}(?:,\d{3})+)(?:[.,]\d+)?$/.test(value);
}, gettext("Please enter a valid number."));


fcdjangoutils.findFirst = function(collection, test) {
  var res = null;
  $.each(collection, function(key, value) {
    if (test.apply(value, [ value ])) {
      res = value;
      return false;
    }
    return true;
  });
  return res;
};

fcdjangoutils.findLast = function(collection, test) {
  var res = null;
  $.each(collection, function(key, value) {
    if (test.apply(value, [ key, value ])) {
      res = value;
    }
  });
  return res;
};

fcdjangoutils.template = function(name) {
  return $('.template .' + name).html().replace(/\.\.\./g, fcdjangoutils.itemIdx++);
};

fcdjangoutils.Timer = function() {
  this.interval=0;

  this.start = function(){
    this.stopTime = null;
    this.startTime = (new Date().getTime());
    return this;
  };

  this.stop = function(){
    if(!this.startTime){
      this.stopTime = null;
      } else {
	this.stopTime = (new Date().getTime());
      this.interval += (this.stopTime - this.startTime);
    }
    return this;
  };

  this.time = function(){
    if(!this.startTime) {
      return null;
    }
    if(!this.stopTime) {
      this.stop();
    }
    return this.interval;
  };

  this.reset = function(){
    this.interval = 0;
    return this.time();
  };

};

$.fn.fcProgressbar = function(options) {
  this.progressbar(options);
  if(!('text' in options)){
    options.text=options.value;
  }
  if(options.value > 55){
    $(this).find("div").html($("<span class='inside'></span>").text(options.text));
  }
  else {
    $(this).find("div").after($("<div class='outer-div'></div>").html($("<span class='outside'></span>").text(options.text)));
  }
};
