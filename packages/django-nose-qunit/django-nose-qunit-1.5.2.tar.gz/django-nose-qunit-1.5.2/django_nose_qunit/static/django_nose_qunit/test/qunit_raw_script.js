/*global raw_script */
QUnit.Django.start();

test("raw_script_urls test: django URL", function () {
  // /raw-script/ url loads a script tag w/a global var defined
  ok(typeof raw_script !== "undefined");
  ok(raw_script);
});

QUnit.Django.end();
