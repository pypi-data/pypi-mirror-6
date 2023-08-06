// Example from http://qunitjs.com/intro/

QUnit.Django.start();

var prettyDate = {
  format: function(now, time) {
    var date = new Date(time || ""),
        diff = (((new Date(now)).getTime() - date.getTime()) / 1000),
        day_diff = Math.floor(diff / 86400);

    if (isNaN(day_diff) || day_diff < 0 || day_diff >= 31) {
      return;
    }

    return day_diff === 0 && (
            diff < 60 && "just now" ||
            diff < 120 && "1 minute ago" ||
            diff < 3600 && Math.floor(diff / 60) + " minutes ago" ||
            diff < 7200 && "1 hour ago" ||
            diff < 86400 && Math.floor(diff / 3600) + " hours ago") ||
        day_diff === 1 && "Yesterday" ||
        day_diff < 7 && day_diff + " days ago" ||
        day_diff < 31 && Math.ceil(day_diff / 7) + " weeks ago";
  },
 
  update: function(now) {
    var links = document.getElementsByTagName("a");
    for (var i = 0; i < links.length; i++) {
      if (links[i].title) {
        var date = prettyDate.format(now, links[i].title);
        if (date) {
          links[i].innerHTML = date;
        }
      }
    }
  }
};

test("prettydate.format", function() {
  function date(then, expected) {
    equal(prettyDate.format("2008/01/28 22:25:00", then), expected);
  }
  date("2008/01/28 22:24:30", "just now");
  date("2008/01/28 22:23:30", "1 minute ago");
  date("2008/01/28 21:23:30", "1 hour ago");
  date("2008/01/27 22:23:30", "Yesterday");
  date("2008/01/26 22:23:30", "2 days ago");
  date("2007/01/26 22:23:30", undefined);
});
 
function domtest(name, now, first, second) {
  test(name, function() {
    var links = document.getElementById("qunit-fixture").getElementsByTagName("a");
    equal(links[0].innerHTML, "January 28th, 2008");
    equal(links[2].innerHTML, "January 27th, 2008");
    prettyDate.update(now);
    equal(links[0].innerHTML, first);
    equal(links[2].innerHTML, second);
  });
}

domtest("prettyDate.update", "2008-01-28T22:25:00Z", "2 hours ago", "Yesterday");
domtest("prettyDate.update, one day later", "2008/01/29 22:25:00", "Yesterday", "2 days ago");

QUnit.Django.end();
