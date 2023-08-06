QUnit.Django.start();

test("html_strings test", function () {
  var dummy = document.getElementById("dummy");
  equal(dummy.innerHTML, "Here\'s the raw HTML for you.");
  ok(dummy);
});

QUnit.Django.end();

